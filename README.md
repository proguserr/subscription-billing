# Subscription-Billing

## Background

Most SaaS backends eventually need real billing logic: plans, upgrades/downgrades, metered usage, invoices, retries, and auditability. This repo implements a pragmatic, production-minded **Subscription Billing & Payments** system with a small footprint that still demonstrates the hard parts: correctness over time, idempotency, async workers, and deployability.

**Live Demo**

- **Web (Admin UI):** https://static-production-518e.up.railway.app  
- **API (FastAPI):** https://subscription-billing-production.up.railway.app  
- **Health:** https://subscription-billing-production.up.railway.app/healthz

---

## Requirements

Using MoSCoW:

**Must have**
- Create users, plans, and subscriptions (monthly cycle).
- Track metered usage (e.g., `api_calls`) and generate invoices per cycle.
- Robust async processing for invoice generation & retries (Celery).
- REST API with predictable JSON, idempotent writes, and health endpoint.
- Deployable with Docker locally and to Railway (Postgres + Redis + API + Workers).
- Basic admin UI to view plans, users, invoices, payments.

**Should have**
- Scheduled tasks (Celery Beat) for cycle billing & cleanup.
- Usage-based overage calculation with a simple tier.
- Audit trail on important writes (created_at, updated_at, status transitions).
- CORS-safe public API for the UI.

**Could have**
- Stripe integration (tokens & webhooks) stubbed behind an interface.
- Prometheus metrics endpoints (latency, queue depth) for observability.

**Won’t have (for MVP)**
- Complex taxation, multi-currency, or proration of mid-cycle upgrades.
- Full RBAC or multi-tenant boundaries.
- PCI scope handling (no real card data handled here).

---

## Method

### Architecture (at a glance)

```mermaid
flowchart LR
  subgraph Client
    UI[Web Admin (Vite/React)]
  end

  UI -->|REST| API

  subgraph Platform
    API[FastAPI API]
    PG[(PostgreSQL)]
    R[(Redis)]
    W[Celery Worker]
    B[Celery Beat (Scheduler)]
  end

  API -- read/write --> PG
  API -- cache & enqueue --> R
  W -- consume jobs --> R
  B -- schedule jobs --> R

  classDef store fill:#1f2937,stroke:#9ca3af,color:#fff;
  class PG,R store;
```

**Why this works**

- **FastAPI** for a small, typed HTTP surface.
- **PostgreSQL** for durable, relational billing data (constraints matter).
- **Redis** for low-latency cache and broker/queue (Celery).
- **Celery worker/beat** separate concerns: job execution vs. scheduling.
- **Vite/React UI** for a thin admin dashboard that talks to the API.

### Domain model (tables & key columns)

- **users**
  - `id UUID PK`, `email UNIQUE`, `created_at timestamptz`
- **plans**
  - `code VARCHAR PK` (e.g., `basic|pro|ent`), `amount_cents INT`, `interval VARCHAR` (month), `trial_days INT`
- **subscriptions**
  - `id UUID PK`, `user_id FK`, `plan_code FK`, `status ENUM(active,canceled)`,
  - `current_period_start date`, `current_period_end date`
- **usage_events**
  - `id UUID PK`, `user_id FK`, `metric VARCHAR`, `quantity BIGINT`, `at timestamptz`
- **invoices**
  - `id UUID PK`, `user_id FK`, `period_start date`, `period_end date`,
  - `amount_cents INT`, `status ENUM(open,paid,void)`, `created_at timestamptz`, `paid_at timestamptz NULL`
- **payments**
  - `id UUID PK`, `invoice_id FK`, `provider VARCHAR`, `amount_cents INT`,
  - `status ENUM(succeeded,failed)`, `attempted_at timestamptz`

**Indexes**
- `idx_usage_user_time(user_id, at)`
- `idx_invoices_user_period(user_id, period_start, period_end)`
- natural keys on plan codes; email uniqueness on users.

### Key flows

1. **Subscribe user**
   - Validate plan → create `subscriptions` row with current monthly window.
2. **Record usage**
   - Append-only `usage_events` with `(user_id, metric, quantity, at)`.
3. **Generate invoice** (on-demand & scheduled)
   - Base fee from plan.
   - Overage: `max(0, usage - included)` × unit price (configurable per metric/plan).
   - Write `invoices` row (status `open`).
   - Emit job to worker for payment attempt (stubbed provider).
4. **Payment attempt**
   - Idempotent by `(invoice_id, attempt_key)`.
   - On success, set `paid_at` + `status=paid`, else retry with backoff.
5. **Cycle roll-over (Beat)**
   - Daily schedule scans subscriptions ending “today”; emits invoice generation jobs and advances window.

### API surface (representative)

- `GET /healthz` → `"ok"`
- `GET /plans`
- `POST /users` `{ email }` → `{ id, email }`
- `POST /subscriptions` `{ user_id, plan_code }` → `{ id, status, current_period_* }`
- `POST /usage` `{ user_id, metric, quantity }` → `{ ok: true }`
- `POST /invoices/generate/{user_id}` → `{ id, amount_cents, usage }`
- `GET /invoices/{user_id}` → list invoices

### Reliability & safety

- **Idempotency** on payment attempts; invoice creation ensures 1 open per user per period.
- **SQL constraints** and **FKs** protect integrity.
- **Async workers** isolate slow/fragile tasks (external payment, email).
- **Health** probes for API; Redis/Postgres connectivity checked at startup.
- **CORS** enabled for the UI origin.

---

## Implementation

### Local (Docker Compose)

Services: `api`, `worker`, `celery-beat`, `postgres`, `redis`, and optional `web` dev server.

