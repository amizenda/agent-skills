# backend-craft

> Build, scaffold, and review **production-ready backend services** — Node/Express and Python/FastAPI.
> Xây dựng, scaffold và review **backend services sẵn sàng cho production** — Node/Express và Python/FastAPI.

A Claude Skill refactored from a flat best-practice checklist into a full skill: a workflow-driven `SKILL.md`, layered `references/` with real code, and executable `scripts/` that scaffold and audit services. The premise — a backend that returns the right JSON in the happy path is not done; it's judged by how it behaves when a dependency is slow, input is hostile, traffic spikes, or it crashes mid-request.

Một Claude Skill được refactor từ một checklist best-practice phẳng thành skill đầy đủ: `SKILL.md` theo workflow, `references/` phân lớp kèm code thật, và `scripts/` chạy được để scaffold và audit service. Tiền đề — một backend trả đúng JSON ở happy path thì chưa xong; nó được đánh giá qua cách hành xử khi dependency chậm, input độc hại, traffic tăng đột biến, hoặc crash giữa request.

---

## English

### What it does

Turns the AI agent into a senior backend engineer that doesn't just *know* best practices but *acts* on them — scaffolds services with resilience defaults already wired in, and audits existing code for production-readiness gaps.

### Workflow

1. **Classify** — `scaffold` | `resilience` | `api-design` | `data` | `security` | `observability` | `review`.
2. **Load the relevant reference** (see below).
3. **Run a script** when the task is concrete (scaffold / health checks / audit).
4. **Self-audit** against the production-readiness checklist.
5. **Emit one artifact** + the single best next step.

### Structure

```
backend-craft/
├── SKILL.md                              # Orchestrator: workflow, self-audit, guardrails
├── _meta.json                            # Metadata
├── README.md                             # This file
├── references/
│   ├── error_and_resilience.md           # Errors, validation, timeouts, retry+jitter, circuit breaker, shutdown
│   ├── database_and_caching.md           # Pooling, transactions, replicas, prepared stmts, cache stampede
│   ├── api_design.md                     # Versioning, pagination, status codes, envelope, rate limiting
│   └── security_and_observability.md     # Secrets, authn/authz, logging, RED metrics, tracing, health checks
└── scripts/
    ├── service_scaffolder.py             # Scaffold Express / FastAPI service with resilience defaults
    ├── healthcheck_scaffolder.py         # Generate liveness / readiness / startup probes
    └── api_auditor.py                    # Scan a service, grade it A–F, list gaps by severity
```

### Installation

```bash
unzip backend-craft.skill -d /path/to/your/project/.claude/skills/
```

### Scripts

```bash
# Scaffold a service (default: express)
python scripts/service_scaffolder.py my-service --framework express
python scripts/service_scaffolder.py my-service --framework fastapi --features auth,ratelimit

# Generate health-check endpoints
python scripts/healthcheck_scaffolder.py --framework express --out src/routes/health.js

# Audit an existing service for production-readiness gaps
python scripts/api_auditor.py ./service --verbose
```

The auditor flags: hardcoded secrets, string-interpolated SQL, leaked stack traces, calls with no timeout, fixed-delay retries, `SELECT *`, unpaginated lists, and missing rate limiting. It's heuristic — it flags candidates for review, not proof of a bug. Requires Python 3.8+.

`--features auth,ratelimit` generates runnable stub files (auth middleware/dependency and an in-memory rate limiter) wired to the service's error envelope — print output includes the one-line mount snippet for each. Express scaffolds pin Express 5 (the current default on npm) and declare Node 18+.

### What changed in the refactor

The original `Backend` skill was a single flat `SKILL.md` of bullet points — good content, but the agent could only *read* it. This version adds: activation triggers, a routed workflow, four layered references with runnable code examples, three executable scripts, a self-audit checklist, an output contract, and guardrails.

---

## Tiếng Việt

### Skill này làm gì

Biến AI agent thành một senior backend engineer không chỉ *biết* best practice mà còn *làm* được — scaffold service với các default về resilience đã wire sẵn, và audit code hiện có để tìm gap production-readiness.

### Workflow

1. **Classify** — phân loại request: `scaffold` | `resilience` | `api-design` | `data` | `security` | `observability` | `review`.
2. **Load reference phù hợp** (xem bên dưới).
3. **Chạy script** khi task cụ thể (scaffold / health check / audit).
4. **Self-audit** theo checklist production-readiness.
5. **Emit một artifact** + bước tiếp theo giá trị nhất.

### Cấu trúc

```
backend-craft/
├── SKILL.md                              # Bộ điều phối: workflow, self-audit, guardrails
├── _meta.json                            # Metadata
├── README.md                             # File này
├── references/
│   ├── error_and_resilience.md           # Error, validation, timeout, retry+jitter, circuit breaker, shutdown
│   ├── database_and_caching.md           # Pooling, transaction, replica, prepared stmt, cache stampede
│   ├── api_design.md                     # Versioning, pagination, status code, envelope, rate limit
│   └── security_and_observability.md     # Secrets, authn/authz, logging, RED metrics, tracing, health check
└── scripts/
    ├── service_scaffolder.py             # Scaffold service Express / FastAPI với resilience mặc định
    ├── healthcheck_scaffolder.py         # Sinh probe liveness / readiness / startup
    └── api_auditor.py                    # Quét service, chấm điểm A–F, liệt kê gap theo mức độ
```

### Cài đặt

```bash
unzip backend-craft.skill -d /path/to/your/project/.claude/skills/
```

### Scripts

```bash
# Scaffold service (mặc định: express)
python scripts/service_scaffolder.py my-service --framework express
python scripts/service_scaffolder.py my-service --framework fastapi --features auth,ratelimit

# Sinh endpoint health-check
python scripts/healthcheck_scaffolder.py --framework express --out src/routes/health.js

# Audit service hiện có để tìm gap production-readiness
python scripts/api_auditor.py ./service --verbose
```

Auditor phát hiện: secret hardcode, SQL nối chuỗi, stack trace lộ ra client, call không có timeout, retry delay cố định, `SELECT *`, list không phân trang, và thiếu rate limit. Đây là heuristic — nó *đánh dấu để review*, không phải bằng chứng chắc chắn của bug. Yêu cầu Python 3.8+.

`--features auth,ratelimit` sinh ra các file stub chạy được (auth middleware/dependency và rate limiter in-memory) đã wire sẵn với error envelope của service — output in kèm dòng mount cho từng feature. Scaffold Express pin Express 5 (default hiện tại trên npm) và khai báo Node 18+.

### Đã thay đổi gì trong lần refactor

Skill `Backend` gốc chỉ là một file `SKILL.md` phẳng gồm các gạch đầu dòng — nội dung tốt, nhưng agent chỉ *đọc* được. Bản này thêm: activation triggers, workflow có routing, bốn reference phân lớp kèm code chạy được, ba script thực thi, checklist self-audit, output contract, và guardrails.

---

## License / Giấy phép

Use freely within your projects. / Dùng tự do trong các project của bạn.
