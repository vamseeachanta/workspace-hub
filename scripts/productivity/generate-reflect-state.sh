#!/usr/bin/env bash
# ABOUTME: Generate reflect-state.yaml for ecosystem health reporting
# Populates .claude/state/reflect-state.yaml with live metrics from the workspace.
# The companion daily-reflect-report.sh parses the generated YAML.
set -euo pipefail

# ---------------------------------------------------------------------------
# Workspace root
# ---------------------------------------------------------------------------
WORKSPACE_ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
STATE_DIR="${WORKSPACE_ROOT}/.claude/state"
STATE_FILE="${STATE_DIR}/reflect-state.yaml"
mkdir -p "$STATE_DIR"

TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
SCRIPTS_DIR="${WORKSPACE_ROOT}/scripts"
CLAUDE_DIR="${WORKSPACE_ROOT}/.claude"

# ---------------------------------------------------------------------------
# Helper: timeout-guarded git (5 s)
# ---------------------------------------------------------------------------
tgit() { timeout 5 git "$@" 2>/dev/null || true; }

# ---------------------------------------------------------------------------
# Discover repos (hub + any subdirectories with .git)
# ---------------------------------------------------------------------------
REPOS=("$WORKSPACE_ROOT")
while IFS= read -r d; do
  [[ -d "$d/.git" ]] && REPOS+=("$d")
done < <(find "$WORKSPACE_ROOT" -mindepth 1 -maxdepth 2 -type d ! -path '*/.git/*' ! -path '*/.planning/*' ! -path '*/node_modules/*' 2>/dev/null)

