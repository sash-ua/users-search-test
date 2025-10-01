# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tool Usage Policy

**MCP Server Priority**: Always prefer using MCP (Model Context Protocol) server tools when available over alternative approaches. For example:
- Use Chrome DevTools MCP for web UI inspection, debugging, and browser interactions
- Use IDE MCP for diagnostics and code intelligence
- Leverage any other available MCP servers for their specialized capabilities

MCP tools provide optimized, purpose-built interfaces and should be your first choice when applicable.

## Project Overview

AI-path is a semantic search application demonstrating vector-based user search with a three-tier architecture:
- **Frontend**: Next.js 14 (React 18) + TypeScript + Material-UI
- **Backend**: NestJS (Node.js + TypeScript) REST API
- **Search/ML**: Python 3.10+ package using OpenAI embeddings + ChromaDB

## Development Setup

### Initial Installation

```bash
# Install Node dependencies
cd front-end && npm install
cd ../back-end && npm install

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r search/requirements.txt
pip install pytest

# Set PYTHON_BIN environment variable
export PYTHON_BIN=$(which python)  # Windows: set PYTHON_BIN=%CD%\.venv\Scripts\python.exe
```

### Environment Variables

Create `.env` in repo root with:
```bash
OPENAI_API_KEY=sk-your-key-here
IS_CORS_ENABLED=true
APP_PORT=3001
PYTHON_BIN=python3
PYTHON_SEARCH_MODULE=search.api
```

Frontend uses `.env.development` with `NEXT_PUBLIC_BACKEND_URL=http://localhost:`.

**Security**: Never commit secrets. Backend validates env vars via `src/shared/configs/validation.schema.ts`.

## Common Commands

### Running the Application

```bash
# Backend (Terminal 1) - runs on port 3001
cd back-end
npm run start          # development with watch mode

# Frontend (Terminal 2) - runs on port 3000
cd front-end
npm run dev

# Production builds
cd back-end && npm run build && npm run start:prod
cd front-end && npm run build && npm run start
```

### Python Search Module

```bash
# From repo root with activated venv

# Interactive query with human-readable output
python -m search.query --query "golang microservices" --k 5 --data data.json

# JSON output (used by backend)
python -m search.api --query "golang microservices" --k 5 --data data.json --normalize --phrase-prefilter

# Export user schema
python -m search.api --export-user-schema  # writes to schemas/user.schema.json

# Chunking examples
# Sentence mode
python -m search.query --query "bicycle" --data data.json --index-chunks --chunking-mode sentence --sentences-per-chunk 3 --sentence-overlap 1

# Token mode (useful for long texts or punctuation-light content)
python -m search.query --query "bicycle" --data data.json --index-chunks --chunking-mode token --tokens-per-chunk 200 --token-overlap 50

# Lint and format Python code
black . && ruff check .

# Run tests
cd search && pytest -q
pytest --cov                # with coverage
```

## Architecture

### Request Flow
1. User submits search via Next.js frontend → `POST /search`
2. NestJS backend (`search.service.ts`) spawns Python subprocess via `python.ts`
3. Backend calls `python -m search.api` with CLI arguments
4. Python module (`api.py`) orchestrates:
   - Load data from JSON file
   - Embed query using OpenAI API
   - Search ChromaDB vector store
   - Return JSON results to stdout
5. Backend parses JSON and returns to frontend

### Python Module (Hexagonal Architecture)

```
search/
├── api.py                    # CLI entry point (JSON output for backend)
├── query.py                  # CLI entry point (human-readable output)
├── models/                   # Pydantic data models (User, Person)
├── ports/                    # Abstract interfaces
│   ├── embeddings.py         # EmbeddingsProvider protocol
│   └── user_vectors.py       # UserVectorsRepo protocol
├── adapters/                 # Concrete implementations
│   ├── openai_embeddings.py  # OpenAI API client
│   └── chroma_user_vectors.py # ChromaDB wrapper
├── services/                 # Business logic
│   ├── ingest_users.py       # Data loading and indexing
│   ├── ingest_strategies.py  # Chunking strategies (sentence/token)
│   └── query_users.py        # Search orchestration
└── utils/                    # Helpers (load_data, load_env, etc.)
```

