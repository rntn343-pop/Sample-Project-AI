#!/usr/bin/env python3
"""Cross-platform PocketSmart AI installer.

Creates/updates the project's virtual environment, installs dependencies, and
prompts the user for the Gemini API key. The script intentionally stays in the
terminal at the end so it is convenient to run by double-clicking when Python
is configured to open .py files in a console.
"""
from __future__ import annotations

import os
import platform
import secrets
import subprocess
import sys
from getpass import getpass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"
ENV_FILE = PROJECT_ROOT / ".env"
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"


def say(message: str = "") -> None:
    print(message, flush=True)


def pause() -> None:
    try:
        input("\nPress Enter to close this installer... ")
    except (EOFError, KeyboardInterrupt):
        pass


def fail(message: str, exit_code: int = 1) -> None:
    say(f"\nERROR: {message}")
    pause()
    raise SystemExit(exit_code)


def run(command: list[str], *, cwd: Path | None = None) -> None:
    say(f"> {' '.join(command)}")
    completed = subprocess.run(command, cwd=str(cwd or PROJECT_ROOT), check=False)
    if completed.returncode != 0:
        fail(f"Command failed with exit code {completed.returncode}.")


def venv_python() -> Path:
    if os.name == "nt":
        return PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    return PROJECT_ROOT / ".venv" / "bin" / "python"


def read_env() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_FILE.exists():
        return values
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def upsert_env(values: dict[str, str]) -> None:
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    elif ENV_EXAMPLE.exists():
        lines = ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    wanted = dict(values)
    found: set[str] = set()
    output: list[str] = []

    for raw in lines:
        stripped = raw.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in wanted:
                output.append(f"{key}={wanted[key]}")
                found.add(key)
                continue
        output.append(raw)

    if output and output[-1].strip():
        output.append("")

    for key, value in wanted.items():
        if key not in found:
            output.append(f"{key}={value}")

    ENV_FILE.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    say("=" * 70)
    say("PocketSmart AI - Installer")
    say("=" * 70)
    say(f"Operating system : {platform.system()} {platform.release()}")
    say(f"Python           : {platform.python_version()}")
    say(f"Project folder   : {PROJECT_ROOT}")

    if sys.version_info < (3, 10):
        fail("Python 3.10 or newer is required. Python 3.11 is recommended.")

    if not REQUIREMENTS.exists():
        fail("requirements.txt was not found. Run this installer from the project folder.")

    current = read_env()
    api_key = getpass("\nEnter your Gemini API key (leave blank to keep the existing key/use local fallback): ").strip()
    if not api_key:
        api_key = current.get("GEMINI_API_KEY", "")

    default_model = current.get("GEMINI_MODEL", "gemini-3.8-flash")

    say("\nGemini model examples:")
    say("  Latest     - gemini-3.8-flash")
    say("  Additional - gemini-3.7-flash")
    say("               gemini-3.6-flash")
    say("               gemini-3.5-flash")
    say("               gemini-3.5-flash-lite")
    say("               gemini-3.1-flash-lite")
    say("               gemini-2.5-flash")
    say("               gemini-2.5-flash-lite")
    say("  Enter any model ID supported by your Gemini API key.")

    model = input(
        f"Gemini model [{default_model}]: "
    ).strip() or default_model

    secret_key = current.get("SECRET_KEY", "").strip()
    if not secret_key or secret_key == "replace-this-with-a-long-random-secret":
        secret_key = secrets.token_urlsafe(48)
        say("Generated a new SECRET_KEY for this installation.")

    say("\n[1/4] Creating/updating Python virtual environment...")
    if not (PROJECT_ROOT / ".venv").exists():
        run([sys.executable, "-m", "venv", ".venv"])
    else:
        say("Virtual environment already exists; keeping it.")

    py = venv_python()
    if not py.exists():
        fail(f"Virtual environment Python executable was not found at: {py}")

    say("\n[2/4] Upgrading pip...")
    run([str(py), "-m", "pip", "install", "--upgrade", "pip"])

    say("\n[3/4] Installing project dependencies...")
    run([str(py), "-m", "pip", "install", "-r", str(REQUIREMENTS)])

    say("\n[4/4] Writing .env configuration...")
    upsert_env(
        {
            "SECRET_KEY": secret_key,
            "GEMINI_API_KEY": api_key,
            "GEMINI_MODEL": model,
        }
    )

    say("\n" + "=" * 70)
    say("Installation complete!")
    say("=" * 70)
    say(f"Environment : {ENV_FILE}")
    say(f"Model       : {model}")
    say(f"API key     : {'configured' if api_key else 'not configured (local fallback enabled)'}")
    say("\nTo launch PocketSmart AI, run:")
    if os.name == "nt":
        say("  python launch.py")
    else:
        say("  python3 launch.py")
    say("\nThe launcher will start the server, keep this terminal open, and open your browser automatically.")
    pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        say("\nInstallation cancelled.")
        pause()
