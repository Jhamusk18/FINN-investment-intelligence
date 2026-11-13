# FINN — Financial Investment Intelligence

**Intelligence That Drives Informed Investment Decisions.**

FINN is a mobile-first AI-powered investment intelligence platform built for the ENAM Holdings AI Engineer Build Challenge. It helps investors monitor portfolio developments, research listed companies and evaluate management accountability.

### What I Built

- **PUSH – Portfolio Intelligence:** Converts corporate announcements across an 18-stock portfolio into a prioritised digest, with financial results summaries and configurable price and volume alerts.
- **PULL – AI-Powered Research:** Enables research on listed companies using annual reports, earnings-call transcripts, presentations and exchange filings, with page-level citations and conversational follow-ups. Evaluates numerical management commitments against subsequently reported financial performance, highlighting variances and outcomes.
- **PROFILE – Investor Preferences:** Provides guest-mode portfolio and alert preferences stored locally on the device.

### Key Technical Decisions

- **Rules before models:** Uses rule-based filing classification first, reducing unnecessary AI calls.
- **BM25 retrieval:** Uses page-aware document retrieval without requiring an embedding service.
- **Caching:** Reuses processed documents and previous results to reduce repeated computation and API costs.
- **Evidence-first answers:** Separates reported facts, calculated metrics and AI interpretation, with source references.
- **Data transparency:** Displays EOD/LIVE timestamps and labels simulated fallback data.

### Limitations and Future Scope

The current prototype does not include authentication, intraday streaming, push notifications, OCR for scanned PDFs or multi-portfolio support. Future improvements include scheduled updates, OCR, cross-company comparisons, improved retrieval and longitudinal management-guidance tracking.

### Technology Stack

React, Vite, Tailwind CSS, Python, FastAPI, BM25, Anthropic Claude API, Yahoo Finance and NSE/Screener data sources. Deployed using Docker on Railway.

**FINN aims to make investment research more accessible, structured and evidence-driven.**
