from chromadb.errors import InvalidArgumentError
from typing import Any
from openai import OpenAI
from dotenv import load_dotenv

from search.adapters.chroma_user_vectors import ChromaUserVectors, get_or_create_collection
from search.adapters.openai_embeddings import OpenAIEmbeddings
from search.services.ingest_users import ingest
from search.services.query_users import search
from search.utils.histogram import print_distance_histogram
from search.utils.load_data import parse_args
from search.utils.load_env import load_env


def main():
    # Load environment variables from .env if present
    load_dotenv()
    args = parse_args()
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
    # Ensure collection matches requested chunking; recreate if not
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
            print("Chunking config changed; recreating collection to reindex embeddings.")
            col = get_or_create_collection(
                args.persist, args.collection, args.space, True, args.model, extra_meta
            )
            repo = ChromaUserVectors(col)
            reindexed = True
    except Exception:
        pass
    try:
        count, _ids = ingest(
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
            verbose=args.verbose,
        )
    except InvalidArgumentError as e:
        if "dimension" in str(e).lower():
            print("Embedding dimension mismatch detected; recreating collection and retrying.")
            col = get_or_create_collection(
                args.persist, args.collection, args.space, True, args.model, extra_meta
            )
            repo = ChromaUserVectors(col)
            count, _ids = ingest(
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
                verbose=args.verbose,
            )
            reindexed = True
        else:
            raise
    print(f"Indexed {count} documents (min-chars={args.min_chars}).")
    try:
        meta = repo.metadata or {}
        space = meta.get("hnsw:space")
        m = meta.get("model")
        print(f"Using collection: {repo.name} (space={space}, model={m})")
    except Exception:
        pass
    if reindexed:
        print("Reindexed collection due to changed chunking/model settings.")

    # Upsert already performed in ingest(); mismatch handled above.

    rows, dists = search(
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

    if args.verbose:
        print_distance_histogram(dists)

    if not rows:
        print("No matches under threshold." if args.threshold else "No matches")
        return

    for rid, dist, _doc, meta in rows:
        first = meta.get('first_name', '')
        last = meta.get('last_name', '')
        chunk_idx = meta.get('chunk_index')
        chunk_cnt = meta.get('chunk_count')
        chunk_text = meta.get('chunk_text')
        print(f"\t{rid}\t{dist:.6f}\t{first}{' ' + last if last else ''}")
        if chunk_idx is not None and chunk_cnt is not None:
            print(f"\t  chunk {chunk_idx+1}/{chunk_cnt}")
        if isinstance(chunk_text, str) and chunk_text.strip():
            snippet = chunk_text[:120].replace('\n', ' ').strip()
            if len(chunk_text) > 120:
                snippet += '…'
            print(f"\t  “{snippet}”")


if __name__ == '__main__':
    main()
