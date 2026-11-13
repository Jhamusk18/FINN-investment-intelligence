# FINN · Financial Investment Intelligence

> **Intelligence That Drives Informed Investment Decisions.**

A mobile-first investing copilot for Indian equities, built for the ENAM Holdings AI Engineer Build Challenge.

- **PUSH** – a prioritised digest of every NSE filing across an 18-stock portfolio, plus threshold alerts on end-of-day price and volume.
- **PULL** – research on *any* listed company, answered only from primary documents, with page-level citations. It includes **Management Guidance vs Actuals**.
- **PROFILE** – guest mode. Preferences are stored on the device.

No login. Open it and tap **Explore FINN**.

---

## Run locally

Requirements: Python 3.11+ and Node 18+.

```bash
# 1. backend
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp ../.env.example ../.env        # optional: add ANTHROPIC_API_KEY
.venv/bin/uvicorn app.main:app --port 8000

# 2. frontend (second terminal) – dev server proxies /api to :8000
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

To run a single process instead, run `cd frontend && npm run build`, then start uvicorn. FastAPI serves `frontend/dist` at `/`.

## Deploy (one service)

The `Dockerfile` builds the React app and serves it from FastAPI, so there is one URL.

- **Render:** New → Blueprint → pick this repo (`render.yaml`), set `ANTHROPIC_API_KEY`, then Deploy.
- **Any Docker host:** `docker build -t finn . && docker run -p 8000:8000 -e ANTHROPIC_API_KEY=... finn`

## Architecture

```
                 ┌────────────────────────── React + Vite + Tailwind (mobile-first, 390px) ─────────────────────────┐
                 │  Splash → PUSH (digest, filter sheet, thresholds) · PULL (chat, cards, guidance) · PROFILE (local) │
                 └───────────────────────────────────────────────┬───────────────────────────────────────────────────┘
                                                                 │ /api
┌──────────────────────────────────────────────── FastAPI ───────┴──────────────────────────────────────────────────────┐
│ push.py      digest + alerts ── classify.py (rules → cheap LLM) ── results card (QoQ/YoY) ── bio from Reg-30 filing │
│ research.py  answers · snapshot cards (deterministic) · guidance vs actuals                                         │
│ rag.py       PDF → pages → chunks (page metadata) → BM25 index per ticker, built on demand with progress            │
│ llm.py       model routing · structured outputs · prompt caching · cost ledger                                       │
│ cache.py     JSON disk cache (classifications, PDFs' text, answers, guidance, digests)                              │
└───────┬───────────────────┬──────────────────────┬─────────────────────────┬──────────────────────────────────────────┘
   NSE API (→BSE→screener)   Yahoo chart API (EOD)   screener.in (docs, tables)   BSE/NSE PDFs
```

### API
| Endpoint | Purpose |
|---|---|
| `GET /api/digest?vol=&px=&material=&overrides=&window=&priority=&companies=&categories=` | 30-day item set with thresholds applied. The client filters this one dataset so counters, feed and labels always agree. |
| `GET /api/alerts` | Only the items that crossed a threshold or are material |
| `GET /api/market` | NIFTY 50 / SENSEX / NIFTY IT with EOD or LIVE mode and a timestamp |
| `GET /api/company/search?q=` | Any listed company (portfolio first, then screener.in search) |
| `GET /api/quote/{sym}` | EOD close for the PULL header |
| `POST /api/research/{sym}/prepare` · `GET …/status` | Fetch and index primary documents with per-document progress |
| `POST /api/research` | Q&A with `[S#]` citations, keeping conversation context |
| `GET /api/research/{sym}/snapshot` | Deterministic financial, trajectory, balance-sheet and cash cards |
| `GET /api/research/{sym}/guidance-vs-actuals` | Promise-by-promise scorecard |
| `POST /api/research/{sym}/upload` | Add your own PDF to the company's index |

## Model routing and cost

| Step | Engine | Why |
|---|---|---|
| Classify filings into 17 categories | **Rules** (NSE subject tag + regex) → `claude-haiku-5-5` only when the rules can't place a filing | ~95% of filings never touch a model. Every verdict is cached by filing URL. |
| Executive background | Regex excerpt from the filing, or Haiku extraction | A primary source at very low cost |
| Results numbers | Standardised tables (no model) | Free and exact |
| Retrieval | **BM25** over page-tagged chunks | No embedding API or model hosting. Financial queries are term-heavy. |
| PULL answer | `claude-sonnet-5-5`, structured JSON output, system prompt cached | The strong model is used only where reasoning is needed |
| Guidance extraction | Haiku, once per transcript (cached) | Bulk extraction |
| Guidance verdicts | Sonnet, once per company per new transcript (cached 24h) | Judgement |

Rough cost: classifying a month of filings for 18 stocks costs under $0.01. A PULL answer (~6k input tokens) costs about $0.02. A full guidance scorecard costs about $0.05–0.08, and repeat runs are free from cache. Live spend is shown in Profile → Appearance & data.

## Data honesty
- Every price carries an **EOD** or **LIVE** badge with a timestamp. Alerts use completed sessions only.
- Simulated items appear only if every live feed fails, and they are labelled everywhere.
- PULL answers come only from retrieved excerpts. Missing information is reported as "Not found in sources". Each finding is tagged **Reported**, **Calculated** or **FINN view**.

See [INTEGRATIONS.md](INTEGRATIONS.md) for the status of each source.

## Repository
```
backend/app/       FastAPI app (connectors/, push.py, research.py, rag.py, llm.py, classify.py)
frontend/src/      screens/ (Splash, Push, FilterSheet, FeedCard, ThresholdsSheet, Pull, PullCards, Profile), components/, lib/
reference/         Challenge PDFs and design references
```
