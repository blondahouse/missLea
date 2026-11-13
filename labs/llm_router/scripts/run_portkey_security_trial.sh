#!/usr/bin/env bash
# This intentionally reproduces a published weakness against local mocks only.
set -euo pipefail
# Work from repository root regardless of the caller's current directory.
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
mkdir -p reports
container="lea-portkey-security-$$"
mock_pid=""
cleanup() {
  docker rm -f "$container" >/dev/null 2>&1 || true
  [[ -z "$mock_pid" ]] || kill "$mock_pid" >/dev/null 2>&1 || true
}
trap cleanup EXIT
python3 -m labs.llm_router.mock_provider --tier primary --port 19100 \
  > reports/portkey-security-mock.log 2>&1 &
mock_pid="$!"
python3 - <<'PY'
import time, urllib.request
for _ in range(100):
    try:
        with urllib.request.urlopen("http://127.0.0.1:19100/health", timeout=0.3) as resp:
            if resp.status == 200: break
    except Exception:
        time.sleep(0.1)
else:
    raise SystemExit("mock provider did not start")
PY
# Do NOT allow localhost as a custom host: the diagnostic checks bypass.
# Gateway runs only in an isolated CI VM with a synthetic-only auth token.
image="portkeyai/gateway@sha256:97f094d9c8a764cbfaa2a7138c0017b247ca923bb06db1b4c13b7f8a33b5200d"
docker run -d --name "$container" --network host \
  -e TRUSTED_CUSTOM_HOSTS=api.openai.com "$image" >/dev/null
python3 -m labs.llm_router.wait --url http://127.0.0.1:8787/public/ \
  --token sk-lab-synthetic-only --seconds 120
python3 -m labs.llm_router.portkey_security
printf '%s\n' "$image" >reports/portkey-security-image.txt
