# FINN — Financial Investment Intelligence

> **Intelligence That Drives Informed Investment Decisions.**

**FINN** is a mobile-first AI-powered investment intelligence platform for Indian equities, developed for the ENAM Holdings AI Engineer Build Challenge.

It helps investors monitor portfolio developments, investigate companies using primary-source documents, and evaluate management's stated guidance against reported financial performance.

## Product Overview

### PUSH — Portfolio Intelligence
A prioritised digest of corporate announcements and material developments across an 18-company demo portfolio. Includes:
- Corporate announcements classified into 17 categories.
- High, medium and routine priority levels.
- End-of-day price movement and unusual-volume alerts based on configurable thresholds.
- Financial results summaries with Revenue, EBITDA, PBT and PAT, including QoQ and YoY comparisons where available.
- Management-change summaries using company disclosures.

### PULL — AI-Powered Company Research
Research any supported listed company using retrieved primary-source documents, including annual reports, earnings-call transcripts, investor presentations and exchange filings.

- Conversational research with follow-up context.
- Page-level source references for retrieved evidence.
- Financial snapshots covering growth, margins, balance sheet and cash flow.
- **Management Guidance vs Actuals:** compares extracted management commitments with subsequently reported performance.
- Clear distinction between reported facts, calculated metrics and FINN's interpretation.

### PROFILE — Investor Preferences
Guest-mode profile with device-local preferences, portfolio settings, alert preferences and data information. No account registration is required.

**Getting started:** Open FINN and select **Explore FINN**.

## Live Demo

https://finn-investment-intelligence-production.up.railway.app/profile

> The demo uses end-of-day market data where applicable. Data mode and timestamps are displayed in the application. Simulated fallback scenarios are explicitly labelled.

## Screenshots

### 1. FINN — Welcome Screen
Introduction to FINN and its three core modules.

![FINN Splash Screen](assets/screenshots/Screenshot%202026-11-13%20181951.png)

### 2. PUSH — Portfolio Intelligence
Prioritised portfolio alerts, corporate announcements and market developments.

![FINN PUSH Dashboard](assets/screenshots/Screenshot%202026-11-13%20182007.png)

### 3. PULL — AI-Powered Company Research
Conversational company research with financial insights and primary-source evidence.

![FINN PULL Research](assets/screenshots/Screenshot%202026-11-13%20182026.png)

### 4. PROFILE — Investor Preferences
Guest-mode profile and investor preference settings.

![FINN Profile](assets/screenshots/Screenshot%202026-11-13%20182035.png)

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI |
| Financial data | Yahoo Finance chart API, NSE announcements, Screener.in |
| Document processing | PyMuPDF, page-aware text extraction |
| Retrieval | BM25 |
| AI | Anthropic Claude API |
| Deployment | Docker, Railway |

## System Architecture

```text
React + Vite + Tailwind
        |
        | REST API
        v
FastAPI Backend
        |
        +---- PUSH
        |       +-- Corporate announcement ingestion
        |       +-- Classification and prioritisation
        |       +-- EOD price and volume alerts
        |       +-- Results and management-change summaries
        |
        +---- PULL
        |       +-- Company document retrieval
        |       +-- PDF page extraction
        |       +-- BM25 retrieval
        |       +-- AI-generated cited answers
        |       +-- Guidance vs Actuals analysis
        |
        +---- PROFILE
                +-- Device-local preferences

External sources:
NSE / BSE / Screener.in / Yahoo Finance / Company PDFs
```

The Dockerfile builds the frontend and serves it through FastAPI, allowing the application to run as a single service.

The workflow:
1. Retrieve relevant earnings-call transcripts.
2. Extract explicitly stated guidance and its reporting period.
3. Retrieve subsequent reported financial results.
4. Compare guidance with actual performance on a comparable basis.
5. Calculate variance and classify the outcome where evidence supports a verdict.
6. Preserve source references for the underlying statements and reported figures.


## API Overview

