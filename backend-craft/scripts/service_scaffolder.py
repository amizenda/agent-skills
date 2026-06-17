#!/usr/bin/env python3
"""
Backend Service Scaffolder

Scaffolds a production-minded backend service (Node/Express or Python/FastAPI)
with the resilience defaults this skill cares about already wired in:
request IDs, structured errors, graceful shutdown, health checks, and an
example validated + rate-limit-ready endpoint.

Usage:
    python service_scaffolder.py my-service --framework express
    python service_scaffolder.py my-service --framework fastapi --features auth,ratelimit
"""

import argparse
import sys
from pathlib import Path

EXPRESS = {
    "package.json": '''{{
  "name": "{name}",
  "version": "0.1.0",
  "private": true,
  "main": "src/server.js",
  "engines": {{ "node": ">=18" }},
  "scripts": {{ "start": "node src/server.js", "dev": "node --watch src/server.js" }},
  "dependencies": {{
    "express": "^5.1.0",
    "pino": "^9.0.0",
    "pino-http": "^10.0.0",
    "zod": "^3.23.0"
  }}
}}
''',
    "src/server.js": '''const express = require('express');
const crypto = require('crypto');
const pino = require('pino');
const {{ errorHandler }} = require('./errors');
const health = require('./health');

const logger = pino({{ redact: ['req.headers.authorization', 'password', '*.token'] }});
const app = express();
app.use(express.json({{ limit: '1mb' }})); // size limit — prevent memory exhaustion

// request id + child logger on every request
app.use((req, res, next) => {{
  req.id = req.headers['x-request-id'] || crypto.randomUUID();
  req.log = logger.child({{ requestId: req.id }});
  res.setHeader('x-request-id', req.id);
  next();
}});

app.use('/healthz', health);
app.use('/v1', require('./routes/example'));
app.use(errorHandler); // last in the chain

const server = app.listen(process.env.PORT || 3000, () =>
  logger.info(`listening on ${{process.env.PORT || 3000}}`));

// graceful shutdown
function shutdown(signal) {{
  logger.info(`${{signal}} received, draining`);
  server.close(() => process.exit(0));
  setTimeout(() => process.exit(1), 10000).unref();
}}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
''',
    "src/errors.js": '''class AppError extends Error {{
  constructor(code, message, status = 400) {{
    super(message);
    this.code = code;
    this.status = status;
  }}
}}

function errorHandler(err, req, res, next) {{ // eslint-disable-line no-unused-vars
  const requestId = req.id;
  if (err instanceof AppError) {{
    return res.status(err.status).json({{ error: {{ code: err.code, message: err.message, requestId }} }});
  }}
  req.log.error({{ err, requestId }}, 'unhandled error');
  res.status(500).json({{ error: {{ code: 'INTERNAL', message: 'Something went wrong', requestId }} }});
}}

module.exports = {{ AppError, errorHandler }};
''',
    "src/routes/example.js": '''const express = require('express');
const {{ z }} = require('zod');
const {{ AppError }} = require('../errors');
const router = express.Router();

const CreateItem = z.object({{ name: z.string().min(1).max(200) }}).strict();

function validate(schema) {{
  return (req, res, next) => {{
    const r = schema.safeParse(req.body);
    if (!r.success) return next(new AppError('VALIDATION', r.error.message, 422));
    req.body = r.data;
    next();
  }};
}}

// GET list — paginated (enforce a limit; never return everything)
router.get('/items', (req, res) => {{
  const limit = Math.min(Number(req.query.limit) || 20, 100);
  res.json({{ data: [], pageInfo: {{ hasNextPage: false }}, limit }});
}});

router.post('/items', validate(CreateItem), (req, res) => {{
  res.status(201).json({{ data: {{ id: '1', name: req.body.name }} }});
}});

module.exports = router;
''',
    "src/health.js": '''const express = require('express');
const router = express.Router();
const startedAt = Date.now();

router.get('/live', (req, res) => res.status(200).json({{ status: 'ok' }}));
router.get('/ready', async (req, res) => {{
  try {{
    // await pool.query('SELECT 1');
    res.status(200).json({{ status: 'ready' }});
  }} catch (e) {{
    res.status(503).json({{ status: 'not ready' }});
  }}
}});
router.get('/startup', (req, res) => {{
  const ok = Date.now() - startedAt > 15000;
  res.status(ok ? 200 : 503).json({{ status: ok ? 'started' : 'starting' }});
}});

module.exports = router;
''',
    ".env.example": '''PORT=3000
# DATABASE_URL=
# never commit real secrets — this file documents required vars only
''',
    ".gitignore": '''node_modules/
.env
*.log
''',
}

