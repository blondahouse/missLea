#!/usr/bin/env bash
# Run real third-party gateways against strictly synthetic local HTTP providers.
set -euo pipefail
# Work from repository root regardless of the caller's current directory.
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

candidate="${1:-}"
case "$candidate" in
  litellm|gomodel|bifrost|portkey) ;;
  *) echo "Usage: bash labs/llm_router/scripts/run_router_trial.sh {litellm|gomodel|bifrost|portkey}" >&2; exit 2 ;;
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

for pair in "primary:19100" "backup:19101" "paid:19102" "forbidden:19103"; do
  tier="${pair%:*}"
  port="${pair#*:}"
  python3 -m labs.llm_router.mock_provider --tier "$tier" --port "$port" >"reports/mock-${tier}.log" 2>&1 &
  mock_pids+=("$!")
done

python3 - <<'PY'
import time, urllib.request
for port in (19100, 19101, 19102, 19103):
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
  docker image inspect "$image" >/dev/null 2>&1 || docker pull "$image" >/dev/null
  start_ms=$(date +%s%3N)
  docker run -d --name "$container" --network host \
    -v "$PWD/labs/llm_router/profiles/litellm.yaml:/app/config.yaml:ro" \
    -e LITELLM_MASTER_KEY=sk-lab-gateway-client \
    "$image" --config /app/config.yaml > /dev/null
  python3 -m labs.llm_router.wait --url "http://127.0.0.1:${port}/v1/models" --token sk-lab-gateway-client --seconds 150
  cold_ready_ms=$(( $(date +%s%3N) - start_ms ))
  python3 -m labs.llm_router.bench --candidate litellm \
    --gateway "http://127.0.0.1:${port}" --profile litellm.yaml \
    --model lab-primary --paid-model lab-paid --expect-fallback \
    --output reports/litellm.json
  python3 -m labs.llm_router.fair_latency --candidate litellm \
    --gateway "http://127.0.0.1:${port}" --model lab-primary \
    --output reports/litellm-latency.json
elif [[ "$candidate" == "bifrost" ]]; then
  image="maximhq/bifrost@sha256:5ec9873acaf1687556b6e4dd854b92b539d9debf87a5a683b66338648b84d3c8"
  port=8080
  docker image inspect "$image" >/dev/null 2>&1 || docker pull "$image" >/dev/null
  start_ms=$(date +%s%3N)
  docker run -d --name "$container" --network host \
    -v "$PWD/labs/llm_router/profiles/bifrost.json:/app/data/config.json:ro" \
    "$image" > /dev/null
  if ! python3 -m labs.llm_router.wait --url "http://127.0.0.1:${port}/health" --token sk-bf-lab-gateway-client --seconds 60; then
    docker logs "$container" >reports/bifrost-startup.txt 2>&1 || true
    echo "Bifrost hardened profile failed health readiness; see startup evidence" >&2
    exit 1
  fi
  cold_ready_ms=$(( $(date +%s%3N) - start_ms ))
  python3 -m labs.llm_router.bench --candidate bifrost \
    --gateway "http://127.0.0.1:${port}" --profile bifrost.json \
    --model lab-primary/lab-model --paid-model lab-paid/lab-model --expect-fallback \
    --output reports/bifrost.json
  python3 -m labs.llm_router.fair_latency --candidate bifrost \
    --gateway "http://127.0.0.1:${port}" --model lab-primary/lab-model \
    --output reports/bifrost-latency.json
elif [[ "$candidate" == "portkey" ]]; then
  image="portkeyai/gateway@sha256:97f094d9c8a764cbfaa2a7138c0017b247ca923bb06db1b4c13b7f8a33b5200d"
  port=8787
  # Explicit allowlist for local-only tests; never use this image with real secrets.
  docker image inspect "$image" >/dev/null 2>&1 || docker pull "$image" >/dev/null
  start_ms=$(date +%s%3N)
  docker run -d --name "$container" --network host \
    -e TRUSTED_CUSTOM_HOSTS=127.0.0.1,localhost \
    "$image" > /dev/null
  python3 -m labs.llm_router.wait --url "http://127.0.0.1:${port}/public/" --token sk-lab-gateway-client --seconds 150
  cold_ready_ms=$(( $(date +%s%3N) - start_ms ))
  python3 -m labs.llm_router.bench --candidate portkey \
    --gateway "http://127.0.0.1:${port}" --profile header-config \
    --model lab-model --paid-model lab-model --expect-fallback \
    --output reports/portkey.json
  python3 -m labs.llm_router.fair_latency --candidate portkey \
    --gateway "http://127.0.0.1:${port}" --model lab-model \
    --output reports/portkey-latency.json
