# Animation Performance

Checklist and debugging guide for smooth 60fps animations.

## The golden rules

### 1. Only animate composite properties
```
✅ GPU-composited (fast):     transform, opacity, filter
❌ Layout-triggering (slow):  width, height, top, left, margin, padding, border
❌ Paint-triggering (slow):   background-color, box-shadow, border-radius changes
```

Instead of animating `width` or `left`:
```css
/* ❌ Causes layout recalculation every frame */
.box { left: 0; transition: left 0.3s; }
.box.active { left: 200px; }

/* ✅ GPU-composited, no layout recalc */
.box { transform: translateX(0); transition: transform 0.3s; }
.box.active { transform: translateX(200px); }
```

### 2. Throttle scroll handlers
```js
/* ❌ Fires 60+ times per second, blocks main thread */
window.addEventListener('scroll', () => {
  element.style.transform = `translateY(${window.scrollY * 0.5}px)`
})

/* ✅ Batched in rAF, passive listener */
let ticking = false
window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      element.style.transform = `translateY(${window.scrollY * 0.5}px)`
      ticking = false
    })
    ticking = true
  }
}, { passive: true })
```

### 3. Use will-change wisely
```css
/* ❌ Too many elements promoted to GPU layers */
* { will-change: transform; }

/* ❌ Permanent will-change wastes GPU memory */
.card { will-change: transform; }

/* ✅ Apply only when animation is imminent */
.card:hover { will-change: transform; }

/* ✅ Or via JS, removed after animation */
el.style.willChange = 'transform'
el.addEventListener('transitionend', () => {
  el.style.willChange = 'auto'
}, { once: true })
```

### 4. CSS position: sticky over JS pinning
```css
/* ✅ Browser-native, zero JS overhead */
.sticky-section {
  position: sticky;
  top: 0;
  height: 100vh;
}

/* ❌ JS-based pinning (GSAP pin does this) adds overhead:
   - Measures scroll position every frame
   - Clones element for space preservation
   - Can cause CLS (Cumulative Layout Shift) */
```

Use GSAP `pin: true` only when you need the timeline scrub behavior that sticky alone can't provide.

### 5. Lazy-init animations
```js
/* ❌ Creates 50 ScrollTrigger instances on page load */
document.querySelectorAll('.card').forEach(card => {
  gsap.from(card, { opacity: 0, scrollTrigger: { trigger: card } })
})

/* ✅ Create ScrollTriggers only when section approaches */
const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return
    // Now create the ScrollTrigger
    initSectionAnimations(entry.target)
    sectionObserver.unobserve(entry.target)
  })
}, { rootMargin: '200px' })  // 200px before viewport

document.querySelectorAll('section').forEach(s => sectionObserver.observe(s))
```

## Reduced motion — accessibility

### CSS
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### JavaScript check
```js
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

if (prefersReducedMotion) {
  // Skip animation setup entirely, or use instant transitions
  gsap.globalTimeline.timeScale(100)  // GSAP: make everything instant
}

// Motion handles this automatically for most animations
```

### Best practice
- Don't just disable all animation — reduce, simplify, or replace with fades
- Essential state changes (loading → loaded) should still have visual feedback
- Decorative parallax and scroll effects can be fully removed
- Focus indicators and hover states should remain

## Debugging jank

### Chrome DevTools workflow
1. **Performance tab** → Record → Scroll through page → Stop
2. Look for **red triangles** (long tasks) and **green bars below 60fps**
3. Click on a long frame → see which functions took the most time
4. **Layers panel** (More Tools → Layers) → see which elements have GPU layers

### Common jank causes and fixes
```
Symptom                          Cause                           Fix
──────────────────────────────────────────────────────────────────────────
Scroll feels sluggish            Non-passive scroll listener     Add { passive: true }
Animation stutters on scroll     Layout property animation       Switch to transform/opacity
Page jumps when section pins     No space preserved for pin      GSAP pinSpacing:true, or manual height
Images flash during scroll       No will-change on animated img  Add will-change: transform
Mobile drops frames              Too many simultaneous anims     Reduce stagger count, simplify
Text blurry during animation     Subpixel rendering              Use translate3d(0,0,0) to force layer
CLS score penalty                Animation changes layout        Preserve space with min-height/aspect-ratio
```

### Performance budget
```
Target: 60fps = 16.6ms per frame budget
├─ JS execution:    < 6ms
├─ Style recalc:    < 2ms
├─ Layout:          < 2ms (ideally 0 if only animating transform/opacity)
├─ Paint:           < 2ms
└─ Composite:       < 2ms

If any single category exceeds its budget → investigate
If total exceeds 16.6ms → frames will drop
```

## Mobile-specific optimizations

1. **Reduce parallax intensity** — `speed * 0.5` on mobile (less GPU work, less motion sickness)
2. **Disable cursor-follow effects** — no cursor on touch devices
3. **Simplify stagger** — reduce from 8 items to 4 visible at once
4. **Use CSS transforms over JS** — CSS animations can run on compositor thread even when main thread is busy
5. **Test with CPU throttling** — DevTools → Performance → CPU 4x slowdown
6. **Avoid `backdrop-filter: blur()`** on animated elements — extremely expensive on mobile GPUs
7. **IntersectionObserver over scroll events** — IO runs off main thread

## Bundle size optimization

```js
// ❌ Import everything
import { motion, AnimatePresence, useScroll, useTransform,
  useMotionValue, useSpring, useInView, Reorder } from "motion/react"

// ✅ Import only what you use (tree-shaking)
import { motion } from "motion/react"
import { useScroll, useTransform } from "motion/react"

// GSAP — import only needed plugins
import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"
// Don't import Draggable, MorphSVG, etc. unless used
```
