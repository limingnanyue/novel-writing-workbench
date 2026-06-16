# Taste-Skill UI Pattern for Web Tools

Applied [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) v2 design principles to an AI writing workbench web UI.

## Three Dials (DIALS)

| Dial | Value | Meaning |
|:-----|:------|:--------|
| `VARIANCE` | 5 | Moderate layout variance — functional tool, not artsy |
| `MOTION` | 3 | Restrained animation — only fade-in, slide-up, pulse |
| `DENSITY` | 5 | Medium information density — enough visible, not cramped |

## Anti-Slop Checklist

When building a web tool UI (not a landing page), enforce these:

- ❌ **No AI-purple gradients** (`#7c3aed`, `#a855f7`) — use functional blues (`#4af`, `#5b8af7`)
- ❌ **No centered hero section** — tools start with workspace, not marketing
- ❌ **No glassmorphism** (`backdrop-filter`, `rgba(...0.1)`) — feels like a brochure
- ❌ **No Inter+slate-900** default — pick fonts/colors deliberately
- ✅ **Terminal-style header** — functional monospace branding
- ✅ **Flat cards** — solid backgrounds, subtle borders, no shadows
- ✅ **Functional buttons** — `pri`/`good`/`dan` variants, no gradient fills
- ✅ **Minimal animation** — `fade .2s`, `pulse 1.5s`, `slide-up .25s` only
- ✅ **Comment discipline** — don't mention hex codes or CSS properties in anti-slop comments (they trigger false-positive audits)

## Design Read (one-liner before coding)

Pattern: "Reading this as: `<page kind>` for `<audience>`, with a `<vibe>` language, leaning toward `<aesthetic family>`."

Example: "创意写作工具 · 中文网文作者 · 终端工具美学 · 拨盘 5/3/5"

## Frontend Budget

- Target **under 30KB** for the full SPA HTML
- No external CSS/JS dependencies
- Inline all styles — no CDN fetches
- CSS-in-`<style>` is acceptable; separate `.css` files add latency

## Version History

- v4.3: Applied taste-skill to workbench (33KB → 27KB)
- v4.4: Further slimmed with ChatPage pattern (27KB)
