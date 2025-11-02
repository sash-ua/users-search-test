# Users search

## Overview
AI-path is a semantic search application demonstrating a full-stack architecture for vector-based user search.

### Stack
- **Front-end**: Next.js 14 (React 18) + TypeScript + Material-UI 6
  - Component-based architecture with custom hooks
  - Auto/light/dark theme support with persistence
  - Responsive design with mobile support
- **Back-end**: NestJS 10 (Node.js + TypeScript)
  - REST API that bridges HTTP requests to Python search module
  - File upload support for datasets
  - Environment-based configuration with validation
- **Search/ML**: Python 3.10+ package
  - OpenAI embeddings for semantic search
  - ChromaDB for vector storage with HNSW indexing
  - Hexagonal architecture (ports/adapters pattern)
  - Support for sentence and token-based chunking

### Architecture Flow
1. User submits search query via Next.js frontend
2. Frontend calls NestJS backend `/search` endpoint
3. Backend spawns Python process (`search.api` module)
4. Python module embeds query, searches ChromaDB, returns JSON results
5. Frontend displays ranked results with metadata and snippets

## Requirements
- **Node.js**: v18+ LTS recommended
- **npm**: v8+ (bundled with Node)
- **Python**: 3.10+ recommended
- **OpenAI API**: API key for embeddings (or compatible provider)
- **OS**: macOS, Linux, or Windows

### Dependencies
- Frontend: `next@14.2.33`, `react@18.2.0`, `@mui/material@6.1.6`, `@mui/icons-material@6.5.0`
- Backend: `@nestjs/core@10.0.0`, `@nestjs/config@4.0.2`, `multer@1.4.5-lts.1`
- Python: `openai`, `chromadb`, `pydantic`, `python-dotenv` (see `search/requirements.txt`)

## Project Structure

### Frontend (`front-end/`)
```
front-end/
├── public/                   # Static assets
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── layout.tsx        # Root layout with metadata
│   │   └── page.tsx          # Home page (130 lines, refactored)
│   ├── components/           # Reusable React components
│   │   ├── ThemeSwitcher.tsx
│   │   ├── SearchForm.tsx
│   │   ├── ChunkingOptions.tsx
│   │   ├── DatasetSelector.tsx
│   │   └── SearchResults.tsx
│   ├── hooks/                # Custom React hooks
│   │   ├── useSearchForm.ts
│   │   ├── useChunking.ts
│   │   └── useDataset.ts
│   ├── providers/            # Context providers
│   │   └── ThemeProvider.tsx # Theme management with persistence
│   └── types/                # TypeScript types
│       └── theme.ts          # ThemeMode enum
├── .env.development
├── .env.production
├── tsconfig.json
└── package.json
```

### Backend (`back-end/`)
```
back-end/
├── src/
│   ├── main.ts                               # NestJS entry point
│   ├── search/
│   │   ├── search.controller.ts             # POST /search
│   │   ├── search.service.ts
│   │   └── python.ts                        # Python bridge
│   ├── datasets/
│   │   └── datasets.controller.ts           # GET/POST /datasets
│   └── shared/
│       ├── configs/validation.schema.ts     # Env validation
│       └── providers/config-provider.ts
└── package.json
```

### Search Module (`search/`)
```
search/
├── api.py                    # JSON output CLI (called by backend)
├── query.py                  # Human-readable CLI
├── models/                   # Pydantic models
├── ports/                    # Interfaces
├── adapters/
│   ├── openai_embeddings.py
│   └── chroma_user_vectors.py
├── services/                 # Business logic (ingest/query)
├── utils/                    # Helpers
└── tests/                    # Pytest unit tests
```

### Data
- `data.json` - Sample dataset at repo root
- `.chroma/` - ChromaDB persistence directory (gitignored)

## Environment Variables

### Frontend (`.env.development`, `.env.production`)
```bash
APP_NAME='Context users search'
APP_ENV=development
NEXT_PUBLIC_APP_PORT=3001
NEXT_PUBLIC_BACKEND_URL=http://localhost:
```

### Backend (NestJS - `.env` or `.env.[NODE_ENV]`)
**Required:**
```bash
IS_CORS_ENABLED=true
APP_NAME=Search API
APP_ENV=development
APP_PORT=3001
PYTHON_BIN=python3
PYTHON_SEARCH_MODULE=search.api
```

**Optional:**
```bash
PYTHON_WORKDIR=/path/to/AI-path
```

### Python Search Module (`.env` in repo root)
**Required:**
```bash
OPENAI_API_KEY=sk-...
```

**Optional:**
```bash
OPENAI_BASE_URL=https://api.openai.com/v1
```

**Note**: Backend loads `.env` and `.env.[NODE_ENV]` via `@nestjs/config`. Python CLI loads `.env` via `python-dotenv`.

#### Local embeddings servers
If you use a self‑hosted OpenAI‑compatible endpoint (e.g. `http://127.0.0.1:1234/v1`), set `OPENAI_BASE_URL` accordingly and use a model that endpoint provides (e.g. `text-embedding-mxbai-embed-large-v1`). When running through the NestJS backend, add the same `OPENAI_API_KEY` (dummy is fine for most local servers) and `OPENAI_BASE_URL` to `back-end/.env` so the spawned Python process inherits them. Forgetting this typically manifests as HTTP 500 errors on `/search`.

## Installation and Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd AI-path
```

### 2. Install Node Dependencies
```bash
# Frontend
cd front-end
npm install

# Backend
cd ../back-end
npm install
```

### 3. Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r search/requirements.txt
pip install pytest
```

**Windows:**
```bash
python3 -m venv .venv
.venv\Scripts\activate
pip install -r search/requirements.txt
pip install pytest
```