| Endpoint | Purpose |
|---|---|
| `GET /api/digest` | Portfolio digest with filter and threshold parameters |
| `GET /api/alerts` | Material and threshold-triggered alerts |
| `GET /api/market` | NIFTY 50, SENSEX and NIFTY IT data |
| `GET /api/company/search?q=` | Company search |
| `GET /api/quote/{sym}` | Company quote |
| `POST /api/research/{sym}/prepare` | Prepare and index company documents |
| `GET /api/research/{sym}/status` | Document processing status |
| `POST /api/research` | Conversational company research |
| `GET /api/research/{sym}/snapshot` | Deterministic financial snapshots |
| `GET /api/research/{sym}/guidance-vs-actuals` | Management guidance scorecard |
| `POST /api/research/{sym}/upload` | Upload a company PDF |

For the complete parameter definitions, refer to the backend implementation.

## Model Routing and Cost Efficiency

FINN uses a tiered approach to reduce unnecessary model calls.

| Task | Approach |
|---|---|
| Filing classification | Rules first; Haiku for ambiguous cases |
| Executive background | Filing extraction, with AI extraction where needed |
| Results numbers | Standardised financial tables |
| Document retrieval | BM25 over page-tagged text chunks |
| Research answers | Claude Sonnet |
| Guidance extraction | Claude Haiku |
| Guidance evaluation | Claude Sonnet |

Frequently repeated operations use caching where implemented.

Cost figures are estimates and depend on input/output token usage, document length, caching and current provider pricing. Actual usage should be checked against the application's cost ledger and Anthropic account.

## Data Sources and Transparency

FINN uses:
- NSE corporate announcements as the primary corporate-filings feed.
- BSE announcements as a fallback where accessible.
- Screener.in for company information, financial tables and document discovery.
- Yahoo Finance chart data for end-of-day prices and volume.
- Company and exchange-hosted PDFs for research evidence.

The application displays data mode and timestamps. When live feeds are unavailable, fallback or simulated data is labelled.

**AI availability:** Without `ANTHROPIC_API_KEY`, the application can still provide available evidence and PUSH functionality, but AI-powered research and Guidance vs Actuals are limited or unavailable.

See [INTEGRATIONS.md](INTEGRATIONS.md) for source-by-source verification and known limitations.

## Run Locally

### Requirements
- Python 3.11+
- Node.js 18+
- npm

### 1. Backend

From the repository root:

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp ../.env.example ../.env
```

Add your Anthropic API key to the root `.env` file if AI features are required.

Start the backend:

```bash
.venv/bin/uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

Open a second terminal at the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open the local frontend URL shown by Vite (typically `http://localhost:5173`).

The development server proxies `/api` requests to the FastAPI backend.

### 3. Single-process production build

The Dockerfile builds the frontend and serves the generated static files through FastAPI.

```bash
docker build -t finn .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=your_key finn
```

Do not commit API keys or `.env` files to GitHub.

## Deployment

FINN is deployed as a Docker-based service on Railway.

To reproduce the deployment:
1. Connect the GitHub repository to a Railway project.
2. Deploy using the repository's Dockerfile.
3. Configure `ANTHROPIC_API_KEY` in the Railway service's Variables section if AI features are required.
4. Generate a public domain in Railway Networking.
5. Open the generated URL and verify the application.


## Known Limitations

- BSE API access may be blocked from cloud environments; the application uses its configured fallback chain.
- Availability and completeness of filings depend on external source access.
- Some financial values, including EBITDA, may be derived from standardised tables and are labelled accordingly.
- Scanned image-only PDFs may not be extractable without OCR.
- AI-powered research and Guidance vs Actuals require a configured Anthropic API key.
- Guest preferences are stored locally and are not synchronised across devices.
- Market data is not guaranteed to be real-time.

## Repository Structure

```text
backend/
  app/
    connectors/
    push.py
    research.py
    rag.py
    llm.py
    classify.py

frontend/
  src/
    screens/
    components/
    lib/

reference/
  challenge documents and design references

Dockerfile
.env.example
INTEGRATIONS.md
WRITEUP.md
```

## Disclaimer

FINN is a prototype developed for the ENAM Holdings AI Engineer Build Challenge. It is an informational research and monitoring tool, not investment advice or a recommendation to buy or sell securities.
