# Covering-email writeup (draft)

**What I built.** FINN is a mobile-first investing copilot with three tabs.

- **PUSH** turns each day's NSE filings for an 18-stock portfolio into a short, prioritised digest. Results cards show Revenue, EBITDA, PBT and PAT with QoQ and YoY changes. Management-change cards show the incoming executive's background, taken from the company's own Regulation 30 disclosure. Routine paperwork is collapsed. End-of-day price and volume alerts fire on thresholds the user sets.
- **PULL** researches any listed company from its own annual reports, call transcripts and presentations. Every claim links to the exact PDF page, and answers keep their context across follow-up questions.
- **Management Guidance vs Actuals** checks each numerical promise from the last four earnings calls against what was later reported.

**Key decisions and trade-offs**
- *Rules before models.* NSE's own subject tags plus regex rules classify about 95% of filings for free. A cheap model handles only the rest, and its answers are cached. The strong model is reserved for research reasoning and guidance verdicts.
- *BM25 instead of embeddings.* Financial questions are full of exact terms ("FY27", "EBITDA margin"). BM25 has zero inference cost and nothing to host, and the retriever can be swapped later.
- *Primary-source bios.* SEBI requires a "brief profile" in appointment filings, so FINN reads the filing instead of scraping LinkedIn. That gives verifiable output at almost no cost.
- *One dataset, client-side filtering.* The backend returns 30 days of items and the app filters them. Counters, feed and pill labels can never disagree.
- *Honesty over polish.* Every number has an EOD or LIVE badge and a timestamp. Simulated data is labelled. "Not found in sources" is a valid answer.

**Deliberately left out:** authentication, push notifications, intraday streaming, embeddings and a vector database, OCR for scanned PDFs, and multi-portfolio support.

**Next steps:** scheduled EOD jobs with real push notifications; a guidance-credibility score tracked over time; cross-company comparisons; embeddings plus re-ranking for long annual reports; OCR; and an eval set for citation accuracy.
