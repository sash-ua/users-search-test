import pytest

chromadb = pytest.importorskip("chromadb")

from typing import Any, Dict, List

from search.adapters.chroma_user_vectors import ChromaUserVectors


class FakeCollection:
    def __init__(self):
        self._deleted: List[str] = []
        self._added: Dict[str, Any] = {}
        self.name = "users"
        self._metadata = {"hnsw:space": "cosine", "model": "m"}

    @property
    def metadata(self):
        return self._metadata

    def delete(self, ids: List[str]):
        self._deleted.extend(ids)

    def add(self, **kwargs):
        self._added = kwargs

    def query(self, **kwargs):
        # Fake a single-row response
        return {
            "ids": [["x"]],
            "documents": [["doc x"]],
            "distances": [[0.1]],
            "metadatas": [[{"parent_id": "p"}]],
        }

    def get(self, ids: List[str], include: List[str]):
        return {
            "ids": ["x"],
            "metadatas": [{"a": 1}],
            "embeddings": [[0.1, 0.2]] if "embeddings" in include else None,
        }


def test_chroma_user_vectors_upsert_and_query_and_get():
    col = FakeCollection()
    repo = ChromaUserVectors(col)

    repo.upsert(["x"], ["doc x"], [[0.1, 0.2]], metadatas=[{"a": 1}])
    assert col._deleted == ["x"]
    assert col._added["ids"] == ["x"]
    assert col._added["documents"] == ["doc x"]
    assert col._added["embeddings"] == [[0.1, 0.2]]
    assert col._added["metadatas"] == [{"a": 1}]

    rows, dists = repo.query([0.1, 0.2], k=1)
    assert rows == [("x", 0.1, "doc x", {"parent_id": "p"})]
    assert dists == [0.1]

    got = repo.get_by_ids(["x"], include_embeddings=True)
    assert "x" in got and got["x"]["metadata"] == {"a": 1}
    assert got["x"]["embedding"] == [0.1, 0.2]