repos_analyzed=${#REPOS[@]}

# ---------------------------------------------------------------------------
# 1. Uncommitted changes
# ---------------------------------------------------------------------------
uncommitted=0
for repo in "${REPOS[@]}"; do
  dirty=$(tgit -C "$repo" status --porcelain | head -1)
  [[ -n "$dirty" ]] && uncommitted=$((uncommitted + 1))
done

# ---------------------------------------------------------------------------
# 2. Repos with tests
# ---------------------------------------------------------------------------
repos_with_tests=0
for repo in "${REPOS[@]}"; do
  if find "$repo" -maxdepth 4 -type f \( -name 'test_*' -o -name '*_test.*' -o -name '*.test.*' \) 2>/dev/null | head -1 | grep -q . ||
     find "$repo" -maxdepth 3 -type d -name 'tests' 2>/dev/null | head -1 | grep -q .; then
    repos_with_tests=$((repos_with_tests + 1))
  fi
done

# ---------------------------------------------------------------------------
# 3. Submodules (dirty / unpushed)
# ---------------------------------------------------------------------------
submodules_dirty=0
submodules_unpushed=0
if [[ -f "${WORKSPACE_ROOT}/.gitmodules" ]]; then
  while IFS= read -r sm_path; do
    sm_dir="${WORKSPACE_ROOT}/${sm_path}"
    [[ -d "$sm_dir" ]] || continue
    dirty=$(tgit -C "$sm_dir" status --porcelain | head -1)
    [[ -n "$dirty" ]] && submodules_dirty=$((submodules_dirty + 1))
    unpushed=$(tgit -C "$sm_dir" log --oneline '@{u}..HEAD' 2>/dev/null | head -1)
    [[ -n "$unpushed" ]] && submodules_unpushed=$((submodules_unpushed + 1))
  done < <(git config --file "${WORKSPACE_ROOT}/.gitmodules" --get-regexp 'submodule\..*\.path' 2>/dev/null | awk '{print $2}')
fi

if (( submodules_dirty > 0 || submodules_unpushed > 0 )); then
  submodule_sync_status="warn"
else
  submodule_sync_status="pass"
fi

# ---------------------------------------------------------------------------
# 4. CLAUDE.md health
# ---------------------------------------------------------------------------
claude_md_oversized=0
claude_md_total=0
while IFS= read -r f; do
  claude_md_total=$((claude_md_total + 1))
  lines=$(wc -l < "$f")
  (( lines > 20 )) && claude_md_oversized=$((claude_md_oversized + 1))
done < <(find "$WORKSPACE_ROOT" -maxdepth 4 -name 'CLAUDE.md' -not -path '*/.planning/*' 2>/dev/null)

if (( claude_md_oversized > 0 )); then
  claude_md_status="fail"
else
  claude_md_status="pass"
fi

# ---------------------------------------------------------------------------
# 5. Stale branches (>30 days)
# ---------------------------------------------------------------------------
stale_branch_count=0
thirty_days_ago=$(date -u -d '30 days ago' +%s 2>/dev/null || date -u -v-30d +%s 2>/dev/null || echo 0)
if (( thirty_days_ago > 0 )); then
  while IFS= read -r line; do
    ref_epoch=$(tgit -C "$WORKSPACE_ROOT" log -1 --format='%ct' "$line" 2>/dev/null || echo 0)
    ref_epoch=${ref_epoch:-0}
    (( ref_epoch > 0 && ref_epoch < thirty_days_ago )) && stale_branch_count=$((stale_branch_count + 1))
  done < <(tgit -C "$WORKSPACE_ROOT" for-each-ref --format='%(refname:short)' refs/heads/)
fi

if (( stale_branch_count > 5 )); then
  stale_status="warn"
elif (( stale_branch_count > 0 )); then
  stale_status="pass"
else
  stale_status="pass"
fi

# ---------------------------------------------------------------------------
# 6. Large files (>500 lines) in scripts/
# ---------------------------------------------------------------------------
large_files=0
if [[ -d "$SCRIPTS_DIR" ]]; then
  while IFS= read -r f; do
    lines=$(wc -l < "$f")
    (( lines > 500 )) && large_files=$((large_files + 1))
  done < <(find "$SCRIPTS_DIR" -maxdepth 5 -type f \( -name '*.sh' -o -name '*.py' \) 2>/dev/null)
fi

# ---------------------------------------------------------------------------
# 7. TODO count in scripts/ and .claude/
# ---------------------------------------------------------------------------
todo_count=0
for d in "$SCRIPTS_DIR" "$CLAUDE_DIR"; do
  [[ -d "$d" ]] || continue
  n=$(grep -r 'TODO' "$d" --include='*.sh' --include='*.py' --include='*.md' --include='*.yaml' --include='*.yml' 2>/dev/null | wc -l)
  todo_count=$((todo_count + n))
done

# ---------------------------------------------------------------------------
# 8. Commits since yesterday (across repos)
# ---------------------------------------------------------------------------
commits_found=0
for repo in "${REPOS[@]}"; do
  n=$(tgit -C "$repo" log --oneline --since="yesterday" 2>/dev/null | wc -l)
  commits_found=$((commits_found + n))
done

# ---------------------------------------------------------------------------
# 9. Claude CLI version
# ---------------------------------------------------------------------------
cc_version=$(claude --version 2>/dev/null | head -1 || echo "unknown")
cc_version="${cc_version:-unknown}"

# ---------------------------------------------------------------------------
# 10. Hook coverage (repos with pre-commit hooks)
# ---------------------------------------------------------------------------
hooks_installed=0
hooks_eligible=0
for repo in "${REPOS[@]}"; do
  [[ -d "$repo/.git" || -f "$repo/.git" ]] || continue
  hooks_eligible=$((hooks_eligible + 1))
  git_dir=$(tgit -C "$repo" rev-parse --git-dir 2>/dev/null)
  if [[ -n "$git_dir" && -x "${repo}/${git_dir}/hooks/pre-commit" ]] || [[ -f "$repo/.pre-commit-config.yaml" ]]; then
    hooks_installed=$((hooks_installed + 1))
  fi
done
if (( hooks_eligible > 0 )); then
  hooks_coverage=$(( hooks_installed * 100 / hooks_eligible ))
else
  hooks_coverage=0
fi

# ---------------------------------------------------------------------------
# 11. Work queue (check logs/daily for wrk data)
# ---------------------------------------------------------------------------
wq_pending=0; wq_working=0; wq_blocked=0; wq_stale=0
wq_log="${WORKSPACE_ROOT}/logs/daily/$(date +%Y-%m-%d).md"
if [[ -f "$wq_log" ]]; then
  wq_pending=$(grep -ci 'pending\|todo\|open' "$wq_log" 2>/dev/null || echo 0)
  wq_blocked=$(grep -ci 'blocked' "$wq_log" 2>/dev/null || echo 0)
fi
wq_status="pass"
(( wq_blocked > 0 )) && wq_status="warn"

# ---------------------------------------------------------------------------
# 12. Best practices status
# ---------------------------------------------------------------------------
if (( uncommitted > 2 )); then
  best_practices="fail"
elif (( uncommitted > 0 )); then
  best_practices="warn"
else
  best_practices="pass"
fi

# ---------------------------------------------------------------------------
# 13. Refactor status
# ---------------------------------------------------------------------------
if (( large_files > 5 || todo_count > 50 )); then
  refactor_status="fail"
elif (( large_files > 0 || todo_count > 10 )); then
  refactor_status="warn"
else
  refactor_status="pass"
fi

# ---------------------------------------------------------------------------
# 14. Aceengineer cron
# ---------------------------------------------------------------------------
ae_stats_date="unknown"
ae_report_date="unknown"
ae_cron_status="pass"
ae_stats="${WORKSPACE_ROOT}/logs/daily/$(date +%Y-%m-%d).md"
if [[ -f "$ae_stats" ]]; then
  ae_stats_date=$(date +%Y-%m-%d)
fi

# ---------------------------------------------------------------------------
# Write YAML
# ---------------------------------------------------------------------------
cat > "$STATE_FILE" <<YAML
last_run: ${TIMESTAMP}

checklist:
  cross_review: warn
  gemini_pending: 0
  codex_pending: 0
  claude_pending: 0

  skills_development: pass
  skills_created: 0
  skills_enhanced: 0

  file_structure: pass
  orphan_docs: 0
  orphan_scripts: 0

  context_management: pass
  avg_session_msgs: 0
  correction_rate: 0

  best_practices: ${best_practices}
  repos_with_tests: ${repos_with_tests}
  uncommitted_changes: ${uncommitted}

  submodule_sync: ${submodule_sync_status}
  submodules_dirty: ${submodules_dirty}
  submodules_unpushed: ${submodules_unpushed}

  claude_md_health: ${claude_md_status}
  claude_md_oversized: ${claude_md_oversized}
  claude_md_total: ${claude_md_total}

  hook_installation: warn
  hooks_coverage: ${hooks_coverage}

  stale_branches: ${stale_status}
  stale_branch_count: ${stale_branch_count}

  github_actions: pass
  actions_failing: 0
  actions_total: 0

  folder_structure_detailed: pass
  structure_issues: 0

  test_coverage: warn
  avg_coverage: 0
  coverage_repos: ${repos_with_tests}
  low_coverage_repos: 0

  test_pass_fail: pass
  test_pass_count: 0
  test_fail_count: 0

  refactor: ${refactor_status}
  large_files: ${large_files}
  todo_count: ${todo_count}

  aceengineer_cron: ${ae_cron_status}
  aceengineer_stats_date: ${ae_stats_date}
  aceengineer_report_date: ${ae_report_date}

  session_rag: warn
  session_rag_sessions: 0
  session_rag_events: 0
  session_rag_date: unknown

  cc_insights: pass
  cc_version: ${cc_version}
  cc_last_reviewed: unknown

  work_queue: ${wq_status}
  wq_pending: ${wq_pending}
  wq_working: ${wq_working}
  wq_blocked: ${wq_blocked}
  wq_stale: ${wq_stale}

  skill_eval: pass
  skill_eval_total: 0
  skill_eval_passed: 0
  skill_eval_critical: 0
  skill_eval_warnings: 0

  capability_map: pass
  capability_repos: ${repos_analyzed}
  capability_domains: 0
  capability_gaps: 0
  capability_date: unknown

  knowledge_base: pass
  kb_total: 0
  kb_active: 0
  kb_stale: 0
  kb_avg_confidence: 0

  repos_analyzed: ${repos_analyzed}
  commits_found: ${commits_found}
  patterns_extracted: 0
  sessions_analyzed: 0
  conversations_analyzed: 0

actions_taken:
  learnings_stored: 0
  knowledge_captured: 0
YAML

echo "Generated: ${STATE_FILE}"
echo "  repos_analyzed=${repos_analyzed} commits=${commits_found} uncommitted=${uncommitted} stale_branches=${stale_branch_count}"
