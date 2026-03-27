# Poké Project

A Pokédex-like web application for browsing, catching, and comparing Gen 1 Pokémon.

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green)
![Vite](https://img.shields.io/badge/Vite-dev-purple)

## Quick Start

Start the application with [pixi](https://pixi.sh) and visit http://localhost:8080 in your web browser.

```sh
pixi run app
```

This starts both the backend API server (port 8000) and the frontend dev server (port 8080) concurrently.

## Architecture

```
poke-project/
├── backend/
│   ├── app.py              # FastAPI application with all endpoints
│   ├── game.etilqs         # SQLite database for caught Pokémon (auto-created)
│   ├── pyproject.toml      # Python project config & pytest settings
│   └── tests/
│       ├── conftest.py     # Shared fixtures (async client, known Pokémon)
│       ├── test_status.py  # Health endpoint tests (5 tests)
│       ├── test_browsing.py# Pokédex browsing tests (24 tests)
│       ├── test_catching.py# Catch/release tests (18 tests)
│       └── test_stats.py   # Stats & leaderboard tests (18 tests)
├── frontend/
│   ├── package.json        # Node.js dependencies
│   ├── vite.config.js      # Vite dev server & build config
│   └── src/
│       ├── index.html      # Entry HTML
│       ├── index.jsx       # Main app component (Crank.js)
│       ├── api.js          # API client & utilities
│       ├── components/
│       │   └── ui.jsx      # Reusable UI components
│       ├── assets/
│       │   └── css/
│       │       └── theme.css  # Full theme stylesheet
│       └── public/
│           └── assets/
│               └── css/
│                   └── reset.css  # CSS reset
├── data/
│   ├── data.csv            # Pokémon dataset (800 entries)
│   └── data.json           # Pokémon data in JSON format
├── pixi.toml               # Pixi workspace config
├── pixi.lock               # Dependency lock file
└── app.sh                  # Startup script
```

### Backend (FastAPI + Python)

The backend is a FastAPI application that serves a REST API. It loads the Pokémon dataset from CSV at startup, filtering to Gen 1 single-word-name Pokémon. Caught Pokémon state is persisted in an SQLite database.

**Key technologies:**
- **FastAPI** — async web framework
- **pandas** — data loading and manipulation
- **aiosqlite** — async SQLite access
- **uvicorn** — ASGI server

### Frontend (Crank.js + Vite)

The frontend uses [Crank.js](https://crank.js.org/) — a JSX-based UI framework with generator components. Vite handles dev server, HMR, and build. The frontend proxies `/api/*` requests to the backend.

**Key technologies:**
- **Crank.js** — JSX UI framework with async generators
- **Vite** — dev server with HMR
- **Immutable.js** — persistent data structures
- **Axios** — HTTP client
- **Babel** — JSX transform + experimental syntax support

## API Reference

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/status` | Health check with uptime, Pokédex size, caught counts |

### Pokédex Browsing

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/names` | List all Pokémon names with Pokédex ID mapping |
| GET | `/info/{name}` | Detailed info for a specific Pokémon (stats, types, sprite) |
| GET | `/types` | List all types with Pokémon counts per type |
| GET | `/search` | Search/filter Pokémon with sorting and pagination |
| GET | `/pokedex` | Full Pokédex with sprites and caught status |

#### Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search by name (partial match) |
| `type` | string | Filter by primary or secondary type |
| `legendary` | bool | Filter legendary Pokémon |
| `min_total` | int | Minimum total stats |
| `max_total` | int | Maximum total stats |
| `sort_by` | string | Sort by: name, total, hp, attack, defense, speed, pokedex_id |
| `order` | string | Sort order: asc or desc |
| `limit` | int | Max results (1-200, default 50) |
| `offset` | int | Offset for pagination |

### Catching & Releasing

| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/catch` | Catch a Pokémon (body: `{"name": "pikachu"}`) |
| PUT | `/release` | Release one of a caught Pokémon |
| GET | `/caught` | List all caught Pokémon with counts and sprites |
| GET | `/catch-history` | Timestamped catch log (newest first) |

### Statistics & Comparison

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stats` | Type distribution, stat leaders, average stats |
| GET | `/leaderboard` | Rank Pokémon by any stat (params: `stat`, `limit`, `order`) |
| GET | `/compare/{name1}/{name2}` | Head-to-head stat comparison |

### API Examples

```sh
# Health check
curl http://localhost:8000/status

# Get all names
curl http://localhost:8000/names

# Get info for Pikachu
curl http://localhost:8000/info/pikachu

# Search for fire types sorted by attack
curl "http://localhost:8000/search?type=fire&sort_by=attack&order=desc"

# Catch a Pokémon
curl -X PUT http://localhost:8000/catch \
  -H "Content-Type: application/json" \
  -d '{"name": "pikachu"}'

# Release a Pokémon
curl -X PUT http://localhost:8000/release \
  -H "Content-Type: application/json" \
  -d '{"name": "pikachu"}'

# View caught Pokémon
curl http://localhost:8000/caught

# Compare two Pokémon
curl http://localhost:8000/compare/pikachu/charizard

# Top 10 by attack
curl "http://localhost:8000/leaderboard?stat=attack&limit=10"

# Pokédex stats
curl http://localhost:8000/stats
```

## Running Tasks

```sh
# Start the full application (backend + frontend)
pixi run app

# Start only the backend
pixi run backend

# Start only the frontend (after npm install)
pixi run frontend

# Install frontend dependencies
pixi run frontend-install
```

## Testing

The backend has a comprehensive test suite with 65 tests covering all endpoints.

```sh
# Run all tests (from the backend directory)
cd backend
pixi run python -m pytest tests/ -v

# Run specific test file
pixi run python -m pytest tests/test_browsing.py -v

# Run with coverage (if pytest-cov installed)
pixi run python -m pytest tests/ --cov=. --cov-report=term-missing
```

## Frontend Components

The UI is built with reusable Crank.js components:

| Component | Description |
|-----------|-------------|
| `TypeBadge` | Colored pill badge for Pokémon types |
| `StatBar` / `StatBars` | Animated stat bar visualizations with gradients |
| `SpriteImage` | Lazy-loaded pixelated sprite display |
| `Card` | Elevated container with title and optional badge |
| `TabBar` | Tab navigation with active indicator |
| `PokedexCard` | Grid card for Pokédex browsing |
| `SearchInput` | Styled search field |
| `TypeFilter` | Clickable type filter buttons |
| `ComparisonRow` | Head-to-head stat comparison display |
| `StatsOverview` | Dashboard with type distribution |
| `LeaderboardTable` | Ranked table with sprites |
| `CatchHistoryList` | Timestamped catch log |
| `EmptyState` | Placeholder for empty views |
| `Spinner` / `LoadingOverlay` | Loading indicators |

## CSS Theme

The project includes a comprehensive CSS theme (`frontend/src/assets/css/theme.css`) with:

- **CSS Custom Properties**: Colors, spacing, typography, shadows, z-index layers
- **Pokémon Type Colors**: All 18 types with background and text colors
- **Component Styles**: Cards, tables, buttons, badges, search bars, grids
- **Stat Visualizations**: Per-stat gradient color bars
- **Animations**: Shimmer, spin, catch bounce, slide-in, fade-out
- **Responsive Design**: Breakpoints at 768px and 480px

## Data Source

The Pokémon dataset (`data/data.csv`) contains 800 Pokémon entries with:
- Pokédex number, name, primary/secondary types
- Base stats: HP, Attack, Defense, Sp. Atk, Sp. Def, Speed, Total
- Generation (1-6) and legendary status

The app filters to **Gen 1 Pokémon with single-word names** (~100 Pokémon) at runtime.

## Supported Platforms

- `linux-64`
- `osx-arm64`

## License

MIT
