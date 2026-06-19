# MuscatPlus Reconciliation Service

`muscatplus_reconciliation` is a small Sanic service that exposes an OpenRefine-compatible reconciliation API for RISM Online authority and source records backed by Solr.

The service:

- serves a reconciliation service document
- accepts reconciliation queries for people, institutions, sources, and subjects
- provides entity suggestions for autocomplete
- returns a small HTML preview for matched entities
- translates between Solr document ids like `person_123` and reconciliation ids like `people/123`

## Project Layout

- `reconciliation_server/server.py`: Sanic app and routes
- `reconciliation_server/service.py`: service document response
- `reconciliation_server/query.py`: reconciliation, suggest, and preview handlers
- `reconciliation_server/query_response.py`: response serialization and preview HTML
- `reconciliation_server/identifiers.py`: id conversion helpers
- `reconciliation_server/solr.py`: Solr client initialization
- `configuration.yml`: local runtime configuration
- `tests/`: basic Sanic endpoint tests

## Requirements

- Python `3.14`
- `uv`
- A reachable Solr core/collection containing the fields used by this service

The repo is pinned to Python `3.14` via `.python-version`, and `pyproject.toml` currently requires `>=3.14,<4`.

## Configuration

Runtime configuration is loaded from `configuration.yml` at import time.

Current local defaults:

```yaml
common:
  debug: yes
  context_uri: yes
  secret: <forwarded secret>
  version: "development"

solr:
  server: "http://localhost:8983/solr/muscatplus_live"
```

Notes:

- `common.debug` controls logging level and whether Sentry is enabled.
- `common.secret` is assigned to `app.config.FORWARDED_SECRET`.
- `common.version` is surfaced in the service document.
- `solr.server` must point at the MuscatPlus Solr index.
- When `debug` is disabled, the code expects a `sentry` section with `dsn` and `environment`.

## Getting Started

Install dependencies:

```bash
uv sync --dev
```

Run the service locally:

```bash
uv run sanic reconciliation_server.server:app --dev --host 0.0.0.0 --port 8000
```

The Sanic app mounts its blueprint under `/reconciliation`, so the main service URLs are:

- `GET /reconciliation/`
- `GET|POST /reconciliation/reconcile`
- `GET /reconciliation/suggest/entity`
- `GET /reconciliation/preview`

## API Overview

### Service document

Request:

```bash
curl http://127.0.0.1:8000/reconciliation/
```

The response advertises reconciliation API version `0.2` and the default types:

- `Person`
- `Institution`
- `Source`

### Reconciliation queries

The service accepts OpenRefine-style batch queries and returns a result array for each query key.

Example `GET` request:

```bash
curl --get \
  --data-urlencode 'queries={"q0":{"query":"Beethoven","type":"Person","limit":5}}' \
  http://127.0.0.1:8000/reconciliation/reconcile
```

Example `POST` request:

```bash
curl -X POST \
  -F 'queries={"q0":{"query":"Beethoven","type":"Person","limit":5}}' \
  http://127.0.0.1:8000/reconciliation/reconcile
```

Supported query behavior from the current implementation:

- `type` filters on `Person`, `Institution`, `Source`, or `Subject`
- source queries add `is_collection_record_b:true`
- source, person, institution, and subject records are queried from Solr
- `limit` is passed through to the Solr request
- `properties` currently recognizes:
  - `siglum`
  - `diamm`

If the `diamm` property is not present, results are filtered to documents without `project_s`.

### Suggest API

Entity suggestions are available from:

```bash
curl --get \
  --data-urlencode 'prefix=Beeth' \
  http://127.0.0.1:8000/reconciliation/suggest/entity
```

This returns up to 20 matches and boosts collection source records, people, and institutions.

### Preview API

The preview endpoint returns a small HTML fragment for a reconciliation id:

```bash
curl --get \
  --data-urlencode 'id=people/123' \
  http://127.0.0.1:8000/reconciliation/preview
```

Accepted reconciliation id prefixes are:

- `people/<id>`
- `institutions/<id>`
- `sources/<id>`
- `subjects/<id>`

These are converted internally to Solr ids such as `person_123` or `source_123`.

## Development

Run tests:

```bash
uv run pytest
```

Run type checking:

```bash
uv run mypy reconciliation_server
```

Run linting if Ruff is installed in your environment:

```bash
uv run ruff check .
```

## Current Caveat

At the time of writing, the existing tests target legacy root-level paths such as `/reconcile`, but the current app routes live under `/reconciliation/...`. In the current checkout, `uv run pytest` fails with `404` responses for that reason rather than because of Solr query failures.
