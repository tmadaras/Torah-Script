
# Canonical Map Import Pack — Extended

Added:
- **Diff tool**: `scripts/diff_canonical_map.py` — compare a new CSV with DB (added/changed/removed) and write a JSON report.
- **Health counters API**: `GET /admin/canonical/health` — returns `missing_map`, `canon_duplicates`, `paleo_fallback_count`, `judges_9_9_dup`.
- **S3 import**: `POST /admin/canonical/import_s3?url=s3://bucket/key&dry_run=true|false` — stream CSV from S3 and import with full validation.
- **Admin UI page**: `ui/AdminCanonicalImport.tsx` — upload CSV, see dry-run vs real import, and link to health endpoint.

## Commands

### Diff against DB
```bash
export DATABASE_URL='postgresql+psycopg2://user:pass@host:5432/dbname'
python scripts/diff_canonical_map.py path/to/new_mapping.csv diff_report.json
```

### Health endpoint
- Mount `api/canonical_health_router.py` in FastAPI:
```python
from api.canonical_health_router import router as canonical_health
app.include_router(canonical_health)
```
- Check: `GET /admin/canonical/health`

### S3 import
- Mount `api/canonical_import_s3_router.py` in FastAPI:
```python
from api.canonical_import_s3_router import router as canonical_import_s3
app.include_router(canonical_import_s3)
```
- Call: `POST /admin/canonical/import_s3?url=s3://bucket/key&dry_run=true`

### Admin UI
- Add `ui/AdminCanonicalImport.tsx` into your admin route and serve it behind auth.
- The page calls `/admin/canonical/import` and links to `/admin/canonical/health`.

## Env
- `DATABASE_URL` (required for diff/health/import)
- `CANONICAL_ROW_SCHEMA` (optional, default `schema/mapping_row.schema.json`)
- AWS creds for S3 import (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`)

