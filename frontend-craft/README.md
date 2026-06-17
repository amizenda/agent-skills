# frontend-craft

> Production frontend that is **both correct and well-designed** — React, Next.js, TypeScript, Tailwind CSS.
> Frontend production vừa **đúng kỹ thuật vừa đẹp có chủ đích** — React, Next.js, TypeScript, Tailwind CSS.

A Claude Skill that merges two disciplines usually kept apart: **design taste** (does it look intentional, or generated?) and **engineering correctness** (is it accessible, performant, type-safe?). Every build runs a **two-pass workflow** so the output ships looking deliberate *and* running correctly.

Một Claude Skill kết hợp hai thứ thường bị tách rời: **thẩm mỹ** (trông có chủ đích, hay giống AI sinh ra?) và **độ đúng kỹ thuật** (accessible, nhanh, type-safe?). Mỗi lần build chạy theo **quy trình 2 pass** để kết quả vừa trông được thiết kế *vừa* chạy đúng.

---

### What it does

`frontend-craft` combines the logic of two skills — a *taste* layer and a *senior-frontend* engineering layer — into one. A component can be technically flawless and still look like every other Tailwind card; it can also look stunning and fail accessibility. This skill forces both to pass.

### The two-pass workflow

1. **Taste pass (art direction)** — decide the *shape* before the markup: design tokens, layout strategy, type scale, spacing rhythm, color intent, motion. Resist the LLM defaults that make UI look generated. → `references/taste_principles.md`
2. **Engineering pass (implementation)** — turn that direction into correct code: Server Components by default, explicit prop types, accessibility, performant images and data fetching. → `references/react_patterns.md`, `nextjs_optimization.md`, `frontend_best_practices.md`

Never skip pass 1 (a clean build of a boring layout is still boring). Never skip pass 2 (a pretty layout that breaks keyboard nav is not done).

### The three dials

Set these at the start of every build and state the values so the user can adjust:

- **DESIGN_VARIANCE** — `conservative` | `balanced` | `bold` (how far layouts deviate from convention)
- **MOTION_INTENSITY** — `none` | `subtle` | `expressive` (animation depth)
- **VISUAL_DENSITY** — `airy` | `balanced` | `dense` (information per viewport)

### Structure

```
frontend-craft/
├── SKILL.md                          # The orchestrator: workflow, dials, self-audits
├── _meta.json                        # Metadata (slug, version)
├── README.md                         # This file
├── references/                       # Docs loaded into context as needed
│   ├── taste_principles.md           # Anti-generic catalog, tokens, layout, motion
│   ├── react_patterns.md             # Compound components, hooks, performance
│   ├── nextjs_optimization.md        # Server Components, images, caching, Web Vitals
│   └── frontend_best_practices.md    # Accessibility, testing, TypeScript, security
└── scripts/                          # Executable tools
    ├── frontend_scaffolder.py        # Scaffold a Next.js / React+Vite project
    ├── component_generator.py        # Generate components with CVA variants + tokens
    └── bundle_analyzer.py            # Grade bundle health (A–F)
```

### Installation

**Claude Code** — unzip into your project's skills folder:

```bash
unzip frontend-craft.skill -d /path/to/your/project/.claude/skills/
```

Or copy the unzipped `frontend-craft/` folder there directly.

### Scripts

```bash
# Scaffold a new project (default: nextjs)
python scripts/frontend_scaffolder.py my-app --template nextjs
python scripts/frontend_scaffolder.py my-app --template react-vite --features auth,forms

# Generate a component (use --variants for primitives like Button/Card)
python scripts/component_generator.py Button --variants --dir src/components/ui
python scripts/component_generator.py UserProfile --type server --with-test --with-story

# Analyze bundle health
python scripts/bundle_analyzer.py ./project --verbose
```

Requires Python 3.8+.

### Notes

- Format: **Claude Skills** (YAML frontmatter `name`/`description`). For the **Aeon** framework, adapt the frontmatter to Aeon's convention; references and scripts are reusable as-is.
- The `references/` and `scripts/` folder names must stay unchanged — `SKILL.md` references them by path (`{baseDir}/references/...`, `{baseDir}/scripts/...`).

