from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Sequence, Tuple, Callable
import re

from search.ports.embeddings import EmbeddingsProvider
from search.ports.user_vectors import UserVectorRepository
from search.utils.ingest import (
    normalize_text,
    hash_text,
    coerce_embedding,
    batched,
    safe_join_fields,
)


@dataclass
class IngestPayloads:
    ids: List[str]
    descriptions: List[str]
    documents: List[str]
    metadatas: List[Dict[str, Any]]

    def __post_init__(self) -> None:
        n = {len(self.ids), len(self.descriptions), len(self.documents), len(self.metadatas)}
        if len(n) != 1:
            raise ValueError(
                "IngestPayloads length mismatch: "
                f"ids={len(self.ids)}, descriptions={len(self.descriptions)}, "
                f"documents={len(self.documents)}, metadatas={len(self.metadatas)}"
            )


# ---- Strategy API --------------------------------------------------------------

class IngestStrategy:
    def run(
            self,
            embeddings: EmbeddingsProvider,
            repo: UserVectorRepository,
            payloads: IngestPayloads,
            *,
            embed_model: str | None,
            verbose: bool = False,
    ) -> Tuple[int, List[str]]:
        raise NotImplementedError


# ---- Shared core for reuse/compute ---------------------------------------------

def _reuse_or_compute_embeddings(
        *,
        ids: Sequence[str],
        texts: Sequence[str],
        metadatas: Sequence[Dict[str, Any]],
        repo: UserVectorRepository,
        embeddings: EmbeddingsProvider,
        embed_model: str | None,
        verbose: bool,
        batch_size: int | None = None,
) -> List[List[float]]:
    """
    For each id/text/metadata:
      - Try to reuse stored embedding if (hash + model) match.
      - Otherwise compute with provider (optionally in batches).
    Returns embeddings aligned with `ids`.
    """
    if not (len(ids) == len(texts) == len(metadatas)):
        raise ValueError("ids/texts/metadatas must be same length")

    existing: Mapping[str, Dict[str, Any]] = repo.get_by_ids(list(ids), include_embeddings=True) or {}
    vectors: List[List[float]] = [[] for _ in ids]
    to_compute_idx: List[int] = []
    reasons: List[str] = []

    for i, rid in enumerate(ids):
        item = existing.get(rid)
        if not item:
            to_compute_idx.append(i)
            if verbose:
                reasons.append(f"{rid}: missing")
            continue

        meta = item.get("metadata", {}) if isinstance(item, dict) else {}
        expected_hash = metadatas[i].get("embed_hash")
        ok_hash = (meta.get("embed_hash") == expected_hash)
        ok_model = (embed_model is None) or (meta.get("embed_model") == embed_model)

        emb_list = coerce_embedding(item.get("embedding") if isinstance(item, dict) else None)
        if ok_hash and ok_model and emb_list:
            vectors[i] = emb_list
            if verbose:
                reasons.append(f"{rid}: reused")
        else:
            to_compute_idx.append(i)
            if verbose:
                if not emb_list:
                    reasons.append(f"{rid}: no embedding stored")
                elif not ok_hash:
                    reasons.append(f"{rid}: hash changed")
                elif not ok_model:
                    reasons.append(f"{rid}: model changed")

    # Compute missing
    if to_compute_idx:
        texts_to_compute = [texts[i] for i in to_compute_idx]
        if batch_size and batch_size > 0:
            cursor = 0
            for batch in batched(texts_to_compute, batch_size):
                new_vecs = embeddings.embed_texts(list(batch))
                for j, vec in enumerate(new_vecs):
                    vectors[to_compute_idx[cursor + j]] = list(vec)
                cursor += len(batch)
        else:
            new_vecs = embeddings.embed_texts(texts_to_compute)
            for j, i in enumerate(to_compute_idx):
                vectors[i] = list(new_vecs[j])

    if verbose:
        reused_count = sum(1 for v in vectors if v)
        computed_count = len(to_compute_idx)
        print(
            f"Embeddings reuse: found={len(existing)}, reused={reused_count}, computed={computed_count}, total={len(ids)}")
        for line in reasons:
            print(f"  {line}")

    return vectors


# ---- Whole-document strategy ---------------------------------------------------

class WholeDocStrategy(IngestStrategy):
    """
    Embeds the whole `description` for each id once.
    Upserts `documents` as provided, with vectors aligned to `ids`.
    """

    def __init__(self, *, embed_batch_size: int | None = None) -> None:
        self.embed_batch_size = embed_batch_size

    def run(
            self,
            embeddings: EmbeddingsProvider,
            repo: UserVectorRepository,
            payloads: IngestPayloads,
            *,
            embed_model: str | None,
            verbose: bool = False,
    ) -> Tuple[int, List[str]]:
        ids = payloads.ids
        descriptions = payloads.descriptions
        documents = payloads.documents
        metadatas = payloads.metadatas

        # Ensure embed model & hash are stamped consistently
        for i, m in enumerate(metadatas):
            if embed_model is not None:
                m["embed_model"] = embed_model
            # If caller didn't provide embed_hash, compute from normalized description
            m.setdefault("embed_hash", hash_text(descriptions[i]))
            # Add full description as chunk_text for consistency with chunked strategy
            m["chunk_text"] = descriptions[i]

        vectors = _reuse_or_compute_embeddings(
            ids=ids,
            texts=descriptions,
            metadatas=metadatas,
            repo=repo,
            embeddings=embeddings,
            embed_model=embed_model,
            verbose=verbose,
            batch_size=self.embed_batch_size,
        )

        repo.upsert(ids, documents, vectors, metadatas)
        return len(ids), list(ids)


# ---- Base chunking strategy ----------------------------------------------------

