from __future__ import annotations

import sys
import urllib.request


def main() -> int:
    base = "http://127.0.0.1:8000"
    for path in ("/health", "/startup", "/docs"):
        with urllib.request.urlopen(base + path, timeout=5) as response:
            print(path, response.status)
    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
