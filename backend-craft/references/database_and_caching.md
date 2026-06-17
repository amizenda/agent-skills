# Database & Caching

Data-layer practices for reliability and throughput. Read this for the `data` path.

---

## Table of Contents

- [Connection Pooling](#connection-pooling)
- [Transactions](#transactions)
- [Read Replicas](#read-replicas)
- [Prepared Statements](#prepared-statements)
- [Caching Strategy](#caching-strategy)
- [Cache Stampede Prevention](#cache-stampede-prevention)

---

## Connection Pooling

Creating a database connection is expensive (TCP + auth + TLS). Reuse them via a pool.

- Size the pool to the workload, not arbitrarily large — too many connections overwhelm the DB.
- A common starting heuristic: `pool_size ≈ (core_count * 2) + effective_spindle_count`, then tune by observation.
- Set a pool **acquire timeout** — if no connection is free, fail fast rather than queue forever.

```js
// node-postgres
import { Pool } from 'pg';
const pool = new Pool({
  max: 20,                       // max connections
  idleTimeoutMillis: 30000,      // close idle connections
  connectionTimeoutMillis: 5000, // acquire timeout — fail fast
});
```

```python
# SQLAlchemy async
from sqlalchemy.ext.asyncio import create_async_engine
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=5,        # acquire timeout
    pool_recycle=1800,     # recycle connections every 30 min
)
```

---

## Transactions

- Scope transactions as tightly as possible — hold locks for the minimum time.
- Do not perform external HTTP calls inside a transaction — a slow call holds the lock and a row.
- Choose the right isolation level; the default (read committed) is right for most cases.

```js
async function transfer(from, to, amount) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query('UPDATE accounts SET balance = balance - $1 WHERE id = $2', [amount, from]);
    await client.query('UPDATE accounts SET balance = balance + $1 WHERE id = $2', [amount, to]);
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release(); // always return the connection to the pool
  }
}
```

```python
# SQLAlchemy async — transaction scoped tightly; no external HTTP calls inside it
from sqlalchemy import text

async def transfer(session_factory, from_id, to_id, amount):
    async with session_factory() as session:
        async with session.begin():          # BEGIN; COMMIT on exit, ROLLBACK on exception
            await session.execute(
                text("UPDATE accounts SET balance = balance - :amt WHERE id = :id"),
                {"amt": amount, "id": from_id},
            )
            await session.execute(
                text("UPDATE accounts SET balance = balance + :amt WHERE id = :id"),
                {"amt": amount, "id": to_id},
            )
    # session is returned to the pool on context exit
```

---

## Read Replicas

For read-heavy workloads, separate read and write traffic:

- Writes go to the primary; reads can go to replicas.
- Be aware of **replication lag** — a read immediately after a write may not see it. Route read-your-own-writes to the primary when consistency matters.
- Don't replicate blindly — a replica adds operational cost; add one when read load is the bottleneck.

---

## Prepared Statements

Always use parameterized / prepared statements:

- **SQL injection prevention** — parameters are never interpreted as SQL.
- **Query plan caching** — the database can reuse the plan.

```js
// GOOD — parameterized
await pool.query('SELECT id, email FROM users WHERE email = $1', [email]);

// NEVER — string interpolation is an injection hole
// await pool.query(`SELECT * FROM users WHERE email = '${email}'`);
```

```python
# SQLAlchemy — bound parameters; never interpolate into the SQL string
from sqlalchemy import text

await session.execute(
    text("SELECT id, email FROM users WHERE email = :email"), {"email": email}
)
# NEVER: text(f"SELECT id, email FROM users WHERE email = '{email}'")
```

Also prefer explicit columns over `SELECT *` — it avoids breaking on schema changes and reduces row width over the wire.

---

## Caching Strategy

Decide the invalidation strategy **upfront** — TTL, event-based, or both. A cache with no clear invalidation plan becomes a correctness bug.

Choose the layer that fits:
- query result cache (e.g. an expensive aggregate)
- computed-value cache (a derived object)
- HTTP response cache (full responses for anonymous traffic)

```js
async function getUser(id) {
  const key = `user:${id}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const user = await pool.query('SELECT id, email FROM users WHERE id = $1', [id]);
  await redis.set(key, JSON.stringify(user.rows[0]), 'EX', 300); // 5 min TTL
  return user.rows[0];
}

// Event-based invalidation on write
async function updateUser(id, data) {
  await pool.query('UPDATE users SET email = $1 WHERE id = $2', [data.email, id]);
  await redis.del(`user:${id}`); // invalidate immediately
}
```

```python
# redis.asyncio + SQLAlchemy — same pattern: read-through cache, invalidate on write
import json
from sqlalchemy import text

async def get_user(redis, session, user_id):
    key = f"user:{user_id}"
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)
    row = (await session.execute(
        text("SELECT id, email FROM users WHERE id = :id"), {"id": user_id}
    )).mappings().first()
    await redis.set(key, json.dumps(dict(row)), ex=300)  # 5 min TTL
    return dict(row)

async def update_user(redis, session, user_id, email):
    await session.execute(
        text("UPDATE users SET email = :email WHERE id = :id"),
        {"email": email, "id": user_id},
    )
    await redis.delete(f"user:{user_id}")  # invalidate immediately
```

Monitor the **hit rate** — a low hit rate means the cache is wasting memory and adding latency for no benefit.

---

## Cache Stampede Prevention

When a hot key expires, many requests miss simultaneously and all hit the database at once (the "thundering herd" / stampede). Two defenses:

**1. Lock (single-flight)** — only one request recomputes; others wait or serve stale.

```js
async function getWithLock(key, compute, ttl = 300) {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const lockKey = `lock:${key}`;
  const gotLock = await redis.set(lockKey, '1', 'NX', 'EX', 10);
  if (!gotLock) {
    // someone else is computing — brief wait, then read
    await new Promise((r) => setTimeout(r, 50));
    return getWithLock(key, compute, ttl);
  }
  try {
    const value = await compute();
    await redis.set(key, JSON.stringify(value), 'EX', ttl);
    return value;
  } finally {
    await redis.del(lockKey);
  }
}
```

**2. Probabilistic early expiration** — recompute slightly before expiry, randomized, so not all clients refresh at the same instant. Good for very hot keys where even a brief lock-wait is too much.