class _BaseChunkedStrategy(IngestStrategy):
    """
    Reusable core for chunk-based ingestion strategies.
    Subclasses must supply `chunker` and `chunk_kind`.
    """

    chunk_kind: str = "sentence"  # override in subclass
    id_prefix: str = "c"  # "c" for sentence chunks, "t" for token chunks

    def __init__(
            self,
            *,
            chunker: Callable[[str], List[str]],
            embed_batch_size: int | None = None,
            enrich_parent_fields: Sequence[str] = ("first_name", "last_name", "email", "phone", "phone_digits"),
    ) -> None:
        self._chunker = chunker
        self.embed_batch_size = embed_batch_size
        self._enrich_fields = tuple(enrich_parent_fields)

    def run(
            self,
            embeddings: EmbeddingsProvider,
            repo: UserVectorRepository,
            payloads: IngestPayloads,
            *,
            embed_model: str | None,
            verbose: bool = False,
    ) -> Tuple[int, List[str]]:
        ids = payloads.ids
        descriptions = payloads.descriptions
        metadatas = payloads.metadatas

        # Build per-chunk records
        all_ids: List[str] = []
        all_docs: List[str] = []
        all_metas: List[Dict[str, Any]] = []
        chunk_texts: List[str] = []

        for i, rid in enumerate(ids):
            desc = descriptions[i]
            chunks = self._chunker(desc) or [desc]
            total = len(chunks)

            # Pre-resolve enrichment fields from parent metadata (avoid repeated dict lookups)
            parent_meta = metadatas[i]
            enrich_values = [normalize_text(str(parent_meta.get(k, ""))) for k in self._enrich_fields]
            enrich_tail = safe_join_fields(rid, *enrich_values)

            for ci, chunk in enumerate(chunks):
                cid = f"{rid}#{self.id_prefix}{ci:04d}"

                # Document content = chunk + (optionally) enrichment tail.
                # Keeping your behavior but safer: only append if non-empty.
                doc = safe_join_fields(chunk, enrich_tail)

                meta = dict(parent_meta)
                if embed_model is not None:
                    meta["embed_model"] = embed_model
                meta["parent_id"] = rid
                meta["chunk_index"] = ci
                meta["chunk_count"] = total
                meta["chunk_text"] = chunk
                meta["chunk_kind"] = self.chunk_kind
                meta["embed_hash"] = hash_text(chunk)

                all_ids.append(cid)
                all_docs.append(doc)
                all_metas.append(meta)
                chunk_texts.append(chunk)

        vectors = _reuse_or_compute_embeddings(
            ids=all_ids,
            texts=chunk_texts,
            metadatas=all_metas,
            repo=repo,
            embeddings=embeddings,
            embed_model=embed_model,
            verbose=verbose,
            batch_size=self.embed_batch_size,
        )

        repo.upsert(all_ids, all_docs, vectors, all_metas)

        if verbose:
            print(f"Indexed {self.chunk_kind}-chunks: records={len(all_ids)} from parents={len(ids)}")
        return len(ids), list(ids)


# ---- Sentence-chunk strategy ---------------------------------------------------

class ChunkedStrategy(_BaseChunkedStrategy):
    def __init__(self, sentences_per_chunk: int = 3, sentence_overlap: int = 1, *,
                 embed_batch_size: int | None = None) -> None:
        self.sentences_per_chunk = max(1, sentences_per_chunk)
        self.sentence_overlap = max(0, sentence_overlap)
        super().__init__(chunker=self._chunk_text_sentences, embed_batch_size=embed_batch_size)
        self.chunk_kind = "sentence"
        self.id_prefix = "c"

    def _chunk_text_sentences(self, s: str) -> List[str]:
        sents = self._split_sentences(s)
        if not sents:
            return [s]
        per = self.sentences_per_chunk
        ov = self.sentence_overlap
        step = max(1, per - ov)
        out: List[str] = []
        i = 0
        n = len(sents)
        while i < n:
            chunk_sents = sents[i: i + per]
            out.append(" ".join(chunk_sents).strip())
            if i + per >= n:
                break
            i += step
        return out

    @staticmethod
    def _split_sentences(s: str) -> List[str]:
        """Naive sentence splitter on punctuation (., !, ?). Keeps punctuation attached."""
        s = s.strip()
        if not s:
            return []
        parts = re.split(r"(?<=[.!?])\s+", s)
        return [p.strip() for p in parts if p and p.strip()]


# ---- Token-chunk strategy ------------------------------------------------------

class TokenChunkStrategy(_BaseChunkedStrategy):
    def __init__(self, tokens_per_chunk: int = 200, token_overlap: int = 50, *,
                 embed_batch_size: int | None = None) -> None:
        self.tokens_per_chunk = max(1, tokens_per_chunk)
        self.token_overlap = max(0, token_overlap)
        super().__init__(chunker=self._chunk_text_tokens, embed_batch_size=embed_batch_size)
        self.chunk_kind = "token"
        self.id_prefix = "t"

    def _chunk_text_tokens(self, s: str) -> List[str]:
        toks = self._tokenize(s)
        if not toks:
            return [s]
        per = self.tokens_per_chunk
        ov = self.token_overlap
        step = max(1, per - ov)
        out: List[str] = []
        i = 0
        n = len(toks)
        while i < n:
            chunk_toks = toks[i: i + per]
            out.append(" ".join(chunk_toks).strip())
            if i + per >= n:
                break
            i += step
        return out

    @staticmethod
    def _tokenize(s: str) -> List[str]:
        # Lightweight word-ish tokenizer: words and punctuation separated
        parts = re.findall(r"\w+|[^\w\s]", s or "")
        return [p for p in parts if p and p.strip()]
