#!/usr/bin/env bash
# Same CI runner, same three mock ports, pinned images, no real provider credentials.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
mkdir -p reports

# Pre-pull all four pinned images BEFORE measuring cold readiness.
images=(
  "docker.litellm.ai/berriai/litellm@sha256:11175975a3093e05e92faee2fe2fe3412a3ae2fcaa849eb0fe25d5f0d8bcb2e9"
  "enterpilot/gomodel@sha256:c50627e093ff88bff311e582a43d7de14e0be29d52cb333ecb3191eac7874f05"
  "maximhq/bifrost@sha256:5ec9873acaf1687556b6e4dd854b92b539d9debf87a5a683b66338648b84d3c8"
  "portkeyai/gateway@sha256:97f094d9c8a764cbfaa2a7138c0017b247ca923bb06db1b4c13b7f8a33b5200d"
)
for image in "${images[@]}"; do docker pull "$image" >/dev/null; done
# Rotate order between CI runs to reduce (not eliminate) position bias.
candidates=(litellm gomodel bifrost portkey)
rotation=$(( ${GITHUB_RUN_NUMBER:-0} % 4 ))
ordered=("${candidates[@]:rotation}" "${candidates[@]:0:rotation}")
printf 'Candidate order: %s\n' "${ordered[*]}" > reports/comparison-environment.txt
uname -a >> reports/comparison-environment.txt
python3 --version >> reports/comparison-environment.txt
failures=0
for candidate in "${ordered[@]}"; do
  echo "::group::Fair synthetic trial: $candidate"
  if bash labs/llm_router/scripts/run_router_trial.sh "$candidate"; then
    echo "$candidate: complete" >> reports/comparison-environment.txt
  else
    echo "$candidate: failed to execute" >> reports/comparison-environment.txt
    failures=$((failures + 1))
  fi
  echo "::endgroup::"
done
python3 -m labs.llm_router.fair_matrix \
  --reports reports --output reports/fair-comparison.json || failures=$((failures + 1))
if (( failures )); then
  echo "::error title=Incomplete Fair Comparison::Check failure artifacts; no winner was chosen"
  exit 1
fi