---

### Skill này làm gì

`frontend-craft` gộp logic của hai skill — tầng *taste* (thẩm mỹ) và tầng *senior-frontend* (kỹ thuật) — làm một. Một component có thể hoàn hảo về kỹ thuật nhưng vẫn trông giống mọi Tailwind card khác; hoặc rất đẹp nhưng lại vỡ accessibility. Skill này ép cả hai chiều phải đạt.

### Quy trình 2 pass

1. **Taste pass (chỉ đạo nghệ thuật)** — quyết định *hình hài* trước khi viết markup: design tokens, chiến lược layout, type scale, nhịp spacing, ý đồ màu sắc, chuyển động. Chống lại các default khiến UI trông giống AI sinh ra. → `references/taste_principles.md`
2. **Engineering pass (triển khai)** — biến định hướng đó thành code đúng: Server Components mặc định, prop types rõ ràng, accessibility, image và data fetching tối ưu. → `references/react_patterns.md`, `nextjs_optimization.md`, `frontend_best_practices.md`

Đừng bỏ pass 1 (triển khai sạch một layout nhàm chán thì vẫn nhàm chán). Đừng bỏ pass 2 (layout đẹp mà vỡ điều hướng bàn phím thì chưa xong).

### Ba "núm chỉnh" (dials)

Đặt ngay đầu mỗi lần build và nêu rõ giá trị để người dùng điều chỉnh:

- **DESIGN_VARIANCE** — `conservative` | `balanced` | `bold` (độ lệch khỏi quy ước layout)
- **MOTION_INTENSITY** — `none` | `subtle` | `expressive` (độ sâu animation)
- **VISUAL_DENSITY** — `airy` | `balanced` | `dense` (mật độ thông tin trên màn hình)

### Cấu trúc

```
frontend-craft/
├── SKILL.md                          # Bộ điều phối: workflow, dials, self-audit
├── _meta.json                        # Metadata (slug, version)
├── README.md                         # File này
├── references/                       # Tài liệu nạp vào context khi cần
│   ├── taste_principles.md           # Catalog anti-generic, tokens, layout, motion
│   ├── react_patterns.md             # Compound components, hooks, performance
│   ├── nextjs_optimization.md        # Server Components, images, caching, Web Vitals
│   └── frontend_best_practices.md    # Accessibility, testing, TypeScript, security
└── scripts/                          # Công cụ chạy được
    ├── frontend_scaffolder.py        # Scaffold project Next.js / React+Vite
    ├── component_generator.py        # Sinh component với CVA variants + tokens
    └── bundle_analyzer.py            # Chấm điểm bundle (A–F)
```

### Cài đặt

**Claude Code** — giải nén vào thư mục skills của project:

```bash
unzip frontend-craft.skill -d /path/to/your/project/.claude/skills/
```

Hoặc copy thẳng folder `frontend-craft/` đã giải nén vào đó.

### Scripts

```bash
# Scaffold project mới (mặc định: nextjs)
python scripts/frontend_scaffolder.py my-app --template nextjs
python scripts/frontend_scaffolder.py my-app --template react-vite --features auth,forms

# Sinh component (dùng --variants cho primitive như Button/Card)
python scripts/component_generator.py Button --variants --dir src/components/ui
python scripts/component_generator.py UserProfile --type server --with-test --with-story

# Phân tích sức khỏe bundle
python scripts/bundle_analyzer.py ./project --verbose
```

Yêu cầu Python 3.8+.

### Lưu ý

- Định dạng: **Claude Skills** (frontmatter YAML `name`/`description`). Nếu dùng cho framework **Aeon**, cần chỉnh frontmatter theo convention của Aeon; phần references và scripts thì tái sử dụng nguyên.
- Tên hai folder `references/` và `scripts/` phải giữ nguyên — `SKILL.md` trỏ tới chúng bằng đường dẫn (`{baseDir}/references/...`, `{baseDir}/scripts/...`). Đổi tên là skill không tìm thấy.

---

## License / Giấy phép

Use freely within your projects. / Dùng tự do trong các project của bạn.
