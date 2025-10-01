from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from search.services.ingest_strategies import (
    IngestPayloads,
    WholeDocStrategy,
    ChunkedStrategy,
    TokenChunkStrategy,
)
from search.utils.ingest import hash_text


class FakeEmbeddings:
    def __init__(self, dim: int = 3) -> None:
        self.dim = dim
        self.calls: List[List[str]] = []

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        self.calls.append(list(texts))
        # Return simple deterministic vectors per call index
        base = [1.0] * self.dim
        return [base[:] for _ in texts]


class FakeRepo:
    def __init__(self, existing: Mapping[str, Dict[str, Any]] | None = None) -> None:
        self._existing = dict(existing or {})
        self.upserts: List[Tuple[List[str], List[str], List[List[float]], List[Dict[str, Any]]]] = []

    @property
    def metadata(self) -> Dict[str, Any] | None:
        return {"hnsw:space": "cosine", "model": "dummy"}

    def upsert(self, ids, documents, vectors, metadatas=None):
        self.upserts.append((list(ids), list(documents), list(vectors), list(metadatas or [])))

    def query(self, vector: List[float], k: int, where_document: str | None = None):
        raise NotImplementedError

    def get_by_ids(self, ids: List[str], include_embeddings: bool = False):
        out: Dict[str, Dict[str, Any]] = {}
        for rid in ids:
            if rid in self._existing:
                out[rid] = self._existing[rid]
        return out


def _payloads() -> IngestPayloads:
    ids = ["u1", "u2"]
    descs = ["Hello world.", "Another user."]
    docs = ["D1", "D2"]
    metas = [{}, {}]
    return IngestPayloads(ids=ids, descriptions=descs, documents=docs, metadatas=metas)


def test_whole_doc_strategy_reuse_and_compute():
    payloads = _payloads()
    # Pre-store embedding for u1 with matching hash+model
    m0 = {"embed_hash": hash_text(payloads.descriptions[0]), "embed_model": "m"}
    existing = {
        "u1": {"embedding": [0.5, 0.5, 0.5], "metadata": m0},
    }
    repo = FakeRepo(existing)
    emb = FakeEmbeddings()

    strat = WholeDocStrategy()
    n, ids = strat.run(embeddings=emb, repo=repo, payloads=payloads, embed_model="m", verbose=True)

    assert n == 2 and ids == payloads.ids
    assert repo.upserts, "Expected an upsert call"
    up_ids, _docs, vectors, metas = repo.upserts[-1]
    assert up_ids == payloads.ids
    # u1 reused, u2 computed
    assert vectors[0] == [0.5, 0.5, 0.5]
    assert vectors[1] == [1.0, 1.0, 1.0]
    # embed_model stamped and embed_hash present
    for i, m in enumerate(metas):
        assert m["embed_model"] == "m"
        assert "embed_hash" in m


def test_sentence_chunk_strategy_builds_chunks_and_metadata():
    ids = ["p1"]
    descs = ["One. Two! Three?"]
    payloads = IngestPayloads(ids=ids, descriptions=descs, documents=[""], metadatas=[{"first_name": "A", "last_name": "B", "email": "x@y", "phone": "+1", "phone_digits": "1"}])
    emb = FakeEmbeddings()
    repo = FakeRepo()
    strat = ChunkedStrategy(sentences_per_chunk=1, sentence_overlap=0)
    n, out_ids = strat.run(embeddings=emb, repo=repo, payloads=payloads, embed_model="m", verbose=True)
    assert n == 1 and out_ids == ids
    up_ids, docs, vectors, metas = repo.upserts[-1]
    assert up_ids == ["p1#c0000", "p1#c0001", "p1#c0002"]
    # docs include enrichment tail (parent id and fields), not empty
    assert all("p1" in d for d in docs)
    # per-chunk metadata
    assert metas[0]["parent_id"] == "p1"
    assert metas[0]["chunk_index"] == 0
    assert metas[0]["chunk_count"] == 3
    assert metas[0]["chunk_kind"] == "sentence"
    assert metas[0]["embed_model"] == "m"
    assert metas[0]["embed_hash"] == hash_text("One.")


def test_token_chunk_strategy_overlap_and_ids():
    ids = ["t1"]
    descs = ["alpha beta gamma delta"]
    payloads = IngestPayloads(ids=ids, descriptions=descs, documents=[""], metadatas=[{}])
    emb = FakeEmbeddings()
    repo = FakeRepo()
    strat = TokenChunkStrategy(tokens_per_chunk=3, token_overlap=1)
    n, out_ids = strat.run(embeddings=emb, repo=repo, payloads=payloads, embed_model=None, verbose=False)
    assert n == 1 and out_ids == ids
    up_ids, docs, vectors, metas = repo.upserts[-1]
    # Expected chunks: [alpha beta gamma], [gamma delta]
    assert up_ids == ["t1#t0000", "t1#t0001"]
    assert metas[0]["chunk_kind"] == "token"
    assert metas[0]["chunk_text"].startswith("alpha beta")

