import argparse
import json
from typing import Any, Dict, List, Optional

import chromadb


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect embeddings stored in a Chroma collection."
    )
    parser.add_argument("--persist", default=".chroma", help="Chroma persistence path")
    parser.add_argument("--collection", default="users", help="Collection name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--id",
        action="append",
        help="Record ID to fetch (can be specified multiple times)",
    )
    group.add_argument(
        "--parent-id",
        help="Parent ID to fetch all chunk records (requires chunk indexing mode)",
    )
    parser.add_argument(
        "--limit", type=int, default=50, help="Max rows when querying by parent-id"
    )
    parser.add_argument(
        "--try-parent",
        action="store_true",
        help="If --id returns no rows and looks like a parent id (no #c), also fetch by parent_id",
    )
    parser.add_argument(
        "--preview", type=int, default=8, help="How many embedding values to preview"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output JSON instead of text summary"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = chromadb.PersistentClient(path=args.persist)
    col = client.get_collection(args.collection)

    include = ["embeddings", "metadatas", "documents"]

    res: Dict[str, Any]
    if args.id:
        res = col.get(ids=args.id, include=include)
        # Optional fallback: if no rows and ids look like parent ids in chunk mode
        fallback_rows: List[Dict[str, Any]] = []
        if (not res.get("ids")) and args.try_parent:
            merged: Dict[str, Any] = {"ids": [], "embeddings": [], "metadatas": [], "documents": []}
            for pid in args.id:
                if "#c" in pid:
                    continue
                r = col.get(where={"parent_id": pid}, include=include, limit=max(1, args.limit))
                # Merge results
                for key in merged:
                    vals = r.get(key)
                    if vals is None:
                        continue
                    # Convert numpy arrays to lists if present
                    try:
                        if hasattr(vals, "tolist"):
                            vals = vals.tolist()
                    except Exception:
                        pass
                    if isinstance(vals, (list, tuple)):
                        merged[key].extend(list(vals))
            res = merged
    else:
        where: Dict[str, Any] = {"parent_id": args.parent_id}
        # Collection.get supports where + limit
        res = col.get(where=where, include=include, limit=max(1, args.limit))

    ids = res.get("ids")
    embs = res.get("embeddings")
    metas = res.get("metadatas")

    # Normalize potential numpy arrays to plain Python lists without relying on truthiness
    try:
        import numpy as np  # type: ignore
    except Exception:  # pragma: no cover - numpy optional
        np = None  # type: ignore

    def to_list(x):
        if x is None:
            return []
        if np is not None and isinstance(x, np.ndarray):  # type: ignore
            return x.tolist()
        return x

    ids = to_list(ids)
    embs = to_list(embs)
    metas = to_list(metas)
    ids = list(ids) if isinstance(ids, (list, tuple)) else []
    embs = list(embs) if isinstance(embs, (list, tuple)) else []
    metas = list(metas) if isinstance(metas, (list, tuple)) else []

    out_rows: List[Dict[str, Any]] = []
    for i, rid in enumerate(ids):
        emb = embs[i] if i < len(embs) else None
        # Convert individual embedding vectors from numpy arrays if needed
        if emb is not None and not isinstance(emb, list):
            try:
                if np is not None and hasattr(emb, "tolist"):
                    emb = emb.tolist()
            except Exception:
                pass
        meta = metas[i] if i < len(metas) else None
        dim = len(emb) if isinstance(emb, list) else None
        preview = emb[: args.preview] if isinstance(emb, list) else None
        out_rows.append(
            {
                "id": rid,
                "dim": dim,
                "preview": preview,
                "metadata": meta or {},
            }
        )

    meta = getattr(col, "metadata", None) or {}
    summary: Dict[str, Any] = {
        "collection": getattr(col, "name", None),
        "model": meta.get("model"),
        "space": meta.get("hnsw:space"),
        "count": len(out_rows),
        "rows": out_rows,
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print(
            f"Collection: {summary['collection']} (space={summary['space']}, model={summary['model']})"
        )
        print(f"Rows: {summary['count']}")
        for row in out_rows:
            rid = row["id"]
            dim = row["dim"]
            md = row["metadata"] or {}
            parent = md.get("parent_id")
            chunk_idx = md.get("chunk_index")
            extras = []
            if parent is not None:
                extras.append(f"parent={parent}")
            if chunk_idx is not None:
                extras.append(f"chunk={chunk_idx}")
            extras_s = (" "+" ".join(extras)) if extras else ""
            prev = row["preview"]
            prev_s = (
                " ".join(f"{x:.5f}" for x in prev) if isinstance(prev, list) else "None"
            )
            print(f"  {rid}\tdim={dim}{extras_s}\t[{prev_s}]")


if __name__ == "__main__":
    main()
