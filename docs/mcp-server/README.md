# MCP Server for search/

A Model Context Protocol (MCP) server that exposes the Python `search/` library as tools. Clients (e.g., IDE agents) can call search and ingestion without spawning subprocesses.

## Features
- Tools
  - `search.run`: ingest (with reuse) and query, returns the same JSON shape as `python -m search.api`
  - `ingest.run`: ingest only, returns counts and collection info
  - `datasets.list`: list available JSON datasets
  - `datasets.upload`: upload a JSON dataset (optional validation via Pydantic)
  - `schema.export_user`: write and return `schemas/user.schema.json`
  - `embeddings.inspect`: preview embedding rows for ids or a parent id
- Environment
  - Reads `.env` and requires `OPENAI_API_KEY`; optional `OPENAI_BASE_URL`
  - Optional: `DATASETS_DIR` (defaults to `search/uploads`), `PYTHON_WORKDIR`

## Layout
- `search_mcp_server/__main__.py`: MCP stdio server wiring + tool registration
- `search_mcp_server/handlers.py`: Pure Python implementations that call the `search/` services
- `search_mcp_server/requirements.txt`: minimal dependencies

## Install
- Python 3.9+
- Create a virtualenv at repo root and install dependencies for both `search/` and the MCP server:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r search/requirements.txt
pip install -r search_mcp_server/requirements.txt
```

- Ensure `.env` contains `OPENAI_API_KEY` (and `OPENAI_BASE_URL` if using a compatible endpoint).

## Run
- Start the stdio MCP server:

```bash
python -m search_mcp_server
```

Your MCP client should launch it via stdio with the working directory set to the repo root.

## Tools

### search.run
- Args: see `search_mcp_server/__main__.py: _schema_search_args()` (maps 1:1 to CLI flags in `search/utils/load_data.py`)
- Returns: same JSON contract as `python -m search.api`

### ingest.run
- Args: see `_schema_ingest_args()`
- Returns: `{ indexed, reindexed, collection, space, model }`

### datasets.list
- Args: none
- Returns: `{ files: string[] }` (paths relative to repo root)

### datasets.upload
- Args: `{ name?: string, content: string, validate?: boolean }`
- Returns: `{ path }` relative to repo root (e.g., `search/uploads/1699999999999_data.json`)

### schema.export_user
- Args: none
- Returns: `{ schema, path }`

### embeddings.inspect
- Args: `{ persist: string, collection: string, ids?: string[], parent_id?: string, limit?: number, preview?: number }`
- Returns: `{ collection, model, space, count, rows[] }`

## Notes
- The server reuses embeddings when `embed_hash` and `embed_model` match; otherwise it recomputes.
- If collection metadata (chunking flags) differs from args, the server recreates the collection and reindexes.
- On Chroma dimension mismatches, the server recreates and retries ingestion automatically.

## Troubleshooting
- `Missing MCP Python SDK` error on start: run `pip install mcp anyio` (see requirements file)
- `OPENAI_API_KEY` missing: add it to `.env` at repo root
- No datasets listed: upload or place files under `search/uploads`
- Permission errors on upload: adjust `DATASETS_DIR` or run with appropriate permissions

## Extending
- Add more tools or resources by implementing handlers in `search_mcp_server/handlers.py` and registering them in `__main__.py`.
- Resource templates (optional): you can expose read-only resources like `schema://user` or `dataset://file/{path}` if your MCP client supports them. The current server focuses on tools for simplicity.
