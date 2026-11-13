"""screener.in connector: company search (any listed company), document links
(annual reports, concall transcripts, PPTs), standardised quarterly P&L, and the
recent exchange-announcement feed (which links straight to the BSE filing PDF)."""
import re
from datetime import datetime

from bs4 import BeautifulSoup

from .. import cache
from ..http import client

BASE = "https://www.screener.in"


def search(q: str) -> list[dict]:
    q = q.strip()
    if not q:
        return []

    def fetch():
        r = client.get(f"{BASE}/api/company/search/", params={"q": q, "v": 3, "fts": 1})
        r.raise_for_status()
        out = []
        for row in r.json():
            url = row.get("url") or ""
            m = re.match(r"/company/([^/]+)/", url)
            if not m or not row.get("id"):
                continue
            out.append({"symbol": m.group(1), "name": row.get("name"), "screener_url": BASE + url})
        return out

    return cache.memo("screener_search", q.lower(), 86400, fetch)


def _num(s: str):
    s = (s or "").replace(",", "").replace("%", "").strip()
    if s in ("", "-", "--"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_table(section) -> dict:
    table = section.find("table") if section else None
    if not table:
        return {}
    head = [th.get_text(" ", strip=True) for th in table.find("thead").find_all("th")]
    rows = {}
    for tr in table.find("tbody").find_all("tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if not cells:
            continue
        label = re.sub(r"\s*\+\s*$", "", cells[0].replace("\xa0", " ")).strip()
        rows[label] = [_num(c) for c in cells[1:]]
    return {"periods": head[1:], "rows": rows}


def _parse_company(html: str, symbol: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    name = (soup.find("h1").get_text(strip=True) if soup.find("h1") else symbol)
    cid = None
    m = re.search(r"/announcements/recent/(\d+)/", html)
    if m:
        cid = m.group(1)
    bse_code = None
    m = re.search(r"bseindia\.com/stock-share-price/[^\"']+/(\d{6})/", html)
    if m:
        bse_code = m.group(1)
    about = soup.select_one(".company-profile .about p, .about p")
    docs = {"annual_reports": [], "concalls": [], "announcements": []}
    dsec = soup.find(id="documents")
    if dsec:
        for li in dsec.select(".annual-reports li a"):
            title = li.get_text(" ", strip=True)
            m = re.search(r"(20\d\d)", title)
            docs["annual_reports"].append({"title": title.split(" from ")[0], "url": li["href"], "year": int(m.group(1)) if m else None})
        for li in dsec.select(".concalls li"):
            period = li.find("div")
            period = period.get_text(" ", strip=True) if period else ""
            for a in li.find_all("a"):
                kind = a.get_text(" ", strip=True)
                href = a.get("href", "")
                if kind in ("Transcript", "PPT") and href.startswith("http"):
                    docs["concalls"].append({"period": period, "kind": kind, "url": href})
        for li in dsec.select("#company-announcements-tab li"):
            a = li.find("a")
            if not a:
                continue
            t = li.find("time")
            sub = li.select_one(".ink-600")
            summary = None
            if sub:
                txt = sub.get_text(" ", strip=True)
                summary = txt.split(" - ", 1)[1].strip() if " - " in txt else None
            title_node = a.find(string=True, recursive=False)
            title = (title_node or a.get_text(" ", strip=True)).strip()
            docs["announcements"].append({
                "title": title,
                "url": a.get("href"),
                "datetime": t.get("datetime") if t else None,
                "summary": summary,
            })
    quarters = _parse_table(soup.find(id="quarters"))
    annual = _parse_table(soup.find(id="profit-loss"))
    balance = _parse_table(soup.find(id="balance-sheet"))
    cashflow = _parse_table(soup.find(id="cash-flow"))
    ratios = {}
    for li in soup.select("#top-ratios li"):
        k = li.select_one(".name")
        v = li.select_one(".value")
        if k and v:
            ratios[k.get_text(" ", strip=True)] = re.sub(r"\s+", " ", v.get_text(" ", strip=True))
    return {
        "symbol": symbol,
        "name": name,
        "screener_id": cid,
        "bse_code": bse_code,
        "url": url,
        "about": about.get_text(" ", strip=True) if about else None,
        "ratios": ratios,
        "docs": docs,
        "quarters": quarters,
        "annual": annual,
        "balance_sheet": balance,
        "cash_flow": cashflow,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
    }


def company(symbol: str, ttl: float = 3 * 3600) -> dict:
    symbol = symbol.upper().strip()

    def fetch():
        last_err = None
        for variant in ("consolidated/", ""):
            url = f"{BASE}/company/{symbol}/{variant}"
            r = client.get(url)
            if r.status_code == 404:
                last_err = "not found"
                continue
            r.raise_for_status()
            data = _parse_company(r.text, symbol, url)
            if data["quarters"].get("rows"):
                return data
            last_err = "no quarterly data"
        raise LookupError(f"{symbol}: {last_err}")

    return cache.memo("screener_company", symbol, ttl, fetch)
