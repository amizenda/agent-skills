# Taste Principles

Design direction for frontend that looks intentional, not generated. This is the reference for the **taste pass** — read it before deciding layout, type, color, or motion.

The premise: LLMs have strong, predictable biases that make UI look "AI-built." This file names those biases so you can break them on purpose, and gives a positive framework for what to do instead.

---

## Table of Contents

- [The Anti-Generic Catalog](#the-anti-generic-catalog)
- [Design Tokens](#design-tokens)
- [Layout Strategy](#layout-strategy)
- [Type Scale & Rhythm](#type-scale--rhythm)
- [Color & Elevation](#color--elevation)
- [Motion](#motion)
- [Direction Presets](#direction-presets)

---

## The Anti-Generic Catalog

These are the specific failure modes that make AI frontend recognizable. Audit every screen against this list.

**Layout tells**
- Reflexive text-left / image-right hero, repeated for every section down the page.
- Symmetric 3-card feature grid as the default answer to "show some features."
- Everything centered in a single narrow column when the content wants structure.
- Bento grids with awkward gaps, or a last row with one orphaned item.
- Equal visual weight everywhere — nothing is clearly the most important thing on screen.

**Typography tells**
- `Inter` (or system sans) at `text-base` everywhere, no scale.
- Headings with no contrast in weight or size against body text.
- Lines running the full container width (measure too long to read comfortably).
- Headings that wrap to 5+ lines or orphan a single word on the last line.
- Cheap meta-labels as decoration: "SECTION 01", "FEATURE 03", "QUESTION 05".

**Color & surface tells**
- One Tailwind hue at default shades (`blue-600`, `gray-100`) and nothing else.
- Every surface `rounded-lg shadow-md` — no intentional elevation system.
- Low-contrast button text that's hard or impossible to read.
- Gradients used as a substitute for an actual idea.

**Content tells**
- Emoji as feature icons.
- Lorem-ipsum-flavored filler copy that says nothing.
- Placeholder images with no aspect-ratio intent.

The fix is never "add more decoration." It's making fewer, more deliberate choices.

---

## Design Tokens

Before any markup, establish a small token set. If the project has an identity, use it. If not, propose one — opinionated beats default.

**Honor an existing identity first.** If the project defines a brand color, font pairing, and voice, those ARE the tokens. Example of a well-defined identity (do not reuse for unrelated projects — it's an illustration of the shape):

```
brand color:  a single strong primary (e.g. #0052FF) + neutral ramp
type:         a display/mono pairing (e.g. Sora display + IBM Plex Mono accents)
voice:        lowercase, sharp, no hashtags — reflected in copy and labels
shape:        consistent radius + a real elevation scale, not reflexive shadow-md
```

**When proposing fresh tokens**, define at minimum:

```css
/* Color: one primary with intent, a neutral ramp, semantic states */
--color-primary:        /* a committed hue, not blue-600 by reflex */
--color-fg:             /* near-black, not pure #000 */
--color-fg-muted:       /* meets 4.5:1 on background */
--color-bg:
--color-surface:        /* elevated surface, distinct from bg */

/* Type: a real scale with display/body contrast */
--font-display:
--font-body:
--text-xs … --text-5xl  /* a ratio-based scale, e.g. 1.25 */

/* Space: a rhythm, not random px values */
--space-1 … --space-16  /* consistent step, e.g. 4px base */

/* Shape: deliberate radius + elevation */
--radius:               /* pick one and commit; not a mix */
--elevation-1 … -3:     /* a system, used to signal hierarchy */
```

Map these into `tailwind.config` as theme extensions so components consume tokens, not hard-coded values.

---

## Layout Strategy

Pick structure deliberately. A few patterns that beat the defaults:

- **Asymmetry with intent** — offset the focal point; let one element dominate. Equal columns read as "didn't decide."
- **Editorial grid** — a real column grid with content spanning different widths, the way print does. Not everything 1/3.
- **Anchored hero** — one clear focal element (oversized type, a single product shot, a live demo) rather than the text-left/image-right reflex.
- **Density contrast between sections** — an airy hero, then a denser proof section, then breathing room again. Rhythm comes from variation.
- **Constrained measure** — body text at 60–75 characters per line regardless of container width (`max-w-prose` or an explicit `ch` width).

Match structure to `DESIGN_VARIANCE`: `conservative` stays close to convention (dashboards, forms); `bold` experiments (landing, marketing).

---

## Type Scale & Rhythm

- Set a **modular scale** (e.g. 1.2–1.333 ratio) so sizes relate to each other instead of being arbitrary.
- Create **contrast** between display and body — in size *and* weight. A bold 48px display over 16px regular body reads as designed; 20px over 16px reads as flat.
- Constrain **measure** for readability — long lines are the single most common AI typography mistake.
- Use **weight and spacing** for hierarchy before reaching for color or boxes.
- Tighten **leading** on large display text (`leading-tight`), loosen on body (`leading-relaxed`).

---

## Color & Elevation

- Commit to a **primary** with a reason, not a reflex. A neutral ramp does most of the work; the primary is a punctuation, not the whole sentence.
- Avoid pure `#000` / `#fff` — slightly tinted near-black and off-white feel more crafted and reduce eye strain.
- Build an **elevation system** (a small set of shadow/border/background steps) and use it to signal hierarchy. `shadow-md` on everything signals nothing.
- Always verify **contrast** — 4.5:1 for body text (this is also an engineering requirement; taste and a11y agree here).

---

## Motion

Motion calibrated by `MOTION_INTENSITY`:

- `none` — no animation. Correct for some dense tools and accessibility-first contexts.
- `subtle` (default) — entrance fades/slides on first paint, hover/active transitions on interactive elements, 150–300ms, ease-out. Respect `prefers-reduced-motion`.
- `expressive` — scroll-driven reveals, spring physics, staggered entrances. Reserve for marketing/landing. Never on forms, tables, or data-critical surfaces.

Rules that always hold:
- Animate `transform` and `opacity`, not layout properties (avoids reflow/jank).
- Always honor `prefers-reduced-motion: reduce`.
- Motion should direct attention or give feedback — never decoration for its own sake.

---

## Direction Presets

Quick starting points. Each sets the three dials and a token posture.

**Minimalist / editorial** (Notion, Linear vibe)
`VARIANCE: balanced · MOTION: subtle · DENSITY: airy`
Restrained palette, generous whitespace, strong type hierarchy, near-monochrome with one accent.

**High-end / premium**
`VARIANCE: bold · MOTION: expressive · DENSITY: airy`
Large display type, lots of negative space, spring motion, considered imagery, calm pace.

**Industrial / technical** (developer-tool vibe)
`VARIANCE: bold · MOTION: subtle · DENSITY: balanced`
Mono accents, sharp contrast, grid visible as a design element, data-forward.

**Dashboard / tool**
`VARIANCE: conservative · MOTION: subtle · DENSITY: dense`
Information first, predictable layout, motion only for feedback, elevation to separate zones.

Pick the closest preset, then adjust the dials to fit the specific brief.
