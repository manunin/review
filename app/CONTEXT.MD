# Context for Coding Agent: Principles of Backend Development with FastAPI

> This document is a concise but comprehensive guideline that the agent (and humans) must follow when creating and maintaining services on FastAPI. All requirements are mandatory by default unless explicitly stated otherwise.

---

## 0. Quick Checklist

* [ ] Python ≥ 3.11, FastAPI ≥ 0.110, Pydantic v2, SQLAlchemy 2.x
* [ ] Strict typing + `mypy`/`pyright`, linting with `ruff`, formatting with `black`
* [ ] Project structure (below) + modular routers + DI via `Depends`
* [ ] `pydantic-settings` for configs; secrets only from env/secret manager
* [ ] Async stack: `httpx` (timeouts+retries), SQLAlchemy Async + DB driver (e.g. `asyncpg`)
* [ ] Migrations via Alembic; transactions and idempotency for writes
* [ ] Stable API contract: versioning, schemas, examples, OpenAPI
* [ ] Unified error format (RFC 7807), error codes and domain-to-HTTP mapping
* [ ] JSON logging, correlation IDs, metrics/traces (OTel), health/readiness endpoints
* [ ] Tests: unit + integration (with test DB/container) + contract tests
* [ ] CI: linters, type checks, tests, coverage, image build, security scans
* [ ] Containerization: multi-stage Dockerfile, non-root user, minimal base
* [ ] Security: CORS, headers, input/output validation, PII protection

---

## 1. Goals and Requirements

* Predictability, explicit errors, backward compatibility.
* Zero side effects outside explicit boundaries (idempotency, transactions).
* Observability by default: logs, metrics, traces, request-id.
* Operational simplicity: standard health checks, config via env.
* Performance: async where justified, timeouts and latency budgets.

## 2. Project Structure

```
app/
  core/
    config.py        # pydantic-settings
    logging.py       # JSON logger, correlation
    security.py      # auth, crypto, CORS
    openapi.py       # tags, descriptions, examples
    models.py        # global models
    exceptions.py    # global exceptions
    pagination.py    # global module e.g. pagination
  tasks/
     ├── router.py
     ├── schemas.py
     ├── models.py
     ├── dependencies.py
     ├── constants.py
     ├── exceptions.py
     ├── service.py
     └── utils.py
  infra/
    db/
      base.py       # engine/sessionmaker, lifespan
      models.py     # ORM tables (SQLAlchemy 2)
      repo.py       # repositories
      migrations/   # alembic
    cache.py        # redis/asgi-cache
    clients/
      http.py       # httpx client with retry/timeout
      mail.py       # mail sender
  requirements
    ├── base.txt
    ├── dev.txt
    └── prod.txt
  templates/
│   └── index.html
  main.py           # FastAPI app creation, middlewares, lifespan
  settings.py

tests/
  unit/
  integration/
  contract/

.env
.gitignore
pyproject.toml
logging.ini
alembic.ini
Dockerfile
compose.yml (optional)
```

* Store all domain directories inside src folder
    app/ - highest level of an app, contains common models, configs, and constants, etc.
    app/main.py - root of the project, which inits the FastAPI app
* Each package has its own router, schemas, models, etc.
    router.py - is a core of each module with all the endpoints
    schemas.py - for pydantic models
    models.py - for db models
    service.py - module specific business logic
    dependencies.py - router dependencies
    constants.py - module specific constants and error codes
    config.py - e.g. env vars
    utils.py - non-business logic functions, e.g. response normalization, data enrichment, etc.
    exceptions.py - module specific exceptions, e.g. PostNotFound, InvalidUserData
* When package requires services or dependencies or constants from other packages - import them with an explicit module name:
```python
from app.auth import constants as auth_constants
from app.notifications import service as notification_service
from app.posts.constants import ErrorCode as PostsErrorCode  # in case we have Standard ErrorCode in constants module of each package
```

## 3. Dependencies and Versions