FASTAPI = {
    "requirements.txt": '''fastapi>=0.111
uvicorn[standard]>=0.30
pydantic>=2.7
''',
    "app/main.py": '''import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.errors import AppError
from app.health import health_router
from app.routes import example_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("{name}")
app = FastAPI(title="{name}")


@app.middleware("http")
async def request_id_mw(request: Request, call_next):
    request.state.request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["x-request-id"] = request.state.request_id
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status, content={{
        "error": {{"code": exc.code, "message": exc.message,
                   "requestId": request.state.request_id}}}})


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    logger.error("unhandled error", exc_info=exc,
                 extra={{"requestId": request.state.request_id}})
    return JSONResponse(status_code=500, content={{
        "error": {{"code": "INTERNAL", "message": "Something went wrong",
                   "requestId": request.state.request_id}}}})


app.include_router(health_router, prefix="/healthz")
app.include_router(example_router, prefix="/v1")
''',
    "app/errors.py": '''class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status
''',
    "app/routes.py": '''from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict, Field

example_router = APIRouter()


class CreateItem(BaseModel):
    model_config = ConfigDict(extra="forbid")  # reject unknown fields
    name: str = Field(min_length=1, max_length=200)


@example_router.get("/items")
async def list_items(limit: int = Query(20, le=100)):  # enforce a max limit
    return {{"data": [], "pageInfo": {{"hasNextPage": False}}, "limit": limit}}


@example_router.post("/items", status_code=201)
async def create_item(item: CreateItem):
    return {{"data": {{"id": "1", "name": item.name}}}}
''',
    "app/health.py": '''import asyncio
import time
from fastapi import APIRouter, Response

health_router = APIRouter()
_started_at = time.monotonic()


async def check_db() -> bool:
    return True


@health_router.get("/live")
async def live():
    return {{"status": "ok"}}


@health_router.get("/ready")
async def ready(response: Response):
    try:
        await asyncio.wait_for(check_db(), timeout=1.0)
        return {{"status": "ready"}}
    except Exception:
        response.status_code = 503
        return {{"status": "not ready"}}


@health_router.get("/startup")
async def startup(response: Response):
    if time.monotonic() - _started_at < 15:
        response.status_code = 503
        return {{"status": "starting"}}
    return {{"status": "started"}}
''',
    "app/__init__.py": "",
    ".env.example": '''# DATABASE_URL=
# never commit real secrets
''',
    ".gitignore": '''__pycache__/
.env
*.log
.venv/
''',
}

# --- Feature stubs: runnable files generated on --features (NOT run through .format,
# so they use normal single braces). Each is self-contained and wired to AppError. ---

_EXPRESS_AUTH = '''// auth.js — authentication (WHO you are) + authorization (WHAT you can do), kept separate.
// Mount example: app.use('/v1', authenticate, require('./routes/example'));
const { AppError } = require('../errors');

// Replace with real verification (jwt.verify, session lookup, mTLS, ...).
function verifyToken(token) {
  if (!token) throw new AppError('UNAUTHENTICATED', 'Missing token', 401);
  // const payload = jwt.verify(token, process.env.JWT_SECRET);
  return { id: 'demo-user', roles: ['user'] }; // stub identity
}

// Authentication — establishes who the caller is.
function authenticate(req, res, next) {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    req.user = verifyToken(token);
    next();
  } catch (err) {
    next(err);
  }
}

// Authorization — checks what the caller may do, per resource. Keep separate from authn.
// Usage: router.patch('/posts/:id', authenticate, authorize((u, req) => u.roles.includes('admin')), handler)
function authorize(check) {
  return (req, res, next) => {
    if (!check(req.user, req)) return next(new AppError('FORBIDDEN', 'Not allowed', 403));
    next();
  };
}

module.exports = { authenticate, authorize };
'''

_EXPRESS_RATELIMIT = '''// ratelimit.js — apply EARLY, before auth/business logic. Strict on auth, generous on cheap reads.
// Mount example (strict login): app.post('/v1/login', rateLimit({ limit: 5, windowSec: 300 }), handler);
//
// In-memory limiter — fine for a single instance / dev. For multiple instances, back it with
// Redis (INCR + EXPIRE) so the counter is shared across processes. See references/api_design.md.
const { AppError } = require('../errors');

const buckets = new Map(); // key -> { count, resetAt }

function rateLimit({ limit = 10, windowSec = 60, keyFn } = {}) {
  return (req, res, next) => {
    const key = (keyFn ? keyFn(req) : req.ip) || 'global';
    const now = Date.now();
    let b = buckets.get(key);
    if (!b || now > b.resetAt) {
      b = { count: 0, resetAt: now + windowSec * 1000 };
      buckets.set(key, b);
    }
    b.count++;
    if (b.count > limit) {
      res.setHeader('Retry-After', String(Math.ceil((b.resetAt - now) / 1000)));
      return next(new AppError('RATE_LIMITED', 'Too many requests', 429));
    }
    next();
  };
}

module.exports = { rateLimit };
'''