**Set PYTHON_BIN (macOS/Linux):**
```bash
export PYTHON_BIN=$(which python)
```

**Set PYTHON_BIN (Windows):**
```bash
set PYTHON_BIN=%CD%\.venv\Scripts\python.exe
```

### 4. Configure Environment Variables

**Repo root `.env`:**
```bash
OPENAI_API_KEY=sk-your-key-here
IS_CORS_ENABLED=true
APP_NAME=Search API
APP_ENV=development
APP_PORT=3001
PYTHON_BIN=python3
PYTHON_SEARCH_MODULE=search.api
OPENAI_BASE_URL=https://api.openai.com/v1
PYTHON_WORKDIR=/path/to/AI-path
```

**Frontend `.env.development`:**
```bash
APP_NAME='Context users search'
APP_ENV=development
NEXT_PUBLIC_APP_PORT=3001
NEXT_PUBLIC_BACKEND_URL=http://localhost:
```

## Running the Project

### Option A: Full Stack (Recommended)

**Terminal 1 - Backend:**
```bash
cd back-end
npm run start
```
API listens on port 3001. Endpoints:
- `POST /search` - Execute semantic search
- `GET /datasets` - List available datasets
- `POST /datasets` - Upload dataset JSON file

**Terminal 2 - Frontend:**
```bash
cd front-end
npm run dev
```
Open **http://localhost:3000** in your browser

### Option B: Python CLI Only

**Human-readable output:**
```bash
python -m search.query --query "golang microservices" --k 5 --data data.json \
  --normalize --phrase-prefilter
```

**JSON output (used by backend):**
```bash
python -m search.api --query "golang microservices" --k 5 --data data.json \
  --normalize --phrase-prefilter
```

**Export user schema:**
```bash
python -m search.api --export-user-schema
```
Writes to `schemas/user.schema.json`

## Search Parameters

### Basic Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--query` | string | - | Text query for semantic search |
| `--k` | int | 5 | Number of results to return |
| `--data` | path | data.json | Path to dataset JSON file |
| `--model` | string | text-embedding-mxbai-embed-large-v1 | Embedding model name |
| `--threshold` | float | - | Max distance threshold to accept |
| `--normalize` | flag | false | Normalize text before embedding |
| `--phrase-prefilter` | flag | false | Substring filter before vector search |

### ChromaDB Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--persist` | path | .chroma | Chroma persistence directory |
| `--collection` | string | users | Collection name |
| `--space` | string | cosine | Vector space metric (cosine/l2/ip) |

### Chunking Parameters (with `--index-chunks`)
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--chunking-mode` | string | sentence | sentence or token |
| `--sentences-per-chunk` | int | 3 | Sentences per chunk (sentence mode) |
| `--sentence-overlap` | int | 1 | Overlap sentences (sentence mode) |
| `--tokens-per-chunk` | int | 200 | Tokens per chunk (token mode) |
| `--token-overlap` | int | 50 | Overlap tokens (token mode) |
| `--chunk-query-multiplier` | int | 5 | Query result multiplier for chunking |

## NPM Scripts

### Frontend (`front-end/`)
```bash
cd ./front-end
npm run dev 
npm run build
npm run start
```

### Backend (`back-end/`)
```bash
cd ./back-end
npm run start     
npm run start:prod  
npm run build     
```

## API Contract

### `POST /search`
**Request Body:**
```json
{
  "query": "golang microservices",
  "k": 5,
  "normalize": true,
  "phrase_prefilter": true,
  "threshold": 0.5,
  "model": "text-embedding-mxbai-embed-large-v1",
  "data": "data.json",
  "index_chunks": true,
  "chunking_mode": "sentence",
  "sentences_per_chunk": 3,
  "sentence_overlap": 1,
  "chunk_query_multiplier": 5
}
```

**Response:**
```json
{
  "query": "golang microservices",
  "k": 5,
  "count": 3,
  "rows": [
    {
      "id": "user_123",
      "distance": 0.234,
      "metadata": {
        "first_name": "John",
        "last_name": "Doe"
      },
      "snippet": "Experienced with golang microservices...",
      "chunk_index": 0,
      "chunk_count": 2
    }
  ],
  "distances": [0.234, 0.456, 0.678],
  "collection": "users",
  "space": "cosine",
  "model": "text-embedding-mxbai-embed-large-v1",
  "reindexed": false
}
```

### Other Endpoints
- `GET /datasets` - List available dataset files
- `POST /datasets` - Upload dataset JSON (multipart/form-data)

## Testing

### Python Tests
```bash
source .venv/bin/activate
cd search
pytest -q
```

### JavaScript/TypeScript Tests
Currently not implemented.
**TODO**: Add unit tests for NestJS backend and Next.js frontend.

## Data and Persistence
- **Input**: `data.json` at repo root (or upload via UI)
- **ChromaDB**: Persists to `.chroma/` directory (gitignored)
- **Auto-reindex**: Collection recreated when chunking settings or model dimensions change

## Frontend Features
- **Theme System**: Auto/light/dark modes with system preference detection
- **Theme Persistence**: Saved in localStorage and URL parameters
- **Responsive Design**: Mobile-friendly layout
- **Component Architecture**: Modular, reusable components with custom hooks
- **Type Safety**: Full TypeScript with strict mode
- **Material-UI**: v6 with Emotion styling

## Notes & TODOs
- [ ] Add LICENSE file
- [ ] Pin Python dependency versions in `requirements.txt`
- [x] ~~Parameterize frontend BACKEND_URL~~ (Done: using `NEXT_PUBLIC_BACKEND_URL`)
- [ ] Add Docker support for consistent deployment
- [ ] Add automated tests for backend and frontend
- [ ] Document Python and Node.js version constraints
- [ ] Add CI/CD pipeline configuration

## License
MIT license.
