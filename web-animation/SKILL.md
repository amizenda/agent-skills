---
name: web-animation
description: Production-ready web animation patterns — scroll-linked, scroll-triggered, entrance, parallax, horizontal pin, gesture, and layout animations. Use this skill whenever the user wants to add motion to a page, build scroll animations, create a landing page with effects, implement parallax or pin+scrub sections, compare animation libraries (Motion/GSAP/CSS), debug janky animations, or optimize animation performance. Also trigger when the user references sites like Halston, Awwwards, or asks "how do they do that scroll effect." Covers vanilla JS, Motion (Framer Motion), GSAP ScrollTrigger, and CSS scroll-timeline. Includes a pattern catalog with copy-paste code, a decision tree for picking techniques, and a performance checklist.
---

# Web Animation

Production scroll, entrance, and interaction animation patterns. From "fade this in" to "pin a section and scrub 5 cards horizontally while drawing an SVG path."

## When to use this skill

- User wants scroll animations (reveal, parallax, pin+scrub, horizontal scroll)
- User wants entrance/exit animations (stagger, fade, slide, scale)
- User wants gesture animations (hover, tap, drag)
- User wants to replicate an effect from a reference site
- User asks "how do they do that" about any motion effect
- User needs to pick between Motion, GSAP, CSS, or vanilla JS
- User wants to optimize animation performance or fix jank
- User is building a landing page, portfolio, or marketing site with motion

## Decision tree — pick the right technique

```
What does the user want?
│
├─ Element appears when scrolling into view
│  └─ SCROLL-TRIGGERED REVEAL → references/scroll-patterns.md #reveals
│     Tool: IntersectionObserver / Motion whileInView / GSAP ScrollTrigger toggleActions
│
├─ Animation progress tied to scroll position (scrub)
│  └─ SCROLL-LINKED → references/scroll-patterns.md #scroll-linked
│     ├─ Horizontal scroll (cards slide sideways) → #horizontal-pin
│     ├─ Parallax (layers at different speeds) → #parallax
│     ├─ Path animation (element follows a path) → #path-follow
│     ├─ Progress bar / counter tied to scroll → #progress
│     └─ Pin section while animating inside → #pin-scrub
│     Tool: GSAP ScrollTrigger scrub / Motion useScroll+useTransform / CSS scroll-timeline
│
├─ Elements animate on page load
│  └─ ENTRANCE ANIMATION → references/entrance-patterns.md
│     ├─ Stagger cascade (items appear one by one)
│     ├─ Hero sequence (tag → title → subtitle → CTA)
│     └─ Count-up numbers
│     Tool: CSS @keyframes / Motion initial+animate / GSAP timeline
│
├─ User hovers, clicks, or drags
│  └─ GESTURE/INTERACTION → references/interaction-patterns.md
│     ├─ Hover reveal (image clip-path, underline scale)
│     ├─ Press/tap feedback (scale down)
│     ├─ Drag to reorder
│     └─ Cursor-follow effects
│     Tool: Motion whileHover/whileTap/whileDrag / CSS :hover / GSAP
│
├─ Element changes position/size in layout
│  └─ LAYOUT ANIMATION → Motion layout / GSAP Flip
│     Tool: Motion (clear winner here)
│
├─ Element mounts/unmounts with animation
│  └─ EXIT ANIMATION → Motion AnimatePresence (unique capability)
│     Tool: Motion (only library that handles this declaratively)
│
├─ Accordion expand/collapse
│  └─ HEIGHT ANIMATION → references/advanced-patterns.md #accordion
│     Tool: Motion AnimatePresence / vanilla JS scrollHeight trick
│
├─ Infinite scrolling text/logos
│  └─ MARQUEE → references/advanced-patterns.md #marquee
│     Tool: CSS @keyframes translateX(-50%) (zero JS preferred)
│
├─ Nav hides on scroll down, shows on scroll up
│  └─ STICKY NAV → references/advanced-patterns.md #sticky-nav
│     Tool: vanilla JS scroll delta / GSAP ScrollTrigger direction
│
├─ Image grid with staggered sizes/offsets
│  └─ MASONRY REVEAL → references/advanced-patterns.md #masonry-grid
│     Tool: CSS Grid + IntersectionObserver / GSAP clip-path
│
├─ Two columns reveal with different animations
│  └─ SPLIT REVEAL → references/advanced-patterns.md #split-reveal
│     Tool: GSAP (clip-path + translateY) / Motion
│
├─ Cards expand to show more content on click
│  └─ EXPANDABLE CARDS → references/advanced-patterns.md #expandable-cards
│     Tool: Motion layout + AnimatePresence / vanilla JS height
│
├─ Service list with image following cursor on hover
│  └─ HOVER IMAGE PREVIEW → references/advanced-patterns.md #solution-cards
│     Tool: vanilla JS mousemove + fixed image
│
└─ SVG path draws itself on scroll
   └─ LINE DRAW → references/advanced-patterns.md #line-draw
      Tool: strokeDashoffset + IntersectionObserver / scroll-linked
```

