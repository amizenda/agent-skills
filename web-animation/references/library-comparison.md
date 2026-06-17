# Library Comparison

Feature-by-feature comparison for animation library selection.

## Feature matrix

```
Feature                    Motion          GSAP            CSS             Vanilla JS
─────────────────────────────────────────────────────────────────────────────────────
Scroll-triggered reveal    ✅ whileInView  ✅ ScrollTrigger ⚠️ limited      ✅ IntObserver
Scroll-linked (scrub)      ✅ useScroll    ✅ scrub:true    ⚠️ scroll-tmln  ✅ manual
Horizontal pin scroll      ⚠️ awkward     ✅ pin+scrub     ❌              ⚠️ sticky hack
Pin section                ⚠️ no native   ✅ pin:true      ✅ sticky        ✅ sticky
Parallax                   ✅ useTransform ✅ ScrollTrigger ✅ scroll-tmln   ✅ manual
Entrance stagger           ✅ variants     ✅ stagger       ⚠️ delay only   ✅ setTimeout
Exit animation             ✅ AnimatePresence ⚠️ manual    ❌              ❌
Layout animation           ✅ layout prop  ⚠️ Flip plugin  ❌              ❌
Gesture (hover/tap/drag)   ✅ built-in     ⚠️ Draggable   ✅ CSS :hover    ✅ events
Spring physics             ✅ native       ⚠️ via plugin   ❌              ⚠️ manual
SVG morph                  ⚠️ basic d     ✅ MorphSVG     ❌              ❌
Text splitting             ⚠️ splitText   ✅ SplitText    ❌              ✅ manual
Timeline sequencing        ⚠️ limited     ✅ native       ✅ @keyframes    ⚠️ manual
React integration          ✅ native       ⚠️ useGSAP     ❌              ❌
Vue/Svelte/vanilla          ⚠️ motion/vue  ✅ any          ✅              ✅
Hardware-accelerated scroll ✅ ScrollTimeline ❌ JS polling ✅ native       ❌
─────────────────────────────────────────────────────────────────────────────────────
Bundle size (gzip)         ~30KB           ~23KB+plugins   0KB             0KB
License                    MIT             Free, all plugins†  N/A         N/A
```

> † **GSAP is 100% free as of April 2025.** Webflow (which acquired GreenSock in Oct 2024) made the entire library — including every previously paid "Club" plugin: SplitText, MorphSVG, DrawSVG, ScrollSmoother, Inertia, and the rest — free for all projects, **including commercial use**. There is no longer a paywall on SplitText/MorphSVG, and SplitText was rewritten ~50% smaller with built-in accessibility. So the only real cost trade-off vs. Motion or CSS is bundle size, not licensing.

## When to pick what

### React app with UI interactions → Motion
- Modal enter/exit, toast notifications, accordion expand
- Drag-to-reorder lists, shared element transitions
- Page route transitions, layout animations
- Hover/tap feedback on components

### Marketing site with scroll choreography → GSAP
- Pinned sections with timeline animations
- Horizontal scroll galleries (Halston-style)
- Text reveal with SplitText, SVG path drawing
- Multi-element orchestrated sequences

### Both in one project → Motion + GSAP
- Motion for React component-level UI (modals, tooltips, layout)
- GSAP for scroll-driven marketing sections (pin, scrub, horizontal)
- Rule: never animate the same element with both libraries

### Simple static page → CSS + vanilla JS
- Basic hover effects, loading spinners
- IntersectionObserver for scroll reveals
- CSS `animation-timeline: scroll()` for parallax (Chrome/Edge/Safari 26+; Firefox behind a flag)
- Smallest possible footprint

## Migration patterns

### Framer Motion → Motion (package rename)
```diff
- import { motion, AnimatePresence } from "framer-motion"
+ import { motion, AnimatePresence } from "motion/react"
```
API is identical. Only the import path changed.

### CSS → Motion
```diff
- /* CSS */
- .card { transition: transform 0.3s ease; }
- .card:hover { transform: scale(1.05); }

+ /* Motion */
+ <motion.div whileHover={{ scale: 1.05 }}
+   transition={{ duration: 0.3 }} />
```

### GSAP → Motion (scroll reveal)
```diff
- // GSAP
- gsap.from('.card', { y: 40, opacity: 0,
-   scrollTrigger: { trigger: '.card', start: 'top 80%' }
- })

+ // Motion
+ <motion.div initial={{ y: 40, opacity: 0 }}
+   whileInView={{ y: 0, opacity: 1 }}
+   viewport={{ once: true }}
+   transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }} />
```

## Install commands

```bash
# Motion (React)
npm install motion

# GSAP (any framework)
npm install gsap
npm install @gsap/react   # React hook

# React Spring (alternative for physics-based)
npm install @react-spring/web
```
