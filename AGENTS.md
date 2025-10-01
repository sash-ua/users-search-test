# Repository Guidelines

## Project Structure & Module Organization
- `search/` (Python package):
  - `models/`, `ports/`, `adapters/`, `services/`, `utils/`, `cli/`, `api.py`, `query.py`
  - Purpose: validate data (Pydantic), embed/search (OpenAI + Chroma) with clean ports/adapters.
- `back-end/` (NestJS): HTTP API that invokes the Python module.
  - `src/search/`: controller/service + Python bridge; `src/datasets/`: JSON upload/list.
  - `src/shared/`: config validation schemas and providers.
- `front-end/` (Next.js 14 App Router + TypeScript + MUI):
  - `src/app/`: Next.js App Router (layout.tsx, page.tsx)
  - `src/components/`: reusable React components (ThemeSwitcher, SearchForm, ChunkingOptions, DatasetSelector, SearchResults)
  - `src/hooks/`: custom React hooks (useSearchForm, useChunking, useDataset)
  - `src/providers/`: context providers (ThemeProvider with localStorage + URL persistence)
  - `src/types/`: TypeScript type definitions (ThemeMode enum)
  - Features: Modern App Router, MUI theming with auto/light/dark mode, client components with 'use client' directive
- `tests/` (recommended): mirror `search/` (e.g., `tests/services/test_ingest.py`).

## Build, Test, and Development Commands
- Python env: `python -m venv .venv && source .venv/bin/activate`
- Python deps: `pip install pydantic pydantic-extra-types chromadb openai python-dotenv`
- Run CLI: `python -m search.query --data data.json --query "bicycle" --k 5`
  - Chunking:
    - Sentence mode: add `--index-chunks --chunking-mode sentence --sentences-per-chunk 3 --sentence-overlap 1`
    - Token mode: add `--index-chunks --chunking-mode token --tokens-per-chunk 200 --token-overlap 50`
- Export User JSON schema: `python -m search.api --export-user-schema`
- JSON API (called by backend): `python -m search.api ...`
- Backend: `cd back-end && npm i && npm run start`
- Frontend: `cd front-end && npm i && npm run dev`
- Lint/format Python: `black . && ruff check .`
- Tests (Python): `pip install pytest && pytest -q`

## Coding Style & Naming Conventions
- Python: PEP 8, 4-space indents, full type hints. Pydantic `Field(..., min_length=..., max_length=..., description=...)`.
- TS/JS: strict TypeScript in backend/frontend; keep modules and files in `kebab-case` or `camelCase` consistently.
- Names: modules `snake_case.py`; classes `PascalCase`; functions/vars `snake_case` (Python) or `camelCase` (TS/JS).
- React:
  - Components in `PascalCase.tsx` (e.g., `ThemeSwitcher.tsx`)
  - Hooks in `camelCase.ts` with `use` prefix (e.g., `useSearchForm.ts`)
  - Extract complex logic into custom hooks, split large components into smaller reusable ones
  - Use TypeScript interfaces for prop types

## Testing Guidelines
- Focus unit tests on `search/services` using fakes for ports (no network/disk).
- Layout: `tests/<area>/test_*.py` (e.g., `tests/services/test_query.py`).
- Optional coverage: `pytest -q --cov`.

## Commit & Pull Request Guidelines
- Commits: concise, imperative; prefer Conventional Commits.
  - Examples: `feat(services): reuse embeddings`, `fix(adapter): numpy truthiness crash`.
- PRs: describe purpose, scope, how to run; include sample output and link issues.

## Security & Configuration
- Never commit secrets. Use `.env` with `OPENAI_API_KEY` and optional `OPENAI_BASE_URL` (Python).
- Backend env (NestJS):
  - Required: `IS_CORS_ENABLED`, `APP_NAME`, `APP_ENV`, `APP_PORT`, `PYTHON_BIN`, `PYTHON_SEARCH_MODULE`
  - Optional: `PYTHON_WORKDIR` (defaults to one level above back-end cwd)
  - Validation schema: `src/shared/configs/validation.schema.ts`
- Frontend env (Next.js):
  - `NEXT_PUBLIC_BACKEND_URL`: backend base URL (default: `http://localhost:`)
  - `NEXT_PUBLIC_APP_PORT`: backend port (default: `3001`)
  - Environment files: `.env.development`, `.env.production`
- Chroma persists locally; customize via flags (`--persist`, `--collection`, `--space`).

## Architecture Overview
- Hexagonal core in `search/`: services depend on ports; adapters implement OpenAI/Chroma.
- Backend shells out to `python -m search.api` and returns JSON.
- Frontend (Next.js + MUI):
  - Component-based architecture with separation of concerns
  - Custom hooks manage form state, chunking options, and dataset operations
  - Theme system: auto-detects system preference (light/dark), allows manual override, persists in localStorage + URL
  - ThemeMode enum for type-safe theme handling
  - Posts to `/search` endpoint, shows top-k results with metadata
  - Chunking controls: toggle Index chunks, choose mode (sentence/token), and tune per-mode parameters. Token chunking is useful for long or punctuation-light texts.