* Python ≥ 3.11 (pattern matching, `tomllib`, performance).
* FastAPI, Starlette, Uvicorn.
* Pydantic v2 + pydantic-settings.
* SQLAlchemy 2.x (annotated declarative) + async driver.
* httpx for external HTTP requests.
* Quality tools: `ruff`, `black`, `mypy`/`pyright`, `pytest`, `coverage`.
* Security: `bandit`, `pip-audit`/`safety`.
* Use Depends()

## 4. Configuration and Secrets

* Only via environment variables/secret manager. No hardcoding.
* Excessively use Pydantic
* Use `BaseSettings` from `pydantic-settings`.
* Secrets (tokens, passwords) — separate fields, never logged, masking applied.

Example:

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "service-name"
    env: str = "dev"
    debug: bool = False

    database_url: str
    redis_url: str | None = None

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_ttl_s: int = 900

    class Config:
        env_file = ".env"  # local only, prod uses env/secret manager

settings = Settings()
```

## 5. Application Creation and Lifespan

* Use `lifespan` instead of old `startup/shutdown`.
* All clients (DB, Redis, httpx) — initialized once and properly closed.

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core import config
from app.infra.db.base import create_engine_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine, session_factory = await create_engine_session(config.settings.database_url)
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory
    yield
    await engine.dispose()

app = FastAPI(title=config.settings.app_name, lifespan=lifespan)
```

## 6. Routes, Schemas, Validation

* Use `pydantic` models for input/output. Responses strictly typed.
* Always specify `response_model`, `status_code`, `summary`, `description`, `responses`.
* Add `examples` for key contracts.
```python
# app/api/v1/routers/users.py
from fastapi import APIRouter, Depends, status
from app.api.v1.schemas import UserIn, UserOut
from app.api.v1.deps import get_user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserIn, svc = Dep    ends(get_user_service)):
    return await svc.create(payload)
```
* Follow REST

## 7. Errors and Exceptions

* Unified error format — RFC 7807 (Problem Details).
* Global handlers map domain/infrastructure exceptions to HTTP.
* Never return stack traces or secrets to the client.

```python
# app/api/v1/errors.py
from fastapi import Request
from fastapi.responses import JSONResponse

class DomainError(Exception):
    def __init__(self, title: str, detail: str = "", status: int = 400, type_: str = "about:blank"):
        self.title, self.detail, self.status, self.type_ = title, detail, status, type_

async def problem_details_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status,
        content={
            "type": exc.type_,
            "title": exc.title,
            "detail": exc.detail,
            "instance": str(request.url),
        },
    )
```
* ValueErrors might become Pydantic ValidationError

```python
# app.profiles.schemas
from pydantic import BaseModel, field_validator
class ProfileCreate(BaseModel):
    username: str
    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit or "
                "special symbol"
            )

        return password


# app.profiles.routes
from fastapi import APIRouter
router = APIRouter()
@router.post("/profiles")
async def get_creator_posts(profile_data: ProfileCreate):
   pass
```

## 8. Security

* CORS: explicit allowlist of origins/methods/headers.
* Authentication: OAuth2 (JWT: short `access`, long `refresh`) or API Key; default is JWT.
* Authorization: roles/permissions at router/service level.
* Required security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy` (if static), `Strict-Transport-Security`.
* Password hashing: `argon2`/`bcrypt`. Never store in plain text.
* Injection protection: parameterized queries, no eval, strict validation.
* PII: mask in logs, provide deletion (privacy by design).

## 9. Data and Database

* SQLAlchemy 2.x. Layers: ORM models → repositories → services.
* Async sessions, explicit transactions, `repeatable read` or higher if needed.
* Migrations via Alembic: each schema in repo, avoid junk auto-gen.
* Indices, unique constraints, foreign keys required.
* N+1 avoidance with `selectinload/joinedload`.
* Explicitly setting the indexes' namings according to your database's convention is preferable over sqlalchemy's.
```python
from sqlalchemy import MetaData

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
```
* Set DB naming conventions
Being consistent with names is important. Some rules we followed:
- lower_case_snake
- singular form (e.g. post, post_like, user_playlist)
- group similar tables with module prefix, e.g. payment_account, payment_bill, post, post_like
- stay consistent across tables, but concrete namings are ok, e.g. 
   - use profile_id in all tables, but if some of them need only profiles that are creators, use creator_id
   - use post_id for all abstract tables like post_like, post_view, but use concrete naming in relevant modules like course_id in chapters.course_id
- _at suffix for datetime
- _date suffix for date
* SQL-first. Pydantic-second
- It's preferable to do all the complex joins and simple data manipulations with SQL.
- It's preferable to aggregate JSONs in DB for responses with nested objects.


Example:

```python
from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
```

## 10. Async and External Calls

* `httpx.AsyncClient` — single instance per app (via lifespan). Timeouts mandatory, retries with exponential backoff, connection limit.
* All calls must have time budgets, cancellation with `asyncio.Timeout`.
* If you must use a library to interact with external services, and it's not async, then make the HTTP calls in an external worker thread.
```python
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from my_sync_library import SyncAPIClient 

