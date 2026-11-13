"""Tiny JSON disk cache with TTL. Keyed by namespace + key; survives restarts."""
import hashlib
import json
import time
from typing import Any, Callable

from .config import CACHE_DIR


def _path(ns: str, key: str):
    h = hashlib.sha1(key.encode()).hexdigest()[:24]
    d = CACHE_DIR / ns
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{h}.json"


def get(ns: str, key: str, ttl: float | None = None) -> Any:
    p = _path(ns, key)
    if not p.exists():
        return None
    try:
        blob = json.loads(p.read_text())
    except Exception:
        return None
    if ttl is not None and time.time() - blob.get("t", 0) > ttl:
        return None
    return blob.get("v")


def put(ns: str, key: str, value: Any) -> Any:
    p = _path(ns, key)
    p.write_text(json.dumps({"t": time.time(), "k": key, "v": value}))
    return value


def age(ns: str, key: str) -> float | None:
    p = _path(ns, key)
    if not p.exists():
        return None
    try:
        return time.time() - json.loads(p.read_text()).get("t", 0)
    except Exception:
        return None


def memo(ns: str, key: str, ttl: float | None, fn: Callable[[], Any]) -> Any:
    v = get(ns, key, ttl)
    if v is not None:
        return v
    return put(ns, key, fn())
