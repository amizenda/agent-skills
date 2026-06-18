# web-animation

Production-ready web animation patterns for modern websites and landing pages.

---

## Overview

A comprehensive animation skill covering every pattern you'll encounter on premium websites — from simple scroll reveals to complex horizontal pin+scrub sections, parallax layers, and gesture-driven interactions.

Each effect is distilled into copy-paste code across four implementation targets: **vanilla JS**, **Motion** (Framer Motion), **GSAP ScrollTrigger**, and **CSS-only**.

## What's inside

```
web-animation/
├── SKILL.md                              # Entry point — decision tree, quick catalog, performance rules
└── references/
    ├── scroll-patterns.md                # 9 scroll patterns with full code
    ├── entrance-patterns.md              # Hero sequences, stagger, count-up, page transitions
    ├── interaction-patterns.md           # Hover, tap, drag, cursor-follow, layout animation
    ├── advanced-patterns.md              # Accordion, marquee, masonry, sticky nav, expandable cards
    ├── library-comparison.md             # Motion vs GSAP vs CSS feature matrix
    └── performance.md                    # 60fps checklist, jank debugging, mobile optimization
```

## Pattern catalog

### Scroll animations
- **Scroll-triggered reveal** — fade/slide when element enters viewport
- **Scroll-linked (scrub)** — animation tied directly to scroll position
- **Horizontal pin scroll** — section pins while content scrolls sideways
- **Pin + scrub timeline** — pinned section with multi-step animation sequence
- **Parallax layers** — elements move at different speeds for depth
- **Path follow** — element traces an SVG path as user scrolls
- **Text reveal** — words/characters illuminate progressively on scroll
- **Progress indicators** — reading bars, step counters tied to scroll

### Entrance animations
- **Hero stagger sequence** — cascading element appearance on page load
- **Stagger cascade** — grid/list items appear one after another
- **Count-up numbers** — animate from 0 to target value
- **Page/route transitions** — animated transitions between pages
- **Loader to content** — loading screen reveal

### Interaction animations
- **Hover image reveal** — clip-path or scale on hover
- **Magnetic button** — element subtly follows cursor within bounds
- **Underline scale** — line draws on hover, retracts on leave
- **Drag to reorder** — list item reordering with physics
- **Custom cursor** — cursor-follow with smooth lerp
- **Layout animation** — elements animate between DOM positions (Motion exclusive)
- **Shared element transition** — same element transitions across views

### Advanced UI patterns
- **Accordion** — smooth height animation for expand/collapse (FAQ, details)
- **Infinite marquee** — continuous scrolling text/logos (CSS-only, zero JS)
- **Masonry staggered grid** — images at different sizes with offset reveals
- **Sticky nav** — hide on scroll down, show on scroll up, opaque after hero
- **Split-layout reveal** — two columns with asymmetric animation timing
- **Expandable cards** — click to expand team/profile cards with bio
- **Hover image preview** — cursor-following image on service list hover
- **Scroll-triggered line draw** — SVG path draws itself on scroll
- **Image comparison slider** — before/after drag slider
- **Scroll-snap sections** — full-page snapping between sections

## Library decision guide

| Situation | Use |
|-----------|-----|
| React app + UI transitions | **Motion** |
| Complex scroll choreography | **GSAP ScrollTrigger** |
| Marketing site with scroll effects | **GSAP** (or both) |
| Simple hover/entrance effects | **CSS** |
| No framework, lightweight page | **Vanilla JS** |
| React app with scroll marketing sections | **Motion + GSAP** together |

## Installation

Download the `.skill` file and either:
- Drag into Claude Desktop settings
- Place in your project's `skills/user/` directory
- Or copy the folder to any location Claude can access

## Sources & references