app = FastAPI()


@app.get("/")
async def call_my_sync_library():
    my_data = await service.get_my_data()

    client = SyncAPIClient()
    await run_in_threadpool(client.make_request, data=my_data)
```

## 11. Idempotency and Consistency

* Repeatable operations (`POST` create) — support `Idempotency-Key`.
* Under the hood — unique keys/dedup table + transaction.
* Streaming writes/retries — only safe ones.

## 12. Pagination, Filtering, Sorting

* Default `limit`/`offset` with max cap (e.g. 100).
* For large sets — cursor-based pagination (base64 cursor).
* Explicit sorting rules, whitelist fields.

## 13. Caching

* Headers: `ETag`/`Last-Modified` for GET, `Cache-Control` where safe.
* Internal cache (Redis) for heavy computations, TTL + invalidation.

## 14. Logging and Observability

* Structured JSON logs, default level `INFO`.
* Correlation ID: read from `X-Request-ID` or generate; propagate to outgoing requests.
* Metrics (Prometheus): latency, RPS, errors by code, DB pools, retries.
* Tracing (OpenTelemetry): spans for routes, DB, external HTTP.

## 15. Response Formats: Dates and Money

* Dates/times — RFC 3339, UTC only, timezone-aware.
* Monetary values — `Decimal`, ISO 4217 currency.
* Never serialize `float` for money.

## 16. Documentation and OpenAPI

* API versioning: `/api/v1` etc. Deprecation — via `deprecated: true` + timelines.
* Docs: `summary`, `description`, `tags`, `examples`.
* Generate and publish OpenAPI JSON artifact in CI.
* Unless your API is public, hide docs by default.
* Help FastAPI to generate an easy-to-understand docs
 - Set response_model, status_code, description, etc.
 - If models and statuses vary, use responses route attribute to add docs for different responses
 ```python
from fastapi import APIRouter, status

router = APIRouter()

