# Backend (NestJS) — Documentation

This backend exposes a simple HTTP API for semantic search and dataset management. It shells out to the Python module (`search.api`) to perform embedding/search and returns structured JSON to clients.

## Overview
- Framework: NestJS 10 (TypeScript)
- Entrypoint: `back-end/src/main.ts`
- Modules:
  - `SearchModule`: `POST /search` — delegates to Python via `child_process.spawn`.
  - `DatasetsModule`: `POST /datasets` (upload JSON) and `GET /datasets` (list uploaded files).
- Python bridge: `back-end/src/search/python.ts` builds CLI args from request body, spawns `python -m search.api`, and parses JSON from stdout.
- Config: Loaded via `@nestjs/config` with Joi validation in `back-end/src/shared/configs/validation.schema.ts`.

## Project Structure (backend)
- `back-end/src/app.module.ts`: Bootstraps config, SearchModule, DatasetsModule, and provides `APP_CONFIG`.
- `back-end/src/main.ts`: Creates Nest app, enables CORS per config, and listens on `APP_PORT`.
- `back-end/src/search/`:
  - `search.controller.ts`: Validates body contains `query`, forwards to service.
  - `search.service.ts`: Invokes Python bridge with typed `SearchQueryArgs`.
  - `python.ts`: Spawns Python and maps request options to CLI flags.
- `back-end/src/datasets/`:
  - `datasets.controller.ts`: Uploads and lists dataset files; optional JSON schema validation via AJV.
- `back-end/src/shared/`:
  - `configs/validation.schema.ts`: Joi env validation.
  - `constants/app-config-token.ts`, `providers/config-provider.ts`, `models/*.ts`, `utils/user.ts` (AJV runtime validation for uploaded users JSON).

## Prerequisites
- Node.js 18+ and npm
- Python 3.9+ available as `python` (or set `PYTHON_BIN`)
- Python deps installed in the repo root (or your configured `PYTHON_WORKDIR`):
  - `pip install pydantic pydantic-extra-types chromadb openai python-dotenv`

## Environment Variables
Defined and validated in `back-end/src/shared/configs/validation.schema.ts:1`.
- `IS_CORS_ENABLED` (boolean, required): Enables CORS for local dev or cross-origin frontends.
- `APP_NAME` (string, required): App label.
- `APP_ENV` (string, required): `development` or `production`.
- `APP_PORT` (number, required): HTTP port (default `3001`).
- `PYTHON_BIN` (string, required): Python executable, e.g. `python` or `python3`.
- `PYTHON_SEARCH_MODULE` (string, required): Python module to run; default `search.api`.
- `PUBLIC_BACKEND_URL` (string, required): Public URL the frontend will use (e.g., `http://localhost:3001`).

Additional runtime variables (optional, not enforced by Joi):
- `PYTHON_WORKDIR`: Working directory for the Python process; defaults to repo root (`resolve(process.cwd(), '..')`).
- `DATASETS_DIR`: Upload directory override; defaults to `<repo>/search/uploads`.
- `USER_SCHEMA_PATH`: Path to `user.schema.json` for dataset validation (else autodetected under `./schemas` or `../schemas`).

Example development env is provided in `back-end/.env.development:1`.

## Install & Run
- Install Node deps: `cd back-end && npm i`
- Start dev server (watch mode): `npm run start`
  - Uses `NODE_ENV=development` and `.env.development`.
- Build: `npm run build`
- Start production build: `npm run start:prod`

Ensure Python environment is ready in the Python working directory (repo root by default):
- `python -m venv .venv && source .venv/bin/activate`
- `pip install pydantic pydantic-extra-types chromadb openai python-dotenv`

## API

### POST /search
- Description: Perform a semantic search by delegating to Python (`search.api`).
- Controller: `back-end/src/search/search.controller.ts:1`
- Request body (JSON): at minimum `{ "query": string }`. Optional fields map to CLI flags:
  - `k` (number)
  - `normalize` (boolean)
  - `phrase_prefilter` (boolean)
  - `threshold` (number | null)
  - `model` (string)
  - `data` (string path to JSON dataset; default `data.json` at repo root)
  - `persist` (string)
  - `collection` (string)
  - `space` (string)
  - `index_chunks` (boolean)
  - `chunking_mode` (`'sentence' | 'token'`)
  - `sentences_per_chunk` (number)
  - `sentence_overlap` (number)
  - `tokens_per_chunk` (number)
  - `token_overlap` (number)
  - `chunk_query_multiplier` (number)