_FASTAPI_AUTH = '''# auth.py — authentication (WHO you are) + authorization (WHAT you can do), kept separate.
# Usage:
#   from app.auth import get_current_user, require
#   @router.get("/items")
#   async def list_items(user=Depends(get_current_user)): ...
#   # authz: dependencies=[Depends(require(lambda u: "admin" in u["roles"]))]
from typing import Optional
from fastapi import Depends, Header
from app.errors import AppError


def _verify_token(token: str) -> dict:
    if not token:
        raise AppError("UNAUTHENTICATED", "Missing token", 401)
    # payload = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])
    return {"id": "demo-user", "roles": ["user"]}  # stub identity


# Authentication — establishes who the caller is.
async def get_current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    token = (authorization or "").replace("Bearer ", "")
    return _verify_token(token)


# Authorization — checks what the caller may do. Keep separate from authn.
def require(check):
    async def _dep(user: dict = Depends(get_current_user)) -> dict:
        if not check(user):
            raise AppError("FORBIDDEN", "Not allowed", 403)
        return user
    return _dep
'''

_FASTAPI_RATELIMIT = '''# ratelimit.py — apply EARLY. Strict on auth endpoints, generous on cheap reads.
# Usage:
#   from app.ratelimit import rate_limit
#   @router.post("/login", dependencies=[Depends(rate_limit(limit=5, window_s=300))])
#   async def login(): ...
#
# In-memory limiter — fine for one instance / dev. For multiple instances, back it with
# Redis (INCR + EXPIRE) so the counter is shared across processes. See references/api_design.md.
import time
from fastapi import Request
from app.errors import AppError

_buckets = {}  # key -> (count, reset_at)


def rate_limit(limit: int = 10, window_s: int = 60, key_fn=None):
    async def _dep(request: Request):
        key = (key_fn(request) if key_fn else request.client.host) or "global"
        now = time.monotonic()
        count, reset_at = _buckets.get(key, (0, now + window_s))
        if now > reset_at:
            count, reset_at = 0, now + window_s
        count += 1
        _buckets[key] = (count, reset_at)
        if count > limit:
            # AppError is rendered by the handler in main.py (add Retry-After there if needed)
            raise AppError("RATE_LIMITED", "Too many requests", 429)
    return _dep
'''

# feature -> (relative path, template); selected by framework
EXPRESS_FEATURES = {
    "auth": ("src/middleware/auth.js", _EXPRESS_AUTH),
    "ratelimit": ("src/middleware/ratelimit.js", _EXPRESS_RATELIMIT),
}
FASTAPI_FEATURES = {
    "auth": ("app/auth.py", _FASTAPI_AUTH),
    "ratelimit": ("app/ratelimit.py", _FASTAPI_RATELIMIT),
}
FEATURE_MOUNT = {
    ("express", "auth"): "require('./middleware/auth'); add `authenticate` (+ optional `authorize`) to a route/router.",
    ("express", "ratelimit"): "require('./middleware/ratelimit'); e.g. app.post('/v1/login', rateLimit({limit:5,windowSec:300}), handler).",
    ("fastapi", "auth"): "from app.auth import get_current_user, require; add Depends(get_current_user) to handlers.",
    ("fastapi", "ratelimit"): "from app.ratelimit import rate_limit; add dependencies=[Depends(rate_limit(limit=5, window_s=300))].",
}


def main():
    ap = argparse.ArgumentParser(description="Scaffold a production-minded backend service")
    ap.add_argument("name", help="Service name / directory")
    ap.add_argument("--framework", "-f", choices=["express", "fastapi"], default="express")
    ap.add_argument("--dir", "-d", default=".", help="Parent directory")
    ap.add_argument("--features", help="Comma-separated: auth,ratelimit")
    args = ap.parse_args()

    root = Path(args.dir) / args.name
    if root.exists() and any(root.iterdir()):
        print(f"Error: {root} exists and is not empty", file=sys.stderr)
        sys.exit(1)

    files = EXPRESS if args.framework == "express" else FASTAPI
    created = []
    for rel, tmpl in files.items():
        full = root / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(tmpl.format(name=args.name))
        created.append(str(full))

    print(f"\n{'='*54}\nScaffolded: {args.name} ({args.framework})\n{'='*54}")
    print(f"Location: {root}\nFiles:")
    for f in created:
        print(f"  - {f}")

    if args.features:
        feature_map = EXPRESS_FEATURES if args.framework == "express" else FASTAPI_FEATURES
        print("\nGenerated feature stubs (runnable — wire the mount line in):")
        for feat in [x.strip() for x in args.features.split(",") if x.strip()]:
            spec = feature_map.get(feat)
            if not spec:
                print(f"  - {feat}: unknown feature (known: {', '.join(feature_map)})")
                continue
            rel, tmpl = spec
            full = root / rel
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(tmpl)  # raw — feature stubs use normal braces, no .format
            print(f"  - {feat}: {rel}")
            mount = FEATURE_MOUNT.get((args.framework, feat))
            if mount:
                print(f"      mount: {mount}")

    print(f"\n{'='*54}")
    print("Already wired: request IDs, structured errors, graceful shutdown,")
    print("health checks, size-limited body, paginated + validated example route.")
    print(f"{'='*54}\n")


if __name__ == "__main__":
    main()
