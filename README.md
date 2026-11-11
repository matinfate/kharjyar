# kharjyar

[![Tests](https://github.com/matinfate/kharjyar/actions/workflows/tests.yml/badge.svg)](https://github.com/matinfate/kharjyar/actions/workflows/tests.yml)

A personal finance REST API with first-class **Jalali (Persian) calendar** support, built with FastAPI.

Track income and expenses, organise them into categories, and get summaries per month or per category — all using Jalali dates (`1405/07/21`) on the API surface while storing standard Gregorian dates in the database.

## Features

- **Categories** — create, list, get and delete (deleting a category that still has transactions is rejected with `409`)
- **Transactions** — full CRUD with income/expense types and optional category
- **Jalali dates in and out** — requests accept `jalali_date` (`1405/07/21` or `1405-07-21`), responses return `jalali_date`; the database stores Gregorian dates
- **Filtering** — list transactions by type, category and a Jalali date range
- **Reports**
  - overall summary (total income, total expense, balance)
  - monthly summary for any Jalali month, including leap-year Esfand
  - expense totals grouped by category
- **Validation** — invalid input (bad dates, negative amounts, unknown categories) returns clear `4xx` errors
- **Automated tests** — pytest suite using an isolated in-memory database, run on every push with GitHub Actions
- **Authentication** — user registration and login with JWT-based authentication
- **User isolation** — users can only access their own categories and transactions
- **Database migrations** — schema versioning and migrations with Alembic

## Tech stack

| Area | Tool |
|---|---|
| Language | Python 3.11+ (Docker image: 3.13) |
| Web framework | FastAPI |
| Server | Uvicorn |
| Validation | Pydantic v2 |
| Database / ORM | SQLite + SQLAlchemy |
| Jalali calendar | jdatetime |
| Testing | pytest, FastAPI TestClient |
| CI | GitHub Actions |

## Getting started

```bash
git clone https://github.com/matinfate/kharjyar.git
cd kharjyar

python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open the interactive API docs at <http://127.0.0.1:8000/docs>.

## API overview

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive a JWT access token |
| GET | `/auth/me` | Get the authenticated user's profile |
| POST | `/categories/` | Create a category |
| GET | `/categories/` | List categories |
| GET | `/categories/{id}` | Get one category |
| DELETE | `/categories/{id}` | Delete a category (`409` if it has transactions) |
| POST | `/transactions/` | Create a transaction |
| GET | `/transactions/` | List transactions — paginated (`page`, `size`), filters below |
| GET | `/transactions/{id}` | Get one transaction |
| PATCH | `/transactions/{id}` | Partially update a transaction |
| DELETE | `/transactions/{id}` | Delete a transaction |
| GET | `/transactions/summary` | Total income, expense and balance |
| GET | `/transactions/summary/monthly?year=1405&month=7` | Summary for one Jalali month |
| GET | `/transactions/summary/by-category` | Expense totals per category |

**Transaction list filters:** `type` (`income` / `expense`), `category_id`, `from_jalali`, `to_jalali`.

### Example

Create a transaction using a Jalali date:

```http
POST /transactions/
Content-Type: application/json

{
  "amount": 50000,
  "type": "expense",
  "jalali_date": "1405/07/21",
  "category_id": 1
}
```

Response:

```json
{
  "id": 1,
  "amount": 50000,
  "type": "expense",
  "description": null,
  "category_id": 1,
  "jalali_date": "1405/07/21"
}
```

Monthly summary:

```http
GET /transactions/summary/monthly?year=1405&month=7
```

```json
{
  "total_income": 1000000,
  "total_expense": 350000,
  "balance": 650000
}
```

## Design notes

- **Gregorian storage, Jalali presentation.** Dates are stored as Gregorian `Date` values so the database can sort, compare and filter natively. Conversion happens only at the API boundary (`app/jalali.py`).
- **Month ranges without leap-year logic.** The last day of a Jalali month is computed as "the day before the first day of the next month", so Esfand correctly has 29 or 30 days without hand-written leap rules.
- **Safe deletes.** A category with transactions cannot be deleted, so financial records are never silently orphaned.
- **Dependency injection for testability.** Endpoints receive their database session through FastAPI's `Depends`, which lets the tests swap in an isolated in-memory database.

## Project structure

```
kharjyar/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and router registration
│   ├── config.py            # Application settings
│   ├── database.py          # Database engine and session management
│   ├── dependencies.py      # Authentication and database dependencies
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── security.py          # Password hashing and JWT handling
│   ├── jalali.py            # Jalali date utilities
│   └── routers/
│       ├── auth.py          # Authentication endpoints
│       ├── categories.py    # Category endpoints
│       └── transactions.py  # Transaction endpoints
├── alembic/
│   ├── versions/            # Database migration scripts
│   ├── env.py
│   └── script.py.mako
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_auth.py         # Authentication tests
│   ├── test_categories.py
│   ├── test_health.py
│   └── test_transactions.py
├── .github/
│   └── workflows/           # GitHub Actions CI
├── .env.example
├── .gitignore
├── alembic.ini
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── LICENSE
└── README.md
```

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Running with Docker

```bash
cp .env.example .env   # then edit SECRET_KEY
docker compose up --build
```

The API is on http://localhost:8000/docs. Data lives in the
`kharjyar_data` volume, so it survives `docker compose down`.

## Roadmap

- [x] Authentication (JWT) with per-user data
- [x] Docker support
- [ ] Update endpoint for categories
- [x] Database migrations (Alembic)

## License

MIT — see [LICENSE](LICENSE).
