from typing import List, Tuple, Dict

from search.ports.embeddings import EmbeddingsProvider
from search.ports.user_vectors import Row, UserVectorRepository
from search.utils.ingest import normalize_text


def search(
    embeddings: EmbeddingsProvider,
    repo: UserVectorRepository,
    query_text: str,
    k: int,
    phrase_prefilter: bool,
    threshold: float | None,
    normalize: bool,
    index_chunks: bool = False,
    chunk_query_multiplier: int = 5,
) -> Tuple[List[Row], List[float]]:
    q = normalize_text(query_text).lower() if normalize else query_text
    q_vecs = embeddings.embed_texts([q])
    q_vec = q_vecs[0] if q_vecs else []
    if not q_vec:
        return [], []

    # If indexing per chunk, query more candidates then aggregate by parent_id
    k_eff = max(1, (k * max(1, chunk_query_multiplier)) if index_chunks else k)

    rows, _ = repo.query(q_vec, k_eff, where_document=q if phrase_prefilter and q else None)
    if phrase_prefilter and q and not rows:
        rows, _ = repo.query(q_vec, k_eff)

    # Aggregate by parent when chunked; otherwise keep as-is
    rows = _aggregate_by_parent(rows) if index_chunks else rows
    # Trim back to requested k
    rows = rows[:k]

    if threshold is None:
        return rows, [r[1] for r in rows]

    filtered = [r for r in rows if r[1] <= threshold] if rows else []
    return filtered, [r[1] for r in rows]


def _aggregate_by_parent(rows: List[Row]) -> List[Row]:
    by_parent: Dict[str, Row] = {}
    for rid, dist, doc, meta in rows:
        parent = meta.get("parent_id") if isinstance(meta, dict) else None
        key = parent or rid
        current = by_parent.get(key)
        if current is None or dist < current[1]:
            # Prefer the best (smallest distance) chunk per parent
            if parent:
                # ensure id reflects parent when aggregating
                by_parent[key] = (parent, dist, doc, meta)
            else:
                by_parent[key] = (rid, dist, doc, meta)
    # Return sorted by ascending distance
    return sorted(by_parent.values(), key=lambda r: r[1])
