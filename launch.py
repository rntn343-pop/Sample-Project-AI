#!/usr/bin/env python3
"""Cross-platform PocketSmart AI launcher.

Starts Uvicorn using the project's virtual-environment Python, waits for the
health endpoint, opens the browser, and keeps the terminal attached to the
server until the user stops it with Ctrl+C.

Model selection examples:
    python launch.py --list-models
    python launch.py --model gemini-3.8-flash
    python launch.py --model gemini-3.5-flash-lite

The --model option overrides GEMINI_MODEL for this launch only. It does not
modify .env.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
HOST = os.getenv("POCKETSMART_HOST", "127.0.0.1")
PORT = int(os.getenv("POCKETSMART_PORT", "8000"))
URL = f"http://{HOST}:{PORT}"
HEALTH_URL = f"{URL}/health"

# These are examples of Gemini models suitable for PocketSmart-style text and
# multimodal recommendation workloads. Availability is account/region/API
# dependent; use `python launch.py --list-models` to see the examples and
# consult Google's current model catalog for your account's actual access.
MODEL_EXAMPLES: tuple[tuple[str, str], ...] = (
    ("gemini-3.8-flash", "Current stable flagship Flash model."),
    ("gemini-3.7-flash", "Previous-generation stable Flash model."),
    ("gemini-3.6-flash", "Stable Flash model balancing speed and multimodal capability."),
    ("gemini-3.5-flash", "Legacy stable Flash model for routine workloads."),
    ("gemini-3.5-flash-lite", "Fast, cost-efficient Flash-Lite model."),
    ("gemini-3.1-flash-lite", "Efficient Flash-Lite model for lightweight workloads."),
    ("gemini-flash-latest", "Alias for the latest Gemini Flash release."),
    ("gemini-flash-lite-latest", "Alias for the latest Gemini Flash-Lite release."),
    ("gemini-2.5-flash", "Older stable Flash model; API access may be limited."),
    ("gemini-2.5-flash-lite", "Older stable Flash-Lite model; API access may be limited."),
)


def say(message: str = "") -> None:
    print(message, flush=True)


def pause() -> None:
    try:
        input("\nPress Enter to close this launcher... ")
    except (EOFError, KeyboardInterrupt):
        pass


def venv_python() -> Path:
    if os.name == "nt":
        return PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    return PROJECT_ROOT / ".venv" / "bin" / "python"


def current_model_from_env() -> str:
    """Read GEMINI_MODEL from .env for display without importing the app."""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return "gemini-3.8-flash"

    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "GEMINI_MODEL":
            return value.strip().strip('"').strip("'") or "gemini-3.8-flash"

    return "gemini-3.8-flash"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch the PocketSmart AI web server."
    )
    parser.add_argument(
        "--model",
        help="Override GEMINI_MODEL for this launch only.",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Show example Gemini model IDs and exit.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start the server without opening a browser automatically.",
    )
    return parser.parse_args()


def print_model_examples() -> None:
    say("\nPocketSmart AI Gemini model examples")
    say("=" * 70)
    for model, description in MODEL_EXAMPLES:
        say(f"  {model:<28} {description}")
    say("=" * 70)
    say("These are examples, not a guarantee that every model is enabled for every key.")
    say("Check Google's current Gemini model catalog or use your account's model listing.")


def wait_for_server(timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=1.5) as response:
                return 200 <= response.status < 300
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.5)
    return False


def main() -> None:
    args = parse_args()

    if args.list_models:
        print_model_examples()
        pause()
        return

    say("=" * 70)
    say("PocketSmart AI - Launcher")
    say("=" * 70)
    say(f"Project : {PROJECT_ROOT}")
    say(f"Web app : {URL}")

    configured_model = current_model_from_env()
    selected_model = args.model.strip() if args.model else configured_model

    say(f"Gemini model: {selected_model}")

    if args.model:
        say("Model override: command line (does not modify .env)")

    py = venv_python()
    if not py.exists():
        say("\nPocketSmart AI is not installed yet.")
        say("Run the installer first:")
        say(f"  {sys.executable} install.py")
        pause()
        return

    command = [
        str(py),
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        HOST,
        "--port",
        str(PORT),
    ]

    child_env = os.environ.copy()
    child_env["GEMINI_MODEL"] = selected_model

    say("\nStarting PocketSmart AI server...")
    say("The server output will remain visible in this terminal.")
    say("Press Ctrl+C to stop PocketSmart AI.\n")

    process = subprocess.Popen(
        command,
        cwd=str(PROJECT_ROOT),
        env=child_env,
    )

    try:
        if wait_for_server():
            say(f"\nServer is ready: {URL}")
            if not args.no_browser:
                say("Opening your default web browser...")
                webbrowser.open(URL, new=2)
            else:
                say("Browser launch disabled (--no-browser).")
        else:
            say("\nThe server did not report healthy within 30 seconds.")
            say(f"Try opening {URL} manually if Uvicorn is still starting.")

        return_code = process.wait()
        say(f"\nPocketSmart AI server stopped (exit code {return_code}).")
    except KeyboardInterrupt:
        say("\nStopping PocketSmart AI...")
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        say("PocketSmart AI has been stopped.")
    finally:
        pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pause()
