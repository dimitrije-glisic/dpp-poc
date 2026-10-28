# Battery Digital Product Passport – Demo

A small, self-contained **Digital Product Passport (DPP)** demo for the fictional industrial battery
manufacturer **Demo Battery Works GmbH**, built with FastAPI, SQLite, SQLAlchemy, Pydantic and Jinja2.

> ⚠️ **Demo only.** The manufacturer is fictional, and all passport values (carbon footprint, recycled
> content, end-of-life information) are illustrative. This is **not** a regulatory-compliant passport (e.g.
> under the EU Battery Regulation 2023/1542).

## Features
- Register batteries with a unique product identifier (REST API)
- Store product identity, technical specs and sustainability / end-of-life data
- List batteries and view internal detail pages
- Public, mobile-friendly passport page per battery
- QR code (PNG or SVG) linking to the public passport page
- Interactive API docs at `/docs` (Swagger UI) and `/redoc`
- Sample data, seed script and pytest suite

## Quick start
Requires Python 3.12 or newer (developed on 3.14).

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

python -m scripts.seed                # load 6 fictional batteries into dpp.db (safe to re-run)
uvicorn app.main:app --reload         # start the server
```

Open:
- http://localhost:8000/batteries – battery list
- http://localhost:8000/passport/DBW-IB-NMC-2023-000201 – an example public passport
- http://localhost:8000/docs – interactive API docs (try `POST /api/batteries` here)

Run the tests:
```bash
pytest
```

### Scanning QR codes with a phone
QR codes encode `PUBLIC_BASE_URL/passport/{product_id}`. The default `http://localhost:8000` only works on
your own machine. To scan from a phone on the same network:

```bash
PUBLIC_BASE_URL=http://<your-LAN-IP>:8000 uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Configuration
| Env var | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./dpp.db` | SQLAlchemy database URL |
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Base URL used in QR codes and `passport_url` |

## Architecture
```
Browser / Swagger UI / phone scanning a QR code
            │
FastAPI app (app/main.py)
 ├─ routers/pages.py → Jinja2 templates (HTML, read-only)
 ├─ routers/api.py   → Pydantic schemas (JSON)
 └─ qr.py            → QR images for passport URLs
            │
crud.py            database access functions
            │
models.py          SQLAlchemy ORM model ── database.py (engine, session, get_db)
            │
SQLite file: dpp.db
```

How a request flows, e.g. `POST /api/batteries`:
1. FastAPI parses the JSON body into `schemas.BatteryCreate`. Pydantic validates it and returns **422**
   on bad input.
2. `get_db()` provides a database session (FastAPI dependency injection).
3. `crud.create_battery()` checks uniqueness (**409** on conflict), then inserts a `models.Battery` row.
4. The ORM object is converted to `schemas.BatteryRead` (via `from_attributes=True`). That model adds the
   computed `passport_url` and is returned as JSON.

The ORM model (`models.py`, which defines storage) and the Pydantic schemas (`schemas.py`, which define the
API contract) are kept separate on purpose. That way the internal `id` is never exposed, and API validation
can change independently of the table.

## Project structure
```
app/
  main.py            app setup, router registration, table creation on startup
  config.py          settings from environment variables
  database.py        engine, session factory, get_db dependency
  models.py          SQLAlchemy Battery model
  schemas.py         Pydantic enums and request/response models
  crud.py            database functions
  qr.py              passport URL builder and QR generation (segno)
  routers/api.py     JSON endpoints
  routers/pages.py   HTML endpoints
  templates/         Jinja2 templates (base layout, list, detail, passport, 404, macros)
  static/style.css
data/sample_batteries.json   fictional sample data
scripts/seed.py              idempotent seed script
tests/                       pytest suite (in-memory SQLite per test)
```

## Data model
A single table, `batteries`:

| Group | Fields |
|---|---|
| Identity | `product_id` (unique, public), `manufacturer`, `model`, `serial_number` (unique per manufacturer), `chemistry`, `capacity_kwh`, `manufacturing_date`, `lifecycle_status` |
| Technical | `nominal_voltage_v`, `weight_kg`, `expected_cycle_life` |
| Sustainability *(illustrative)* | `carbon_footprint_kg_co2e_per_kwh`, `recycled_cobalt_pct`, `recycled_lithium_pct`, `recycled_nickel_pct`, `recycled_lead_pct`, `end_of_life_info` |
| Meta | `is_demo_data`, `created_at`, `updated_at` (UTC) |

Enumerations:
- `chemistry`: `LFP`, `NMC`, `NCA`, `LTO`, `LEAD_ACID`, `NIMH`
- `lifecycle_status`: `manufactured`, `in_service`, `second_life`, `end_of_life`, `recycled`

Validation rules:
- `product_id` must match `^[A-Z0-9][A-Z0-9-]{2,63}$`
- Capacity, voltage, weight and cycle life must be greater than 0
- Percentages must be between 0 and 100
- `manufacturing_date` must not be in the future
- Unknown fields are rejected

## API
| Method | Path | Description |
|---|---|---|
| POST | `/api/batteries` | Register a battery (201, 409 duplicate, 422 invalid) |
| GET | `/api/batteries?status=&limit=&offset=` | List batteries |
| GET | `/api/batteries/{product_id}` | Get one battery (404 if unknown) |
| PATCH | `/api/batteries/{product_id}/status` | Change lifecycle status, body `{"lifecycle_status": "in_service"}` |
| GET | `/api/batteries/{product_id}/qr?format=png\|svg` | QR code image for the passport URL |
| GET | `/health` | Health check |

HTML pages:
- `/batteries` – list
- `/batteries/{product_id}` – internal detail page with QR code
- `/passport/{product_id}` – public passport

Example:
```bash
curl -X POST http://localhost:8000/api/batteries -H "Content-Type: application/json" -d '{
  "product_id": "DBW-IB-NCA-2025-000501",
  "manufacturer": "Demo Battery Works GmbH",
  "model": "PeakPack NCA 40",
  "serial_number": "PP40-25-000501",
  "chemistry": "NCA",
  "capacity_kwh": 40,
  "manufacturing_date": "2025-02-10",
  "nominal_voltage_v": 360,
  "weight_kg": 260,
  "expected_cycle_life": 2500,
  "carbon_footprint_kg_co2e_per_kwh": 80,
  "recycled_cobalt_pct": 14,
  "end_of_life_info": "Return to an authorised take-back partner."
}'
```

## Known limitations
- **No authentication:** anyone who can reach the server can register batteries or change their status.
- **No migrations:** tables are created with `create_all`. After changing `models.py`, delete `dpp.db`
  and re-seed.
- **Single table:** passports are not versioned, and material composition is a fixed set of columns.
  A natural next step is `Battery` 1:1 `Passport` 1:N `Material`, plus a version history.
- **Lifecycle transitions are not enforced:** any status can be set at any time.
- **Guessable IDs:** public passport URLs use human-readable product IDs.
- **SQLite:** suitable for a single-user demo, not for concurrent writes.
