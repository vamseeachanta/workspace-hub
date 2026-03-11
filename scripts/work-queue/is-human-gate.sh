#!/usr/bin/env bash
# is-human-gate.sh <stage_number>
# Exit 0 if stage requires human approval (STOP and wait).
# Exit 1 if stage is auto-proceed (continue immediately, no user prompt).
# Usage: is-human-gate.sh 7 && echo "STOP" || echo "CONTINUE"
set -euo pipefail

STAGE="${1:?Usage: is-human-gate.sh <stage_number>}"
STAGES_DIR="$(cd "$(dirname "$0")/stages" && pwd)"

# Canonical human-gate stages (matches stage YAML human_gate: true)
case "$STAGE" in
  1|5|7|17) exit 0 ;;  # STOP — await user
  *)
    # Also check the YAML for forward-compatibility
    YAML=$(ls "${STAGES_DIR}/stage-$(printf '%02d' "$STAGE")-"*.yaml 2>/dev/null | head -1)
    if [[ -n "$YAML" ]] && grep -q "^human_gate: true" "$YAML"; then
      exit 0  # STOP
    fi
    exit 1  # CONTINUE
    ;;
esac
