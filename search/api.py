import json
from typing import Any, Dict, List

from chromadb.errors import InvalidArgumentError
from openai import OpenAI
from dotenv import load_dotenv

from search.adapters.chroma_user_vectors import ChromaUserVectors, get_or_create_collection
from search.adapters.openai_embeddings import OpenAIEmbeddings
from search.services.ingest_users import ingest
from search.services.query_users import search as svc_search
from search.utils.export_user_schema import export_user_schema
from search.utils.load_data import parse_args
from search.utils.load_env import load_env


def main() -> None:
    # Load environment variables from .env if present
    load_dotenv()
    args = parse_args()

    # If only schema is requested, print and exit before any network/env requirements
    if getattr(args, "export_user_schema", False):
        export_user_schema()
        return

    api_key, base_url = load_env()
    client = OpenAI(base_url=base_url, api_key=api_key)
    embeddings = OpenAIEmbeddings(client, args.model)
    extra_meta = {
        "index_chunks": bool(args.index_chunks),
        "chunking_mode": getattr(args, "chunking_mode", "sentence"),
        "sentences_per_chunk": int(args.sentences_per_chunk),
        "sentence_overlap": int(args.sentence_overlap),
        "tokens_per_chunk": int(getattr(args, "tokens_per_chunk", 200)),
        "token_overlap": int(getattr(args, "token_overlap", 50)),
    }

    col = get_or_create_collection(
        args.persist, args.collection, args.space, args.force_recreate, args.model, extra_meta
    )
    repo = ChromaUserVectors(col)
    reindexed = False
    # If metadata does not match requested chunking settings, recreate collection
    try:
        meta = repo.metadata or {}

        def _as_bool(v: Any) -> bool:
            if isinstance(v, bool):
                return v
            if isinstance(v, (int, float)):
                return v != 0
            if isinstance(v, str):
                return v.strip().lower() in ("1", "true", "yes", "on")
            return bool(v)

        def _as_int(v: Any, default: int = 0) -> int:
            try:
                return int(v)
            except Exception:
                return default

        mismatch = (
            _as_bool(meta.get("index_chunks")) != bool(args.index_chunks)
            or str(meta.get("chunking_mode") or "sentence").lower() != str(getattr(args, "chunking_mode", "sentence")).lower()
            or _as_int(meta.get("sentences_per_chunk"), -1) != int(args.sentences_per_chunk)
            or _as_int(meta.get("sentence_overlap"), -1) != int(args.sentence_overlap)
            or _as_int(meta.get("tokens_per_chunk"), -1) != int(getattr(args, "tokens_per_chunk", 200))
            or _as_int(meta.get("token_overlap"), -1) != int(getattr(args, "token_overlap", 50))
        )
        if mismatch and not args.force_recreate:
            col = get_or_create_collection(
                args.persist, args.collection, args.space, True, args.model, extra_meta
            )
            repo = ChromaUserVectors(col)
            reindexed = True
    except Exception:
        pass
    try:
        ingest(
            embeddings,
            repo,
            args.data,
            args.normalize,
            args.min_chars,
            embed_model=args.model,
            index_chunks=args.index_chunks,
            sentences_per_chunk=args.sentences_per_chunk,
            sentence_overlap=args.sentence_overlap,
            chunking_mode=getattr(args, "chunking_mode", "sentence"),
            tokens_per_chunk=getattr(args, "tokens_per_chunk", 200),
            token_overlap=getattr(args, "token_overlap", 50),
            verbose=False,
        )
    except InvalidArgumentError as e:
        if "dimension" in str(e).lower():
            col = get_or_create_collection(
                args.persist, args.collection, args.space, True, args.model, extra_meta
            )
            repo = ChromaUserVectors(col)
            ingest(
                embeddings,
                repo,
                args.data,
                args.normalize,
                args.min_chars,
                embed_model=args.model,
                index_chunks=args.index_chunks,
                sentences_per_chunk=args.sentences_per_chunk,
                sentence_overlap=args.sentence_overlap,
                chunking_mode=getattr(args, "chunking_mode", "sentence"),
                tokens_per_chunk=getattr(args, "tokens_per_chunk", 200),
                token_overlap=getattr(args, "token_overlap", 50),
                verbose=False,
            )
            reindexed = True
        else:
            raise

    rows, dists = svc_search(
        embeddings,
        repo,
        args.query,
        args.k,
        phrase_prefilter=args.phrase_prefilter,
        threshold=args.threshold,
        normalize=args.normalize,
        index_chunks=args.index_chunks,
        chunk_query_multiplier=args.chunk_query_multiplier,
    )

    result_rows: List[Dict[str, Any]] = []
    for rid, dist, _doc, meta in rows:
        m = meta or {}
        snippet = m.get("chunk_text")
        if isinstance(snippet, str) and len(snippet) > 200:
            snippet = snippet[:200].rstrip() + "…"
        item = {
            "id": rid,
            "distance": dist,
            "metadata": m,
            "snippet": snippet,
            "chunk_index": m.get("chunk_index"),
            "chunk_count": m.get("chunk_count"),
        }
        result_rows.append(item)

    out = {
        "query": args.query,
        "k": args.k,
        "count": len(result_rows),
        "rows": result_rows,
        "distances": dists,
        "collection": getattr(repo, "name", None),
        "space": (repo.metadata or {}).get("hnsw:space") if getattr(repo, "metadata", None) else None,
        "model": (repo.metadata or {}).get("model") if getattr(repo, "metadata", None) else None,
        "reindexed": reindexed,
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
