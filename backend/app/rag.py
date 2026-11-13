"""Primary-document retrieval for PULL.

Pipeline (per company, on demand, cached):
  screener.in doc links -> download PDF (BSE / company IR) -> PyMuPDF text per page
  -> ~1,100-char chunks with page metadata -> BM25 index.
BM25 is a deliberate cost choice: zero inference cost, no embedding model to host, works
well on financial text where exact terms (EBITDA, FY27, margin) matter. The retrieval
interface is isolated so an embedding retriever can be swapped in later."""
import hashlib
import math
import re
import threading
import time
from datetime import datetime

import pymupdf as fitz  # PyMuPDF
from rank_bm25 import BM25Okapi

from . import cache, config
from .connectors import screener
from .http import client

MAX_PDF_BYTES = 30 * 1024 * 1024
CHUNK = 1100
OVERLAP = 180

STATUS: dict[str, dict] = {}
_INDEX: dict[str, dict] = {}
_locks: dict[str, threading.Lock] = {}
_glock = threading.Lock()

SYN = {
    "revenue": ["sales", "income", "topline", "revenues"],
    "margin": ["margins", "ebit", "operating", "opm"],
    "guidance": ["guide", "guided", "outlook", "expect", "expecting", "target", "aspire", "range"],
    "growth": ["grow", "growing", "yoy", "increase"],
    "profit": ["pat", "net", "earnings"],
    "debt": ["borrowings", "leverage", "loans"],
    "cash": ["cashflow", "fcf", "operating", "conversion"],
    "capex": ["capital", "expenditure", "investment", "capacity"],
    "risk": ["risks", "headwind", "challenge", "uncertainty", "pressure", "concern"],
    "sustainable": ["sustain", "durable", "going", "forward", "maintain"],
}
STOP = set("the a an of to in for on and or is are was were be by with as at from that this it its what how has have had does do did which who will would can could should about into than then over under".split())


