#!/usr/bin/env bash
# comprehensive-learning-nightly.sh
# Nightly cron wrapper for ace-linux-1: pull state, rsync sessions, run pipeline.
# set -euo pipefail ensures git pull failure aborts before the pipeline runs.
set -euo pipefail

cd /mnt/local-analysis/workspace-hub

# Preflight: confirm PyYAML available (required for Phase 7 WRK frontmatter validation)
python3 -c "import yaml" 2>/dev/null || {
  echo "ERROR: PyYAML not installed — install python3-yaml before scheduling this cron" >&2
  echo "       Phase 7 will create malformed WRK files without it." >&2
  exit 1
}

# Step 1: pull derived state files (hard gate — pipeline must not run on stale state)
git pull --no-rebase origin main

# Step 2: rsync raw sessions from contributor machines — each independently best-effort
rsync -az --no-delete --timeout=30 \
  -e "ssh -o ConnectTimeout=10 -o BatchMode=yes" \
  ace-linux-2:.claude/state/sessions/ \
  .claude/state/sessions-archive/ace-linux-2/ 2>/dev/null || true

rsync -az --no-delete --timeout=30 \
  -e "ssh -o ConnectTimeout=10 -o BatchMode=yes" \
  ACMA-ANSYS05:.claude/state/sessions/ \
  .claude/state/sessions-archive/acma-ansys05/ 2>/dev/null || true

# Step 3: run pipeline
exec claude --skill comprehensive-learning