```bash
docker compose up -d postgres redis
docker compose up -d api worker celery-beat
# dev UI locally (optional)
docker compose run --rm -p 5173:5173 web sh -c "npm install && npm run dev -- --host 0.0.0.0"
```

**DB init** is handled by `db/init.sql` (types, tables, seed plans).

**Env snippets (compose)**
- `DATABASE_URL=postgresql+asyncpg://billing:billing@postgres:5432/billing`
- `REDIS_URL=redis://redis:6379/0`

### Railway (production-ish)

- **Postgres** (managed), **Redis** (managed).
- **API service (FastAPI)**  
  - Source: GitHub repo root  
  - Dockerfile Path: `api/Dockerfile` (build root-aware)  
  - Vars: Postgres/Redis variable references; `CORS_ORIGINS` set for the static site.
- **Worker & Beat (Celery)**  
  - Dockerfile Path: `worker/Dockerfile`  
  - **Worker** command:  
    ```
    celery -A app.celery_app:celery_app worker -l info
    ```
  - **Beat** command:  
    ```
    celery -A app.celery_app:celery_app beat -l info
    ```
  - Vars: same Postgres/Redis references.
- **Static Web (Vite/React)**  
  - Root Directory: `web`  
  - Build: `npm install --no-audit --no-fund && npm run build`  
  - Output: `dist`  
  - Vars: `VITE_API_BASE=https://subscription-billing-production.up.railway.app`

---

## Load Test (M2 Air, Docker Compose)

**Goal:** sanity-check throughput/latency for reads & basic writes under modest concurrency.

**Setup**
- Machine: MacBook Air M2, 8-core, 8GB RAM.
- Tooling: `k6` container against `http://localhost:8080`.
- DB primed with 1k users; Redis warm.  
- Scenarios:  
  - `GET /plans` (cacheable read)  
  - `POST /users` (idempotent write surrogate: 1% of total)  
  - `POST /invoices/generate/{user}` (invocation only; payment stubbed)

**Profile**
- Duration 5m ramp → 10m steady.
- VUs ramp 10 → 150.

**Results (distinct run)**

| Endpoint                          | RPS (avg) | P50 | P95 | P99 | Error |
|-----------------------------------|-----------|-----|-----|-----|------:|
| `GET /plans`                      | 950       | 6ms | 18ms| 31ms| 0.00% |
| `POST /users`                     | 55        | 24ms| 61ms| 95ms| 0.15% |
| `POST /invoices/generate/{user}`  | 120       | 32ms| 88ms| 140ms| 0.42% |

**Interpretation**
- Reads are effectively cached and DB-light.  
- Invoice generation is bounded by DB round-trips but remains <100ms P95 on laptop hardware.  
- Low error rate came from intentional 429s when user creation was hammered; acceptable guardrail.

**Trade-offs**
- Using Redis for both cache and broker is pragmatic here; split roles for higher throughput or stricter SLOs.
- Celery default prefetch/acks settings were conservative; tuning could push worker throughput further.

---

## Debugging story (real incident)

**Symptom**  
`celery-beat` failed to build/deploy on Railway with:
```
failed to calculate checksum ... "/worker/app": not found
```

**Root cause**  
Railway built the service from the **repo root** while the Dockerfile used `COPY worker/...`. When the service’s Root Directory was set to `worker/`, the build context moved; `COPY worker/app` then pointed to a non-existent path (`worker/worker/app`).

**Fix**  
Keep the service **Root Directory empty (repo root)** and set **Dockerfile Path = worker/Dockerfile**. The worker Dockerfile then copies with `COPY worker/app ./app`.  
A similar issue earlier surfaced as a `psycopg2` import error; the fix was to ensure the DSN uses the async driver:
```
DATABASE_URL=postgresql+asyncpg://...
```
and that `asyncpg` is in requirements.

**Lesson**  
Be explicit about build context vs. Dockerfile paths. Treat DSNs as contracts—driver mismatches lead to misleading import errors.

---

## Milestones

1. **MVP API & Data model** – plans, users, subs, usage, invoices.  
2. **Async pipeline** – Celery worker + beat with backoff & idempotency.  
3. **Admin UI** – plans/users/invoices/payments basic screens.  
4. **Deployment** – Docker Compose local; Railway prod-ish with public URLs.  
5. **Load testing & tuning** – baseline numbers captured; cache verified.

---

## Gathering Results

**Functional checks**
- Subscription lifecycle → invoices → payment status transitions.
- Invariants: one open invoice per user per billing period.

**Operational**
- Health checks for API, worker readiness logs, beat scheduler tick.
- Error budget: <0.5% under 150 VUs on laptop hardware; acceptable for MVP.

**What to add next**
- Per-plan metric config (included units and overage price).
- Stripe integration (webhook retries + idempotency keys).
- Metrics endpoint and dashboard (latency, queue depth, invoice throughput).
- Proration policy for mid-cycle plan changes.

---

## Appendix: Commands

**Generate invoice via API**
```bash
# Create user
curl -s -X POST https://subscription-billing-production.up.railway.app/users \
  -H 'Content-Type: application/json' -d '{"email":"demo@example.com"}'

# Subscribe to plan
curl -s -X POST https://subscription-billing-production.up.railway.app/subscriptions \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"<USER_ID>","plan_code":"pro"}'

# Record usage
curl -s -X POST https://subscription-billing-production.up.railway.app/usage \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"<USER_ID>","metric":"api_calls","quantity":120000}'

# Generate invoice
curl -s -X POST https://subscription-billing-production.up.railway.app/invoices/generate/<USER_ID>
```

---

## Need Professional Help in Developing Your Architecture?

Please contact me at [sammuti.com](https://sammuti.com) :)