@router.post(
    "/endpoints",
    response_model=DefaultResponseModel,  # default response pydantic model 
    status_code=status.HTTP_201_CREATED,  # default status code
    description="Description of the well documented endpoint",
    tags=["Endpoint Category"],
    summary="Summary of the Endpoint",
    responses={
        status.HTTP_200_OK: {
            "model": OkResponse, # custom pydantic model for 200 response
            "description": "Ok Response",
        },
        status.HTTP_201_CREATED: {
            "model": CreatedResponse,  # custom pydantic model for 201 response
            "description": "Creates something from user request",
        },
        status.HTTP_202_ACCEPTED: {
            "model": AcceptedResponse,  # custom pydantic model for 202 response
            "description": "Accepts request and handles it later",
        },
    },
)
async def documented_route():
    pass
 ```

## 17. Testing

* Unit tests for business logic (no DB). Integration — with test DB (e.g. postgres in container) and real `FastAPI` app via `httpx.AsyncClient`.
* Contract tests via OpenAPI (schemathesis) for critical endpoints.
* Data factories (factory-boy/custom), Faker.
* Coverage target ≥ 80% on critical modules.
* Set tests client async from day 0. Writing integration tests with DB will most likely lead to messed up event loop errors in the future. Set the async test client immediately

## 18. Performance

* Uvicorn workers: based on CPU/IO profile, by default multiple via gunicorn+uvicorn workers.
* Response compression (GZip/Brotli) — for large payloads.
* Avoid unnecessary serialization/copies.
* DB connection pool tuning for load, min/max bounds.

## 19. Background Tasks and Scheduling

* Light — `BackgroundTasks`. Heavy/long — separate worker (Celery/RQ/Arq) with broker (Redis/RabbitMQ), idempotent handlers.
* Scheduling — external scheduler, not inside web app.

## 20. Files, Streams, WebSocket

* Large files — streamed: `StreamingResponse`.
* Temp files — safe dir, auto cleanup.
* WebSocket — only if necessary, with auth and limits.

## 21. Versioning, Quality, CI/CD

* Simplified Git flow: `main` (release), `develop`/feature branches.
* Conventional Commits; auto-generate CHANGELOG.
* pre-commit: `ruff`
* CI: build image, publish, migrations; OpenAPI artifacts, test reports.

## 22. Containerization and Runtime

* Dockerfile: multi-stage (builder → runtime), minimal base image (distroless/ubi-micro), non-root user.
* Config via env. Healthcheck. Readiness/Liveness endpoints (`/healthz`, `/readyz`).
* Logs only to stdout/stderr (JSON).

## 23. Migrations and Releases

* Code and schema migrations — atomic. Strategy: expand/contract for compatibility.
* Rollback: compatible versions, feature flags to disable new paths.

## 24. Internationalization and Localization (optional)

* Store only keys, culture handled client-side. Date/money formats — client-side.

## 25. Data Retention Policies

* Minimize PII, encryption at rest (DB/volumes) and in transit (TLS).
* Retention periods, deletion/anonymization procedures.

## 26. Code Style and Typing Standards

* Always use type annotations. `from __future__ import annotations`.
* Ban `Any`, `# type: ignore` only with justification.
* Exceptions — specific, no "magic".

## 27. Agent Rules under Uncertainty

* Make safe assumptions: UTC, idempotency on writes, capped limits (`limit ≤ 100`).
* Don’t invent protocols: follow REST, HTTP codes, OpenAPI.
* If tech choice is equal — prefer simpler/standard.
* For external integrations — always add timeouts/retries/logging.

---

# Appendix: Templates

## A. Example Depends/DI

```python
# app/api/v1/deps.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.base import get_session
from app.domain.services import UserService
from app.infra.db.repo import UserRepo

async def get_db() -> AsyncSession:
    async with get_session() as s:
        yield s

def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(UserRepo(db))
```

## B. Unified Error Response (RFC 7807)

```python
from fastapi import FastAPI
from app.api.v1.errors import DomainError, problem_details_handler

app = FastAPI()
app.add_exception_handler(DomainError, problem_details_handler)
```

## C. Request-ID Logger (sketch)

```python
import logging, uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        logging.LoggerAdapter(logging.getLogger("app"), {"request_id": rid})
        return response
```

## D. OpenAPI Enhancements

```python
# app/core/openapi.py
from fastapi import FastAPI

def enhance_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = app.openapi()
    openapi_schema["info"]["x-logo"] = {"url": "/static/logo.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema
```

---

# MR/PR Review Criteria

* API contracts don’t break backward compatibility.
* Tests and migrations included; coverage > target minimum.
* Logs structured, `X-Request-ID` present.
* Timeouts/retries set for external calls.
* No secret leaks in logs/exceptions.
* Endpoint docs filled (summary/description/examples).

---

# Default Decisions Dictionary

* DB: PostgreSQL, UTC, `asyncpg`.
* Cache: Redis (if needed), TTL ≥ 60s for non-critical data.
* Auth: JWT (access 15 min, refresh 7–30 days), access stored in `Authorization: Bearer` header.
* Pagination: limit/offset, default `limit` = 50, max = 100.
* Logs: JSON to stdout, level `INFO`, secrets masked.
* Date format: RFC3339, `Z` suffix; money — `Decimal` + `currency`.

---

> End of document. Keep it up to date, changes via PR and review.