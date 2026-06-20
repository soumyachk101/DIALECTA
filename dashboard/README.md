# DIALECTA — Dashboard (Next.js)

Lightweight Decision Log + Settings UI. Streams via the FastAPI backend.

## Run

```bash
cd dashboard
npm install
cp .env.example .env.local
npm run dev          # http://localhost:3000
```

Pages:
- `/` — Decision Log (reverse-chronological)
- `/decisions/[id]` — full transcript with the radial debate view
- `/settings` — connected accounts, agent tuning sliders, stated values

The `/v1/*` path is proxied to `BACKEND_URL` (default `http://localhost:8000`) via the Next.js rewrite in `next.config.mjs`.
