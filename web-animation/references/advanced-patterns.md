# Advanced UI Animation Patterns

Patterns extracted from premium Webflow templates (Harroway, Halston, Metrik Studio). Accordion, marquee, masonry grid, sticky nav, split-layout reveals, and expandable cards.

## Table of contents
1. [Accordion expand/collapse](#accordion)
2. [Infinite marquee scroll](#marquee)
3. [Masonry staggered image grid](#masonry-grid)
4. [Sticky nav — hide/show on scroll](#sticky-nav)
5. [Split-layout asymmetric reveal](#split-reveal)
6. [Expandable team/profile cards](#expandable-cards)
7. [Solution cards with hover image](#solution-cards)
8. [Image comparison slider](#image-compare)
9. [Scroll-triggered line draw](#line-draw)
10. [Scroll-snapped full-page sections](#scroll-snap)

---

## Accordion expand/collapse {#accordion}

Smooth height transition for FAQ, service details, or any collapsible content.

### Vanilla JS — auto-height animation
```js
// The hard part: animating to/from height:auto
function toggleAccordion(trigger) {
  const content = trigger.nextElementSibling
  const isOpen = trigger.classList.contains('open')

  if (isOpen) {
    // Collapse: set explicit height first, then animate to 0
    content.style.height = content.scrollHeight + 'px'
    content.offsetHeight // force reflow
    content.style.height = '0'
    trigger.classList.remove('open')
  } else {
    // Expand: animate to scrollHeight, then set auto
    content.style.height = content.scrollHeight + 'px'
    trigger.classList.add('open')
    content.addEventListener('transitionend', () => {
      if (trigger.classList.contains('open')) {
        content.style.height = 'auto' // allow content resize
      }
    }, { once: true })
  }
}

// CSS:
// .accordion-content {
//   height: 0; overflow: hidden;
//   transition: height 0.4s cubic-bezier(0.16, 1, 0.3, 1);
// }

// Rotate the icon
// .accordion-trigger svg {
//   transition: transform 0.3s ease;
// }
// .accordion-trigger.open svg {
//   transform: rotate(45deg);
// }
```

### Motion (React)
```tsx
import { motion, AnimatePresence } from "motion/react"

function Accordion({ items }) {
  const [openId, setOpenId] = useState<string | null>(null)

  return (
    <div>
      {items.map(item => (
        <div key={item.id}>
          <button onClick={() => setOpenId(openId === item.id ? null : item.id)}>
            <span>{item.question}</span>
            <motion.span
              animate={{ rotate: openId === item.id ? 45 : 0 }}
              transition={{ duration: 0.2 }}
            >+</motion.span>
          </button>
          <AnimatePresence>
            {openId === item.id && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                style={{ overflow: 'hidden' }}
              >
                <p style={{ padding: '16px 0' }}>{item.answer}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  )
}
```

---

## Infinite marquee scroll {#marquee}

Continuous horizontal scrolling text/logos. Used by Harroway for "Solutions" keyword display and client logos.

### CSS-only (preferred — zero JS)
```html
<div class="marquee">
  <div class="marquee-track">
    <span class="marquee-item">Signal</span>
    <span class="marquee-sep">·</span>
    <span class="marquee-item">Narrative</span>
    <span class="marquee-sep">·</span>
    <span class="marquee-item">Leverage</span>
    <span class="marquee-sep">·</span>
    <!-- Duplicate the content for seamless loop -->
    <span class="marquee-item">Signal</span>
    <span class="marquee-sep">·</span>
    <span class="marquee-item">Narrative</span>
    <span class="marquee-sep">·</span>
    <span class="marquee-item">Leverage</span>
    <span class="marquee-sep">·</span>
  </div>
</div>

<style>
.marquee {
  overflow: hidden;
  white-space: nowrap;
}
.marquee-track {
  display: inline-flex;
  animation: marquee 20s linear infinite;
}
@keyframes marquee {
  to { transform: translateX(-50%); }
}
/* Pause on hover (optional) */
.marquee:hover .marquee-track {
  animation-play-state: paused;
}

/* Reverse direction variant */
.marquee--reverse .marquee-track {
  animation-direction: reverse;
}

@media (prefers-reduced-motion: reduce) {
  .marquee-track { animation: none; }
}
</style>
```

### Stacked marquee (two rows, opposite directions)
```html
<div class="marquee-stack">
  <div class="marquee"><div class="marquee-track"><!-- content duplicated --></div></div>
  <div class="marquee marquee--reverse"><div class="marquee-track"><!-- content duplicated --></div></div>
</div>
```

### Logo marquee with fade edges
```css
.marquee {
  -webkit-mask-image: linear-gradient(
    to right,
    transparent 0%, black 10%, black 90%, transparent 100%
  );
  mask-image: linear-gradient(
    to right,
    transparent 0%, black 10%, black 90%, transparent 100%
  );
}
```

---

## Masonry staggered image grid {#masonry-grid}

Images arranged at different sizes and offsets, revealing with staggered timing. Used by Harroway in the process section (4 images, staggered heights).

### CSS grid with offset reveals
```html
<div class="mosaic" data-stagger-group>
  <div class="mosaic-item mosaic-tall" data-stagger-item data-delay="0">
    <img src="..." alt="" />
  </div>
  <div class="mosaic-item mosaic-short" data-stagger-item data-delay="150">
    <img src="..." alt="" />
  </div>
  <div class="mosaic-item mosaic-medium" data-stagger-item data-delay="100">
    <img src="..." alt="" />
  </div>
  <div class="mosaic-item mosaic-tall" data-stagger-item data-delay="200">
    <img src="..." alt="" />
  </div>
</div>

<style>
.mosaic {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  align-items: start; /* allows uneven heights */
}
.mosaic-tall   { aspect-ratio: 3/4; }
.mosaic-short  { aspect-ratio: 4/3; margin-top: 60px; } /* offset down */
.mosaic-medium { aspect-ratio: 1/1; margin-top: 30px; }

.mosaic-item {
  overflow: hidden;
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}
.mosaic-item.visible { opacity: 1; transform: none; }

.mosaic-item img {
  width: 100%; height: 100%; object-fit: cover;
  transform: scale(1.15); /* start zoomed */
  transition: transform 0.9s cubic-bezier(0.16, 1, 0.3, 1);
}
.mosaic-item.visible img {
  transform: scale(1); /* zoom to normal */
}
</style>
```

### GSAP with clip-path reveal
```js
gsap.utils.toArray('.mosaic-item').forEach((item, i) => {
  gsap.from(item, {
    clipPath: 'inset(100% 0 0 0)',  // reveal from bottom
    duration: 1,
    ease: 'power3.inOut',
    scrollTrigger: {
      trigger: item,
      start: 'top 85%',
    },
    delay: i * 0.15
  })
  // Parallax zoom on the image inside
  gsap.from(item.querySelector('img'), {
    scale: 1.2,
    duration: 1.2,
    ease: 'power2.out',
    scrollTrigger: { trigger: item, start: 'top 85%' }
  })
})
```

---

## Sticky nav — hide/show on scroll {#sticky-nav}

Navigation hides on scroll down, shows on scroll up. Background becomes opaque after scrolling past hero.

### Vanilla JS
```js
function initStickyNav(nav, { tolerance = 6, minOffset = 80, heroHeight = null } = {}) {
  let lastScrollY = 0
  let ticking = false

  window.addEventListener('scroll', () => {
    if (ticking) return
    ticking = true

    requestAnimationFrame(() => {
      const currentY = window.scrollY
      const delta = currentY - lastScrollY        // per-frame movement (small)
      const pastHero = heroHeight ? currentY > heroHeight : currentY > 100

      // Direction-based, with a small tolerance to avoid jitter.
      // NOTE: `tolerance` guards against sub-pixel noise; `minOffset` keeps the nav
      // visible near the top. Don't compare per-frame delta against a large number —
      // a single frame rarely moves 80px, so the nav would almost never hide.
      if (Math.abs(delta) > tolerance) {
        if (delta > 0 && currentY > minOffset) {
          nav.style.transform = 'translateY(-100%)'   // scrolling down
        } else {
          nav.style.transform = 'translateY(0)'        // scrolling up (or near top)
        }
      }

      // Opaque background after hero
      nav.classList.toggle('nav--solid', pastHero)

      lastScrollY = currentY
      ticking = false
    })
  }, { passive: true })
}

// CSS:
// .nav {
//   position: fixed; top: 0; left: 0; right: 0; z-index: 100;
//   transition: transform 0.3s ease, background 0.3s ease;
//   background: transparent;
// }
// .nav--solid { background: rgba(6, 6, 14, 0.9); backdrop-filter: blur(12px); }
```

### With GSAP ScrollTrigger
```js
ScrollTrigger.create({
  start: 'top -80',
  end: 99999,
  onUpdate: (self) => {
    // self.direction: 1 = down, -1 = up
    gsap.to('.nav', {
      yPercent: self.direction === 1 ? -100 : 0,
      duration: 0.3,
      ease: 'power2.out'
    })
  }
})

// Solid background after hero
ScrollTrigger.create({
  trigger: '.hero',
  start: 'bottom top',
  onEnter: () => document.querySelector('.nav').classList.add('nav--solid'),
  onLeaveBack: () => document.querySelector('.nav').classList.remove('nav--solid'),
})
```

---

## Split-layout asymmetric reveal {#split-reveal}

Two-column layout where left and right sides reveal with different animations or timing. Common in about/intro sections.

### Pattern: text slides up, image clips in
```js
// Text side — fade up
gsap.from('.split-text', {
  y: 60, opacity: 0, duration: 0.8, ease: 'power3.out',
  scrollTrigger: { trigger: '.split-section', start: 'top 70%' }
})

// Image side — clip-path reveal from right
gsap.from('.split-image', {
  clipPath: 'inset(0 100% 0 0)',  // hidden from right
  duration: 1, ease: 'power3.inOut',
  scrollTrigger: { trigger: '.split-section', start: 'top 70%' },
  delay: 0.2
})

// Image inner — parallax counter-move
gsap.from('.split-image img', {
  scale: 1.15, duration: 1.4, ease: 'power2.out',
  scrollTrigger: { trigger: '.split-section', start: 'top 70%' }
})
```

### Motion
```tsx
<motion.div className="split-section" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr' }}>
  <motion.div
    initial={{ y: 60, opacity: 0 }}
    whileInView={{ y: 0, opacity: 1 }}
    viewport={{ once: true }}
    transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
  >
    <h2>...</h2><p>...</p>
  </motion.div>

  <motion.div
    initial={{ clipPath: 'inset(0 100% 0 0)' }}
    whileInView={{ clipPath: 'inset(0 0% 0 0)' }}
    viewport={{ once: true }}
    transition={{ duration: 1, ease: [0.77, 0, 0.175, 1], delay: 0.2 }}
    style={{ overflow: 'hidden' }}
  >
    <motion.img
      initial={{ scale: 1.15 }}
      whileInView={{ scale: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 1.4, ease: [0.16, 1, 0.3, 1] }}
      src="..." alt=""
    />
  </motion.div>
</motion.div>
```

---

## Expandable team/profile cards {#expandable-cards}

Card expands on click to reveal bio, social links, and full portrait. Used by Harroway for team section.

### Motion layout animation
```tsx
function TeamCard({ member }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <motion.div
      layout
      onClick={() => setIsOpen(!isOpen)}
      style={{ cursor: 'pointer', overflow: 'hidden', borderRadius: 12 }}
      transition={{ layout: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } }}
    >
      <motion.div layout="position" style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <motion.img layout src={member.avatar} alt="" style={{ width: 56, height: 56, borderRadius: '50%' }} />
        <div>
          <motion.h3 layout="position">{member.name}</motion.h3>
          <motion.p layout="position" style={{ opacity: 0.5 }}>{member.role}</motion.p>
        </div>
        <motion.span animate={{ rotate: isOpen ? 45 : 0 }} transition={{ duration: 0.2 }}>+</motion.span>
      </motion.div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            <p>{member.bio}</p>
            <div className="social-links">...</div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
```

---

## Solution cards with hover image {#solution-cards}

List of services/solutions where hovering reveals a large preview image. Used by Harroway for solutions section.

### Implementation
```html
<div class="solution-list" id="solution-list">
  <a class="solution-row" data-img="img1.jpg">
    <span class="solution-name">New Development Sales</span>
    <span class="solution-stat">2,400+ clients</span>
    <span class="solution-arrow">→</span>
  </a>
  <!-- more rows... -->
</div>
<div class="solution-preview" id="solution-preview">
  <img id="preview-img" src="" alt="" />
</div>

<script>
const preview = document.getElementById('solution-preview')
const previewImg = document.getElementById('preview-img')
const rows = document.querySelectorAll('.solution-row')

rows.forEach(row => {
  row.addEventListener('mouseenter', () => {
    previewImg.src = row.dataset.img
    preview.classList.add('active')
  })
  row.addEventListener('mouseleave', () => {
    preview.classList.remove('active')
  })
  row.addEventListener('mousemove', (e) => {
    preview.style.top = e.clientY + 'px'
    preview.style.left = e.clientX + 'px'
  })
})
</script>

<style>
.solution-preview {
  position: fixed;
  width: 300px; height: 200px;
  pointer-events: none;
  z-index: 50;
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.9);
  transition: opacity 0.3s, transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden; border-radius: 8px;
}
.solution-preview.active {
  opacity: 1; transform: translate(-50%, -50%) scale(1);
}
.solution-preview img {
  width: 100%; height: 100%; object-fit: cover;
}
</style>
```

---

## Image comparison slider {#image-compare}

Before/after slider for showcasing transformations. Drag or hover to reveal.

```html
<div class="compare" id="compare">
  <img class="compare-after" src="after.jpg" alt="" />
  <div class="compare-before" id="compare-clip">
    <img src="before.jpg" alt="" />
  </div>
  <div class="compare-handle" id="compare-handle"></div>
</div>

<script>
const compare = document.getElementById('compare')
const clip = document.getElementById('compare-clip')
const handle = document.getElementById('compare-handle')

compare.addEventListener('mousemove', (e) => {
  const rect = compare.getBoundingClientRect()
  const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
  clip.style.clipPath = `inset(0 ${(1 - x) * 100}% 0 0)`
  handle.style.left = x * 100 + '%'
})
</script>
```

---

## Scroll-triggered line draw {#line-draw}

SVG path draws itself as user scrolls. Used for process flows, connections between sections.

```js
const path = document.querySelector('.draw-line')
const length = path.getTotalLength()

path.style.strokeDasharray = length
path.style.strokeDashoffset = length

// Scroll-linked version
function updateLineDraw(progress) {
  path.style.strokeDashoffset = length * (1 - progress)
}

// Triggered version (draw once on scroll)
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      path.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(0.16, 1, 0.3, 1)'
      path.style.strokeDashoffset = '0'
      observer.unobserve(entry.target)
    }
  })
}, { threshold: 0.3 })

observer.observe(path.closest('svg'))
```

---

## Scroll-snapped full-page sections {#scroll-snap}

Each section takes full viewport height, scroll snaps between them.

```css
.snap-container {
  height: 100vh;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
}

.snap-section {
  height: 100vh;
  scroll-snap-align: start;
  scroll-snap-stop: always; /* prevent skipping sections */
}

/* Smooth behavior */
@media (prefers-reduced-motion: no-preference) {
  .snap-container { scroll-behavior: smooth; }
}
```

**Combine with IntersectionObserver** to trigger animations when each section snaps into view.
