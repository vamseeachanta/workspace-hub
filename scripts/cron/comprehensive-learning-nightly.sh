#!/usr/bin/env bash
# comprehensive-learning-nightly.sh
# Nightly cron wrapper for dev-primary: pull state, rsync sessions, run pipeline.
# set -euo pipefail ensures git pull failure aborts before the pipeline runs.
set -euo pipefail

# Ensure uv and other user-installed tools are on PATH (cron has minimal PATH)
export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"

WORKSPACE_HUB="$(cd "$(dirname "$0")/../.." && pwd)"
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
# Use shared git-safe library for coordinated git access (#1548)
GIT_SAFE_LOG_PREFIX="[comprehensive-learning]"
source "${WORKSPACE_HUB}/scripts/cron/lib/git-safe.sh"
git_safe_init "$WORKSPACE_HUB"
git_safe_pull

# Step 2: rsync raw sessions from contributor machines — each independently best-effort
# ace-linux-2: sessions at /mnt/workspace-hub/.claude/state/sessions/ (not ~/.claude/state/)
rsync -az --timeout=30 \
  -e "ssh -o ConnectTimeout=10 -o BatchMode=yes" \
  ace-linux-2:/mnt/workspace-hub/.claude/state/sessions/ \
  "$WORKSPACE_HUB/.claude/state/sessions-archive/ace-linux-2/" 2>/dev/null || true

rsync -az --timeout=30 \
  -e "ssh -o ConnectTimeout=10 -o BatchMode=yes" \
  licensed-win-1:.claude/state/sessions/ \
  "$WORKSPACE_HUB/.claude/state/sessions-archive/licensed-win-1/" 2>/dev/null || true

# Step 2b: export Hermes sessions to orchestrator JSONL (best-effort — #1719)
echo "--- Hermes session export $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/cron/hermes-session-export.sh 2>&1 || \
  echo "WARNING: Hermes session export failed"

# Step 2b2: export Codex sessions to orchestrator JSONL (best-effort — #194)
echo "--- Codex session export $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/cron/codex-session-export.sh 2>&1 || \
  echo "WARNING: Codex session export failed"

# Step 2b3: export Gemini sessions to orchestrator JSONL (best-effort — provider parity)
echo "--- Gemini session export $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/cron/gemini-session-export.sh 2>&1 || \
  echo "WARNING: Gemini session export failed"

# Step 2c: sync Hermes memory to Claude state (best-effort — #1719)
echo "--- Agent memory sync $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/cron/sync-agent-memories.sh 2>&1 || \
  echo "WARNING: agent memory sync failed"

# Step 3a: portfolio signals update (best-effort — WRK-1020)
LOG_FILE="logs/portfolio-signals/$(date +%Y-%m-%d).log"
mkdir -p "$(dirname "$LOG_FILE")"
echo "--- Portfolio signals update $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/cron/update-portfolio-signals.sh 2>&1 | tee -a "$LOG_FILE" || \
  echo "WARNING: portfolio signals update failed — see $LOG_FILE"

# Step 3b: AI agent readiness — CLI presence + version check (best-effort — WRK-306)
echo "--- AI agent readiness $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/readiness/ai-agent-readiness.sh || true

# Step 3c: release-notes scan (best-effort — WRK-1140)
echo "--- Release notes scan $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/automation/nightly-release-scan.sh || \
  echo "WARNING: release notes scan failed — see above"

# Auto-commit any WRK items created by the release scan (best-effort — must not abort nightly)
if ! git diff --quiet .claude/work-queue/ config/ai-tools/release-scan-state.yaml 2>/dev/null; then
  {
    # Stage release-scan files, then use git-safe for commit/push (#1548)
    find .claude/work-queue/pending/ -name 'WRK-*.md' -mmin -2 -exec git add {} +
    git add config/ai-tools/release-scan-state.yaml .claude/work-queue/INDEX.md
    git_safe_commit "chore(release-scan): nightly scan — $(date +%Y-%m-%d)"
    git_safe_push
  } || echo "WARNING: release-scan auto-commit/push failed — changes remain local"
fi

