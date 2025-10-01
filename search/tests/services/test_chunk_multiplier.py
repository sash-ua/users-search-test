from typing import Any, Dict, List, Tuple

import math

from search.services.query_users import search as query_search


# Types from ports for clarity
Row = Tuple[str, float, str, Dict[str, Any]]


class FakeEmbeddings:
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        # Return a non-empty deterministic vector regardless of text
        return [[1.0, 0.0, -1.0] for _ in texts]


class FakeRepo:
    def __init__(self, rows: List[Row]):
        self._rows = rows

    def upsert(self, ids, documents, vectors, metadatas=None):
        raise NotImplementedError

    def query(self, vector: List[float], k: int, where_document: str | None = None):
        # Ignore the vector and where_document for this offline test.
        # Return the top-k rows and dummy distances list.
        sel = self._rows[: max(1, k)]
        dists = [r[1] for r in sel]
        return sel, dists

    def get_by_ids(self, ids: List[str], include_embeddings: bool = False):
        raise NotImplementedError


def _rows_for_chunk_scenario() -> List[Row]:
    # Construct a ranking of chunk-level rows where the top-k includes
    # duplicates from the same parent, and additional parents appear just beyond k.
    # Format: (id, distance, document, metadata)
    data: List[Row] = [
        ("A#1", 0.10, "chunk A1", {"parent_id": "A"}),
        ("A#2", 0.12, "chunk A2", {"parent_id": "A"}),
        ("B#1", 0.13, "chunk B1", {"parent_id": "B"}),
        ("C#1", 0.14, "chunk C1", {"parent_id": "C"}),
        ("D#1", 0.15, "chunk D1", {"parent_id": "D"}),
        ("E#1", 0.16, "chunk E1", {"parent_id": "E"}),
    ]
    return data


def test_chunk_query_multiplier_improves_parent_recall():
    rows = _rows_for_chunk_scenario()
    repo = FakeRepo(rows)
    emb = FakeEmbeddings()

    # Request k parents
    k = 3

    # Baseline: multiplier=1 (effectively k_eff = k); duplicates from A reduce unique parents
    base_rows, _ = query_search(
        embeddings=emb,
        repo=repo,
        query_text="anything",
        k=k,
        phrase_prefilter=False,
        threshold=None,
        normalize=False,
        index_chunks=True,
        chunk_query_multiplier=1,
    )

    base_parents = [m.get("parent_id") for (_, _, _, m) in base_rows]
    assert len(base_rows) <= k
    assert len(set(base_parents)) == len(base_rows)
    # With the given rows, we expect only A and B (2 parents) in the top-k
    assert set(base_parents).issubset({"A", "B"})

    # With a larger multiplier, more candidates are pulled before aggregation,
    # enabling additional parents (e.g., C) to surface into the top-k after aggregation.
    wide_rows, _ = query_search(
        embeddings=emb,
        repo=repo,
        query_text="anything",
        k=k,
        phrase_prefilter=False,
        threshold=None,
        normalize=False,
        index_chunks=True,
        chunk_query_multiplier=3,
    )
    wide_parents = [m.get("parent_id") for (_, _, _, m) in wide_rows]

    assert len(wide_rows) == k
    assert len(set(wide_parents)) == k
    # Expect C to appear when k is widened before aggregation
    assert "C" in wide_parents

