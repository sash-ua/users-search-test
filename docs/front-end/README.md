# Frontend (Next.js 14 + MUI) — Documentation

This frontend is a Next.js App Router app using Material UI (MUI) with a simple search UI, chunking controls, dataset upload, and a theme system (auto/light/dark) persisted in localStorage and synchronized with the URL.

## Overview
- Framework: Next.js 14 App Router, React 18, TypeScript
- UI: Material UI v6, Emotion
- Theming: Auto/Light/Dark with URL + localStorage persistence
- Features:
  - Search form that posts to the backend `/search` endpoint
  - Chunking options (sentence or token-based) with parameters
  - Dataset selection or upload before querying
  - Pageless single-view UX with loading and error states

## Project Structure
- `front-end/src/app/`
  - `layout.tsx`: Root layout, wraps app with `<ThemeProvider/>`
  - `page.tsx`: Main page containing the form, results, and theme switcher
- `front-end/src/components/`
  - `ThemeSwitcher.tsx`: Cycles auto/light/dark modes
  - `SearchForm.tsx`: Main form UI (query, k, model, flags)
  - `ChunkingOptions.tsx`: Chunking & overlap controls
  - `DatasetSelector.tsx`: Select existing dataset or upload new JSON
  - `SearchResults.tsx`: Displays result rows with expandable details
  - `Loading.tsx`: Suspense fallback loader
- `front-end/src/hooks/`
  - `useSearchForm.ts`: Form state, computes `BACKEND_URL` from env, fetches results
  - `useChunking.ts`: Chunking state and defaults
  - `useDataset.ts`: List datasets, handle file selection and upload
- `front-end/src/providers/`
  - `ThemeProvider.tsx`: Context + MUI theme provider with mode persistence
- `front-end/src/types/`
  - `theme.ts`: `ThemeMode` enum

## Environment Variables
- `NEXT_PUBLIC_BACKEND_URL` (string): Backend base URL prefix, e.g., `http://localhost:`
- `NEXT_PUBLIC_APP_PORT` (string or number): Backend port, e.g., `3001`

These are concatenated in `useSearchForm.ts`:
```ts
const BACKEND_URL = `${process.env.NEXT_PUBLIC_BACKEND_URL}${process.env.NEXT_PUBLIC_APP_PORT}`;
```

Example env files:
- `front-end/.env.development:1`
- `front-end/.env.production:1`

Ensure the final URL is valid (e.g., `http://localhost:3001`).

## Install & Run
- Install deps: `cd front-end && npm i`
- Development: `npm run dev` (default port 3000)
- Production build: `npm run build && npm run start`

Requires the backend running and reachable at `BACKEND_URL`.

## UX Flow
1. Choose dataset
   - Select an existing dataset from the list (fetched from `GET /datasets`)
   - Or upload a JSON file (stored to `search/uploads` by backend), optionally renaming it
2. Configure search
   - Enter `query`, optionally set `k`, `threshold`, `model`
   - Toggle `Normalize` and `Phrase prefilter`
3. Optional chunking
   - Enable `Index chunks`
   - Choose `Mode` (`sentence` or `token`)
   - Configure per-mode parameters and `Query multiplier`
4. Submit
   - Frontend posts to `${BACKEND_URL}/search` with the selected/ uploaded dataset path
   - Shows results with distances and optional chunk details

## Components & Hooks
- `ThemeProvider.tsx`
  - Persists `themeMode` in localStorage
  - Mirrors mode to URL via `?themeMode=auto|light|dark`
  - Respects system preference when `auto`
- `ThemeSwitcher.tsx`
  - Cycles Auto → Light → Dark
- `useSearchForm.ts`
  - Holds form state and builds request payload
  - Sends POST `/search`; handles loading, error, and result state
- `useChunking.ts`
  - Default values: sentence mode, sensible overlaps and multipliers
- `useDataset.ts`
  - Loads available datasets from `GET /datasets`
  - Handles file selection + multipart upload to `POST /datasets`

## Request Payload
Built in `page.tsx` before POST:
- Required: `query: string`
- Optional: `k`, `normalize`, `phrase_prefilter`, `threshold`, `model`
- Dataset: `data` set to either chosen dataset path or uploaded file path
- Chunking (when enabled):
  - `index_chunks: true`
  - `chunking_mode: 'sentence' | 'token'`
  - Sentence mode: `sentences_per_chunk`, `sentence_overlap`
  - Token mode: `tokens_per_chunk`, `token_overlap`
  - Always: `chunk_query_multiplier`

## Styling
- Uses MUI v6 theme and components
- `CssBaseline` applied at root
- Minimal custom CSS, leverages MUI system props

## Troubleshooting
- Backend URL wrong: Confirm `NEXT_PUBLIC_BACKEND_URL` and `NEXT_PUBLIC_APP_PORT` produce a valid URL
- CORS errors: Set `IS_CORS_ENABLED=true` on backend
- Upload failures: Ensure backend reachable and has write permissions for uploads dir
- Empty datasets: Backend may have none yet; upload a JSON file or place one under `search/uploads`

## Extending
- Add more search fields: extend `useSearchForm` state and form inputs; update payload in `page.tsx`
- Result rendering: update `SearchResults.tsx` to show additional metadata
- Theming: customize palette in `ThemeProvider.tsx` via `createTheme`
