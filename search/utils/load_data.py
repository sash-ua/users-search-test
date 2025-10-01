import argparse
import json
import sys
from typing import Any


def load_json(path: str) -> list[dict[str, Any]]:
    try:
        with open(path) as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print(f"Error: The file {path} was not found.", file=sys.stderr)
        return []
    except json.JSONDecodeError:
        print(f"Error: The file {path} could not be decoded.", file=sys.stderr)
        return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load users, embed descriptions, and query Chroma.")
    parser.add_argument("--export-user-schema", action="store_true",
                        help="Export user JSON schema for search.api output and exit")
    parser.add_argument("--data", default="data.json", help="Path to users JSON file")
    parser.add_argument("--persist", default=".chroma", help="Path for Chroma persistence store")
    parser.add_argument("--collection", default="users", help="Chroma collection name")
    parser.add_argument("--space", default="cosine", help="Vector space metric for HNSW index (cosine, l2, ip)")
    parser.add_argument("--force-recreate", action="store_true",
                        help="Drop and recreate the collection with the requested space")
    parser.add_argument("--model", default="text-embedding-mxbai-embed-large-v1", help="Embedding model name")
    parser.add_argument("--query", default="", help="Query text")
    parser.add_argument("--k", type=int, default=5, help="Top-k results to return")
    parser.add_argument("--threshold", type=float, help="Max distance threshold to accept")
    parser.add_argument("--normalize", action="store_true",
                        help="Normalize text (lowercase, collapse spaces) before embedding")
    parser.add_argument("--min-chars", type=int, default=10, help="Minimum description length to index")
    parser.add_argument("--phrase-prefilter", action="store_true",
                        help="Apply substring prefilter using the query text")
    parser.add_argument("--verbose", action="store_true", help="Verbose output: histogram and reuse details")
    # Chunking and indexing controls
    parser.add_argument("--index-chunks", action="store_true",
                        help="Index each description as sentence-based chunks and aggregate by parent on query")
    parser.add_argument("--chunking-mode", choices=["sentence", "token"], default="sentence",
                        help="Chunking mode when --index-chunks: sentence (default) or token")
    parser.add_argument("--sentences-per-chunk", type=int, default=3,
                        help="Number of sentences per chunk when --chunking-mode=sentence")
    parser.add_argument("--sentence-overlap", type=int, default=1,
                        help="Sentence overlap between adjacent chunks when --chunking-mode=sentence")
    parser.add_argument("--tokens-per-chunk", type=int, default=200,
                        help="Number of tokens per chunk when --chunking-mode=token")
    parser.add_argument("--token-overlap", type=int, default=50,
                        help="Token overlap between adjacent chunks when --chunking-mode=token")
    parser.add_argument("--chunk-query-multiplier", type=int, default=5,
                        help="Multiply k for initial retrieval in chunk mode before aggregating by parent")
    return parser.parse_args()