def _tok(s: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", s.lower()) if w not in STOP]


def _expand(q: str) -> list[str]:
    toks = _tok(q)
    out = list(toks)
    for t in toks:
        out += SYN.get(t, [])
    return out


def doc_id(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()[:12]


def _pdf_pages(url: str, data: bytes | None = None) -> list[list]:
    key = url
    hit = cache.get("pdf_pages", key)
    if hit is not None:
        return hit
    if data is None:
        r = client.get(url, headers={"Referer": "https://www.bseindia.com/"})
        r.raise_for_status()
        data = r.content
        if len(data) > MAX_PDF_BYTES:
            data = data[:MAX_PDF_BYTES]
    if not data.startswith(b"%PDF"):
        raise ValueError("not a PDF")
    pages = []
    with fitz.open(stream=data, filetype="pdf") as pdf:
        for i, page in enumerate(pdf):
            txt = page.get_text("text")
            txt = re.sub(r"[ \t]+", " ", txt)
            txt = re.sub(r"\n{2,}", "\n", txt).strip()
            pages.append([i + 1, txt])
    return cache.put("pdf_pages", key, pages)


def pdf_pages(url: str) -> list[list]:
    return _pdf_pages(url)


def _chunks(doc: dict, pages: list[list]) -> list[dict]:
    out = []
    for pno, txt in pages:
        if len(txt) < 80:
            continue
        i = 0
        while i < len(txt):
            piece = txt[i : i + CHUNK]
            out.append({"doc": doc["id"], "page": pno, "text": piece})
            if i + CHUNK >= len(txt):
                break
            i += CHUNK - OVERLAP
    return out


def _fmt(v):
    if v is None:
        return "-"
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:g}"


def table_text(c: dict) -> str:
    """Render screener's standardised tables (compiled from exchange filings) as text."""
    lines = []
    for title, key, n in (("Quarterly P&L (₹ Cr)", "quarters", 9), ("Annual P&L (₹ Cr)", "annual", 6),
                          ("Balance sheet (₹ Cr)", "balance_sheet", 5), ("Cash flow (₹ Cr)", "cash_flow", 5)):
        t = c.get(key) or {}
        if not t.get("rows"):
            continue
        periods = t["periods"][-n:]
        lines.append(f"## {title}\nItem | " + " | ".join(periods))
        for label, vals in t["rows"].items():
            if label in ("Raw PDF",) or not any(v is not None for v in vals):
                continue
            lines.append(f"{label} | " + " | ".join(_fmt(v) for v in vals[-n:]))
    if c.get("ratios"):
        lines.append("## Key ratios (current)\n" + "; ".join(f"{k}: {v}" for k, v in c["ratios"].items()))
    return "\n".join(lines)


def _select_docs(c: dict) -> list[dict]:
    docs = []
    seen = set()
    concalls = c["docs"]["concalls"]
    transcripts = [d for d in concalls if d["kind"] == "Transcript"][:5]
    ppts = [d for d in concalls if d["kind"] == "PPT"][:2]
    for d in transcripts:
        docs.append({"title": f"Earnings call transcript – {d['period']}", "kind": "transcript", "period": d["period"], "url": d["url"]})
    for d in ppts:
        docs.append({"title": f"Investor presentation – {d['period']}", "kind": "presentation", "period": d["period"], "url": d["url"]})
    ars = sorted([a for a in c["docs"]["annual_reports"] if a.get("year")], key=lambda a: -a["year"])
    for a in ars[:1]:
        docs.append({"title": f"Annual Report {a['year']}", "kind": "annual_report", "period": f"FY{str(a['year'])[2:]}", "url": a["url"]})
    out = []
    for d in docs:
        if d["url"] in seen:
            continue
        seen.add(d["url"])
        d["id"] = doc_id(d["url"])
        out.append(d)
    return out


def _set(sym, **kw):
    st = STATUS.setdefault(sym, {"state": "idle", "docs": [], "errors": []})
    st.update(kw)
    st["updated"] = time.time()


def build_index(sym: str) -> dict:
    sym = sym.upper()
    with _glock:
        lock = _locks.setdefault(sym, threading.Lock())
    with lock:
        if sym in _INDEX and time.time() - _INDEX[sym]["built"] < 6 * 3600:
            return _INDEX[sym]
        _set(sym, state="resolving", progress=0.02, message="Finding primary documents", errors=[])
        c = screener.company(sym)
        docs = _select_docs(c)
        table_doc = {
            "id": "fin_tables", "title": "Standardised financials (compiled from exchange filings)",
            "kind": "table", "period": "latest", "url": c["url"],
        }
        _set(sym, state="downloading", progress=0.05, docs=[{**d, "state": "queued"} for d in docs],
             message=f"Fetching {len(docs)} documents", company=c["name"])
        chunks = [{"doc": "fin_tables", "page": None, "text": t} for t in re.split(r"(?=^## )", table_text(c), flags=re.M) if t.strip()]
        ready_docs = [table_doc]
        for i, d in enumerate(docs):
            STATUS[sym]["docs"][i]["state"] = "processing"
            _set(sym, message=f"Reading {d['title']}", progress=0.05 + 0.9 * i / max(1, len(docs)))
            try:
                pages = _pdf_pages(d["url"])
                d["pages"] = len(pages)
                ch = _chunks(d, pages)
                if not ch:
                    raise ValueError("no extractable text (scanned PDF?)")
                chunks += ch
                ready_docs.append(d)
                STATUS[sym]["docs"][i]["state"] = "ready"
                STATUS[sym]["docs"][i]["pages"] = len(pages)
            except Exception as e:  # keep going; report honestly
                STATUS[sym]["docs"][i]["state"] = "error"
                STATUS[sym]["errors"].append(f"{d['title']}: {e}")
        # uploaded docs for this ticker
        for up in cache.get("uploads", sym) or []:
            pages = cache.get("pdf_pages", up["url"]) or []
            chunks += _chunks(up, pages)
            ready_docs.append(up)
        idx = _make(sym, c, ready_docs, chunks)
        _set(sym, state="ready", progress=1.0, message=f"{len(ready_docs)} sources indexed · {len(chunks)} passages")
        return idx


def _make(sym, c, docs, chunks):
    bm = BM25Okapi([_tok(ch["text"]) for ch in chunks]) if chunks else None
    idx = {"symbol": sym, "company": c, "docs": {d["id"]: d for d in docs}, "chunks": chunks, "bm25": bm, "built": time.time()}
    _INDEX[sym] = idx
    return idx


def ensure_async(sym: str) -> dict:
    sym = sym.upper()
    if sym in _INDEX:
        return STATUS.get(sym, {"state": "ready"})
    st = STATUS.get(sym)
    if st and st["state"] not in ("idle", "error", "ready"):
        return st
    _set(sym, state="queued", progress=0.0, message="Queued", docs=[], errors=[])

    def run():
        try:
            build_index(sym)
        except Exception as e:
            _set(sym, state="error", message=str(e))

    threading.Thread(target=run, daemon=True).start()
    return STATUS[sym]


def get_index(sym: str):
    return _INDEX.get(sym.upper())


def search(idx: dict, query: str, k: int = 8, kinds: set | None = None, doc_ids: set | None = None, per_doc: int = 3) -> list[dict]:
    if not idx or not idx["bm25"]:
        return []
    scores = idx["bm25"].get_scores(_expand(query))
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    out, per = [], {}
    for i in order:
        ch = idx["chunks"][i]
        d = idx["docs"].get(ch["doc"])
        if d is None:
            continue
        if kinds and d["kind"] not in kinds:
            continue
        if doc_ids and d["id"] not in doc_ids:
            continue
        if per.get(d["id"], 0) >= per_doc:
            continue
        if scores[i] <= 0 and out:
            break
        per[d["id"]] = per.get(d["id"], 0) + 1
        out.append({**ch, "score": round(float(scores[i]), 3)})
        if len(out) >= k:
            break
    return out


def add_upload(sym: str, filename: str, data: bytes) -> dict:
    """Index a user-supplied primary document. Raises on failure (UI shows the error)."""
    sym = sym.upper()
    did = hashlib.sha1(data).hexdigest()[:12]
    path = config.CACHE_DIR / "uploads"
    path.mkdir(exist_ok=True, parents=True)
    (path / f"{did}.pdf").write_bytes(data)
    url = f"/api/files/{did}.pdf"
    pages = _pdf_pages(url, data)
    doc = {"id": did, "title": f"Uploaded: {filename}", "kind": "upload", "period": "user", "url": url, "pages": len(pages)}
    ch = _chunks(doc, pages)
    if not ch:
        raise ValueError("No extractable text found — the PDF may be scanned images.")
    ups = [u for u in (cache.get("uploads", sym) or []) if u["id"] != did] + [doc]
    cache.put("uploads", sym, ups)
    idx = _INDEX.get(sym)
    if idx:
        idx["docs"][did] = doc
        idx["chunks"] = [c for c in idx["chunks"] if c["doc"] != did] + ch
        _make(sym, idx["company"], list(idx["docs"].values()), idx["chunks"])
    return {**doc, "passages": len(ch)}
