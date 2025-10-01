from typing import Any, Dict, List

from search.services.ingest_users import ingest


class FakeEmbeddings:
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        # deterministic vector per text length
        return [[float(len(t)), 0.0, 1.0] for t in texts]


class CaptureRepo:
    def __init__(self) -> None:
        self.upserts: list[dict[str, Any]] = []

    def get_by_ids(self, ids: List[str], include_embeddings: bool = False):
        return {}

    def upsert(self, ids, documents, vectors, metadatas=None):
        self.upserts.append({
            'ids': ids,
            'documents': documents,
            'vectors': vectors,
            'metadatas': metadatas,
        })


def test_token_chunking_produces_token_chunks(tmp_path):
    # Create a small data file with no sentence punctuation to stress sentence-splitter
    data = [
        {
            "first_name": "Alice",
            "last_name": "Bond",
            "age": 30,
            "phone": None,
            "username": "u1u",
            "email": "u1@example.com",
            "description": " ".join(["word"] * 120),
        }
    ]
    p = tmp_path / 'data.json'
    p.write_text(__import__('json').dumps(data), encoding='utf-8')

    emb = FakeEmbeddings()
    repo = CaptureRepo()

    count, ids = ingest(
        emb,
        repo,  # type: ignore[arg-type]
        str(p),
        normalize=False,
        min_chars=0,
        embed_model=None,
        index_chunks=True,
        chunking_mode='token',
        tokens_per_chunk=50,
        token_overlap=10,
        verbose=False,
    )

    # Validate that chunks were created with token-based IDs and metadata
    assert count == 1
    assert ids == ["u1u"]
    assert repo.upserts, "Expected an upsert call"
    up = repo.upserts[-1]
    chunk_ids = up['ids']

    assert any(cid.startswith('u1u#t') for cid in chunk_ids), "Expected token-chunk ids"
    metas: List[Dict[str, Any]] = up['metadatas']
    assert metas and all(m.get('chunk_kind') == 'token' for m in metas), "chunk_kind should be 'token'"
    assert all(m.get('chunk_count') == 3 for m in metas)
    assert all(m.get('parent_id') == 'u1u' for m in metas)
