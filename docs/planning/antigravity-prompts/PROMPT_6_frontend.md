# PROMPT 6 — Accessible Frontend

Paste everything below this line into Antigravity.

---

Continue following `AGENTS.md`, especially §7 (accessibility). Build the
frontend as plain HTML/CSS/JS in `frontend/` — no build step, no
framework, calling the backend at same-origin relative paths (e.g.
`/api/chat`).

`frontend/index.html`:
- Semantic structure: `<header>`, `<nav>` for persona/language switcher,
  `<main>` with clearly labeled `<section>`s for: chat assistant, crowd
  status panel, transport widget, sustainability tips.
- A persona switcher (fan / volunteer / organizer / venue_staff) as
  actual `<button>` elements with `aria-pressed` state, not divs with
  click handlers.
- A stadium dropdown (`<select>` with `<label>`), language dropdown, and
  an accessibility-need dropdown, all properly labeled.
- A visible "High contrast & large text" toggle `<button>` with
  `aria-pressed`, that adds/removes a class on `<body>` — provide the
  corresponding CSS in `styles.css` (larger base font size, higher
  contrast color pairs, thicker focus outlines).
- Chat panel: a scrollable log region with `aria-live="polite"` so new
  assistant replies are announced to screen readers, a labeled text
  input, and a submit button (real `<button type="submit">` inside a
  `<form>`, not a JS-only click handler, so Enter key submission works
  for free).
- Crowd panel: render each zone's density as a labeled bar/row that shows
  the level as **text and an icon/pattern**, not color alone (AGENTS.md
  §7 — color can't be the only signal). Include the zone name and % as
  visible text.
- Keyboard navigability: confirm tab order is logical top-to-bottom,
  all interactive elements are reachable and operable via keyboard alone
  (no `div onclick` without `tabindex`/keydown handling).

`frontend/styles.css`:
- Clean, modern, high-contrast-friendly default palette. Respect
  `prefers-reduced-motion` for any animations/transitions.
- A `.high-contrast` body class variant with stronger contrast ratios and
  larger base font size.

`frontend/app.js`:
- No inline event handlers in HTML — attach everything via
  `addEventListener` in this file, in small named functions (AGENTS.md
  §3).
- Functions to: fetch stadium list on load, send chat messages and render
  replies into the log (escaping any HTML in the assistant's text to
  avoid injection when rendering into the DOM), fetch/poll crowd status,
  fetch transport options, fetch sustainability tips, and toggle
  high-contrast mode.
- Handle fetch errors gracefully (show a small inline error message in
  the UI, don't fail silently or throw an uncaught error to the console
  as the only feedback).

Show me all three files, then confirm the app is usable end-to-end
(chat, crowd panel, persona switch, accessibility toggle) when served via
the backend's static mount.
