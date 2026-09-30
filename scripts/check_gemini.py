from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Gemini text or multimodal connectivity")
    parser.add_argument("--image", type=Path, help="Optional local image to include in the prompt")
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    if not api_key:
        print("GEMINI_API_KEY is not set. Configure .env first.")
        return 1

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("google-genai is not installed. Run: pip install -r requirements.txt")
        return 1

    client = genai.Client(api_key=api_key)
    prompt = "Reply with exactly one sentence confirming that PocketSmart AI Gemini connectivity works."
    contents: list[object] = [prompt]

    if args.image:
        if not args.image.exists():
            print(f"Image not found: {args.image}")
            return 1
        mime = "image/jpeg"
        suffix = args.image.suffix.lower()
        if suffix == ".png":
            mime = "image/png"
        elif suffix == ".webp":
            mime = "image/webp"
        contents.append(types.Part.from_bytes(data=args.image.read_bytes(), mime_type=mime))
        contents.append("Briefly describe only the visible colors and clothing style in this outfit image.")

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=200),
    )
    print(response.text or "No text returned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
