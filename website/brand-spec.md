# Skills For Real Teams · Website Brand Spec

## Direction

- Name: Night Editorial
- Narrative: make the workflow legible before showing the catalog; present AI skills as a handoff system for real software teams rather than a prompt collection.
- Temperature: calm, precise, warm, technical.
- Information model: concise editorial hero with the only installation entry, visible workflow routes, a toolbar-led two-column skill index, then durable file artifacts.
- Navigation: no persistent top bar. A quiet text-only language control sits in the hero's upper-right corner; the product name and GitHub destination remain in the footer.
- Primary viewing context: laptop and desktop; mobile retains the complete browsing and installation path.

## Brand Assets

The product name “Skills For Real Teams” is the primary recognition element. The website uses a text wordmark and does not display a standalone SRT logo or logo-based favicon. The supplied poster artwork remains in the repository as unchanged source material, but the production page does not display or load it.

### Core

- `assets/srt-brand/og-image.png`: 1200 × 630 social sharing image derived from the supplied delivery poster.

### Chinese

- `assets/srt-brand/posters/zh/product.png`
- `assets/srt-brand/posters/zh/delivery.png`
- `assets/srt-brand/posters/zh/codebase.png`
- `assets/srt-brand/posters/zh/tech-debt.png`

### English

- `assets/srt-brand/posters/en/product.png`
- `assets/srt-brand/posters/en/delivery.png`
- `assets/srt-brand/posters/en/codebase.png`
- `assets/srt-brand/posters/en/tech-debt.png`

The supplied posters remain unchanged composite assets. Do not delete or rewrite them when changing the website. Delivery and technical-debt posters must describe local Tasks as the implementation unit; a remote Issue is optional Spec-level tracking, not the main workflow boundary.

## Color System

- Ground: `#07101d`
- Deep ground: `#050b14`
- Surface: `#101d31`
- Raised surface: `#14243a`
- Primary text: `#f3eedf`
- Paper surface: `#e9e1cd`
- Secondary text: `#9aa6ad`
- Primary accent: `#ff6b35`
- Accent hover: `#ff8b55`
- Ready state: `#d9f99d`
- Informational state: `#94e9df`
- Hairline border: `rgba(243, 238, 223, 0.14)`

Orange is the only interactive accent. Lime and cyan are reserved for explicit file or workflow states; they are not decorative alternatives. Purple is not part of the system.

The ground includes a fixed atmospheric layer: broad, low-contrast navy glows, one restrained warm halo, and a sparse CSS star field. Stars stay below 1.2px at full intensity and remain behind all content; they add depth without becoming an illustration or reducing text contrast.

## Typography

- Display and Latin body: `"Avenir Next"` with native platform fallbacks
- Chinese body fallback: `"PingFang SC"`, then `"Hiragino Sans GB"`
- Labels and code: `"SFMono-Regular"` with cross-platform monospace fallbacks
- The production page does not block rendering on external font requests.
- Hero scale: `clamp(4rem, 5.8vw, 5.2rem)`
- Body scale: `clamp(1rem, 1.25vw, 1.14rem)`
- Chinese display headings use `-0.018em` tracking, keep deliberate line breaks for cadence, and omit punctuation at line endings. English display headings retain tighter tracking. Body copy keeps normal punctuation.
- Hero copy receives roughly three fifths of the desktop canvas. Installation is presented as a paper-toned functional component rather than hero imagery. Agent selection updates one shared command instead of repeating the install flow.

## Shape and Spacing

- Base spacing unit: 8px
- Main spacing values: 16, 24, 32, 48, 64, 96, 128
- Control radius: 8px
- Panel radius: 16px
- Skills use grouped two-column editorial rows with a sticky desktop toolbar. Mobile collapses to one column and keeps filters horizontally scrollable.
- Workflow routes are separated by whitespace and a short vertical accent. Compact arrow glyphs communicate handoff direction; full-width rules and long connector lines are intentionally avoided.

## Elevation and Motion

- Prefer borders and contrast over elevation. The production page does not use decorative shadows.
- Reserve orange for active, selected, and actionable elements.
- Interaction feedback: 180-240ms.
- Use restrained reveal motion to clarify reading order, a scroll-progress line for orientation on the long catalog, and a short command transition for Agent state changes.
- The atmospheric layer may show one brief meteor at a time. Meteors use only transform and opacity, remain invisible for most of their 16-29 second cycles, and disappear entirely when `prefers-reduced-motion` is active.
- No autoplay carousel.
- Respect `prefers-reduced-motion`.

## Production Decisions

- `index.html`, `styles.css`, and `script.js` implement the production site.
- The skill index is generated from `skills/*/*/SKILL.md` into `skills-data.js`; website copy must not maintain a separate manual skill list.
- Product, delivery, codebase, technical-debt, config, writing, and archive-distillation domains are represented through the generated skill index rather than a separate graphic capability section.
- GitHub Pages regenerates skill data before publishing.
