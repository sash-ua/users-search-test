# search/ (Python) — Documentation

Hexagonal core for embedding and semantic search of user data. Provides:
- Clean ports (`ports/`) and adapters (`adapters/`) for embeddings and vector store
- Services to ingest data and run queries with optional chunking
- Two CLIs:
  - Human‑readable CLI: `python -m search.query`
  - JSON API for backend: `python -m search.api`

## Architecture
- Ports
  - `ports/embeddings.py`: `EmbeddingsProvider` protocol (`embed_texts`)
  - `ports/user_vectors.py`: `UserVectorRepository` protocol (`upsert`, `query`, `get_by_ids`)
- Adapters
  - `adapters/openai_embeddings.py`: OpenAI v1 client, configurable model
  - `adapters/chroma_user_vectors.py`: Chroma persistent client with HNSW space and metadata
- Services
  - `services/ingest_users.py`: Build payloads from JSON and ingest via strategies
  - `services/query_users.py`: Run vector search and aggregate chunk results by parent
  - `services/ingest_strategies.py`: Whole doc, sentence chunking, token chunking; embedding reuse
- Utils
  - `utils/load_data.py`: CLI args; JSON loader; chunking flags
  - `utils/load_env.py`: Reads `OPENAI_API_KEY` and optional `OPENAI_BASE_URL`
  - `utils/export_user_schema.py`: Writes JSON schema for `User`
  - `utils/ingest.py`: text normalization, hashing, batching helpers
  - `utils/histogram.py`: top‑k distance histogram
  - `utils/dump_embeddings.py`: inspect collection rows/embeddings
- Models
  - `models/user.py`, `models/person.py`: Pydantic v2 models for validation
  - `models/collection_item.py`: typed representation for repository returns

## Installation
- Python 3.9+
- Create venv and install deps at repo root (so backend can run `-m search.api`):
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -r search/requirements.txt`
  - Optionally: `pip install pytest && pytest -q`

## Environment
- Required: `OPENAI_API_KEY`
- Optional: `OPENAI_BASE_URL` (for OpenAI‑compatible providers)
- Load order: `.env` is supported via `python-dotenv` in both CLIs
- Example: `search/.env:1`

### Using a local embeddings server
If you run an OpenAI‑compatible embeddings server locally (e.g. at `http://127.0.0.1:1234/v1`), set `OPENAI_BASE_URL` so the library targets it instead of api.openai.com.

Quick check (outside the app):
```bash
curl http://127.0.0.1:1234/v1/embeddings \
  -H 'Content-Type: application/json' \
  -d '{"model":"text-embedding-mxbai-embed-large-v1","input":"Hello"}'
```

Then, either:
- Put the vars in `search/.env` when running the CLIs directly:
  ```bash
  OPENAI_API_KEY=dummy
  OPENAI_BASE_URL=http://127.0.0.1:1234/v1
  ```
- Or, when launching via the NestJS backend, ensure the backend `.env` also includes `OPENAI_API_KEY` and `OPENAI_BASE_URL` so the child Python process inherits them.

Common pitfall: forgetting to set `OPENAI_BASE_URL` while pointing the model to a local one (e.g. `text-embedding-mxbai-embed-large-v1`). This leads to a 500 from the backend because Python cannot reach a valid provider. Ensure both `OPENAI_API_KEY` and `OPENAI_BASE_URL` are present in the environment used to run Python.

## CLI — Human Output
Run an indexed query with optional chunking:
```bash
python -m search.query \
  --data data.json \
  --persist .chroma \
  --collection users \
  --space cosine \
  --model text-embedding-mxbai-embed-large-v1 \
  --query "bicycle" --k 5 \
  --normalize --phrase-prefilter \
  --index-chunks --chunking-mode sentence \
  --sentences-per-chunk 3 --sentence-overlap 1 \
  --chunk-query-multiplier 5
```
Key flags (see `utils/load_data.py`):
- Data/indexing: `--data`, `--persist`, `--collection`, `--space`, `--force-recreate`, `--min-chars`
- Model/query: `--model`, `--query`, `--k`, `--threshold`, `--normalize`, `--phrase-prefilter`, `--verbose`
- Chunking: `--index-chunks`, `--chunking-mode [sentence|token]`, per‑mode params, `--chunk-query-multiplier`

Behavior highlights:
- Embedding reuse: stored vectors reused when `embed_hash` and `embed_model` match; else recomputed
- Auto reindex: if collection metadata chunking config differs from requested flags, collection is recreated
- Dimension mismatch: on Chroma dimension errors, collection is recreated then re‑ingested
- Chunking search: when `--index-chunks`, query retrieves `k * chunk_query_multiplier` items and aggregates best chunk per parent

## CLI — JSON API
Used by the NestJS backend. Prints a single JSON object to stdout.
```bash
python -m search.api --data data.json --query "bicycle" --k 5
```
Additional command:
- `--export-user-schema`: writes `schemas/user.schema.json` and exits

Response shape (subset):
```json
{
  "query": "bicycle",
  "k": 5,
  "count": 5,
  "rows": [
    {
      "id": "alice#c0000",
      "distance": 0.1234,
      "snippet": "…",
      "metadata": {
        "first_name": "Alice",
        "last_name": "Smith",
        "parent_id": "alice",
        "chunk_index": 0,
        "chunk_count": 4,
        "chunk_text": "…",
        "chunk_kind": "sentence"
      }
    }
  ],
  "distances": [0.12, 0.23, 0.31, 0.44, 0.52],
  "collection": "users",
  "space": "cosine",
  "model": "text-embedding-mxbai-embed-large-v1",
  "reindexed": false
}
```

## Data Model & Schema
- User array input validated via Pydantic v2 models (`models/person.py`, `models/user.py`)
- Export schema to `schemas/user.schema.json`:
  - `python -m search.api --export-user-schema`

Expected JSON rows include fields like `username`, `first_name`, `last_name`, `email`, `phone`, `description`.

## Chunking Strategies
- WholeDocStrategy: embed full description once; metadata includes `chunk_text` for parity
- ChunkedStrategy (sentence): naive punctuation‑based splitting, sliding window with overlap
- TokenChunkStrategy: lightweight tokenizer with sliding window and overlap
- Metadata stamped per chunk: `parent_id`, `chunk_index`, `chunk_count`, `chunk_text`, `chunk_kind`, `embed_hash`, plus parent fields

## Chroma Persistence
- Persistent path: `--persist` (default `.chroma`)
- Collection metadata: `hnsw:space`, `model`, plus chunking parameters used for reindex checks
- Query options: `where_document` substring filter used when `--phrase-prefilter`

## Utilities
- Dump embeddings: inspect stored rows/vectors
  ```bash
  python -m search.utils.dump_embeddings --persist .chroma --collection users --id alice --preview 8
  # or by parent id in chunk mode
  python -m search.utils.dump_embeddings --persist .chroma --collection users --parent-id alice --limit 20
  ```
- Distance histogram (verbose mode in `search.query`): prints a coarse summary of top‑k distances

## Testing
- Install: `pip install pytest`
- Run: `pytest -q`
- Tests cover: chunking behavior, adapter interactions (via fakes), ingestion mapping, env loading

## Troubleshooting
- Missing API key: ensure `OPENAI_API_KEY` is set (or in `.env`)
- Non‑JSON stdout: do not print extra logs when using `search.api`; use `search.query` for manual runs
- Reindex loops: verify chunking flags remain consistent; use `--force-recreate` if switching modes
- Bad dataset: validate users file against exported schema or the NestJS dataset validation

---

See also: backend documentation for how the Node process shells out to `python -m search.api` and consumes this JSON.