Example request:
```bash
curl -X POST "$PUBLIC_BACKEND_URL/search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "bicycle",
    "k": 5,
    "data": "data.json",
    "index_chunks": true,
    "chunking_mode": "sentence",
    "sentences_per_chunk": 3,
    "sentence_overlap": 1
  }'
```

- Response: JSON produced by the Python module (parsed from stdout). On error, HTTP 200 with `{ error: string }` for input validation issues (e.g., missing `query`), or the request rejects if Python fails/returns non-JSON.

Arguments mapping implemented in `back-end/src/search/python.ts:1`.

### POST /datasets
- Description: Upload a JSON dataset file.
- Controller: `back-end/src/datasets/datasets.controller.ts:1`
- Content-Type: `multipart/form-data`
- Fields:
  - `file` (required): the JSON file
  - `name` (optional): target filename; defaults to original name
  - `validate` (optional): any truthy value triggers JSON schema validation (AJV) against `user.schema.json`
- Storage:
  - Directory: `${DATASETS_DIR || <repo>/search/uploads}`
  - Saved as `search/uploads/<timestamp>_<name>.json` under repo root
- Validation:
  - If `validate` is set and file `mimetype` is `application/json`, validates the array against a user schema resolved by `back-end/src/shared/utils/user.ts:1`.

Example request:
```bash
curl -X POST "$PUBLIC_BACKEND_URL/datasets" \
  -F "file=@data.json;type=application/json" \
  -F "name=data.json" \
  -F "validate=1"
```
- Response: `{ "path": "search/uploads/1696039999999_data.json" }` or `{ error, details }` on validation failure.

### GET /datasets
- Description: List previously uploaded `.json` files.
- Response: `{ files: string[] }` where each entry is a path like `search/uploads/<file>.json` (relative to repo root).

## Python Bridge Details
- File: `back-end/src/search/python.ts:1`
- Command form: `${PYTHON_BIN} -m ${PYTHON_SEARCH_MODULE} [flags...]`
- Working directory: `${PYTHON_WORKDIR || resolve(process.cwd(), '..')}` so that the Python module `search.api` resolves from the repo root.
- Output contract: The Python process must emit a single JSON object/array on stdout. The bridge parses stdout; non-zero exit codes or invalid JSON are treated as errors.
- Flags mapping: Each request field is converted to the corresponding CLI flag (e.g., `index_chunks` -> `--index-chunks`).

## CORS & Port
- CORS: Enabled when `IS_CORS_ENABLED=true` (useful for local Next.js dev).
- Port: Reads `APP_PORT` (default `3001`). See `back-end/src/main.ts:1`.

## Troubleshooting
- Python not found: Set `PYTHON_BIN` to a valid interpreter (e.g., `python3`).
- Module not found: Ensure `PYTHON_SEARCH_MODULE=search.api` and working directory points to repo root (set `PYTHON_WORKDIR` if running from a different folder).
- JSON parse errors: Confirm Python prints valid JSON to stdout and no extra logs (stderr is captured separately).
- Permission issues on upload: Check `DATASETS_DIR` path is writable by the Node process.
- Schema resolution errors: Set `USER_SCHEMA_PATH` explicitly or place `user.schema.json` under `./schemas` or `../schemas`.

## Development Tips
- Run backend: `cd back-end && npm run start` (watch mode).
- Example search call: see QuickStart in root README or the cURL above.
- Extend search args: update `back-end/src/shared/models/search-query-args.model.ts:1` and the arg builder in `python.ts`.
- Frontend integration: point `NEXT_PUBLIC_BACKEND_URL` to the backend URL; backend already validates `PUBLIC_BACKEND_URL` for consistency.

---

For the overall system flow and Python module usage, also see the repository’s root README and the `search/` package documentation.
