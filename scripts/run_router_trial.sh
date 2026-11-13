#!/usr/bin/env bash
# Run real third-party gateways against strictly synthetic local HTTP providers.
set -euo pipefail

candidate="${1:-}"
case "$candidate" in
  litellm|gomodel|bifrost|portkey) ;;
  *) echo "Usage: bash scripts/run_router_trial.sh {litellm|gomodel|bifrost|portkey}" >&2; exit 2 ;;
esac

command -v docker >/dev/null || { echo "Docker required" >&2; exit 2; }
command -v python3 >/dev/null || { echo "Python 3 required" >&2; exit 2; }
mkdir -p reports
container="lea-router-lab-${candidate}-$$"
mock_pids=()
cleanup() {
  docker rm -f "$container" >/dev/null 2>&1 || true
  for pid in "${mock_pids[@]}"; do kill "$pid" >/dev/null 2>&1 || true; done
}
trap cleanup EXIT

for pair in "primary:19100" "backup:19101" "paid:19102"; do
  tier="${pair%:*}"
  port="${pair#*:}"
  python3 -m router_lab.mock_provider --tier "$tier" --port "$port" >"reports/mock-${tier}.log" 2>&1 &
  mock_pids+=("$!")
done

python3 - <<'PY'
import time, urllib.request
for port in (19100, 19101, 19102):
    for _ in range(100):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=0.3) as r:
                if r.status == 200: break
        except Exception:
            time.sleep(0.1)
    else:
        raise SystemExit(f"mock provider {port} not ready")
PY

if [[ "$candidate" == "litellm" ]]; then
  image="docker.litellm.ai/berriai/litellm@sha256:11175975a3093e05e92faee2fe2fe3412a3ae2fcaa849eb0fe25d5f0d8bcb2e9"
  port=4000
  # No database, hence no claim that LiteLLM enforces real dollar budgets.
  docker run -d --name "$container" --network host \
    -v "$PWD/router_lab/profiles/litellm.yaml:/app/config.yaml:ro" \
    -e LITELLM_MASTER_KEY=sk-lab-synthetic-only \
    "$image" --config /app/config.yaml > /dev/null
  python3 -m router_lab.wait --url "http://127.0.0.1:${port}/v1/models" --token sk-lab-synthetic-only --seconds 150
  python3 -m router_lab.bench --candidate litellm \
    --gateway "http://127.0.0.1:${port}" --profile litellm.yaml \
    --model lab-primary --paid-model lab-paid --expect-fallback \
    --output reports/litellm.json
elif [[ "$candidate" == "bifrost" ]]; then
  image="maximhq/bifrost@sha256:5ec9873acaf1687556b6e4dd854b92b539d9debf87a5a683b66338648b84d3c8"
  port=8080
  docker run -d --name "$container" --network host \
    -v "$PWD/router_lab/profiles/bifrost.json:/app/data/config.json:ro" \
    "$image" > /dev/null
  python3 -m router_lab.wait --url "http://127.0.0.1:${port}/v1/models" --token sk-lab-synthetic-only --seconds 150
  python3 -m router_lab.bench --candidate bifrost \
    --gateway "http://127.0.0.1:${port}" --profile bifrost.json \
    --model lab-primary/lab-model --paid-model lab-paid/lab-model --expect-fallback \
    --output reports/bifrost.json
elif [[ "$candidate" == "portkey" ]]; then
  image="portkeyai/gateway@sha256:97f094d9c8a764cbfaa2a7138c0017b247ca923bb06db1b4c13b7f8a33b5200d"
  port=8787
  # Explicit allowlist for local-only tests; never use this image with real secrets.
  docker run -d --name "$container" --network host \
    -e TRUSTED_CUSTOM_HOSTS=127.0.0.1,localhost \
    "$image" > /dev/null
  python3 -m router_lab.wait --url "http://127.0.0.1:${port}/public/" --token sk-lab-synthetic-only --seconds 150
  python3 -m router_lab.bench --candidate portkey \
    --gateway "http://127.0.0.1:${port}" --profile header-config \
    --model lab-model --paid-model lab-model --expect-fallback \
    --output reports/portkey.json
else
  image="enterpilot/gomodel@sha256:c50627e093ff88bff311e582a43d7de14e0be29d52cb333ecb3191eac7874f05"
  port=8080
  docker run -d --name "$container" --network host \
    -e GOMODEL_MASTER_KEY=sk-lab-synthetic-only \
    -e VLLM_BASE_URL=http://127.0.0.1:19100/v1 \
    -e VLLM_MODELS=lab-model \
    "$image" > /dev/null
  python3 -m router_lab.wait --url "http://127.0.0.1:${port}/v1/models" --token sk-lab-synthetic-only --seconds 120
  python3 -m router_lab.bench --candidate gomodel \
    --gateway "http://127.0.0.1:${port}" --profile env-vllm \
    --model vllm/lab-model \
    --output reports/gomodel.json
fi

docker inspect --format 'Local image ID: {{.Image}}' "$container" \
  > "reports/${candidate}-image.txt"
printf 'Image ref: %s\n' "$image" >> "reports/${candidate}-image.txt"
docker stats --no-stream --format 'Memory (snapshot): {{.MemUsage}}; CPU (snapshot): {{.CPUPerc}}' "$container" \
  > "reports/${candidate}-metrics.txt"
echo "Candidate '$candidate': synthetic trial finished."
