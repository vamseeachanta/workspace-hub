#!/usr/bin/env bash
# Run sync, then collect equality even when a checkout refuses synchronization.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${HYGIENE_MANIFEST:?manifest required}"
: "${HYGIENE_ROOT:?root required}"
: "${HYGIENE_STATE:?status destination required}"
: "${HYGIENE_EQUALITY_OUTPUT:?equality destination required}"
: "${HYGIENE_PUBLIC_ALIAS:?public alias required}"
: "${HYGIENE_COLLECT_TIMEOUT_SECONDS:?collection timeout required}"
# A collector override permits disposable contract tests without probing installed software.
COLLECTOR="${HYGIENE_COLLECTOR:-${SCRIPT_DIR}/../readiness/collect-equality.sh}"
rc=0
bash "${SCRIPT_DIR}/repo-sync.sh" --manifest "$HYGIENE_MANIFEST" \
  --root "$HYGIENE_ROOT" --state "$HYGIENE_STATE" || rc=$?
# Buffer until collection succeeds; partial YAML from a failed collector is not evidence.
if evidence="$(EQ_PUBLIC_HOST="$HYGIENE_PUBLIC_ALIAS" timeout "$HYGIENE_COLLECT_TIMEOUT_SECONDS" \
    bash "$COLLECTOR" --stdout --machine "$HYGIENE_PUBLIC_ALIAS")"; then
  printf '%s\n' "$evidence" | bash "${SCRIPT_DIR}/repo-sync.sh" --attach-equality \
    --state "$HYGIENE_STATE" --output "$HYGIENE_EQUALITY_OUTPUT" || rc=$?
else
  rc=$?
fi
exit "$rc"
