from typing import Any, Dict, List, Tuple

from search.services.query_users import search as query_search


Row = Tuple[str, float, str, Dict[str, Any]]


class RecordingEmbeddings:
    def __init__(self) -> None:
        self.calls: List[List[str]] = []

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        self.calls.append(list(texts))
        return [[0.1, 0.2, 0.3]] * len(texts)


class PrefilterFallbackRepo:
    def __init__(self, rows: List[Row]):
        self._rows = rows
        self.calls: List[Dict[str, Any]] = []

    def upsert(self, *a, **k):
        raise NotImplementedError

    def query(self, vector: List[float], k: int, where_document: str | None = None):
        self.calls.append({"k": k, "where_document": where_document})
        if where_document:
            return [], []
        sel = self._rows[: max(1, k)]
        dists = [r[1] for r in sel]
        return sel, dists

    def get_by_ids(self, *a, **k):
        raise NotImplementedError


def test_phrase_prefilter_fallback_and_normalize():
    rows: List[Row] = [("A", 0.1, "doc", {"parent_id": "A"})]
    repo = PrefilterFallbackRepo(rows)
    emb = RecordingEmbeddings()
    out, dists = query_search(
        embeddings=emb,
        repo=repo,
        query_text="HeLLo",
        k=1,
        phrase_prefilter=True,
        threshold=None,
        normalize=True,
        index_chunks=False,
    )
    # Fallback happened (two calls, one with where_document, one without)
    assert len(repo.calls) == 2
    assert repo.calls[0]["where_document"] == "hello"
    assert repo.calls[1]["where_document"] is None
    # Query text normalized before embedding
    assert emb.calls and emb.calls[0] == ["hello"]
    assert out and out[0][0] == "A"


def test_threshold_filters_rows():
    class R:
        def embed_texts(self, texts: List[str]) -> List[List[float]]:
            return [[1.0, 0.0, 0.0]]

    class Repo:
        def query(self, vector: List[float], k: int, where_document: str | None = None):
            rows: List[Row] = [
                ("x", 0.10, "d", {}),
                ("y", 0.15, "d", {}),
            ]
            return rows[:k], [r[1] for r in rows[:k]]

    out, dists = query_search(R(), Repo(), "q", 2, phrase_prefilter=False, threshold=0.12, normalize=False)
    # Only rows <= threshold remain
    assert [rid for (rid, *_rest) in out] == ["x"]
    # Distances list mirrors before-threshold trimming
    assert dists == [0.10, 0.15]

