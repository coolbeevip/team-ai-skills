# Skills For Real Teams — Website Brand Spec

## Direction

- Name: Dark Systems Editorial
- Narrative: make the workflow visible; present AI skills as an operating system for real software teams rather than a prompt collection.
- Temperature: technical, authoritative, energetic, restrained.
- Primary viewing context: laptop and desktop; mobile is a complete secondary path.

## Brand Assets

The product posters are the primary recognition assets. Website HTML must reference the copied files below rather than recreate their illustrations.

### Core

- `assets/srt-brand/logo.png`: exact crop of the supplied SRT logo.
- `assets/srt-brand/favicon.png`: square favicon treatment derived from the exact logo crop.
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

The supplied posters contain the real SRT logo. The website uses an exact raster crop of that mark for navigation and favicon assets; it does not redraw or regenerate the logo. A future official SVG export can replace `logo.png` without changing the layout.

## Color System

- Ground: `#070b0f`
- Surface: `#0d151c`
- Raised surface: `#121e27`
- Primary text: `#f4f7f8`
- Secondary text: `#91a0aa`
- Cyan accent: `#19d5e6`
- Amber state: `#ffb547`
- Green state: `#72d47b`
- Hairline border: `rgba(121, 226, 235, 0.16)`

Amber and green are semantic workflow colors, not decorative alternatives to cyan. Purple is not part of the system.

## Typography

- Display and body: `"Noto Sans SC"`
- Labels and code: `"IBM Plex Mono"`
- Hero scale: `clamp(3.6rem, 7vw, 7.4rem)`
- Body scale: `clamp(1rem, 1.3vw, 1.18rem)`
- Chinese display headings use line breaks for cadence and omit punctuation, especially at line endings. Body copy keeps normal punctuation.
- Hero copy receives roughly half of the desktop canvas, uses open line spacing, and must not be compressed to make room for imagery.

## Shape and Spacing

- Base spacing unit: 8px
- Main spacing values: 16, 24, 32, 48, 64, 96, 128
- Control radius: 6px
- Panel radius: 12px
- Poster radius: 18px
- Poster treatment: framed, with a visible radius, hairline border, and surrounding negative space. Edge-to-edge treatment is not used in production.
- Capability posters use an equal-width two-column grid, retain their full aspect ratio, and do not scale the image on hover.

## Elevation and Motion

- Use deep, soft shadows to separate surfaces.
- Reserve cyan edge light for active or selected elements.
- Interaction feedback: 180ms.
- Content transition: 420ms using `cubic-bezier(0.22, 1, 0.36, 1)`.
- No autoplay carousel.
- Respect `prefers-reduced-motion`.

## Production Decisions

- `index.html`, `styles.css`, and `script.js` implement the production site.
- The skill index is generated from `skills/*/*/SKILL.md` into `skills-data.js`; website copy must not maintain a separate manual skill list.
- GitHub Pages regenerates skill data before publishing.