## Library selection — when to use what

Read `references/library-comparison.md` for full API comparison. Quick decision:

### Motion (formerly Framer Motion)
**Use when:** React project + UI transitions + layout animations + gesture + exit animations.
**Sweet spot:** Component-level micro-interactions, page transitions, drag-to-reorder, modal enter/exit, shared layout animations.
**Don't use for:** Complex multi-element timeline sequences, pinned scroll sections (possible but awkward), non-React projects.

```bash
npm install motion
```
```jsx
import { motion } from "motion/react"
```

### GSAP + ScrollTrigger
**Use when:** Complex scroll choreography, pin+scrub, horizontal scroll galleries, SVG morphing, text splitting, timeline sequences across many elements.
**Sweet spot:** Marketing sites, agency portfolios, Awwwards-level scroll experiences, anything where scroll drives the animation.
**Don't use for:** Simple UI state transitions (overkill), React layout animations (Motion does it better).

```bash
npm install gsap
```
```js
import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"
gsap.registerPlugin(ScrollTrigger)
```

### CSS only
**Use when:** Simple hover effects, entrance fades, loading spinners, reduced-motion fallbacks, or when zero-JS is a requirement.
**Sweet spot:** `:hover` transitions, `@keyframes` loops, `animation-timeline: scroll()` (Chrome/Edge/Safari 26+; Firefox behind a flag).
**Don't use for:** Complex sequencing, scroll-linked with pin, or scroll-timeline in Firefox without an `@supports` fallback (it ships in Chrome/Edge/Safari 26+ but is still behind a flag in Firefox).

### Vanilla JS
**Use when:** No framework, lightweight pages, custom scroll logic, or learning fundamentals.
**Sweet spot:** IntersectionObserver reveals, requestAnimationFrame parallax, simple counter animations.
**Don't use for:** Production React apps (use Motion), complex timelines (use GSAP).

### Combining libraries
Motion + GSAP in the same project is valid and common:
- Motion for UI components (modals, tooltips, layout shifts, gesture)
- GSAP ScrollTrigger for scroll-driven marketing sections (pin, scrub, horizontal)
- Keep them on separate DOM trees — don't let both animate the same element

## Pattern catalog — quick reference

Each pattern below has a one-liner showing the concept. Full implementation with options in the referenced file.

### Scroll-triggered reveal (most common)
```jsx
// Motion
<motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true }} transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }} />

// GSAP
gsap.from(".card", { y: 40, opacity: 0, stagger: 0.1,
  scrollTrigger: { trigger: ".cards", start: "top 80%" } })

// Vanilla JS
new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible') })
}, { threshold: 0.2 }).observe(element)
```

### Horizontal scroll pin (Halston-style)
```js
// GSAP — the gold standard for this pattern
gsap.to(".track", {
  xPercent: -100 * (cards.length - 1) / cards.length,
  ease: "none",
  scrollTrigger: {
    trigger: ".wrapper",
    pin: true,
    scrub: 1,
    end: () => "+=" + document.querySelector(".track").scrollWidth, // full impl uses scrollWidth - innerWidth for exact travel — see scroll-patterns.md
  }
})

// Vanilla JS fallback — see references/scroll-patterns.md #horizontal-pin-vanilla
```

### Parallax layers
```jsx
// Motion
const { scrollYProgress } = useScroll()
const y1 = useTransform(scrollYProgress, [0, 1], [0, -200])  // slow
const y2 = useTransform(scrollYProgress, [0, 1], [0, -400])  // fast

// CSS — wrap in @supports for progressive enhancement (see scroll-patterns.md)
.layer {
  animation: parallax linear;
  animation-timeline: scroll();
  animation-duration: 1ms; /* Firefox requires a non-zero duration to apply it */
}
@keyframes parallax { to { transform: translateY(-200px); } }
```

### Stagger entrance
```jsx
// Motion variants
const container = { visible: { transition: { staggerChildren: 0.08 } } }
const item = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

<motion.div variants={container} initial="hidden" animate="visible">
  {items.map(i => <motion.div key={i} variants={item} />)}
</motion.div>
```

### Count-up number
```js
function countUp(el, target, duration = 1500) {
  const start = performance.now()
  ;(function tick(now) {
    const t = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - t, 3)  // ease-out cubic
    el.textContent = Math.round(target * eased)
    if (t < 1) requestAnimationFrame(tick)
  })(start)
}
```

### Infinite marquee (CSS-only)
```css
.marquee-track {
  display: inline-flex;
  animation: marquee 20s linear infinite;
}
@keyframes marquee { to { transform: translateX(-50%); } }
/* Content must be duplicated inside .marquee-track for seamless loop */
```

### Accordion expand/collapse
```tsx
// Motion — smooth height:auto animation
<AnimatePresence>
  {isOpen && (
    <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }}
      exit={{ height: 0 }} style={{ overflow: 'hidden' }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }} />
  )}
</AnimatePresence>
```

