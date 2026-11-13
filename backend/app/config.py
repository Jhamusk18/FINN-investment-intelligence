"""Runtime configuration. Everything comes from environment variables (.env supported)."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
# Model routing: cheap model for bulk work, stronger model only where reasoning matters.
FAST_MODEL = os.getenv("FINN_FAST_MODEL", "claude-haiku-5-5")
STRONG_MODEL = os.getenv("FINN_STRONG_MODEL", "claude-sonnet-5-5")

CACHE_DIR = Path(os.getenv("FINN_CACHE_DIR", BASE_DIR / "data" / "cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR = BASE_DIR / "data" / "sample"
FRONTEND_DIST = Path(os.getenv("FINN_FRONTEND_DIST", BASE_DIR.parent / "frontend" / "dist"))

# Force sample mode (e.g. for offline demos). Sample data is always labelled SIMULATED.
FORCE_SAMPLE = os.getenv("FINN_FORCE_SAMPLE", "0") == "1"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def llm_enabled() -> bool:
    return bool(ANTHROPIC_API_KEY)
