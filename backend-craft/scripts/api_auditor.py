#!/usr/bin/env python3
"""
Backend Production-Readiness Auditor

Scans a backend service (Node/Express or Python/FastAPI) for common
production-readiness gaps: missing timeouts, hardcoded secrets, SQL injection
risk, unbounded list endpoints, missing rate limits, and leaked error detail.

Heuristic / pattern-based — it flags candidates for review, not proof of a bug.

Usage:
    python api_auditor.py ./service
    python api_auditor.py ./service --verbose
    python api_auditor.py ./service --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

SRC_EXTS = {".js", ".ts", ".mjs", ".jsx", ".tsx", ".py"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", ".next", "venv", ".venv"}

# (severity, label, compiled regex, message)
CHECKS = [
    ("high", "hardcoded_secret",
     # char class includes base64/JWT chars (+ / = .) so encoded keys aren't missed;
     # min length raised to 16 to offset the broader class and reduce false positives.
     re.compile(r"""(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['"][A-Za-z0-9_+/=.\-]{16,}['"]"""),
     "Possible hardcoded secret — move to environment/vault"),
    ("high", "sql_injection",
     re.compile(r"""(query|execute)\s*\(\s*[`'"].*\$\{.*\}.*[`'"]|(SELECT|INSERT|UPDATE|DELETE)\b.*\+\s*\w+"""),
     "String-interpolated SQL — use parameterized/prepared statements"),
    ("high", "leaked_error",
     re.compile(r"""res\.(send|json)\([^)]*(err\.stack|error\.stack|\bstack\b)"""),
     "Stack trace returned to client — wrap in a structured error envelope"),
    ("medium", "fetch_no_timeout",
     re.compile(r"""\b(fetch|axios\.(get|post|put|delete)|requests\.(get|post))\b"""),
     "External call — verify an explicit timeout is set"),
    ("medium", "fixed_retry",
     re.compile(r"""setTimeout\([^,]+,\s*\d+\s*\).*retr|retr.*setTimeout\([^,]+,\s*\d+\s*\)""", re.I),
     "Retry with a fixed delay — use exponential backoff + jitter"),
    ("medium", "select_star",
     re.compile(r"""SELECT\s+\*\s+FROM""", re.I),
     "SELECT * — prefer explicit columns"),
    ("low", "list_no_pagination",
     re.compile(r"""\.(get|route)\(\s*['"][^'"]*s['"]\s*,"""),
     "List-style route — verify pagination (limit/cursor) is enforced"),
]

# Files/areas that hint a concern is handled (used to soften some findings)
RATE_LIMIT_HINTS = re.compile(r"""rate.?limit|ratelimit|express-rate-limit|slowapi|limiter""", re.I)
TIMEOUT_HINTS = re.compile(r"""timeout|AbortController|abort\(|httpx\.Timeout""", re.I)
PAGINATION_HINTS = re.compile(r"""\blimit\b|\bcursor\b|\boffset\b|pageInfo|paginate|per[_-]?page""", re.I)


def iter_source_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in SRC_EXTS and not any(d in p.parts for d in SKIP_DIRS):
            yield p


def scan_file(path: Path, root: Path):
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings, False, False
    lines = text.splitlines()
    has_timeout = bool(TIMEOUT_HINTS.search(text))
    has_ratelimit = bool(RATE_LIMIT_HINTS.search(text))
    has_pagination = bool(PAGINATION_HINTS.search(text))

    for sev, label, rx, msg in CHECKS:
        # Soften timeout finding if the file clearly configures timeouts somewhere
        if label == "fetch_no_timeout" and has_timeout:
            continue
        # Soften pagination finding if the file uses limit/cursor/offset anywhere
        # (file-granular, like the timeout softening above — avoids flagging
        # correctly-paginated list routes such as the scaffolder's own example).
        if label == "list_no_pagination" and has_pagination:
            continue
        for i, line in enumerate(lines, 1):
            if rx.search(line):
                findings.append({
                    "severity": sev, "check": label,
                    "file": str(path.relative_to(root)), "line": i,
                    "message": msg, "snippet": line.strip()[:120],
                })
    return findings, has_timeout, has_ratelimit


def grade(findings):
    score = 100
    weight = {"high": 15, "medium": 7, "low": 3}
    for f in findings:
        score -= weight.get(f["severity"], 3)
    score = max(0, min(100, score))
    g = ("A" if score >= 90 else "B" if score >= 80 else
         "C" if score >= 70 else "D" if score >= 60 else "F")
    return score, g


def main():
    ap = argparse.ArgumentParser(description="Audit a backend service for production-readiness gaps")
    ap.add_argument("service_dir", nargs="?", default=".", help="Service directory (default: .)")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    ap.add_argument("--verbose", "-v", action="store_true", help="Show every finding (not just top per check)")
    args = ap.parse_args()

    root = Path(args.service_dir).resolve()
    if not root.exists():
        print(f"Error: not found: {root}", file=sys.stderr)
        sys.exit(1)

    all_findings = []
    files_scanned = 0
    any_ratelimit = False
    for f in iter_source_files(root):
        files_scanned += 1
        found, _, has_rl = scan_file(f, root)
        any_ratelimit = any_ratelimit or has_rl
        all_findings.extend(found)

    # Whole-service finding: no rate limiting anywhere
    if not any_ratelimit and files_scanned > 0:
        all_findings.append({
            "severity": "medium", "check": "no_rate_limiting",
            "file": "(service-wide)", "line": 0,
            "message": "No rate limiting detected anywhere — add limits on login/signup/search",
            "snippet": "",
        })

    score, g = grade(all_findings)

    if args.json:
        print(json.dumps({
            "service": str(root), "files_scanned": files_scanned,
            "score": score, "grade": g, "findings": all_findings,
        }, indent=2))
        return

    print("=" * 64)
    print("BACKEND PRODUCTION-READINESS AUDIT")
    print("=" * 64)
    print(f"\nService: {root}")
    print(f"Files scanned: {files_scanned}")
    print(f"Readiness score: {score}/100 ({g})")

    order = {"high": 0, "medium": 1, "low": 2}
    all_findings.sort(key=lambda x: order.get(x["severity"], 3))

    if not all_findings:
        print("\nNo obvious gaps found. (Heuristic scan — still review manually.)")
    else:
        seen = set()
        print("\n--- FINDINGS (highest severity first) ---")
        for f in all_findings:
            key = (f["check"], f["file"], f["line"])
            if not args.verbose and f["check"] in seen and f["file"] != "(service-wide)":
                continue
            seen.add(f["check"])
            loc = f["file"] if f["line"] == 0 else f"{f['file']}:{f['line']}"
            print(f"\n  [{f['severity'].upper()}] {f['check']}  ({loc})")
            print(f"    {f['message']}")
            if f["snippet"]:
                print(f"    > {f['snippet']}")
        if not args.verbose:
            print("\n  (run with --verbose to see every occurrence)")

    print("\n" + "=" * 64)


if __name__ == "__main__":
    main()
