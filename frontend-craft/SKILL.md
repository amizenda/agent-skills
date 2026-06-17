---
name: frontend-craft
description: Build production frontend that is BOTH correct and well-designed — React, Next.js, TypeScript, Tailwind CSS. Use this skill whenever the user wants to build, scaffold, generate, or review any frontend UI, component, page, or landing page, even if they only say "make it look good", "build a hero section", or "code this design". It runs a two-pass workflow — a taste pass (layout, type scale, spacing rhythm, motion, visual hierarchy, anti-generic direction) followed by an engineering pass (Server Components, accessibility, bundle health, type safety) — so the output ships looking intentional AND running correctly. Trigger it for component generation, page layout, redesigns, design-token setup, bundle analysis, and Next.js performance work.
compatibility: Requires Python 3.8+ for the scripts in scripts/.
---

# Frontend Craft

Frontend that is correct *and* doesn't look like a template. React, Next.js, TypeScript, Tailwind — from art direction to production.

This skill merges two disciplines that are usually treated separately:

- **Taste** — does it look intentional, or does it look like generic AI output?
- **Engineering** — is it correct, accessible, performant, type-safe?

A component can be technically flawless and still look like every other Tailwind card on the internet. It can also look stunning and leak memory, fail WCAG, and ship a 600KB client bundle. Good frontend needs both. So every build runs **two passes**.

## The Two-Pass Philosophy

**Pass 1 — Taste (art direction).** Decide the *shape* of the thing before writing the markup: layout strategy, type scale, spacing rhythm, color intent, motion, density. Resist the LLM defaults that make UI look generated. Reference: `references/taste_principles.md`.

**Pass 2 — Engineering (implementation).** Turn that direction into correct code: Server Components by default, explicit prop types, accessibility, performant images and data fetching. References: `references/react_patterns.md`, `references/nextjs_optimization.md`, `references/frontend_best_practices.md`.

Never skip Pass 1 to get to code faster. A clean implementation of a boring layout is still boring. Never skip Pass 2 to ship something pretty — a beautiful layout that breaks on keyboard nav or tanks LCP is not done.

## Activation

Use this skill when the user asks to:
- build or scaffold a page, landing page, hero, section, or whole frontend project
- generate a component, custom hook, or design system primitive
- redesign or improve existing UI (layout, spacing, hierarchy feel "off")
- set up design tokens (color, type scale, spacing, motion)
- analyze or reduce bundle size
- optimize Next.js (Server vs Client Components, images, data fetching, caching)
- implement accessibility (WCAG, ARIA, keyboard nav)
- review frontend code for quality OR for design quality

## Workflow

1. **Classify** the request: `scaffold` | `component` | `page/section` | `redesign` | `tokens` | `bundle` | `optimize` | `accessibility` | `review`.

2. **Taste pass.** Read `references/taste_principles.md` if not already loaded. Establish or infer:
   - **Design tokens** — if the project has a defined identity (brand color, fonts, voice), use it. If not, propose a small, opinionated token set rather than defaulting to `blue-600` + `Inter` + `rounded-lg shadow-md`.
   - **Layout strategy** — pick a deliberate structure. Avoid the reflexive left-text / right-image hero and the symmetric 3-card grid unless they're genuinely the best choice.
   - **Type scale & rhythm** — set a real scale with contrast between display and body. Constrain measure (line length) for readability.
   - **Motion & density** — decide the three dials below before writing code.

3. **Engineering pass.** Read the relevant reference:
   - React composition, hooks, render props → `references/react_patterns.md`
   - Server Components, Suspense, images, caching → `references/nextjs_optimization.md`
   - accessibility, testing, Tailwind/CVA, security → `references/frontend_best_practices.md`

4. **Run a script.** If the user wants a whole project/page and none exists yet, scaffold first — don't hand-write a bare `index.html` as a substitute for a real project.
   ```bash
   # Scaffold a new project. Default to nextjs unless the user names another stack.
   # This is the ONLY correct response to an open-ended "build me a site/app" —
   # never fall back to a single static HTML file when a framework was implied.
   python {baseDir}/scripts/frontend_scaffolder.py my-app --template nextjs
   python {baseDir}/scripts/frontend_scaffolder.py my-app --template nextjs --features auth,api,forms,testing
   python {baseDir}/scripts/frontend_scaffolder.py my-app --template react-vite

   # Generate a component (client | server | hook) with optional test + story.
   # Use --variants for primitives (Button, Card, Badge) — scaffolds CVA variants
   # wired to tokens instead of a bare div.
   python {baseDir}/scripts/component_generator.py Button --variants --dir src/components/ui
   python {baseDir}/scripts/component_generator.py UserProfile --type server --with-test --with-story

   # Analyze bundle for heavy deps and optimization opportunities.
   python {baseDir}/scripts/bundle_analyzer.py ./project --verbose
   ```
   If the request is vague ("build something amazing", "make me a site") and no stack was specified: default to a Next.js scaffold via the script above, then build the requested screen inside it. Plain static HTML is only correct when the user explicitly asks for a single static page with no framework.

