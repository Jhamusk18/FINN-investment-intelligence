"""Demo portfolio + ad-hoc research set. The engine itself is not limited to these:
any company resolvable on screener.in can be researched (see connectors/screener.search)."""

PORTFOLIO = [
    # symbol, name, sector
    ("INFY", "Infosys Ltd", "IT Services"),
    ("TCS", "Tata Consultancy Services Ltd", "IT Services"),
    ("RELIANCE", "Reliance Industries Ltd", "Conglomerate"),
    ("HDFCBANK", "HDFC Bank Ltd", "Private Bank"),
    ("ICICIBANK", "ICICI Bank Ltd", "Private Bank"),
    ("BAJFINANCE", "Bajaj Finance Ltd", "NBFC"),
    ("LT", "Larsen & Toubro Ltd", "Engineering & Construction"),
    ("SUNPHARMA", "Sun Pharmaceutical Industries Ltd", "Pharma"),
    ("TITAN", "Titan Company Ltd", "Consumer Discretionary"),
    ("ASIANPAINT", "Asian Paints Ltd", "Paints"),
    ("MARUTI", "Maruti Suzuki India Ltd", "Automobiles"),
    ("TATASTEEL", "Tata Steel Ltd", "Metals"),
    ("ITC", "ITC Ltd", "FMCG"),
    ("DMART", "Avenue Supermarts Ltd", "Retail"),
    ("POLYCAB", "Polycab India Ltd", "Cables & Wires"),
    ("PERSISTENT", "Persistent Systems Ltd", "IT Services"),
    ("DIXON", "Dixon Technologies (India) Ltd", "Electronics Mfg"),
    ("IRCTC", "Indian Railway Catering & Tourism Corp Ltd", "Travel"),
]

# Zomato now trades as ETERNAL (Eternal Ltd) on NSE/screener.
ADHOC = [
    ("ETERNAL", "Eternal Ltd (Zomato)", "Internet / Food delivery"),
    ("TRENT", "Trent Ltd", "Retail"),
    ("KPITTECH", "KPIT Technologies Ltd", "Auto Software"),
    ("HAL", "Hindustan Aeronautics Ltd", "Defence"),
]

BANKS = {"HDFCBANK", "ICICIBANK"}  # EBITDA is not meaningful for banks

INDICES = [
    ("^NSEI", "NIFTY 50"),
    ("^BSESN", "SENSEX"),
    ("^CNXIT", "NIFTY IT"),
]


def as_dicts(rows, group):
    return [{"symbol": s, "name": n, "sector": sec, "group": group} for s, n, sec in rows]


ALL_KNOWN = {s: n for s, n, _ in PORTFOLIO + ADHOC}
