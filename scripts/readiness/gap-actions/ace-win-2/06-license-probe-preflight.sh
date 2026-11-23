#!/usr/bin/env bash
# Read-only solver probe summary for the ace-win-2 BELOW-BASELINE solver row.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# shellcheck source=../../lib/probe-solvers.sh
source scripts/readiness/lib/probe-solvers.sh

printf 'orcaflex=%s evidence=%s\n' "$(probe_orcaflex)" "$(probe_orcaflex_evidence)"
printf 'orcawave=%s evidence=%s\n' "$(probe_orcawave)" "$(probe_orcawave_evidence)"
printf 'ansys=%s evidence=%s\n' "$(probe_ansys)" "$(probe_ansys_evidence)"
printf 'aqwa=%s evidence=%s\n' "$(probe_aqwa)" "$(probe_aqwa_evidence)"

cat <<'EOF'

Interpretation:
  The ace-win-2 baseline requires "licensed" for these solvers.
  Current shared probes intentionally emit only present/absent/unknown unless a real
  license checkout/status signal exists. Install roots and SDK imports do not satisfy
  the licensed-solver baseline.

Next executable action:
  land or create the Windows license-status probe, then refresh equality evidence.
EOF