else
  image="enterpilot/gomodel@sha256:c50627e093ff88bff311e582a43d7de14e0be29d52cb333ecb3191eac7874f05"
  port=8080
  docker image inspect "$image" >/dev/null 2>&1 || docker pull "$image" >/dev/null
  start_ms=$(date +%s%3N)
  docker run -d --name "$container" --network host \
    -e GOMODEL_MASTER_KEY=sk-lab-gateway-client \
    -e VLLM_BASE_URL=http://127.0.0.1:19100/v1 \
    -e VLLM_MODELS=lab-model \
    -e SGLANG_BASE_URL=http://127.0.0.1:19101/v1 \
    -e SGLANG_MODELS=lab-model \
    -e OPENAI_API_KEY=sk-lab-synthetic-only \
    -e OPENAI_BASE_URL=http://127.0.0.1:19102/v1 \
    -e OPENAI_MODELS=lab-model \
    -e VIRTUAL_MODELS='[{"source":"lab-free","strategy":"failover","targets":[{"model":"vllm/lab-model"},{"model":"sglang/lab-model"}]}]' \
    -e RETRY_MAX_RETRIES=0 \
    -e GOMODEL_OFFLINE=true \
    "$image" > /dev/null
  python3 -m labs.llm_router.wait --url "http://127.0.0.1:${port}/v1/models" --token sk-lab-gateway-client --seconds 120
  cold_ready_ms=$(( $(date +%s%3N) - start_ms ))
  python3 -m labs.llm_router.bench --candidate gomodel \
    --gateway "http://127.0.0.1:${port}" --profile three-upstream-virtual-failover \
    --model lab-free --paid-model openai/lab-model --expect-fallback \
    --output reports/gomodel.json
  python3 -m labs.llm_router.fair_latency --candidate gomodel \
    --gateway "http://127.0.0.1:${port}" --model lab-free \
    --output reports/gomodel-latency.json
fi

case "$candidate" in
  litellm) security_model=lab-primary; security_paid_model=lab-paid ;;
  bifrost) security_model=lab-primary/lab-model; security_paid_model=lab-paid/lab-model ;;
  portkey) security_model=lab-model; security_paid_model=lab-model ;;
  gomodel) security_model=lab-free; security_paid_model=openai/lab-model ;;
esac

printf 'Cold ready, image already available: %s ms\n' "$cold_ready_ms" > "reports/${candidate}-cold-ready.txt"
python3 -m labs.llm_router.security_suite \
  --candidate "$candidate" --gateway "http://127.0.0.1:${port}" \
  --model "$security_model" --paid-model "$security_paid_model" \
  --output "reports/${candidate}-security.json"

# Best-effort pinned binary/package version evidence (never infer from "latest").
case "$candidate" in
  litellm)
    docker exec "$container" python -c 'import importlib.metadata; print(importlib.metadata.version("litellm"))' \
      > "reports/${candidate}-version.txt" 2>/dev/null || echo "version not exposed" > "reports/${candidate}-version.txt"
    ;;
  bifrost)
    docker logs "$container" 2>&1 | grep -E -m 1 'v[0-9]+[.][0-9]+[.][0-9]+' \
      > "reports/${candidate}-version.txt" || echo "version not exposed" > "reports/${candidate}-version.txt"
    ;;
  gomodel|portkey)
    printf '%s\n' "version not independently verified in this run" > "reports/${candidate}-version.txt"
    ;;
esac

docker inspect --format 'Local image ID: {{.Image}}' "$container" \
  > "reports/${candidate}-image.txt"
printf 'Image ref: %s\n' "$image" >> "reports/${candidate}-image.txt"
docker stats --no-stream --format 'Memory (snapshot): {{.MemUsage}}; CPU (snapshot): {{.CPUPerc}}' "$container" \
  > "reports/${candidate}-metrics.txt"
echo "Candidate '$candidate': synthetic trial finished."
