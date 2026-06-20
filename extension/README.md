# DIALECTA — Browser Extension (MV3)

Intercepts checkout / send / post actions and opens a live 4-agent debate before you commit.

## Load unpacked

1. `npm install && npm run build` (or use the prebuilt `dist/` once available)
2. Open `chrome://extensions`
3. Enable **Developer mode**
4. Click **Load unpacked** and select this `extension/` directory (or the `dist/` build output)

## How it works

- `src/content/content-script.ts` — listens for buy/checkout/send button clicks, extracts page context, and asks the service worker to open a debate
- `src/background/service-worker.ts` — creates a session with the backend and opens the debate view in a new tab
- `src/popup/debate.html` + `debate.ts` + `debate.css` — the radial debate UI (4 agent seats around a centered decision prompt, per `Docs/UI_UX.md` §4.3)

## Configuration

The extension talks to `http://localhost:8000` by default. Change `BACKEND_URL` in
`src/background/service-worker.ts` and `src/popup/popup.ts` to point at a deployed instance.