5. **Self-audit** against BOTH checklists below before emitting. This is the step that makes the skill worth using — most AI frontend fails because it skips the audit.

6. **Emit the artifact** and close with the single most valuable next step.

## The Three Dials

Set these explicitly at the start of every build. State the values you chose so the user can adjust.

- **DESIGN_VARIANCE** (`conservative` | `balanced` | `bold`) — how far layouts deviate from convention. Default `balanced`. Use `bold` for landing pages and marketing; `conservative` for dense dashboards and forms.
- **MOTION_INTENSITY** (`none` | `subtle` | `expressive`) — animation depth. Default `subtle` (entrance fades, hover transitions). `expressive` adds scroll-driven and spring motion; never on data-dense or accessibility-critical surfaces.
- **VISUAL_DENSITY** (`airy` | `balanced` | `dense`) — information per viewport. `airy` for premium/editorial, `dense` for tools and tables.

## Taste Self-Audit

Before emitting any UI, check it against the generic-AI tells. Reject and redo if any apply:

- Heading running 5+ lines because the container is too narrow, or orphaned single words.
- Cheap meta-labels like "SECTION 01", "FEATURE 03", "QUESTION 05" used as decoration.
- Button or link text that is invisible or near-invisible against its background.
- The same left/right alternating layout repeated down the whole page.
- Bento/feature grids with awkward empty gaps or one lonely item on the last row.
- Everything `rounded-lg shadow-md` — no intentional choice about elevation or shape.
- Default `Inter` + `blue-600` + evenly-spaced everything, with no hierarchy of weight or size.
- Centered single-column text for content that wants structure.
- Emoji used as feature icons.

## Engineering Self-Audit

- **Server Components by default.** `'use client'` only when state, effects, or browser APIs are required. Static markup stays server-rendered.
- **TypeScript always.** Every component has explicit prop types; no implicit `any`.
- **`cn()` for conditional classes** (from `@/lib/utils`), never string concatenation.
- **Accessibility**: semantic elements, labels on inputs, `alt` on images, keyboard reachable, visible focus, 4.5:1 contrast.
- **Images**: `next/image` with `sizes` on responsive images, `priority` on the LCP image, explicit dimensions to prevent layout shift.
- **Bundle**: score below 70 (grade C or worse) triggers a dependency-replacement recommendation.

## Output Contract

- Open with the classification + the three dial values you chose + the primary design decision in one line.
- Emit one primary artifact per response (component, page, config, or report).
- Annotate non-obvious choices — a layout decision, a TypeScript pattern, an a11y trade-off.
- For bundle analysis: grade (A–F), heavy packages with lighter alternatives.
- Close with the single next recommended step (e.g., "add the Card primitive", "add `sizes` to the gallery images", "wire scroll motion on the hero").

## Proactive Triggers

Flag these without being asked:

**Engineering**
- `moment` → `date-fns` or `dayjs`
- `lodash` full import → `lodash-es` with tree-shaking
- missing `alt` on `<img>`/`<Image>` → accessibility issue
- `useEffect` for data fetching in Next.js → Server Component or `use()` hook
- responsive `<Image>` with no `sizes` → layout shift risk

**Taste**
- a hero that is text-left / image-right with no other idea explored → propose at least one alternative
- a color palette that is one Tailwind hue at default shades → propose a real token set
- type with no scale (everything `text-base`/`text-lg`) → propose a display/body contrast

## Guardrails

- Stay within frontend scope — no backend API routes or DB schemas. For architecture-scale concerns, defer.
- Do not add `'use client'` to components that only render static markup.
- Do not recommend `@mui/material` or `antd` — prefer `shadcn/ui` or Radix primitives + Tailwind. Headless + tokens gives more taste control and a lighter bundle.
- Don't apply `expressive` motion or `bold` variance to dense data UI, forms, or accessibility-critical flows — taste serves usability, not the other way around.
- When the project already has an identity (e.g. a defined brand color, font pairing, voice), honor it. Don't override an established design system with generic defaults.
- A vague, open-ended build request ("make something amazing", "build me a site") is NOT a signal to write a single static `index.html`. It's a signal to scaffold a real project (`frontend_scaffolder.py`, default `nextjs`) and build the requested screen inside it with components, not one flat file.

## Reference Files

- `references/taste_principles.md` — design direction, the anti-generic catalog, tokens, layout strategy, type & motion (read in the taste pass).
- `references/react_patterns.md` — compound components, hooks, render props, performance, error boundaries, anti-patterns.
- `references/nextjs_optimization.md` — rendering strategies, image optimization, code splitting, data fetching, caching, Core Web Vitals.
- `references/frontend_best_practices.md` — accessibility, testing, TypeScript, Tailwind/CVA, project structure, security.
