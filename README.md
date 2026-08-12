**Name:** Israel Adetubo  
**Contact:** israetubo@gmail.com

# HabotConnect Backend

A Flask REST API for a booking platform connecting Parents with LSAs (Learning Support Assistant) — supports searching for available skilled assistants, booking sessions and then processing payments via a Razorpay-style webhook integration.

## Tech Stack

- **Flask** + **Flask-RESTful** — REST API framework (MVC)
- **Flask-SQLAlchemy** + **Flask-Migrate (Alembic)** — ORM and database migrations
- **Flask-Marshmallow** — request validation and response serialization
- **Flask-JWT-Extended** — authentication
- **PostgreSQL** — database
- **Razorpay** (mocked) — payment gateway integration

## Setup Instructions

### Prerequisites
- Python 3.10+
- Docker (for PostgreSQL) or a local PostgreSQL install

### 1. Clone and set up a virtual environment
```bash
git clone <repo-url>
cd habotconnect-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start PostgreSQL
```bash
docker run --name habotconnect-db \
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=habotconnect_dev \
  -p 5432:5432 -d postgres:16
```

### 3. Configure environment variables
Create a `.env` file in the project root:
DATABASE_URL=postgresql://postgres:devpassword@localhost:5432/habotconnect_dev
SECRET_KEY=your-dev-secret-key
JWT_SECRET_KEY=your-dev-jwt-secret
RAZORPAY_WEBHOOK_SECRET=your-dev-webhook-secret

### 4. Run database migrations
```bash
flask db upgrade
```

### 5. Run the app
```bash
python run.py
```
API is available at `http://localhost:5000/api/v1`.

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/parent/signup` | Register a new parent |
| POST | `/auth/parent/login` | Log in as a parent, returns JWT |
| POST | `/auth/lsa/signup` | Register a new LSA |
| POST | `/auth/lsa/login` | Log in as an LSA, returns JWT |

### LSA Search
| Method | Endpoint | Description |
|---|---|---|
| GET | `/lsas/search` | Search available LSAs. Query params: `skills` (comma-separated), `min_experience`, `page`, `page_size` (max 100) |

### Bookings (require `Authorization: Bearer <token>` header)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/bookings` | Create a booking (parent only) |
| GET | `/bookings` | List the logged-in user's bookings (parent sees their own, LSA sees theirs) |
| GET | `/bookings/<id>` | Get a single booking (only accessible to the parent or LSA on that booking) |

### Payments
| Method | Endpoint | Description |
|---|---|---|
| POST | `/payments/webhook` | Razorpay webhook receiver — verifies `X-Razorpay-Signature`, processes `payment.captured` / `payment.failed` events, updates booking status |

## Query Optimizations

- **Eager loading (`joinedload`)** on booking retrieval — fetching a booking or list of bookings loads the related `Parent` and `LSAProfile` names in the same query, avoiding N+1 queries when serializing `parent_name`/`lsa_name`.
- **`selectinload`** on LSA search — skills are loaded in a single batched query rather than once per LSA result.
- **Indexed columns** — `email` (parents, LSA profiles), `session_date`, `status`, and a compound index on `(lsa_id, session_date)` on bookings, since availability checks filter on exactly this combination.
- **Paginated search** — `/lsas/search` caps `page_size` at 100 to prevent unbounded result sets from a single request.
- **Idempotent webhook processing** — `Payment.processed_event_id` is unique-indexed, so a retried webhook event is detected and short-circuited via an indexed lookup rather than reprocessing payment logic.

## Known Limitations

- **Booking overlap prevention is currently application-level only** (a `SELECT ... FOR UPDATE` row lock checks for conflicting bookings before insert). Under concurrent requests for a slot with *no prior bookings*, this does not fully eliminate a race condition. A production-ready fix would add a PostgreSQL exclusion constraint (`EXCLUDE USING gist`, requiring the `btree_gist` extension) to enforce non-overlapping bookings at the database level — deferred here due to time constraints on this submission.
- **Payment gateway integration is mocked** — `payment_gateway.py` simulates Razorpay's Order creation response rather than making a real API call, so the full flow can be built and tested without live API keys.

## Design Choice: Flask (MVC) vs. Django (MVT)
 
I chose Flask over Django because the brief explicitly asks for a "modular, lightweight RESTful API" 
There's no server-rendered page, no admin console and no multi app monolith in scope, so Django's templating engine and `django.contrib.admin` would have been dead weight carried for features this service never touches. Flask let me build exactly the layers this problem needed and nothing more: 
Flask-RESTful `Resource` classes handle routing and HTTP concerns only, Marshmallow schemas own request validation and response serialization as their own layer and a dedicated `services/` module (`booking_service.py`, `webhook_service.py`) holds the actual business logic overlap detection, idempotent webhook processing which is fully decoupled from both the HTTP layer and the ORM. 
Django's MVT tends to collapse controller logic into the View by convention and with the admin site sitting right there, it's an easy crutch to lean on for CRUD instead of deliberately layering resource → schema → service → model for an API only booking/payment service like this one, Flask's unopinionated structure kept those boundaries explicit rather than implicit and that's why.

## Running Tests
```bash
pytest
```