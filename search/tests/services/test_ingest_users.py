import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from search.services.ingest_users import build_payloads, ingest


class FakeEmbeddings:
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class CaptureRepo:
    def __init__(self) -> None:
        self.calls: List[Tuple[List[str], List[str], List[List[float]], List[Dict[str, Any]]]] = []

    def upsert(self, ids, documents, vectors, metadatas=None):
        self.calls.append((list(ids), list(documents), list(vectors), list(metadatas or [])))

    def query(self, *a, **k):
        raise NotImplementedError

    def get_by_ids(self, *a, **k):
        return {}


def _write_users(path: Path, desc: str = "A description") -> None:
    data = [
        {
            "username": "alice",
            "email": "alice@example.com",
            "description": desc,
            "first_name": "Alice",
            "last_name": "Anderson",
            "age": 30,
            "phone": "+12025550123",
        }
    ]
    path.write_text(json.dumps(data))


def test_build_payloads_and_ingest_whole(tmp_path: Path):
    p = tmp_path / "users.json"
    _write_users(p, desc="Hello world")
    ids, descriptions, docs, metas = build_payloads(str(p), normalize=False, min_chars=1)
    assert ids == ["alice"]
    assert descriptions == ["Hello world"]

    repo = CaptureRepo()
    n, out_ids = ingest(FakeEmbeddings(), repo, str(p), normalize=False, min_chars=1, embed_model="m", index_chunks=False)
    assert n == 1 and out_ids == ["alice"]
    ids, docs, vecs, metas = repo.calls[-1]
    assert ids == ["alice"]
    assert vecs and isinstance(vecs[0], list)
    # embed_hash precomputed by build_payloads
    assert "embed_hash" in metas[0]
    assert metas[0]["embed_model"] == "m"


def test_ingest_chunked_token_ids(tmp_path: Path):
    p = tmp_path / "users.json"
    _write_users(p, desc="alpha beta gamma delta")
    repo = CaptureRepo()
    n, out_ids = ingest(
        FakeEmbeddings(),
        repo,
        str(p),
        normalize=False,
        min_chars=1,
        embed_model=None,
        index_chunks=True,
        chunking_mode="token",
        tokens_per_chunk=3,
        token_overlap=1,
    )
    assert n == 1 and out_ids == ["alice"]
    ids, _docs, _vecs, metas = repo.calls[-1]
    # Chunks with token prefix #t
    assert ids[0].startswith("alice#t")
    assert metas[0]["parent_id"] == "alice"

