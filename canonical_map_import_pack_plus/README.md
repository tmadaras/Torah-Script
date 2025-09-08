
# Canonical Map Import Pack

**Purpose:** Prevent data corruption and guarantee that your 39→24 per-token canonical map
is valid before it ever touches the database.

## Structure
- `schema/mapping_row.schema.json` — strict JSON Schema for each CSV row.
- `sql/preflight.sql` — applies your canonical schema (requires `canonical_mapping_schema.sql` nearby).
- `scripts/validate_csv.py` — CLI validator with row-by-row error messages.
- `scripts/load_canonical_map_csv.py` — Transactional UPSERT into `tanach_canonical_map` (Postgres).
- `api/canonical_import_router.py` — `POST /admin/canonical/import` (multipart CSV, `dry_run` support).
- `tests/` — pytest examples for validator and router.

## Usage
### Validate locally
```bash
python scripts/validate_csv.py /path/to/mapping.csv schema/mapping_row.schema.json
```

### Import locally (UPSERT)
```bash
export DATABASE_URL='postgresql+psycopg2://user:pass@host:5432/dbname'
python scripts/load_canonical_map_csv.py /path/to/mapping.csv schema/mapping_row.schema.json --dry-run
python scripts/load_canonical_map_csv.py /path/to/mapping.csv schema/mapping_row.schema.json
```

### FastAPI (server-side)
```python
from fastapi import FastAPI
from api.canonical_import_router import router
app = FastAPI()
app.include_router(router)  # POST /admin/canonical/import
```

**Tip:** Set `CANONICAL_ROW_SCHEMA=schema/mapping_row.schema.json` in server env.


## New Tools Added

### 4) Diff Tool
```bash
python scripts/diff_csv_vs_db.py /path/to/mapping.csv
```
→ Prints JSON summary of how many rows are **added**, **removed**, or **changed** compared to DB.

### 5) Health Counters Endpoint
- `GET /health/canonical/counters`
- Returns JSON with counts for:
  - `missing_map`
  - `canon_duplicates`
  - `paleo_fallback_count`
  - `judges_9_9_dup`

Integrate this with monitoring/alerts so issues are caught immediately after import.

