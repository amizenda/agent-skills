# Interaction Animation Patterns

Gesture-driven animations: hover, tap, drag, cursor-follow.

## Hover effects

### Image reveal on hover
```css
.card-image {
  clip-path: inset(100% 0 0 0);           /* hidden: clipped from bottom */
  transition: clip-path 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.card:hover .card-image {
  clip-path: inset(0);                     /* revealed: fully visible */
}

/* With scale */
.card-image img {
  transform: scale(1.1);
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.card:hover .card-image img {
  transform: scale(1);
}
```

### Underline scale on hover
```css
.link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 1px;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.link:hover::after { transform: scaleX(1); }
```

### Magnetic button (cursor attraction)
```js
function magneticButton(btn, strength = 0.3) {
  btn.addEventListener('mousemove', (e) => {
    const rect = btn.getBoundingClientRect()
    const x = (e.clientX - rect.left - rect.width / 2) * strength
    const y = (e.clientY - rect.top - rect.height / 2) * strength
    btn.style.transform = `translate(${x}px, ${y}px)`
  })
  btn.addEventListener('mouseleave', () => {
    btn.style.transition = 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)'
    btn.style.transform = 'translate(0, 0)'
    setTimeout(() => btn.style.transition = '', 400)
  })
}
```

### Motion hover + tap
```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.97 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  click me
</motion.button>

// Card with tilt
<motion.div
  whileHover={{ y: -4, boxShadow: "0 8px 30px rgba(0,0,0,0.12)" }}
  transition={{ duration: 0.2 }}
  className="card"
/>
```

## Drag interactions

### Motion drag
```tsx
<motion.div
  // Use ONE: `drag` (both axes) OR `drag="x"` / `drag="y"` (single axis)
  drag="x"
  dragConstraints={{ left: -200, right: 200 }}
  dragElastic={0.1}             // how much it stretches past constraints
  dragMomentum={true}           // fling momentum after release
  whileDrag={{ scale: 1.05, cursor: "grabbing" }}
/>
```

### Drag to reorder (Motion Reorder)
```tsx
import { Reorder } from "motion/react"

function ReorderList({ items, onReorder }) {
  return (
    <Reorder.Group values={items} onReorder={onReorder}>
      {items.map(item => (
        <Reorder.Item key={item.id} value={item}>
          {item.name}
        </Reorder.Item>
      ))}
    </Reorder.Group>
  )
}
```

## Cursor-follow

### Custom cursor
```js
const cursor = document.querySelector('.custom-cursor')
let mouseX = 0, mouseY = 0, cursorX = 0, cursorY = 0

document.addEventListener('mousemove', (e) => {
  mouseX = e.clientX; mouseY = e.clientY
})

;(function loop() {
  // Smooth follow with lerp
  cursorX += (mouseX - cursorX) * 0.15
  cursorY += (mouseY - cursorY) * 0.15
  cursor.style.transform = `translate(${cursorX}px, ${cursorY}px)`
  requestAnimationFrame(loop)
})()

// Enlarge on hover over interactive elements
document.querySelectorAll('a, button').forEach(el => {
  el.addEventListener('mouseenter', () => cursor.classList.add('hover'))
  el.addEventListener('mouseleave', () => cursor.classList.remove('hover'))
})

// CSS: .custom-cursor { position: fixed; top: -8px; left: -8px; width: 16px; height: 16px;
//   border-radius: 50%; border: 1px solid var(--blue); pointer-events: none;
//   transition: width 0.2s, height 0.2s; z-index: 9999; }
// .custom-cursor.hover { width: 40px; height: 40px; top: -20px; left: -20px; }
```

## Layout animation (Motion exclusive)

### Shared layout transition
```tsx
// Element smoothly animates between two positions in the DOM
function Card({ isExpanded, onClick }) {
  return (
    <motion.div layout onClick={onClick}
      transition={{ layout: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } }}>
      <motion.h3 layout="position">{title}</motion.h3>
      {isExpanded && (
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          Expanded content
        </motion.p>
      )}
    </motion.div>
  )
}
```

### Shared element transition (layoutId)
```tsx
// Same element animates between two components/pages
// In list view:
<motion.img layoutId={`img-${id}`} src={thumb} />

// In detail view:
<motion.img layoutId={`img-${id}`} src={full} />

// Wrap both in <AnimatePresence> — Motion handles the transition automatically
```
