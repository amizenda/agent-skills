# Entrance Animation Patterns

Animations that play on page load or component mount.

## Table of contents
1. [Hero entrance sequence](#hero-sequence)
2. [Stagger cascade](#stagger)
3. [Count-up numbers](#count-up)
4. [Page/route transitions](#page-transitions)
5. [Loader to content](#loader-reveal)

---

## Hero entrance sequence {#hero-sequence}

Elements appear one after another with increasing delay. The most common landing page pattern.

### Vanilla JS — delay cascade
```js
function heroEntrance(selectors, baseDelay = 150) {
  selectors.forEach((sel, i) => {
    const el = document.querySelector(sel)
    if (!el) return
    setTimeout(() => {
      el.style.transition = 'opacity 0.8s ease, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)'
      el.style.opacity = '1'
      el.style.transform = 'translateY(0)'
    }, baseDelay * (i + 1))
  })
}

// CSS initial state:
// .hero-tag, .hero-title, .hero-sub, .hero-cta { opacity: 0; transform: translateY(24px); }

// Call after DOM ready
heroEntrance(['.hero-tag', '.hero-title', '.hero-sub', '.hero-cta'])
```

### Motion — orchestrated variants
```tsx
const heroVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.15, delayChildren: 0.3 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1, y: 0,
    transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] }
  }
}

function Hero() {
  return (
    <motion.section variants={heroVariants} initial="hidden" animate="visible">
      <motion.span variants={itemVariants} className="tag">premier base</motion.span>
      <motion.h1 variants={itemVariants}>meet <span>sam</span></motion.h1>
      <motion.p variants={itemVariants}>signal → narrative → leverage</motion.p>
      <motion.div variants={itemVariants} className="cta-group">
        <button>explore</button>
        <button>docs</button>
      </motion.div>
    </motion.section>
  )
}
```

### GSAP timeline
```js
const tl = gsap.timeline({ defaults: { ease: 'power3.out', duration: 0.8 } })

tl.from('.hero-tag',   { y: 24, opacity: 0 })
  .from('.hero-title', { y: 36, opacity: 0 }, '-=0.65')
  .from('.hero-sub',   { y: 20, opacity: 0 }, '-=0.6')
  .from('.hero-cta',   { y: 20, opacity: 0 }, '-=0.55')
  .from('.scroll-cue', { opacity: 0 }, '-=0.3')
```

### Timing guidelines
```
Element          Delay     Duration    Why
─────────────────────────────────────────────────
Eyebrow/tag      0.2s      0.7s       First visible, sets context
Headline         0.35s     0.8s       Primary focus, slightly longer
Subtitle         0.5s      0.7s       Supporting info
CTA buttons      0.65s     0.6s       Final action, quickest
Scroll indicator 0.9s      0.5s       Ambient, fade only
─────────────────────────────────────────────────
Total sequence: ~1.4s from first to last element visible
```

**Rule: total hero entrance should never exceed 2 seconds.** Users get impatient. The sequence should feel brisk, not ceremonial.

---

## Stagger cascade {#stagger}

Multiple items of the same type appear one after another.

### Best practices
- **Max 6-8 items visible** at once in a stagger group. If 20 cards are on screen, only stagger the first visible batch
- **Stagger delay: 0.06-0.12s** per item. Below 0.06s feels simultaneous, above 0.15s feels slow
- **Direction should follow reading order** — left-to-right, top-to-bottom for LTR layouts
- **All items should be visible within 0.8s** of the first one appearing

### Vanilla JS
```js
function staggerReveal(elements, { delay = 80, threshold = 0.15 } = {}) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return
      const parent = entry.target
      const children = parent.querySelectorAll('[data-stagger-item]')

      children.forEach((child, i) => {
        setTimeout(() => child.classList.add('visible'), i * delay)
      })

      observer.unobserve(parent)
    })
  }, { threshold })

  elements.forEach(el => observer.observe(el))
}

// Usage
staggerReveal(document.querySelectorAll('[data-stagger-group]'))
```

### Motion
```tsx
// Define once, reuse everywhere
export const stagger = {
  container: {
    hidden: {},
    visible: { transition: { staggerChildren: 0.08 } }
  },
  item: {
    hidden: { opacity: 0, y: 24 },
    visible: {
      opacity: 1, y: 0,
      transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] }
    }
  }
}

// Usage
<motion.div variants={stagger.container} initial="hidden" whileInView="visible"
  viewport={{ once: true }}>
  {items.map(item => (
    <motion.div key={item.id} variants={stagger.item}>{item.name}</motion.div>
  ))}
</motion.div>
```

---

## Count-up numbers {#count-up}

Numbers animate from 0 (or any start) to target value.

### Vanilla JS — production version
```js
function countUp(element, target, {
  duration = 1500,
  start = 0,
  prefix = '',
  suffix = '',
  decimals = 0,
  easing = (t) => 1 - Math.pow(1 - t, 3)  // ease-out cubic
} = {}) {
  const startTime = performance.now()

  function tick(now) {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    const value = start + (target - start) * easing(progress)
    element.textContent = prefix + value.toFixed(decimals) + suffix
    if (progress < 1) requestAnimationFrame(tick)
  }

  requestAnimationFrame(tick)
}

// Trigger on scroll
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return
    const el = entry.target
    countUp(el, parseInt(el.dataset.target), {
      suffix: el.dataset.suffix || '',
      prefix: el.dataset.prefix || '',
      duration: parseInt(el.dataset.duration || '1500')
    })
    observer.unobserve(el)
  })
}, { threshold: 0.5 })

document.querySelectorAll('[data-countup]').forEach(el => observer.observe(el))

// <span data-countup data-target="180" data-suffix="+">0</span>
```

### React hook
```tsx
import { useEffect, useState, useRef } from 'react'
import { useInView } from 'motion/react'

function useCountUp(target: number, duration = 1500) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-20%' })
  const [value, setValue] = useState(0)

  useEffect(() => {
    if (!isInView) return
    const start = performance.now()

    function tick(now: number) {
      const t = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - t, 3)
      setValue(Math.round(target * eased))
      if (t < 1) requestAnimationFrame(tick)
    }

    requestAnimationFrame(tick)
  }, [isInView, target, duration])

  return { ref, value }
}

// Usage
function Stat({ target, label, suffix = '' }) {
  const { ref, value } = useCountUp(target)
  return (
    <div ref={ref}>
      <span className="stat-number">{value}{suffix}</span>
      <span className="stat-label">{label}</span>
    </div>
  )
}
```

---

## Page/route transitions {#page-transitions}

### Motion + React Router / Next.js
```tsx
import { AnimatePresence, motion } from "motion/react"

const pageVariants = {
  enter:   { opacity: 0, y: 20 },
  center:  { opacity: 1, y: 0 },
  exit:    { opacity: 0, y: -20 }
}

function AnimatedPage({ children, key }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={key}
        variants={pageVariants}
        initial="enter"
        animate="center"
        exit="exit"
        transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

**`mode="wait"`** — waits for exit animation to complete before mounting the new page. Without it, both pages are visible simultaneously during transition.

---

## Loader to content {#loader-reveal}

Transition from a loading state to the actual page content.

### Pattern: clip-path reveal
```js
// Loader covers full screen, then reveals content by shrinking
const loader = document.querySelector('.loader')

window.addEventListener('load', () => {
  // Wait for fonts + critical images
  setTimeout(() => {
    loader.style.transition = 'clip-path 0.8s cubic-bezier(0.77, 0, 0.175, 1)'
    loader.style.clipPath = 'inset(0 0 100% 0)'  // shrink upward

    setTimeout(() => {
      loader.remove()
      // Trigger hero entrance after loader
      heroEntrance(['.hero-tag', '.hero-title', '.hero-sub', '.hero-cta'])
    }, 800)
  }, 300)
})

// CSS: .loader { position: fixed; inset: 0; z-index: 9999;
//   background: var(--bg); clip-path: inset(0); }
```
