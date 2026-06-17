---
name: backend-craft
description: Build, scaffold, and review reliable backend services — error handling, resilience, databases, caching, API design, security, and observability. Use this skill whenever the user wants to create a backend service or API, add resilience (timeouts, retries, circuit breakers), design or review REST endpoints, set up health checks or graceful shutdown, harden security, add logging/metrics/tracing, or audit an existing service for production-readiness. Works across Node/Express and Python/FastAPI.
compatibility: Requires Python 3.8+ for the scripts in scripts/.
metadata: {"emoji":"⚙️","os":["linux","darwin","win32"]}
---

# Backend Craft

Reliable backend services — from scaffold to production. Error handling, resilience, databases, caching, API design, security, observability.

The premise: a backend that returns the right JSON in the happy path is not done. Production backends are judged by how they behave when a dependency is slow, when input is hostile, when traffic spikes, and when something crashes mid-request. This skill makes those concerns first-class instead of afterthoughts.

## Activation

Use this skill when the user asks to:
- scaffold a new backend service or API (Express or FastAPI)
- add resilience: timeouts, retries with backoff, circuit breakers, graceful shutdown
- design or review REST API endpoints (versioning, pagination, status codes, error envelope)
- implement input validation or rate limiting
- set up health checks (liveness, readiness, startup)
- harden security (secrets handling, authn/authz separation, least privilege)
- add observability (structured logging, metrics, distributed tracing)
- audit an existing service for production-readiness

## Workflow

1. **Classify** the request: `scaffold` | `resilience` | `api-design` | `data` | `security` | `observability` | `review`.

2. **Load the relevant reference**:
   - error handling, timeouts, retry/backoff, circuit breaker, graceful shutdown → `references/error_and_resilience.md`
   - connection pooling, transactions, read replicas, caching, stampede prevention → `references/database_and_caching.md`
   - versioning, pagination, status codes, error envelope, rate limiting → `references/api_design.md`
   - secrets, authn/authz, logging, metrics, tracing, health checks → `references/security_and_observability.md`

3. **Run a script** when the task is concrete:
   ```bash
   # Scaffold a new service (default: express). FastAPI also supported.
   python {baseDir}/scripts/service_scaffolder.py my-service --framework express
   python {baseDir}/scripts/service_scaffolder.py my-service --framework fastapi --features auth,ratelimit

   # Generate health-check endpoints (liveness, readiness, startup)
   python {baseDir}/scripts/healthcheck_scaffolder.py --framework express --out src/routes/health.js
   python {baseDir}/scripts/healthcheck_scaffolder.py --framework fastapi --out app/health.py

   # Audit an existing service for production-readiness gaps
   python {baseDir}/scripts/api_auditor.py ./service --verbose
   ```
   For an open-ended "build me an API" with no stack named, default to an Express scaffold via the script, then build the requested endpoints inside it — don't hand-write a single unstructured file.

4. **Self-audit** against the checklist below before emitting.

5. **Emit the artifact** (service structure, endpoint, config, or audit report) and close with the single most valuable next step.

## Production-Readiness Self-Audit

Before emitting any backend code, verify:

**Resilience**
- Every external call (DB, HTTP, cache) has an explicit timeout — never wait forever.
- Retries use exponential backoff **with jitter**; non-idempotent operations carry idempotency keys.
- Failing dependencies are wrapped in a circuit breaker, not hammered.
- Graceful shutdown: stop accepting new requests, drain in-flight, close connections, handle SIGTERM.

**Input & errors**
- All external input validated at the entry point (body, query, headers, path) — whitelist, reject unknown fields, enforce size limits.
- Stack traces never reach the client; errors return a structured envelope (code, message, request ID).
- Expected errors → appropriate 4xx; unexpected → 500 + alert.

**Data**
- Connections pooled; transactions scoped as tightly as possible; prepared statements always.
- Cache has an explicit invalidation strategy and stampede protection.

**Security**
- Secrets come from environment/vault, never code or committed config.
- Authentication (who you are) and authorization (what you can do) are separate concerns.
- Sensitive data (passwords, tokens, PII) is never logged.

**Observability**
- Structured (JSON) logs with a request ID propagated across services.
- RED metrics exposed: Rate, Errors, Duration (latency percentiles).
- Health checks are fast and cheap — don't hit the database on every liveness probe.

## Output Contract

- Open with the classification and the primary decision or gap in one line.
- Emit one primary artifact per response (service, endpoint, config, or report).
- Annotate non-obvious choices — why a timeout value, why a circuit breaker here, an authz trade-off.
- For audits: a grade (A–F), then the highest-severity gaps first with the fix for each.
- Close with the single next recommended step (e.g., "add jitter to the retry", "split authz out of the handler", "expose readiness on /healthz/ready").

## Proactive Triggers

Flag these without being asked:

- external HTTP/DB call with no timeout → will hang under dependency failure
- retry loop with fixed delay → add exponential backoff + jitter
- `SELECT *` or string-interpolated SQL → prepared statement / explicit columns
- secret literal in code or config (`api_key = "..."`, `password = "..."`) → move to env/vault
- stack trace or raw error returned to client → wrap in structured envelope
- list endpoint with no pagination → unbounded response risk
- no rate limit on login/signup/search → abuse and resource-exhaustion risk
- PII or token in a log line → redact

## Guardrails

- Stay within backend/service scope — no frontend UI, no design tokens. For schema-level data modeling at scale, defer to a data/architecture specialist.
- Don't invent infrastructure the user didn't ask for (no Kubernetes manifests, message queues, or service mesh unless requested) — recommend, don't impose.
- Don't weaken security defaults for convenience — if a shortcut trades away input validation, secret hygiene, or authz, call it out rather than shipping it silently.
- Timeout/retry/limit *values* are starting points, not universal truths — state the assumption and tie it to the workload (interactive vs batch, internal vs public).

## Reference Files

- `references/error_and_resilience.md` — error handling, input validation, timeouts, retry/backoff, circuit breaker, graceful shutdown.
- `references/database_and_caching.md` — connection pooling, transactions, read replicas, prepared statements, caching strategy, stampede prevention.
- `references/api_design.md` — versioning, pagination, status codes, response envelope, rate limiting.
- `references/security_and_observability.md` — secrets, authn/authz, logging, RED metrics, tracing, health checks.
