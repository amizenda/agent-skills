# API Design

Consistent, evolvable HTTP APIs. Read this for the `api-design` path.

---

## Table of Contents

- [Versioning](#versioning)
- [Pagination](#pagination)
- [Status Codes](#status-codes)
- [Response Envelope](#response-envelope)
- [Rate Limiting](#rate-limiting)

---

## Versioning

Decide a versioning strategy from day one — retrofitting it later is painful.

- **Path versioning** (`/v1/users`) — most visible, easiest to route and cache. Most common.
- **Header versioning** (`Accept: application/vnd.api.v1+json`) — cleaner URLs, harder to test by hand.

Pick one and be consistent. Within a major version, only make backward-compatible changes (add fields, never remove or repurpose them).

---

## Pagination

Every list endpoint needs pagination — an unbounded list is a latent outage as data grows.

**Offset pagination** — simple, supports jumping to a page, but slow on deep pages and can skip/duplicate rows under concurrent writes.

```
GET /v1/users?limit=20&offset=40
```

**Cursor pagination** — stable under writes, fast at any depth; can't jump to an arbitrary page. Preferred for large or fast-changing datasets.

```
GET /v1/users?limit=20&cursor=eyJpZCI6MTAwfQ

{
  "data": [ ... ],
  "pageInfo": { "nextCursor": "eyJpZCI6MTIwfQ", "hasNextPage": true }
}
```

Include enough metadata for the client to continue (a next cursor or a total count for offset).

---

## Status Codes

Use codes that mean what they say:

| Code | Use for |
|------|---------|
| 200 | Successful GET/PUT/PATCH |
| 201 | Resource created (POST) — include `Location` header |
| 204 | Success with no body (DELETE) |
| 400 | Malformed request |
| 401 | Not authenticated |
| 403 | Authenticated but not authorized |
| 404 | Resource not found |
| 409 | Conflict (e.g. duplicate, version mismatch) |
| 422 | Validation failed (well-formed but semantically invalid) |
| 429 | Rate limited — include `Retry-After` |
| 500 | Unexpected server error |
| 503 | Dependency unavailable / shutting down |

Distinguish 401 (who are you?) from 403 (you can't do this) — they drive different client behavior.

---

## Response Envelope

Use the same shape everywhere so clients can parse uniformly.

```jsonc
// Success
{ "data": { ... } }

// List
{ "data": [ ... ], "pageInfo": { "nextCursor": "...", "hasNextPage": true } }

// Error — matches the error envelope from error_and_resilience.md
{ "error": { "code": "VALIDATION", "message": "email is invalid", "requestId": "req_abc123" } }
```

Consistency beats cleverness — a predictable envelope is worth more than a perfectly minimal one.

---

## Rate Limiting

Protect expensive operations and limit abuse.

- Apply per-user and/or per-IP limits on expensive ops — login, signup, search, password reset.
- Use **different limits for different operations** — generous on cheap reads, strict on writes and auth.
- Return a `Retry-After` header on 429 so well-behaved clients know when to come back.
- Rate-limit **early** in the pipeline — before auth and business logic — to save resources.

```js
// Token-bucket sketch backed by Redis
async function rateLimit(key, { limit = 10, windowSec = 60 }) {
  const count = await redis.incr(key);
  if (count === 1) await redis.expire(key, windowSec);
  if (count > limit) {
    const ttl = await redis.ttl(key);
    throw new AppError('RATE_LIMITED', 'Too many requests', 429, { retryAfter: ttl });
  }
}

// Strict limit on login, generous elsewhere
app.post('/v1/login', (req, res, next) =>
  rateLimit(`login:${req.ip}`, { limit: 5, windowSec: 300 }).then(() => next()).catch(next));
```

Tie the limit to the operation's cost and threat model — public auth endpoints are strict; internal read APIs can be generous.
