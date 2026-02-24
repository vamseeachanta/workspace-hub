#!/usr/bin/env bash
# comprehensive-learning-nightly.sh
# Nightly cron wrapper for ace-linux-1: pull state, rsync sessions, run pipeline.
# set -euo pipefail ensures git pull failure aborts before the pipeline runs.
set -euo pipefail

WORKSPACE_HUB="/mnt/local-analysis/workspace-hub"
cd "$WORKSPACE_HUB"

# Preflight: confirm PyYAML available (required for Phase 7 WRK frontmatter validation)
source scripts/lib/python-resolver.sh
${PYTHON} -c "import yaml" 2>/dev/null || {
  echo "ERROR: PyYAML not installed — install python3-yaml before scheduling this cron" >&2
  echo "       Phase 7 will create malformed WRK files without it." >&2
  exit 1
}

# Step 1: pull derived state files (hard gate — pipeline must not run on stale state)
mkdir -p "$WORKSPACE_HUB/.claude/state/learning-reports" 2>/dev/null
git pull --no-rebase origin main

# Step 2: rsync raw sessions from contributor machines — each independently best-effort
# ace-linux-2: sessions at /mnt/workspace-hub/.claude/state/sessions/ (not ~/.claude/state/)
rsync -az --timeout=30 \
  -e "ssh -o ConnectTimeout=10 -o BatchMode=yes" \
  ace-linux-2:/mnt/workspace-hub/.claude/state/sessions/ \
  "$WORKSPACE_HUB/.claude/state/sessions-archive/ace-linux-2/" 2>/dev/null || true

rsync -az --timeout=30 \
  -e "ssh -o ConnectTimeout=10 -o BatchMode=yes" \
  ACMA-ANSYS05:.claude/state/sessions/ \
  "$WORKSPACE_HUB/.claude/state/sessions-archive/acma-ansys05/" 2>/dev/null || true

# Step 3b: AI agent readiness — CLI presence + version check (best-effort — WRK-306)
echo "--- AI agent readiness $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/readiness/ai-agent-readiness.sh || true

# Step 4: validate skill frontmatter (best-effort — WRK-308)
echo "--- Skill validation $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/skills/validate-skills.sh .claude/skills || \
  echo "WARNING: skill validation issues found — see above"

# Step 5: readiness checks (best-effort — 9 checks, WRK-308)
echo "--- Readiness checks $(date +%Y-%m-%dT%H:%M:%S) ---"
READINESS_SCRIPT="scripts/readiness/nightly-readiness.sh"
[[ -f "$READINESS_SCRIPT" ]] && bash "$READINESS_SCRIPT" || \
  echo "INFO: nightly-readiness.sh not found at $READINESS_SCRIPT"

# Step 6: test health check — detect code-without-test sessions (best-effort — WRK-236)
echo "--- Test health check $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/readiness/test-health-check.sh || true

# Step 7: provider cost tracking — token spend per session and WRK item (best-effort — WRK-237)
echo "--- Provider cost tracking $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/readiness/provider-cost-tracker.sh || true

# Step 3: run pipeline
# Cron usage: bash scripts/cron/comprehensive-learning-nightly.sh >> /mnt/local-analysis/workspace-hub/.claude/state/learning-reports/cron.log 2>&1
exec claude --skill comprehensive-learning