# Step 4: validate skill frontmatter (best-effort — WRK-308)
echo "--- Skill validation $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/skills/validate-skills.sh .claude/skills || \
  echo "WARNING: skill validation issues found — see above"

# Step 4b: skill curation (best-effort — WRK-1009)
echo "--- Skill curation $(date +%Y-%m-%dT%H:%M:%S) ---"
SKILL_CURATION_SCRIPT="scripts/cron/skill-curation-nightly.sh"
[[ -f "$SKILL_CURATION_SCRIPT" ]] && bash "$SKILL_CURATION_SCRIPT" || \
  echo "INFO: skill-curation-nightly.sh not found at $SKILL_CURATION_SCRIPT"

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

# Step 8: rebuild agent-readable specs index (best-effort — WRK-328)
echo "--- Specs index rebuild $(date +%Y-%m-%dT%H:%M:%S) ---"
source scripts/lib/python-resolver.sh
${PYTHON} scripts/readiness/build-specs-index.py || \
  echo "WARNING: specs index rebuild failed — see above"

# Step 3d: Phase 1b — scan Codex sessions for drift (best-effort — WRK-1101)
echo "--- Codex drift scan $(date +%Y-%m-%dT%H:%M:%S) ---"
YESTERDAY=$(date -d "yesterday" +%Y/%m/%d 2>/dev/null || date -v-1d +%Y/%m/%d 2>/dev/null || echo "")
if [[ -n "$YESTERDAY" ]]; then
    CODEX_DIR="${HOME}/.codex/sessions/${YESTERDAY}"
    if [[ -d "$CODEX_DIR" ]]; then
        for codex_log in "$CODEX_DIR"/rollout-*.jsonl; do
            [[ -f "$codex_log" ]] || continue
            bash scripts/session/detect-drift.sh --log "$codex_log" --provider codex --no-git || true
        done
        echo "  Codex drift scan complete for ${YESTERDAY}"
    else
        echo "  No Codex sessions found for ${YESTERDAY}"
    fi
else
    echo "  WARNING: could not determine yesterday's date"
fi

# Step 3f: Phase 1b — scan Hermes sessions for drift (best-effort — #1719)
echo "--- Hermes drift scan $(date +%Y-%m-%dT%H:%M:%S) ---"
YESTERDAY_DATE=$(date -d "yesterday" +%Y%m%d 2>/dev/null || date -v-1d +%Y%m%d 2>/dev/null || echo "")
HERMES_ORCH="logs/orchestrator/hermes/session_${YESTERDAY_DATE}.jsonl"
if [[ -n "$YESTERDAY_DATE" && -f "$HERMES_ORCH" ]]; then
    bash scripts/session/detect-drift.sh --log "$HERMES_ORCH" --provider hermes --no-git || true
    echo "  Hermes drift scan complete for ${YESTERDAY_DATE}"
else
    echo "  No Hermes orchestrator log found for ${YESTERDAY_DATE:-unknown}"
fi

# Step 9: harvest workflow-tip candidates from Wednesday ai-tooling research (best-effort)
if [[ "$(date +%u)" -eq 3 ]]; then
    echo "--- Workflow tip harvest $(date +%Y-%m-%dT%H:%M:%S) ---"
    bash scripts/cron/harvest-workflow-tips.sh "$WORKSPACE_HUB" || \
      echo "WARNING: workflow tip harvest failed — see above"
fi

# Step 3e: run pipeline (WRK-1076: notify on completion)
# Cron usage: bash scripts/cron/comprehensive-learning-nightly.sh >> /mnt/local-analysis/workspace-hub/.claude/state/learning-reports/cron.log 2>&1
_nightly_exit=0
bash scripts/learning/comprehensive-learning.sh || _nightly_exit=$?

# Step 10: commit all learning artifacts to git (best-effort — #1780)
echo "--- Commit learning artifacts $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/cron/commit-learning-artifacts.sh 2>&1 || \
  echo "WARNING: learning artifact commit failed — changes remain local"

bash scripts/notify.sh cron nightly-learning \
  "$([ "${_nightly_exit}" -eq 0 ] && echo pass || echo fail)" \
  "exit_code=${_nightly_exit}" || true
exit "${_nightly_exit}"
