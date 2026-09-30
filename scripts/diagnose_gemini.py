from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
load_dotenv(ENV_FILE, override=True)


def masked(value: str) -> str:
    value = value.strip()
    if not value:
        return "NOT SET"
    if len(value) <= 10:
        return "SET (short key)"
    return f"{value[:5]}...{value[-4:]}"


def main() -> int:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

    print(f"Project root : {ROOT}")
    print(f".env path    : {ENV_FILE}")
    print(f".env exists  : {ENV_FILE.exists()}")
    print(f"API key      : {masked(key)}")
    print(f"Model        : {model}")

    if not key:
        print("\nERROR: GEMINI_API_KEY is not loaded from .env.")
        return 1

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        print(f"\nERROR: google-genai is not installed: {exc}")
        print("Run: python -m pip install -U google-genai")
        return 1

    try:
        import google.genai
        print(f"google-genai : {getattr(google.genai, '__version__', 'unknown')}")
    except Exception:
        pass

    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=model,
            contents="Reply with exactly: POCKETSMART_GEMINI_OK",
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=50,
            ),
        )
        print("\nGemini API call: SUCCESS")
        print("Response:", (response.text or "").strip())
        return 0
    except Exception as exc:
        print("\nGemini API call: FAILED")
        print(f"{type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
