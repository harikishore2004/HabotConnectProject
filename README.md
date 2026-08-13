# LSA Service Booking API

**Author:** M Hari Kishore  
**Contact:** mharikishore.work@gmail.com

A Flask-based REST API for booking Learning Support Assistant (LSA) services, connecting Parents with available LSAs based on skill matching.

---

## Table of Contents
- [LSA Service Booking API](#lsa-service-booking-api)
  - [Table of Contents](#table-of-contents)
  - [Tech Stack](#tech-stack)
  - [Project Structure](#project-structure)
  - [Setup Instructions](#setup-instructions)
    - [Option A: Run with Docker (recommended)](#option-a-run-with-docker-recommended)
    - [Option B: Run locally (without Docker for the app)](#option-b-run-locally-without-docker-for-the-app)
    - [Running Tests](#running-tests)
  - [Database Schema \& Relationships](#database-schema--relationships)
    - [Entities](#entities)
    - [Relationships](#relationships)
  - [API Endpoint Documentation](#api-endpoint-documentation)
    - [`POST /api/v1/bookings/`](#post-apiv1bookings)
    - [`GET /api/v1/lsas/search/`](#get-apiv1lsassearch)
  - [Query Optimization Choices](#query-optimization-choices)
  - [Third-Party Integration (Mock)](#third-party-integration-mock)
  - [Testing](#testing)
  - [CI/CD Pipeline](#cicd-pipeline)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | Flask |
| REST Layer | Flask-RESTful (`Resource` classes) |
| ORM | SQLAlchemy (via Flask-SQLAlchemy) |
| Validation & Config | Pydantic v2 + pydantic-settings |
| Database | PostgreSQL 16 |
| API Docs | OpenAPI 3.0 (Swagger UI) |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Containerization | Docker + docker-compose |

---

## Project Structure

```
lsa_booking_project/
├── app/
│   ├── __init__.py          # App factory (Flask-RESTful Api, Swagger UI)
│   ├── config.py              # Pydantic settings
│   ├── extensions.py          # SQLAlchemy instance
│   ├── models/                 # Parent, LSAProfile, BookingRequest
│   ├── routes/                 # Flask-RESTful Resource classes
│   ├── schemas/                # Pydantic request/response validation
│   ├── services/                # Mock payment/verification integration
│   ├── utils/                   # Logging, seed data
│   └── static/openapi.yaml     # Swagger spec
├── tests/                        # pytest suite
├── .github/workflows/tests.yml  # CI pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── main.py
```

## Setup Instructions

### Option A: Run with Docker (recommended)

**Prerequisites:** Docker, Docker Compose

```bash
git clone https://github.com/harikishore2004/HabotConnectProject.git
cd HabotConnectProject
cp .env.example .env
docker compose up --build
```

This starts both the PostgreSQL container and the Flask app. The app will be available at `http://localhost:5000`, and Swagger docs at `http://localhost:5000/docs`.

### Option B: Run locally (without Docker for the app)

**Prerequisites:** Python 3.11+, a running PostgreSQL instance

```bash
git clone <repository-url>
cd lsa-booking-project
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # edit DB credentials to match your local Postgres
```

Start Postgres via Docker (app runs locally, DB in container):
```bash
docker-compose up db -d
```


Run the app:
```bash
python main.py
```

### Running Tests

Create a separate test database (Postgres does not auto-create it):
```bash
docker exec -it lsa_postgres createdb -U lsa_user lsa_db_test
```

```bash
pytest -v
```

---

## Database Schema & Relationships

### Entities

**`Parent`**
| Column | Type | Notes |
|---|---|---|
| id | Integer, PK | |
| full_name | String(120) | |
| email | String(150) | Unique, indexed |
| phone_number | String(20) | Nullable |
| created_at | DateTime (tz-aware) | |

**`LSA_Profile`**
| Column | Type | Notes |
|---|---|---|
| id | Integer, PK | |
| full_name | String(120) | |
| email | String(150) | Unique, indexed |
| bio | Text | Nullable |
| is_available | Boolean | Indexed |
| hourly_rate | Numeric(8,2) | Never Float, to avoid currency rounding errors |
| skills | JSON (list of strings) | See design trade-off note below |
| created_at | DateTime (tz-aware) | |

**`Booking_Request`**
| Column | Type | Notes |
|---|---|---|
| id | Integer, PK | |
| parent_id | Integer, FK → parents.id | Indexed |
| lsa_id | Integer, FK → lsa_profiles.id | Indexed |
| session_date | DateTime (tz-aware) | Must be a future date (validated) |
| notes | Text | Nullable |
| status | Enum (pending/confirmed/cancelled/completed) | Native Postgres ENUM, indexed |
| payment_reference | String(120) | Set after mock payment service call |
| created_at | DateTime (tz-aware) | |

### Relationships

- **Parent & Booking_Request**: One-to-Many. One parent can make many booking requests. Cascade delete: removing a parent removes their bookings.
- **LSA_Profile & Booking_Request**: One-to-Many. One LSA can be booked many times. Cascade delete: removing an LSA removes their bookings.
- **LSA_Profile.skills**: Stored as a JSON column (list of strings) directly on the LSA row, rather than a separate `Skill` table + many-to-many join table.


---

## API Endpoint Documentation

Full interactive documentation available at `/docs` (Swagger UI) once the app is running, generated from `app/static/openapi.yaml`.

### `POST /api/v1/bookings/`

Creates a new booking request.

**Request body:**
```json
{
  "parent_id": 1,
  "lsa_id": 1,
  "session_date": "2026-09-01T10:00:00+00:00",
  "notes": "First session, please confirm timing."
}
```

**Validation rules:**
- `parent_id`, `lsa_id`: required, positive integers, must reference existing records.
- `session_date`: required, ISO 8601 datetime, must include timezone info, must be in the future.
- `notes`: optional, max 1000 characters.

**Responses:**
| Status | Meaning |
|---|---|
| 201 | Booking created successfully |
| 400 | Validation failed (bad payload, invalid/past session_date) |
| 404 | Parent or LSA not found |
| 409 | LSA exists but is currently unavailable |
| 502 | Mock payment/verification service call failed |

### `GET /api/v1/lsas/search/`

Searches for LSAs, optionally filtered by skill and/or availability.

**Query parameters:**
| Param | Type | Notes |
|---|---|---|
| skills | string | Comma-separated, e.g. `?skills=Math,Reading`. Case-insensitive. |
| is_available | boolean | `?is_available=true` |

**Responses:**
| Status | Meaning |
|---|---|
| 200 | Returns `{ "count": int, "results": [...] }` |
| 400 | Invalid query parameters |

---

## Query Optimization Choices

1. **Single query per request, no N+1 problem.** `GET /api/v1/lsas/search/` executes exactly one `SELECT` against `lsa_profiles` regardless of how many LSAs are returned. Skills live as a JSON column on the same row, so there's no related table requiring per-row lazy-loaded queries - the classic N+1 pattern (1 query for the list + N queries for each row's related data) is structurally avoided by the schema choice itself, not just by using eager-loading flags.
2. **Indexed filter columns.** `is_available` on `lsa_profiles`, and `parent_id`/`lsa_id` on `booking_requests`, are indexed - filtering and join lookups avoid full table scans as data grows.
3. **Database-level enum enforcement.** `Booking_Request.status` uses a native Postgres `ENUM` type rather than a free-text string, preventing invalid states from ever being written and avoiding the need for application-side `CHECK` logic on every write.
4. **`db.session.get()` for primary-key lookups.** Parent/LSA existence checks in the booking endpoint use SQLAlchemy's primary-key-optimized `get()` rather than a full `filter_by().first()` query.

---

## Third-Party Integration (Mock)

`app/services/payment_service.py` simulates a call to an external payment/verification gateway using the `requests` library.

- **Timeout handling:** configurable via `MOCK_API_TIMEOUT_SECONDS`, raises a custom `PaymentServiceError` on timeout.
- **Connection/HTTP error handling:** any `requests.exceptions.RequestException` (connection errors, non-2xx responses via `raise_for_status()`) is caught and converted to `PaymentServiceError`.
- **Malformed response handling:** invalid JSON from the external service is caught separately and also converted to `PaymentServiceError`.
- **Logging:** all failure paths are logged with context (`logger.error`/`logger.warning`) before propagating as a clean 502 response to the client - no raw stack traces or unhandled exceptions reach the API consumer.
- A local mock endpoint (`POST /api/v1/mock/payment/`) is included for manual/dev testing, simulating occasional latency and a ~10% random failure rate to exercise the error-handling paths realistically. Automated tests mock `requests.post` directly instead of calling this endpoint, so the test suite has no network dependency.

---

## Testing

Run with:
```bash
pytest -v
```

Coverage includes:
- **Success cases:** valid booking creation, LSA search with/without filters.
- **Failure cases:** missing required fields, non-existent parent/LSA, unavailable LSA, payment service timeout.
- **Edge cases:** past-dated session_date rejection, case-insensitive skill matching, no-match search results.

All tests run against an isolated PostgreSQL test database (`lsa_db_test`), created fresh per test session via `db.create_all()`/`db.drop_all()`. No external network calls are made during tests - the payment service call is mocked via `unittest.mock.patch`.

---

## CI/CD Pipeline

`.github/workflows/tests.yml` runs on every push/PR to `main`/`develop`:
1. Spins up a temporary PostgreSQL 16 service container.
2. Installs dependencies.
3. Waits for the database to be ready (`pg_isready`).
4. Runs the full pytest suite against it.
5. Verifies the Docker image builds successfully (separate job, runs only if tests pass).


