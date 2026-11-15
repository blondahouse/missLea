"""One-time Infisical self-hosted bootstrap/health probe; NO secrets API testing.

Documentary Cloud Free vs self-host feature gaps must be assessed separately.
An HTTP 200 from /api/status does not prove machine identity, vault security,
recovery or authorization. No account signup is performed.
"""
from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

URL = "http://127.0.0.1:18080/api/status"


def trial() -> dict:
    started = time.monotonic()
    for _ in range(100):
        try:
            with urlopen(URL, timeout=4) as res:
                # Body is intentionally ignored; do not leak startup settings.
                if res.status == 200:
                    return {
                        "provider": "infisical",
                        "mode": "self_hosted_ephemeral_three_containers",
                        "synthetic_only": True,
                        "checks": {"http_health_ready": True},
                        "not_tested": [
                            "machine identity, authorization scopes and revoke",
                            "managed Infisical Cloud Free feature entitlements",
                            "security broker / credential exposure",
                            "encrypted database recovery and key rotation",
                            "audit retention and host-loss recovery",
                        ],
                        "setup_seconds": round(time.monotonic() - started, 1),
                        "status": "PASS_HEALTH_ONLY_NOT_COMPARABLE_SECURITY",
                    }
        except (HTTPError, URLError, TimeoutError, OSError):
            pass
        time.sleep(2)
    raise RuntimeError("Infisical did not respond to /api/status on localhost")


if __name__ == "__main__":
    print(json.dumps(trial(), indent=2))
