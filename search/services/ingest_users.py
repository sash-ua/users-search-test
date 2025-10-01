from typing import Any, Dict, List, Tuple
import hashlib

from search.models.user import User
from search.ports.embeddings import EmbeddingsProvider
from search.ports.user_vectors import UserVectorRepository
from search.utils.ingest import normalize_text
from search.utils.load_data import load_json
from search.utils.map_data import normalize_phone_for_search
from search.services.ingest_strategies import (
    IngestPayloads,
    IngestStrategy,
    WholeDocStrategy,
    ChunkedStrategy,
    TokenChunkStrategy,
)


def build_payloads(
    data_path: str, normalize: bool = False, min_chars: int = 0
) -> Tuple[List[str], List[str], List[str], List[Dict[str, Any]]]:
    ids: List[str] = []
    descriptions: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    for raw in load_json(data_path):
        user = User(**raw)
        desc = user.description
        if normalize:
            desc = normalize_text(desc).lower()
        if not desc or len(desc.strip()) < min_chars:
            continue
        ids.append(user.username)
        descriptions.append(desc)
        phone_display = str(user.phone or "")
        phone_digits = normalize_phone_for_search(raw.get("phone", "") or phone_display)
        embed_hash = hashlib.sha256((desc or "").encode("utf-8")).hexdigest()
        metadatas.append(
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": phone_display,
                "phone_digits": phone_digits,
                # Used to decide whether to reuse an existing embedding
                "embed_hash": embed_hash,
            }
        )
        documents.append(
            f"{desc} {user.username} {user.first_name} {user.last_name} {user.email} {phone_display} {phone_digits}"
        )
    return ids, descriptions, documents, metadatas


def ingest(
    embeddings: EmbeddingsProvider,
    repo: UserVectorRepository,
    data_path: str,
    normalize: bool,
    min_chars: int,
    embed_model: str | None = None,
    index_chunks: bool = False,
    sentences_per_chunk: int = 3,
    sentence_overlap: int = 1,
    chunking_mode: str = "sentence",
    tokens_per_chunk: int = 200,
    token_overlap: int = 50,
    verbose: bool = False,
) -> Tuple[int, List[str]]:
    ids, descriptions, documents, metadatas = build_payloads(
        data_path, normalize, min_chars
    )
    payloads = IngestPayloads(
        ids=ids, descriptions=descriptions, documents=documents, metadatas=metadatas
    )
    strategy: IngestStrategy
    if index_chunks:
        if (chunking_mode or "sentence").lower() == "token":
            strategy = TokenChunkStrategy(tokens_per_chunk=tokens_per_chunk, token_overlap=token_overlap)
        else:
            strategy = ChunkedStrategy(sentences_per_chunk=sentences_per_chunk, sentence_overlap=sentence_overlap)
    else:
        strategy = WholeDocStrategy()
    return strategy.run(
        embeddings=embeddings,
        repo=repo,
        payloads=payloads,
        embed_model=embed_model,
        verbose=verbose,
    )
