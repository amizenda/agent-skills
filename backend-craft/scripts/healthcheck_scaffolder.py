#!/usr/bin/env python3
"""
Health-Check Endpoint Scaffolder

Generates liveness, readiness, and startup health-check endpoints following
the distinction in references/security_and_observability.md:
  - liveness:  process alive (no external deps)  -> restart on fail
  - readiness: can serve traffic (checks deps)    -> remove from LB on fail
  - startup:   slow-start grace window

Usage:
    python healthcheck_scaffolder.py --framework express --out src/routes/health.js
    python healthcheck_scaffolder.py --framework fastapi --out app/health.py
"""

import argparse
import sys
from pathlib import Path

EXPRESS = '''// health.js — liveness / readiness / startup probes
// Mount with: app.use('/healthz', require('./health'));
const express = require('express');
const router = express.Router();

// Inject your real dependency checks here (db pool, cache client, etc.)
// Keep them FAST and CHEAP — never run heavy queries in a probe.
async function checkDatabase() {
  // await pool.query('SELECT 1');  // wire up your pool
  return true;
}

const startedAt = Date.now();
const STARTUP_GRACE_MS = 15000;

// Liveness — is the process alive? No external calls.
router.get('/live', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Readiness — can we serve traffic right now? Check critical deps, with a timeout.
router.get('/ready', async (req, res) => {
  try {
    await Promise.race([
      checkDatabase(),
      new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 1000)),
    ]);
    res.status(200).json({ status: 'ready' });
  } catch (err) {
    res.status(503).json({ status: 'not ready', reason: err.message });
  }
});

// Startup — has the app finished booting? Lets orchestrators delay liveness.
router.get('/startup', (req, res) => {
  const elapsed = Date.now() - startedAt;
  if (elapsed < STARTUP_GRACE_MS) {
    return res.status(503).json({ status: 'starting', elapsedMs: elapsed });
  }
  res.status(200).json({ status: 'started' });
});

module.exports = router;
'''

FASTAPI = '''# health.py — liveness / readiness / startup probes
# Include with: app.include_router(health_router, prefix="/healthz")
import asyncio
import time
from fastapi import APIRouter, Response

health_router = APIRouter()

_started_at = time.monotonic()
_STARTUP_GRACE_S = 15.0


async def check_database() -> bool:
    # await db.execute("SELECT 1")   # wire up your engine/pool
    return True


# Liveness — is the process alive? No external calls.
@health_router.get("/live")
async def live():
    return {"status": "ok"}


# Readiness — can we serve traffic right now? Check critical deps, with a timeout.
@health_router.get("/ready")
async def ready(response: Response):
    try:
        await asyncio.wait_for(check_database(), timeout=1.0)
        return {"status": "ready"}
    except Exception as exc:  # noqa: BLE001
        response.status_code = 503
        return {"status": "not ready", "reason": str(exc)}


# Startup — has the app finished booting?
@health_router.get("/startup")
async def startup(response: Response):
    elapsed = time.monotonic() - _started_at
    if elapsed < _STARTUP_GRACE_S:
        response.status_code = 503
        return {"status": "starting", "elapsed_s": round(elapsed, 1)}
    return {"status": "started"}
'''


def main():
    ap = argparse.ArgumentParser(description="Scaffold health-check endpoints")
    ap.add_argument("--framework", "-f", choices=["express", "fastapi"], required=True)
    ap.add_argument("--out", "-o", required=True, help="Output file path")
    args = ap.parse_args()

    content = EXPRESS if args.framework == "express" else FASTAPI
    out = Path(args.out)
    if out.exists():
        print(f"Error: {out} already exists (refusing to overwrite)", file=sys.stderr)
        sys.exit(1)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content)

    print(f"Created {args.framework} health checks at {out}")
    print("Endpoints: /healthz/live, /healthz/ready, /healthz/startup")
    print("Next: wire check_database() to your real pool, and flip /ready to 503 during shutdown.")


if __name__ == "__main__":
    main()