**Key concepts**:
- `ports/` define abstract interfaces (dependency inversion)
- `adapters/` implement ports for specific technologies (OpenAI, ChromaDB)
- `services/` contain business logic and depend only on ports
- Chunking strategies: `sentence` (split by sentences) or `token` (split by token count)

### Backend Python Bridge

`back-end/src/search/python.ts` spawns Python process using `child_process.spawn()`:
- Constructs CLI arguments from `SearchQueryArgs`
- Sets `cwd` to repo root (or `PYTHON_WORKDIR`)
- Parses JSON from stdout
- If Python exits non-zero or JSON parse fails, returns error

### Frontend Architecture

Component structure with separation of concerns:
- `src/components/` - Presentational components (SearchForm, SearchResults, etc.)
- `src/hooks/` - Custom hooks for state management (useSearchForm, useChunking, useDataset)
- `src/providers/` - Context providers (ThemeProvider with localStorage persistence)
- `src/app/page.tsx` - Main page orchestration (~130 lines)

## Key Files

- `back-end/src/search/python.ts:6` - Python subprocess execution
- `search/api.py:17` - Main Python CLI entry point
- `search/services/ingest_users.py` - Data ingestion and chunking logic
- `search/services/query_users.py` - Search orchestration with phrase prefiltering
- `search/adapters/chroma_user_vectors.py:39` - ChromaDB collection creation with auto-reindexing

## Data Flow

### Indexing
1. Load users from JSON file (`data.json`)
2. Optional: chunk user data (sentence or token-based)
3. Generate embeddings for each user/chunk via OpenAI API
4. Store in ChromaDB collection (persisted to `.chroma/`)

### Querying
1. Optional: phrase prefilter (substring match before vector search)
2. Embed query text
3. Vector search in ChromaDB (cosine/L2/IP distance)
4. Optional: if chunking enabled, de-duplicate users and multiply k by `chunk_query_multiplier`
5. Return results with distance scores and snippets

### Auto-reindexing
Collection is recreated if:
- Model embedding dimensions mismatch
- Chunking settings change (mode, sentences_per_chunk, etc.)

## Testing

```bash
# Python tests
source .venv/bin/activate
cd search
pytest -q                           # quick mode
pytest -v                           # verbose
pytest search/tests/services/       # specific directory

# No JavaScript/TypeScript tests currently implemented
```

**Testing guidelines**: Focus unit tests on `search/services/` using fake implementations for ports (no network/disk). Test layout: `tests/<area>/test_*.py`.

## Coding Style

### Python
- Follow PEP 8 with 4-space indentation
- Full type hints on all functions
- Pydantic models use `Field(..., min_length=..., max_length=..., description=...)`
- Naming: modules `snake_case.py`, classes `PascalCase`, functions/vars `snake_case`

### TypeScript/JavaScript
- Strict TypeScript in backend and frontend
- Modules and files: `kebab-case` or `camelCase` consistently
- Functions/vars: `camelCase`

### React
- Components: `PascalCase.tsx` (e.g., `ThemeSwitcher.tsx`)
- Hooks: `camelCase.ts` with `use` prefix (e.g., `useSearchForm.ts`)
- Extract complex logic into custom hooks
- Split large components into smaller reusable ones
- Use TypeScript interfaces for prop types

## Commit Guidelines

Use Conventional Commits format with concise, imperative messages:
- `feat(services): reuse embeddings cache`
- `fix(adapter): handle numpy array truthiness crash`
- `refactor(frontend): extract search form hook`

## Notes

- ChromaDB data persists to `.chroma/` (gitignored)
- Backend expects Python binary at `$PYTHON_BIN` environment variable
- Frontend theme preference saved in localStorage + URL params
- Dataset uploads supported via `POST /datasets` (multipart/form-data)