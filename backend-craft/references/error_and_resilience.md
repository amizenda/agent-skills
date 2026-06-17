# Error Handling & Resilience

How a backend behaves under failure. Read this for the `resilience` and error-handling paths.

---

## Table of Contents

- [Error Handling](#error-handling)
- [Input Validation](#input-validation)
- [Timeouts Everywhere](#timeouts-everywhere)
- [Retry Patterns](#retry-patterns)
- [Circuit Breaker](#circuit-breaker)
- [Graceful Shutdown](#graceful-shutdown)

---

## Error Handling

Principles:
- Never expose stack traces to clients — log internally, return a generic message.
- Use a structured error response: `code`, `message`, `requestId` — enables debugging without leaking internals.
- Fail fast on bad input — validate at the entry point, not deep in business logic.
- Unexpected errors → 500 + alert. Expected errors → the appropriate 4xx.

**Structured error envelope (Express):**

```js
// errors.js
class AppError extends Error {
  constructor(code, message, status = 400) {
    super(message);
    this.code = code;       // machine-readable, e.g. 'INVALID_EMAIL'
    this.status = status;   // HTTP status
  }
}

// error middleware — last in the chain
function errorHandler(err, req, res, next) {
  const requestId = req.id;
  if (err instanceof AppError) {
    // Expected error — safe to surface code + message
    return res.status(err.status).json({
      error: { code: err.code, message: err.message, requestId },
    });
  }
  // Unexpected — log full detail internally, return generic message
  req.log.error({ err, requestId }, 'unhandled error');
  res.status(500).json({
    error: { code: 'INTERNAL', message: 'Something went wrong', requestId },
  });
}
```

**FastAPI equivalent:**

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code, self.message, self.status = code, message, status

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message,
                           "requestId": request.state.request_id}},
    )

@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    logger.error("unhandled error", exc_info=exc,
                 extra={"requestId": request.state.request_id})
    return JSONResponse(status_code=500, content={
        "error": {"code": "INTERNAL", "message": "Something went wrong",
                  "requestId": request.state.request_id}})
```

---

## Input Validation

- Validate everything from outside — query params, headers, body, path params.
- Whitelist valid input, don't blacklist bad — reject unknown fields.
- Validate early, before any processing — saves resources, gives clearer errors.
- Size limits on all inputs — prevent memory-exhaustion attacks.

Use a schema validator at the boundary (`zod` for Node, `pydantic` for FastAPI):

```js
import { z } from 'zod';

const CreateUser = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150),
}).strict(); // .strict() rejects unknown fields

function validate(schema) {
  return (req, res, next) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      return next(new AppError('VALIDATION', result.error.message, 422));
    }
    req.body = result.data; // parsed + typed
    next();
  };
}
```

FastAPI gets this for free — declare a Pydantic model as the body type and validation happens before the handler runs. Add `model_config = ConfigDict(extra='forbid')` to reject unknown fields.

---

## Timeouts Everywhere

A call with no timeout is a latent outage. Set them on every boundary:

- Database queries: typically 5–30s depending on the query.
- External HTTP calls: a **connect** timeout *and* a **read** timeout — don't wait forever.
- Overall request timeout — at the gateway or middleware level.
- Background jobs: a max execution time — prevents zombie processes.

```js
// Node fetch with timeout via AbortController
async function fetchWithTimeout(url, ms = 5000) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), ms);
  try {
    return await fetch(url, { signal: ctrl.signal });
  } finally {
    clearTimeout(t);
  }
}
```

```python
import httpx
# connect + read timeouts, explicitly
timeout = httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=5.0)
async with httpx.AsyncClient(timeout=timeout) as client:
    r = await client.get(url)
```

---

## Retry Patterns

- Exponential backoff: 1s, 2s, 4s, 8s… — prevents a thundering herd.
- Add **jitter**: randomize the delay — prevents synchronized retries across clients.
- Idempotency keys for non-idempotent operations — makes them safe to retry.
- Pair with a circuit breaker for failing dependencies — stop hammering, fail fast.

```js
async function retry(fn, { attempts = 4, base = 1000, cap = 10000 } = {}) {
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === attempts - 1) throw err;
      const backoff = Math.min(cap, base * 2 ** i);
      const jitter = Math.random() * backoff; // full jitter
      await new Promise((r) => setTimeout(r, jitter));
    }
  }
}
```

Only retry on transient failures (network errors, 503, 429 with Retry-After). Never retry on 4xx like 400/401/403 — the request won't get more valid by repeating it.

---

## Circuit Breaker

When a dependency is failing, stop sending traffic to it for a cooldown window. Three states:

- **Closed** — normal; requests flow. Count failures.
- **Open** — failure threshold exceeded; reject immediately for a cooldown, don't call the dependency.
- **Half-open** — after cooldown, allow a *single* trial request through (reject the rest). Success → close; failure → open again.

```js
class CircuitBreaker {
  constructor({ threshold = 5, cooldown = 30000 } = {}) {
    this.threshold = threshold;
    this.cooldown = cooldown;
    this.failures = 0;
    this.state = 'closed';
    this.openedAt = 0;
    this.trialInFlight = false; // half-open: admit only ONE probe at a time
  }
  async call(fn) {
    if (this.state === 'open') {
      if (Date.now() - this.openedAt < this.cooldown) {
        throw new AppError('CIRCUIT_OPEN', 'Dependency unavailable', 503);
      }
      this.state = 'half-open';
    }
    // In half-open, let a single trial through; reject the rest until it resolves.
    // Without this gate, every concurrent request floods the recovering dependency.
    if (this.state === 'half-open') {
      if (this.trialInFlight) {
        throw new AppError('CIRCUIT_OPEN', 'Dependency recovering', 503);
      }
      this.trialInFlight = true;
    }
    try {
      const result = await fn();
      this.failures = 0;
      this.state = 'closed';
      return result;
    } catch (err) {
      this.failures++;
      if (this.failures >= this.threshold) {
        this.state = 'open';
        this.openedAt = Date.now();
      }
      throw err;
    } finally {
      this.trialInFlight = false; // free the slot whether the probe passed or failed
    }
  }
}
```

---

## Graceful Shutdown

On SIGTERM, shut down cleanly so no in-flight request is dropped:

1. Stop accepting new requests first — drain the load balancer.
2. Wait for in-flight requests to complete — with a timeout.
3. Close database connections cleanly — prevent connection leaks.
4. SIGTERM → graceful; force exit (SIGKILL behavior) only after the timeout.

```js
function setupGracefulShutdown(server, { drainMs = 10000 } = {}) {
  async function shutdown(signal) {
    console.log(`${signal} received, draining...`);
    server.close(async () => {       // stop accepting new connections
      await db.close();              // close pool
      process.exit(0);
    });
    setTimeout(() => {
      console.error('drain timeout, forcing exit');
      process.exit(1);
    }, drainMs).unref();
  }
  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));
}
```
