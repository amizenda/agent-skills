# Scroll Animation Patterns

Complete implementations for every scroll animation type. Each pattern includes vanilla JS, Motion (React), and GSAP versions.

## Table of contents
1. [Scroll-triggered reveals](#reveals)
2. [Scroll-linked basics](#scroll-linked)
3. [Parallax](#parallax)
4. [Horizontal pin scroll](#horizontal-pin)
5. [Pin + scrub](#pin-scrub)
6. [Path follow](#path-follow)
7. [Progress indicators](#progress)
8. [Text reveal on scroll](#text-reveal)
9. [Horizontal pin — vanilla JS](#horizontal-pin-vanilla)

---

## Reveals {#reveals}

Animation fires once (or each time) element enters viewport.

### Vanilla JS — IntersectionObserver
```js
// Reusable reveal system
function initReveals(selector = '[data-reveal]', options = {}) {
  const defaults = { threshold: 0.15, rootMargin: '0px 0px -60px 0px' }
  const config = { ...defaults, ...options }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return
      const el = entry.target
      const delay = parseInt(el.dataset.delay || '0')
      setTimeout(() => el.classList.add('revealed'), delay)
      if (el.dataset.once !== 'false') observer.unobserve(el)
    })
  }, config)

  document.querySelectorAll(selector).forEach(el => observer.observe(el))
  return observer
}

// CSS
// [data-reveal] { opacity: 0; transform: translateY(40px);
//   transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1),
//               transform 0.7s cubic-bezier(0.16, 1, 0.3, 1); }
// [data-reveal].revealed { opacity: 1; transform: none; }

// Usage
// <div data-reveal data-delay="200">...</div>
```

### Motion (React)
```tsx
// ScrollReveal.tsx — reusable wrapper
import { motion, type Variants } from "motion/react"

const revealVariants: Variants = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] } }
}

export function ScrollReveal({ children, delay = 0, className = '' }) {
  return (
    <motion.div
      variants={revealVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-60px" }}
      transition={{ delay }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// Stagger group variant
const staggerContainer: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08, delayChildren: 0.1 } }
}

export function StaggerReveal({ children }) {
  return (
    <motion.div variants={staggerContainer} initial="hidden" whileInView="visible"
      viewport={{ once: true }}>
      {children}
    </motion.div>
  )
}
```

### GSAP ScrollTrigger
```js
// Batch reveal with stagger
gsap.utils.toArray('.card').forEach((card, i) => {
  gsap.from(card, {
    y: 40,
    opacity: 0,
    duration: 0.7,
    ease: 'power3.out',
    scrollTrigger: {
      trigger: card,
      start: 'top 85%',           // trigger when top of card hits 85% of viewport
      toggleActions: 'play none none none',  // play once
      // toggleActions: 'play none none reverse',  // replay on scroll back
    }
  })
})

// Stagger a group together
gsap.from('.feature-card', {
  y: 40, opacity: 0,
  stagger: 0.1,
  duration: 0.7,
  ease: 'power3.out',
  scrollTrigger: { trigger: '.features-grid', start: 'top 80%' }
})
```

### Reveal direction variants
```css
/* Fade up (default) */
[data-reveal="up"]    { transform: translateY(40px); }
/* Fade down */
[data-reveal="down"]  { transform: translateY(-40px); }
/* Fade left */
[data-reveal="left"]  { transform: translateX(60px); }
/* Fade right */
[data-reveal="right"] { transform: translateX(-60px); }
/* Scale up */
[data-reveal="scale"] { transform: scale(0.92); }
/* Blur in */
[data-reveal="blur"]  { filter: blur(10px); transform: translateY(20px); }

/* All share same revealed state */
[data-reveal].revealed {
  opacity: 1; transform: none; filter: none;
}
```

---

## Scroll-linked {#scroll-linked}

Animation progress is directly tied to scroll position. Scroll forward = animation advances. Scroll back = animation reverses.

### Core concept — mapping scroll to value
```js
// The fundamental pattern: map scroll progress (0→1) to any CSS value
function lerp(start, end, progress) {
  return start + (end - start) * progress
}

function getScrollProgress(element) {
  const rect = element.getBoundingClientRect()
  const vh = window.innerHeight
  // 0 = element just entered bottom, 1 = element left top
  return Math.max(0, Math.min(1, (vh - rect.top) / (vh + rect.height)))
}
```

### Motion — useScroll + useTransform
```tsx
import { motion, useScroll, useTransform } from "motion/react"
import { useRef } from "react"

function ScrollLinkedSection() {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]  // from element entering to leaving
  })

  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0])
  const x = useTransform(scrollYProgress, [0, 0.5, 1], [100, 0, -100])
  const scale = useTransform(scrollYProgress, [0, 0.5, 1], [0.8, 1, 0.8])

  return (
    <motion.div ref={ref} style={{ opacity, x, scale }}>
      Content moves with scroll
    </motion.div>
  )
}
```

---

## Parallax {#parallax}

Layers move at different speeds relative to scroll, creating depth.

### Vanilla JS
```js
function initParallax() {
  const layers = document.querySelectorAll('[data-parallax]')

  function update() {
    layers.forEach(layer => {
      const speed = parseFloat(layer.dataset.parallax) || 0.5
      const rect = layer.parentElement.getBoundingClientRect()
      const center = rect.top + rect.height / 2
      const offset = (center - window.innerHeight / 2) * speed
      layer.style.transform = `translateY(${-offset}px)`
    })
  }

  let ticking = false
  window.addEventListener('scroll', () => {
    if (!ticking) { requestAnimationFrame(() => { update(); ticking = false }); ticking = true }
  }, { passive: true })
}

// <div class="parallax-container">
//   <div data-parallax="0.3">Slow layer (background)</div>
//   <div data-parallax="0.6">Medium layer</div>
//   <div data-parallax="1.0">Fast layer (foreground)</div>
// </div>
```

### Motion
```tsx
function ParallaxSection() {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] })

  const bgY = useTransform(scrollYProgress, [0, 1], [-100, 100])
  const fgY = useTransform(scrollYProgress, [0, 1], [-200, 200])

  return (
    <section ref={ref} style={{ position: 'relative', overflow: 'hidden' }}>
      <motion.div style={{ y: bgY }} className="bg-layer" />
      <motion.div style={{ y: fgY }} className="fg-layer" />
    </section>
  )
}
```

### CSS scroll-timeline (Chrome/Edge 115+, Safari 26+; Firefox behind a flag)

Ships in Chrome/Edge/Safari; in Firefox it's implemented but behind the `layout.css.scroll-driven-animations.enabled` flag. Because unsupported browsers simply ignore `animation-timeline`, wrap it in `@supports` so the layer falls back to a static position instead of an un-timed animation running on load.

```css
/* Progressive enhancement — ignored where unsupported, so the layer just stays put */
@supports (animation-timeline: scroll()) {
  .parallax-layer {
    animation: parallax-move linear both;
    animation-timeline: scroll();
    animation-range: entry 0% exit 100%;
    animation-duration: 1ms; /* Firefox requires a non-zero duration to apply it */
  }
}

@keyframes parallax-move {
  from { transform: translateY(-80px); }
  to   { transform: translateY(80px); }
}

@media (prefers-reduced-motion: reduce) {
  .parallax-layer { animation: none; }
}
```

---

## Horizontal pin scroll {#horizontal-pin}

Section is pinned (fixed) while content scrolls horizontally. The Halston/Awwwards pattern.

### GSAP — production standard
```tsx
import { useRef } from "react"
import { useGSAP } from "@gsap/react"

function HorizontalScroll({ children }) {
  const containerRef = useRef(null)
  const trackRef = useRef(null)

  useGSAP(() => {
    const track = trackRef.current
    const scrollDistance = track.scrollWidth - window.innerWidth

    gsap.to(track, {
      x: -scrollDistance,
      ease: "none",
      scrollTrigger: {
        trigger: containerRef.current,
        pin: true,
        scrub: 1,               // smooth scrub with 1s lag
        end: () => `+=${scrollDistance}`,
        invalidateOnRefresh: true,  // recalc on resize
      }
    })
  }, { scope: containerRef })

  return (
    <section ref={containerRef}>
      <div ref={trackRef} style={{ display: 'flex', width: 'max-content' }}>
        {children}
      </div>
    </section>
  )
}
```

### Key options for horizontal pin
```js
scrollTrigger: {
  trigger: container,
  pin: true,                    // pin the section
  pinSpacing: true,             // add space below for scroll (default true)
  scrub: true,                  // direct 1:1 with scroll (no smoothing)
  scrub: 1,                     // 1 second lag (feels smoother)
  scrub: 0.5,                   // 0.5s lag (responsive but smooth)
  snap: 1 / (cards.length - 1), // snap to each card
  start: "top top",             // pin starts when section top hits viewport top
  end: () => "+=" + scrollDistance,
  anticipatePin: 1,             // prevents jump on pin start
  invalidateOnRefresh: true,    // recalculate on resize
}
```

### Horizontal pin — vanilla JS {#horizontal-pin-vanilla}

No library needed. Uses `position: sticky` + scroll-linked transform.

```html
<section class="hscroll-wrapper" style="height: 400vh;">
  <div class="hscroll-sticky" style="position: sticky; top: 0; height: 100vh; overflow: hidden;">
    <div class="hscroll-track" id="track" style="display: flex; will-change: transform;">
      <!-- cards here, each flex-shrink: 0; width: 400px; -->
    </div>
  </div>
</section>

<script>
const wrapper = document.querySelector('.hscroll-wrapper')
const track = document.getElementById('track')
let ticking = false

window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      const rect = wrapper.getBoundingClientRect()
      const vh = window.innerHeight
      const scrollable = rect.height - vh

      if (rect.top <= 0 && rect.bottom >= vh) {
        const progress = Math.max(0, Math.min(1, -rect.top / scrollable))
        const maxScroll = track.scrollWidth - window.innerWidth
        track.style.transform = `translateX(${-progress * maxScroll}px)`
      }
      ticking = false
    })
    ticking = true
  }
}, { passive: true })
</script>
```

**Why `height: 400vh`?** This creates the scroll distance. More height = more scroll needed = slower horizontal movement. Formula: `wrapper height = 100vh + (desired scroll distance)`. For 5 cards at 400px each (2000px total), a wrapper of 400-500vh feels natural.

---

## Pin + scrub {#pin-scrub}

Pin a section and animate multiple things inside it as the user scrolls.

### GSAP timeline + ScrollTrigger
```js
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".pinned-section",
    pin: true,
    scrub: 1,
    start: "top top",
    end: "+=3000",     // 3000px of scroll to complete
  }
})

// Chain animations — they play sequentially as user scrolls
tl.from(".step-1", { opacity: 0, y: 40 })
  .to(".step-1-image", { scale: 1.1 }, "<")  // "<" = same time as previous
  .from(".step-2", { opacity: 0, y: 40 })
  .to(".step-1", { opacity: 0.3 })            // dim previous step
  .from(".step-3", { opacity: 0, x: -60 })
  .to(".progress-bar", { scaleX: 1 }, 0)      // runs across entire timeline
```

---

## Path follow {#path-follow}

Element follows a defined path as user scrolls. Good for illustrating a process flow visually.

### SVG path + getPointAtLength
```js
const path = document.querySelector('#motion-path')
const dot = document.querySelector('#follower')
const pathLength = path.getTotalLength()

// Also draw the trail
path.style.strokeDasharray = pathLength
path.style.strokeDashoffset = pathLength

function updatePathAnimation(progress) {
  // Move dot along path
  const point = path.getPointAtLength(progress * pathLength)
  dot.style.transform = `translate(${point.x}px, ${point.y}px)`

  // Draw trail behind dot
  path.style.strokeDashoffset = pathLength * (1 - progress)
}

// Connect to scroll (use any scroll progress method)
```

---

## Progress indicators {#progress}

Visual indicators tied to scroll position.

### Reading progress bar
```js
// Vanilla JS
const bar = document.querySelector('.progress-bar')

window.addEventListener('scroll', () => {
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  const progress = window.scrollY / docHeight
  bar.style.transform = `scaleX(${progress})`
}, { passive: true })

// CSS: .progress-bar { position: fixed; top: 0; left: 0; right: 0; height: 3px;
//   background: var(--blue); transform-origin: left; transform: scaleX(0); }
```

### Section progress with step counter
```js
function getSectionProgress(wrapper) {
  const rect = wrapper.getBoundingClientRect()
  const scrollable = rect.height - window.innerHeight
  if (rect.top > 0) return 0
  if (rect.bottom < window.innerHeight) return 1
  return Math.max(0, Math.min(1, -rect.top / scrollable))
}

// Use: const progress = getSectionProgress(section)
// Current step: Math.floor(progress * totalSteps) + 1
// Display: `${currentStep} / ${totalSteps}`
```

---

## Text reveal on scroll {#text-reveal}

Words or characters reveal progressively as user scrolls.

### Word-by-word opacity (scroll-linked)
```tsx
// Motion — each word fades as scroll progresses
function TextReveal({ text }) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start 80%", "end 40%"] })
  const words = text.split(' ')

  return (
    <p ref={ref} style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3em' }}>
      {words.map((word, i) => {
        const start = i / words.length
        const end = start + 1 / words.length
        return <Word key={i} word={word} range={[start, end]} progress={scrollYProgress} />
      })}
    </p>
  )
}

function Word({ word, range, progress }) {
  const opacity = useTransform(progress, range, [0.15, 1])
  return <motion.span style={{ opacity }}>{word}</motion.span>
}
```

### GSAP SplitText approach
```js
import { SplitText } from "gsap/SplitText"
gsap.registerPlugin(SplitText)

const split = new SplitText(".reveal-text", { type: "words" })

gsap.from(split.words, {
  opacity: 0.15,
  stagger: 0.05,
  scrollTrigger: {
    trigger: ".reveal-text",
    start: "top 80%",
    end: "bottom 40%",
    scrub: true,
  }
})
```
