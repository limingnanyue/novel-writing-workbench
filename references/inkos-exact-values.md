# InkOS Exact UI Values — Faithful Reproduction Reference

> Exact values extracted from Narcooo/inkos (v1.5.0) for 100% faithful reproduction.
> "参考X" = exact pixel/color/animation reproduction, not "inspired by".

## oklch Color Palette

### Light mode (:root)
```
--background: oklch(0.985 0.005 80)
--foreground: oklch(0.13 0.02 60)
--card: oklch(1 0 0)
--card-foreground: oklch(0.15 0.015 60)
--primary: oklch(0.45 0.12 25)          # ink red
--primary-foreground: oklch(0.98 0.006 76)
--secondary: oklch(0.94 0.01 76)
--muted: oklch(0.94 0.008 76)
--muted-foreground: oklch(0.38 0.02 60)
--accent: oklch(0.92 0.02 85)           # gold foil
--destructive: oklch(0.55 0.18 25)
--border: oklch(0.84 0.01 76)
--ring: oklch(0.45 0.12 25)
--radius: 0.6rem
```

### Dark mode (.dark)
```
--background: oklch(0.12 0.01 250)      # obsidian
--foreground: oklch(0.97 0.005 250)
--card: oklch(0.18 0.015 250)
--primary: oklch(0.78 0.14 85)          # warm amber
--secondary: oklch(0.22 0.02 250)
--muted: oklch(0.22 0.015 250)
--border: oklch(0.30 0.02 250)
--ring: oklch(0.78 0.14 85)
```

## Font Stack (3-tier)
```
--font-serif: 'Instrument Serif', Georgia, serif     # Headings & story content
--font-sans:  'DM Sans', system-ui, sans-serif        # UI controls
--font-mono:  'JetBrains Mono', monospace             # Data, logs, code
```

## Animation Keyframes (8 required)

```css
/* 1. Staggered entrance for 2x8 creation grid */
@keyframes staggerIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
/* Each child: nth-child(1):delay=0s, (2):.04s ... (8):.28s */

/* 2-3. Message slide in (separate left/right) */
@keyframes msgSlideRight {
  from { opacity: 0; transform: translateX(20px); }
  to   { opacity: 1; transform: translateX(0); }
}
@keyframes msgSlideLeft {
  from { opacity: 0; transform: translateX(-20px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* 4. Thinking glow pulse */
@keyframes thinkGlow {
  0%, 100% { box-shadow: 0 0 4px var(--primary); }
  50%      { box-shadow: 0 0 12px var(--primary); }
}

/* 5. Typing wave (3 dots) */
@keyframes typingWave {
  0%, 60%, 100% { opacity: .2; transform: scale(.8); }
  30%           { opacity: 1; transform: scale(1); }
}

/* 6. Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* 7. Icon pop */
@keyframes iconPop {
  0%   { transform: scale(.8); opacity: 0; }
  70%  { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}

/* 8. Blinking cursor (for streaming text) */
@keyframes blinky {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0; }
}
```

## Sidebar Structure (260px)

```
┌─ Logo + Brand ──────────────────────────┐
│ [InkOS Logo SVG: dark circle, orange    │
│  ink drop, gold nib]                    │
│  InkOS Studio                           │
├─ CREATION (2x4 grid) ───────────────────┤
│ [📖长篇小说] [📜短篇]                    │
│ [✒️同人] [📑番外]                       │
│ [🪄仿写] [📥续写]                       │
│ [🔀分支互动] [🎮开放世界]               │
├─ My Bookshelf (collapsible) ──────────┤
│ [▶ site: 0fr→1fr CSS Grid animation]    │
│  ├ 📂 Book 1                            │
│  │ ├ session 1                          │
│  │ └ session 2                          │
│  └ + 新建会话                           │
├─ History (collapsible) ─────────────────┤
│ Sessions (same collapse pattern)        │
├─ SYSTEM ────────────────────────────────┤
│ 📦 模型余额                             │
│ ⚙️ 服务商                                │
│ ⚙️ 项目设置                              │
│ ⚡ Daemon [RUNNING badge]                │
│ ⌨️ 日志                                  │
├─ TOOLS ────────────────────────────────┤
│ 🪄 风格                                  │
│ 📥 导入                                  │
│ 📈 雷达                                  │
│ 🩺 诊断                                  │
├─ Status ───────────────────────────────┤
│ ● Agent online  12ms                    │
└──────────────────────────────────────────┘
```

## Key Component Classes

```css
/* Sidebar item */
.sb-item { w-full; flex; items-center; gap-3; px-3; py-2; rounded-lg; text-sm; transition-all; }
.sb-item.active { bg-secondary; shadow-sm; border; border-border; font-medium; }

/* Glass panel */
.glass-panel { bg-card/80; backdrop-filter: blur(12px); border; border-border; rounded-radius; }

/* Paper sheet (book cards) */
.paper-sheet { bg-card; border; border-border; rounded-xl; p-5; shadow-sm; 
  hover:shadow-md; transition-all; cursor-pointer; }

/* Creation entry grid */
.creation-entry { rounded-xl; bg-secondary/50; border; border-border; p-3;
  transition-all; hover:bg-muted; hover:border-primary/20; }

/* Balance progress bar */
.bc-bar { height: 4px; bg-border; rounded; overflow-hidden; }
.bc-bar-fill { height: 100%; bg-primary; rounded; transition: width .3s; }

/* Streaming text cursor */
.m-bub.streaming { border-left: 2px solid var(--primary); }
.m-bub.streaming::after { content: "▍"; animation: blinky .8s step-end infinite; }
```

## Theme Toggle (◐)

Position: `fixed; top: 8px; right: 8px; z-index: 50`
Style: `w-[30px]; h-[30px]; rounded-full; border; bg-background/80; backdrop-filter: blur(12px)`
Icon: ☀️ in light mode, 🌙 in dark mode, or ◐ toggle
Transition: `transition: all .3s ease`
Only visible on mobile (<768px) since desktop sidebar has no header.

## SVG Noise Texture

```css
body::before {
  content: '';
  position: fixed; inset: 0;
  opacity: 0.025;
  pointer-events: none;
  z-index: 0;
  background-image: url("data:image/svg+xml,...");
}
/* Use feTurbulence with fractalNoise, baseFrequency=0.9, numOctaves=4 */
```

## Creation Entry Grid (2x8)

```css
.creation-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  padding: 0 12px;
}
.creation-entry:nth-child(1) { animation: staggerIn .3s ease both; animation-delay: 0s; }
.creation-entry:nth-child(2) { animation: staggerIn .3s ease both; animation-delay: .04s; }
/* ... through nth-child(8) with .28s delay */
```

## Collapsible (CSS Grid 0fr→1fr)

```html
<div class="collapse" id="collapse1">
  <div class="collapse-inner"> <!-- min-height: 0 -->
    <!-- content here, natural height -->
  </div>
</div>
```
```css
.collapse { display: grid; grid-template-rows: 0fr; transition: grid-template-rows .2s; overflow: hidden; }
.collapse.open { grid-template-rows: 1fr; }
.collapse-inner { min-height: 0; overflow: hidden; }
```
No JS height measurement needed — pure CSS. Toggle by adding/removing `.open` class.
