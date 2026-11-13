"""EOD prices & volumes from Yahoo Finance's public chart endpoint (same data yfinance uses).

Data-honesty rules:
- Alerts are computed ONLY on completed daily bars (EOD). While the market is open the
  in-progress bar is excluded.
- Index tiles show the latest Yahoo quote. During market hours that is labelled LIVE
  (Yahoo quotes can be delayed); otherwise EOD with the bar's close timestamp.
"""
from datetime import datetime, timedelta, timezone

from .. import cache
from ..http import client

IST = timezone(timedelta(hours=5, minutes=30))
CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}"


def market_open(now: datetime | None = None) -> bool:
    now = (now or datetime.now(IST)).astimezone(IST)
    if now.weekday() >= 5:
        return False
    t = now.hour * 60 + now.minute
    return 9 * 60 + 15 <= t < 15 * 60 + 30


def _fetch_chart(sym: str, rng: str = "3mo") -> dict:
    r = client.get(CHART.format(sym=sym), params={"range": rng, "interval": "1d"})
    r.raise_for_status()
    res = r.json()["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    bars = []
    for ts, o, c, v in zip(res.get("timestamp", []), q.get("open", []), q.get("close", []), q.get("volume", [])):
        if c is None:
            continue
        bars.append({"t": ts, "close": round(c, 2), "volume": v or 0})
    return {"meta": res["meta"], "bars": bars}


def chart(sym: str) -> dict:
    ttl = 300 if market_open() else 3600
    return cache.memo("yahoo", sym, ttl, lambda: _fetch_chart(sym))


def eod_stats(symbol: str, exchange_suffix: str = ".NS") -> dict:
    """Last completed session close, % change, volume and 20-day average volume."""
    data = chart(symbol + exchange_suffix)
    bars = data["bars"]
    today_ist = datetime.now(IST).date()
    if market_open() and bars and datetime.fromtimestamp(bars[-1]["t"], IST).date() == today_ist:
        bars = bars[:-1]  # exclude the in-progress session
    if len(bars) < 2:
        raise ValueError("not enough bars")
    last, prev = bars[-1], bars[-2]
    window = [b["volume"] for b in bars[-21:-1] if b["volume"]]
    avg20 = sum(window) / len(window) if window else 0
    session = datetime.fromtimestamp(last["t"], IST).date()
    return {
        "symbol": symbol,
        "close": last["close"],
        "prev_close": prev["close"],
        "change_pct": round((last["close"] / prev["close"] - 1) * 100, 2),
        "volume": last["volume"],
        "avg_volume_20d": round(avg20),
        "volume_multiple": round(last["volume"] / avg20, 2) if avg20 else None,
        "session_date": session.isoformat(),
        # NSE close is 15:30 IST
        "as_of": datetime.combine(session, datetime.min.time(), IST).replace(hour=15, minute=30).isoformat(),
        "mode": "EOD",
        "source": "Yahoo Finance (NSE)",
        "spark": [b["close"] for b in bars[-20:]],
    }


def index_tile(sym: str, label: str) -> dict:
    data = chart(sym)
    meta, bars = data["meta"], data["bars"]
    live = market_open()
    price = meta.get("regularMarketPrice") or bars[-1]["close"]
    today_ist = datetime.now(IST).date()
    # previous close = last bar that is not today's session
    prior = [b for b in bars if datetime.fromtimestamp(b["t"], IST).date() < today_ist]
    last_bar_today = bars and datetime.fromtimestamp(bars[-1]["t"], IST).date() == today_ist
    if live or last_bar_today:
        prev = prior[-1]["close"] if prior else bars[-2]["close"]
    else:
        prev = bars[-2]["close"]
    ts = meta.get("regularMarketTime") or bars[-1]["t"]
    as_of = datetime.fromtimestamp(ts, IST)
    if not live:
        as_of = as_of.replace(hour=15, minute=30, second=0) if as_of.hour * 60 + as_of.minute >= 930 else as_of
    return {
        "symbol": sym,
        "label": label,
        "value": round(price, 2),
        "change_pct": round((price / prev - 1) * 100, 2) if prev else None,
        "spark": [b["close"] for b in bars[-20:]],
        "mode": "LIVE" if live else "EOD",
        "as_of": as_of.isoformat(),
        "source": "Yahoo Finance" + (" (quotes may be delayed)" if live else ""),
    }
