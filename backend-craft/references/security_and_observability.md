# Security & Observability

Keeping a service safe and visible in production. Read this for the `security` and `observability` paths.

---

## Table of Contents

- [Secrets](#secrets)
- [Authentication vs Authorization](#authentication-vs-authorization)
- [Security Hygiene](#security-hygiene)
- [Structured Logging](#structured-logging)
- [Metrics: the RED Method](#metrics-the-red-method)
- [Distributed Tracing](#distributed-tracing)
- [Health Checks](#health-checks)

---

## Secrets

- Secrets come from environment variables or a vault — **never** in code or committed config files.
- Different secrets per environment; rotate on a schedule and on suspected compromise.
- Don't log secrets, and don't echo them in error messages.

```js
// GOOD
const apiKey = process.env.PAYMENT_API_KEY;
if (!apiKey) throw new Error('PAYMENT_API_KEY is not set'); // fail at boot, not at first use

// NEVER
// const apiKey = 'sk_live_abc123...';
```

Fail fast at startup if a required secret is missing — better a clear boot error than a 500 on the first real request.

---

## Authentication vs Authorization

Keep these separate — they answer different questions:

- **Authentication** — *who are you?* (verify identity: token, session, mTLS)
- **Authorization** — *what are you allowed to do?* (check permissions on the resource)

```js
// authn middleware — establishes identity
function authenticate(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const user = verifyToken(token); // throws AppError('UNAUTHENTICATED', ..., 401) if invalid
  req.user = user;
  next();
}

// authz check — done per resource, not globally
function canEditPost(user, post) {
  return user.id === post.authorId || user.roles.includes('admin');
}

app.patch('/v1/posts/:id', authenticate, async (req, res, next) => {
  const post = await getPost(req.params.id);
  if (!post) return next(new AppError('NOT_FOUND', 'Post not found', 404));
  if (!canEditPost(req.user, post)) {
    return next(new AppError('FORBIDDEN', 'Not allowed', 403)); // 403, not 401
  }
  // ... proceed
});
```

Mixing the two (e.g. a single "isLoggedIn" gate) leads to privilege bugs where any authenticated user can touch any resource.

---

## Security Hygiene

- **Least privilege** — service accounts and DB users get the minimum permissions they need, nothing more.
- **Dependencies updated regularly** — automate with Dependabot/Renovate; a known CVE in a transitive dep is still your problem.
- Validate and sanitize all input (see `error_and_resilience.md`).
- Set security headers and TLS at the edge; don't terminate auth decisions on the client.

---

## Structured Logging

- Emit **structured logs (JSON)** — parseable by log aggregators, queryable by field.
- Put a **request ID** in every log line — trace one request across services.
- Use appropriate levels: `debug` in dev, `info`/`error` in prod; don't drown signal in noise.
- **Never log sensitive data** — passwords, tokens, full PII. Redact at the logger.

```js
import pino from 'pino';
const logger = pino({
  redact: ['req.headers.authorization', 'password', '*.token'], // redaction is not optional
});

// request-id middleware
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] || crypto.randomUUID();
  req.log = logger.child({ requestId: req.id });
  res.setHeader('x-request-id', req.id);
  next();
});
```

---

## Metrics: the RED Method

For every service, track three things — **R**ate, **E**rrors, **D**uration:

- **Rate** — requests per second.
- **Errors** — failed requests per second (and as a percentage).
- **Duration** — latency distribution, reported as **percentiles** (p50, p95, p99), never just the average — averages hide tail latency.

Alert on **symptoms, not causes**: alert on a high error rate or p99 latency (what users feel), not on CPU usage (which may be fine or irrelevant). Build dashboards that show normal so you can spot abnormal.

---

## Distributed Tracing

For microservices, propagate a trace context (e.g. W3C `traceparent`) so a single request can be followed across service hops. A trace shows where time goes — which downstream call is the bottleneck — in a way logs alone can't.

Use OpenTelemetry for vendor-neutral instrumentation; export to whatever backend you run (Jaeger, Tempo, a hosted APM).

---

## Health Checks

Distinguish the probe types — they trigger different orchestrator actions:

- **Liveness** — is the process alive? Fail → restart the container.
- **Readiness** — can it serve traffic right now? Fail → remove from the load balancer (but don't restart).
- **Startup** — for slow-starting services, gives the app time to boot before liveness kicks in.

Keep checks **fast and cheap**. A liveness probe should not hit the database — if the DB is briefly slow, you don't want every instance restarted into a crash loop. Readiness *may* check critical dependencies, but lightly.

```js
// liveness — process is up, nothing external
app.get('/healthz/live', (req, res) => res.status(200).json({ status: 'ok' }));

// readiness — can we serve? check critical deps with a short timeout
app.get('/healthz/ready', async (req, res) => {
  try {
    await Promise.race([
      pool.query('SELECT 1'),
      new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 1000)),
    ]);
    res.status(200).json({ status: 'ready' });
  } catch {
    res.status(503).json({ status: 'not ready' });
  }
});
```

During graceful shutdown, flip readiness to 503 first so the load balancer drains the instance before it stops.
