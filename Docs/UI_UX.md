# DIALECTA — UI/UX Specification

## 1. Design Principles

- **Dark, minimal, premium.** No cartoon avatars, no template-feeling cards, no default shadcn look-and-feel left untouched.
- **The debate is the hero.** Every screen exists to either set up or display the live debate — nothing should compete with it visually.
- **Feels engineered, not generated.** Sharp edges over soft gradients, restrained motion, real typographic hierarchy instead of size-only emphasis.

## 2. Color System

| Token | Hex | Usage |
|---|---|---|
| `bg-base` | `#0A0A0C` | App background, near-black, not pure black |
| `bg-elevated` | `#13141A` | Cards, debate panel background |
| `border-subtle` | `#23252E` | Hairline borders/dividers |
| `text-primary` | `#F4F4F6` | Primary text |
| `text-muted` | `#8B8D98` | Secondary/meta text |
| `accent-cyan` | `#38BDF8` | Optimist + primary interactive accent |
| `accent-violet` | `#7C3AED` | Ethicist + brand accent (logo, key CTAs) |
| `accent-amber` | `#F5A524` | Skeptic |
| `accent-emerald` | `#34D399` | Analyst |

This carries your existing GitHub-profile palette (`#38bdf8` / `#7c3aed`) into the product itself, so the brand is consistent across README, profile, and app.

## 3. Typography

- **Headings, labels, agent names, data/numbers:** JetBrains Mono — gives the "control room" feel appropriate to a debate interface.
- **Body copy, debate messages:** Space Grotesk — readable at speed, doesn't fight the mono headers.
- Scale: 12 / 14 / 16 / 20 / 28 / 40px. No in-between sizes — keeps hierarchy obvious.

## 4. Key Screens

### 4.1 Onboarding
- Single-column, dark, one decision per screen (connect accounts → set values → demo intervention).
- Progress shown as a thin 1px line filling left-to-right in `accent-cyan`, not a stepper with circles.

### 4.2 Dashboard / Decision Log
- Left rail: minimal icon nav (Log, Settings). No labels at rest, label on hover — keeps it quiet.
- Main panel: reverse-chronological list of past decisions. Each row: decision summary, outcome badge (`accepted` / `overridden` / `ignored` in muted color, not traffic-light red/green — this isn't a pass/fail system), timestamp in JetBrains Mono.

### 4.3 Live Debate View
- **Radial layout**, not a chat list: the decision sits center, the four agents arranged around it like seats at a table — this is the single most important visual choice, because it's what makes "parliament" legible at a glance instead of just being four chat bubbles.
- Each agent has a fixed position and color (per §2) so users learn the layout once and never have to re-read labels.
- Turns animate in with a short (150ms) fade + 4px rise — no bounce, no spring physics. Calm, not playful.
- Moderator's closing line appears center, replacing the decision prompt, in `accent-violet`.

### 4.4 Browser Extension Popup (Intervention Card)
- Compact version of the radial layout, collapsed to a vertical stack given popup width constraints.
- Top: the intercepted action in plain language ("About to buy: [item], ₹[amount]").
- Below: agent turns stream in one at a time, each prefixed by a 6px color dot (no avatars/icons needed).
- Two actions only at the bottom: **Continue anyway** (ghost button) and **Cancel** (solid, `accent-cyan`) — deliberately not making "cancel" feel like the "correct" answer through color alone; both are neutral, the debate content should do the persuading, not the button styling.

### 4.5 Settings
- Connected accounts: simple list with provider name, connected date, and a text-only "Disconnect" link (not a destructive-red button — disconnecting isn't dangerous, it's just a preference).
- Agent tuning: 4 sliders (one per agent, "gentle ↔ blunt"), labeled in JetBrains Mono.
- Stated values: plain textarea, one statement per line, reorderable by drag for priority.

## 5. Agent Visual Identity

| Agent | Color | Tone marker |
|---|---|---|
| Optimist | `accent-cyan` | Upward chevron `▲` |
| Skeptic | `accent-amber` | Question mark `?` |
| Analyst | `accent-emerald` | Hash `#` |
| Ethicist | `accent-violet` | Dot-in-circle `◉` |

No illustrated mascots — a color + a single geometric glyph per agent is enough to make them instantly distinguishable without looking templated.

## 6. States & Microinteractions

| State | Visual |
|---|---|
| Idle | Decision prompt centered, four agent seats empty/dim |
| Listening (voice mode) | Center prompt replaced by a thin waveform in `accent-cyan` |
| Debating | Agents light up in turn order as their turn streams in; inactive seats stay dimmed at 40% opacity |
| Resolved | Moderator line takes center stage; the two action buttons fade in below |

## 7. Accessibility

- All agent color coding is paired with a glyph (§5) and a text label — never color alone.
- Contrast: `text-primary` on `bg-base`/`bg-elevated` exceeds WCAG AA for body text at the chosen sizes.
- Voice mode output is also rendered as text in real time for screen reader / deaf-and-hard-of-hearing users — never audio-only.
- Browser extension popup is fully keyboard-navigable (Tab between agents' "expand citation" affordance, Enter to act on Continue/Cancel).
