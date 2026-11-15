"""Runtime configuration. Everything comes from environment variables (.env supported)."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Provider: the first key that is set wins (Anthropic > Groq free tier > Gemini free tier).
PROVIDER = os.getenv("FINN_LLM_PROVIDER", "").strip().lower() or (
    "anthropic" if ANTHROPIC_API_KEY else "groq" if GROQ_API_KEY else "gemini" if GEMINI_API_KEY else "none")

# Free-tier providers share one OpenAI-compatible request format (Bearer key, JSON mode).
OPENAI_COMPAT = {
    "groq": ("https://api.groq.com/openai/v1/chat/completions", GROQ_API_KEY),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", GEMINI_API_KEY),
}

# Model routing: cheap model for bulk work, stronger model only where reasoning matters.
_DEFAULT_MODELS = {
    "groq": ("openai/gpt-oss-20b", "openai/gpt-oss-120b"),
    "gemini": ("gemini-flash-lite-latest", "gemini-flash-lite-latest"),
    "anthropic": ("claude-haiku-5-5", "claude-sonnet-5-5"),
}
_fast, _strong = _DEFAULT_MODELS.get(PROVIDER, _DEFAULT_MODELS["anthropic"])
FAST_MODEL = os.getenv("FINN_FAST_MODEL", _fast)
STRONG_MODEL = os.getenv("FINN_STRONG_MODEL", _strong)

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
    if PROVIDER == "anthropic":
        return bool(ANTHROPIC_API_KEY)
    return PROVIDER in OPENAI_COMPAT and bool(OPENAI_COMPAT[PROVIDER][1])