### Sticky nav — hide/show
```js
// rAF-gated; hide when scrolling down (past 80px), show when scrolling up
let lastY = 0, ticking = false
window.addEventListener('scroll', () => {
  if (ticking) return
  ticking = true
  requestAnimationFrame(() => {
    const y = window.scrollY
    if (Math.abs(y - lastY) > 6)  // ignore sub-pixel jitter
      nav.style.transform = (y > lastY && y > 80) ? 'translateY(-100%)' : 'translateY(0)'
    lastY = y
    ticking = false
  })
}, { passive: true })
```

### Masonry image grid with clip-path reveal
```js
gsap.from('.mosaic-item', {
  clipPath: 'inset(100% 0 0 0)',
  stagger: 0.15, duration: 1, ease: 'power3.inOut',
  scrollTrigger: { trigger: '.mosaic', start: 'top 80%' }
})
```

### Hover image preview (cursor-following)
```js
row.addEventListener('mousemove', (e) => {
  preview.style.top = e.clientY + 'px'
  preview.style.left = e.clientX + 'px'
})
// preview: position:fixed, pointer-events:none, transform:translate(-50%,-50%)
```

→ Full pattern implementations: `references/scroll-patterns.md`, `references/entrance-patterns.md`, `references/interaction-patterns.md`

## Performance rules — non-negotiable

Read `references/performance.md` for the full checklist. Critical rules:

1. **Only animate `transform` and `opacity`** — these are composited on the GPU. Animating `width`, `height`, `margin`, `padding`, `top`, `left` causes layout thrashing and jank. Use `transform: translateX/Y/scale/rotate` instead.

2. **Use `will-change` sparingly** — only on elements that are about to animate. Remove after animation completes. Never set `will-change: transform` on 50 elements simultaneously.

3. **Throttle scroll handlers** — always use `requestAnimationFrame` gating or `passive: true` event listeners. Never do DOM reads inside a scroll handler without batching.

4. **`position: sticky` over JS pin** — when possible, use CSS `position: sticky` for pinning instead of JS-based pinning. Lower overhead, smoother, no layout recalc.

5. **Respect `prefers-reduced-motion`** — wrap all motion in `@media (prefers-reduced-motion: no-preference)` or check `window.matchMedia('(prefers-reduced-motion: reduce)')`. Motion provides this automatically.

6. **Lazy-init scroll animations** — don't create 50 ScrollTrigger instances on page load. Use IntersectionObserver to lazily create them when sections approach the viewport.

7. **Keep stagger counts reasonable** — staggering 100 items causes 100 simultaneous animations. Cap visible stagger groups at 6-8 items max.

8. **Test on mobile** — animations that feel smooth on a MacBook Pro will drop frames on mid-range Android. Profile on real devices or throttle CPU in DevTools.

## Architecture — where animation lives in code

```
src/
├── animations/
│   ├── variants.ts          # Motion variant definitions (reusable)
│   ├── scroll-config.ts     # ScrollTrigger configs
│   └── utils.ts             # easing functions, countUp, lerp
├── components/
│   ├── ScrollReveal.tsx      # Wrapper: fade-in on scroll
│   ├── HorizontalScroll.tsx  # Pin + scrub horizontal section
│   ├── Parallax.tsx          # Parallax layer wrapper
│   └── StaggerGrid.tsx       # Grid with staggered children
├── hooks/
│   ├── useScrollProgress.ts  # Custom scroll progress for a section
│   └── useCountUp.ts         # Count-up animation hook
└── lib/
    └── gsap.ts               # GSAP plugin registration (single file)
```

**Rules:**
- Register GSAP plugins once in a single file, import everywhere
- Create reusable wrapper components (`<ScrollReveal>`, `<Parallax>`) instead of repeating animation props
- Define Motion variants in a shared file, not inline
- Clean up GSAP timelines and ScrollTriggers on unmount (`useGSAP` hook handles this)
- Never mix Motion and GSAP on the same DOM element

## Common easing functions

```
ease-out cubic:   [0.16, 1, 0.3, 1]     ← best for entrances (fast start, smooth stop)
ease-in-out:      [0.4, 0, 0.2, 1]      ← best for transitions between states
spring:           { type: "spring", stiffness: 300, damping: 24 }  ← natural feel
linear:           "none" / [0, 0, 1, 1]  ← only for scroll-linked (scrub)
```

**Never use `linear` for triggered animations** — it looks robotic. Always apply easing. Default to ease-out cubic for reveals.

## Reference files

Read these for full implementations with all options and edge cases:

| File | When to read |
|------|-------------|
| `references/scroll-patterns.md` | Any scroll animation (reveal, parallax, pin, horizontal, path) |
| `references/entrance-patterns.md` | Page-load sequences, stagger, hero animations, counters |
| `references/interaction-patterns.md` | Hover, tap, drag, cursor-follow, gesture animations |
| `references/advanced-patterns.md` | Accordion, marquee, masonry grid, sticky nav, split reveal, expandable cards, line draw |
| `references/library-comparison.md` | Choosing between Motion / GSAP / CSS / vanilla JS |
| `references/performance.md` | Optimizing animation performance, debugging jank |
