"""Wait for a local gateway to be reachable before probing it."""
from __future__ import annotations

import argparse
import time
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--seconds", type=int, default=90)
    args = parser.parse_args()
    if not args.url.startswith("http://127.0.0.1:"):
        raise SystemExit("local only")
    stop = time.monotonic() + args.seconds
    while time.monotonic() < stop:
        request = urllib.request.Request(
            args.url, headers={"Authorization": "Bearer " + args.token}
        )
        try:
            with urllib.request.urlopen(request, timeout=2) as response:
                if response.status == 200:
                    print("Gateway ready")
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(1)
    raise SystemExit("Gateway readiness timeout")


if __name__ == "__main__":
    main()