- [Motion docs](https://motion.dev/) — React animation API reference
- [GSAP docs](https://gsap.com/) — ScrollTrigger, timeline, SplitText
- [Awwwards](https://www.awwwards.com/) — award-winning animation patterns
- [MDN Web Animations](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API) — native browser APIs

## Library status (verified June 2026)

- **GSAP** — 100% free since April 2025, including all former Club plugins (SplitText, MorphSVG, DrawSVG, ScrollSmoother…) and commercial use. Stewarded by Webflow.
- **CSS scroll-timeline** (`animation-timeline: scroll()`) — supported in Chrome/Edge 115+ and Safari 26+; behind a flag in Firefox. Use an `@supports` guard and `animation-duration: 1ms` (Firefox) for the parallax examples.
- **Motion** — current package is `motion` with the `motion/react` entry point (formerly Framer Motion).

---

# web-animation (Tiếng Việt)

Bộ pattern animation web production-ready cho website và landing page hiện đại.

---

## Tổng quan

Một bộ skill animation toàn diện bao phủ mọi pattern bạn sẽ gặp trên các website premium — từ scroll reveal đơn giản đến horizontal pin+scrub phức tạp, parallax layers, và gesture-driven interactions.

Được xây dựng bằng cách nghiên cứu các website premium và award-winning, sau đó chắt lọc mỗi hiệu ứng thành code copy-paste cho bốn target: **vanilla JS**, **Motion** (Framer Motion), **GSAP ScrollTrigger**, và **CSS thuần**.

## Bên trong có gì

```
web-animation/
├── SKILL.md                              # Entry point — decision tree, catalog nhanh, performance rules
└── references/
    ├── scroll-patterns.md                # 9 scroll pattern đầy đủ code
    ├── entrance-patterns.md              # Hero sequence, stagger, count-up, page transition
    ├── interaction-patterns.md           # Hover, tap, drag, cursor-follow, layout animation
    ├── advanced-patterns.md              # Accordion, marquee, masonry, sticky nav, expandable cards
    ├── library-comparison.md             # Ma trận so sánh Motion vs GSAP vs CSS
    └── performance.md                    # Checklist 60fps, debug jank, tối ưu mobile
```

## Danh mục pattern

### Scroll animation
- **Scroll-triggered reveal** — fade/slide khi element vào viewport
- **Scroll-linked (scrub)** — animation gắn trực tiếp với vị trí scroll
- **Horizontal pin scroll** — section bị pin lại trong khi nội dung trượt ngang
- **Pin + scrub timeline** — section pin với chuỗi animation nhiều bước
- **Parallax layers** — các element di chuyển tốc độ khác nhau tạo chiều sâu
- **Path follow** — element di chuyển theo đường SVG khi scroll
- **Text reveal** — từ/ký tự sáng lên dần khi scroll
- **Progress indicators** — thanh tiến trình, bộ đếm bước gắn với scroll

### Entrance animation
- **Hero stagger** — các element hero xuất hiện tuần tự khi load trang
- **Stagger cascade** — items trong grid/list xuất hiện lần lượt
- **Count-up** — số đếm từ 0 lên giá trị mục tiêu
- **Page transition** — chuyển trang có animation
- **Loader reveal** — màn hình loading chuyển sang nội dung

### Interaction animation
- **Hover image reveal** — clip-path hoặc scale khi hover
- **Magnetic button** — element nhẹ nhàng theo cursor
- **Underline scale** — gạch chân vẽ ra khi hover
- **Drag to reorder** — kéo thả sắp xếp lại list
- **Custom cursor** — cursor tùy chỉnh với smooth lerp
- **Layout animation** — element animate giữa các vị trí DOM (chỉ Motion)

### Pattern UI nâng cao
- **Accordion** — animation height mượt cho expand/collapse (FAQ)
- **Infinite marquee** — text/logo cuộn liên tục (CSS thuần, không JS)
- **Masonry grid** — ảnh kích thước khác nhau với stagger reveal
- **Sticky nav** — ẩn khi scroll xuống, hiện khi scroll lên
- **Split-layout reveal** — hai cột với timing animation bất đối xứng
- **Expandable cards** — click mở rộng thẻ team/profile
- **Hover image preview** — ảnh theo cursor khi hover vào danh sách
- **Line draw** — SVG path tự vẽ khi scroll
- **Image comparison** — slider so sánh before/after
- **Scroll-snap** — snap giữa các section toàn trang

## Hướng dẫn chọn thư viện

| Tình huống | Dùng |
|------------|------|
| React app + UI transitions | **Motion** |
| Scroll choreography phức tạp | **GSAP ScrollTrigger** |
| Marketing site với scroll effects | **GSAP** (hoặc cả hai) |
| Hover/entrance đơn giản | **CSS** |
| Không framework, trang nhẹ | **Vanilla JS** |
| React app có marketing section cuộn | **Motion + GSAP** kết hợp |

## Cách cài đặt

Download file `.skill` và:
- Kéo thả vào Claude Desktop settings
- Đặt vào thư mục `skills/user/` của project
- Hoặc copy folder vào bất kỳ vị trí nào Claude có thể truy cập

## Nguồn & tham khảo

- [Motion docs](https://motion.dev/) — React animation API reference
- [GSAP docs](https://gsap.com/) — ScrollTrigger, timeline, SplitText
- [Awwwards](https://www.awwwards.com/) — award-winning animation patterns
- [MDN Web Animations](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API) — native browser APIs

## Tình trạng thư viện (đã xác minh tháng 6/2026)

- **GSAP** — miễn phí 100% từ tháng 4/2025, bao gồm tất cả plugin Club trước đây (SplitText, MorphSVG, DrawSVG, ScrollSmoother...) và cả commercial use. Được Webflow bảo trợ.
- **CSS scroll-timeline** (`animation-timeline: scroll()`) — hỗ trợ trên Chrome/Edge 115+ và Safari 26+; Firefox cần bật flag. Dùng `@supports` guard và `animation-duration: 1ms` (cho Firefox) trong các ví dụ parallax.
- **Motion** — package hiện tại là `motion` với entry point `motion/react` (trước đây là Framer Motion).

---

*Built for builders. Ship with motion.*
