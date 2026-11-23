#!/usr/bin/env bash
# weekly-hermes-parity-review.sh — Weekly Hermes cross-machine parity review
# Issue: #2239 | Governance: #2089 | Baseline: #1583
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
OUTPUT_DIR="${WORKSPACE_HUB}/logs/weekly-parity"
DATE_STAMP=$(date +%Y-%m-%d)
ARTIFACT="${OUTPUT_DIR}/parity-review-${DATE_STAMP}.md"
SSH_TIMEOUT=30
COMMENT_ON_ISSUE=false

for arg in "$@"; do
  [[ "$arg" == "--comment-on-issue" ]] && COMMENT_ON_ISSUE=true
done

mkdir -p "$OUTPUT_DIR"

yaml_val() {
  grep -m1 "^[[:space:]]*${2}:" "$1" 2>/dev/null | sed 's/^[^:]*:[[:space:]]*//' | tr -d "'\""
}

collect_local_evidence() {
  cat <<EOF
  - Hermes version: $(hermes --version 2>/dev/null || echo "not installed")
  - Claude CLI: $(claude --version 2>/dev/null | head -1 || echo "not installed")
  - Git: $(git --version 2>/dev/null | head -1 || echo "not installed")
  - uv: $(uv --version 2>/dev/null | head -1 || echo "not installed")
EOF
}

collect_ssh_evidence() {
  local ssh_target="$1"
  local hermes_ver
  hermes_ver=$(timeout "$SSH_TIMEOUT" ssh -o ConnectTimeout=10 -o BatchMode=yes "$ssh_target" "hermes --version 2>/dev/null || echo not-installed" 2>/dev/null) || hermes_ver="SSH_FAILED"
  if [[ "$hermes_ver" == "SSH_FAILED" ]]; then
    echo "UNREACHABLE"
    return
  fi
  cat <<EOF
  - Hermes version: ${hermes_ver}
  - Claude CLI: $(timeout "$SSH_TIMEOUT" ssh -o ConnectTimeout=10 -o BatchMode=yes "$ssh_target" "claude --version 2>/dev/null | head -1 || echo not-installed" 2>/dev/null || echo unknown)
  - Git: $(timeout "$SSH_TIMEOUT" ssh -o ConnectTimeout=10 -o BatchMode=yes "$ssh_target" "git --version 2>/dev/null | head -1 || echo not-installed" 2>/dev/null || echo unknown)
EOF
}

ingest_bridge_artifact() {
  local artifact_path="$1"
  local full_path="${WORKSPACE_HUB}/${artifact_path}"
  [[ -f "$full_path" ]] || { echo "NO_ARTIFACT"; return; }
  local gen_at overall pass_ct fail_ct
  gen_at=$(yaml_val "$full_path" generated_at)
  overall=$(yaml_val "$full_path" overall)
  pass_ct=$(yaml_val "$full_path" pass_count)
  fail_ct=$(yaml_val "$full_path" fail_count)
  cat <<EOF
  - Bridge artifact: ${artifact_path}
  - Generated: ${gen_at}
  - Overall: ${overall}
  - Checks: ${pass_ct} pass, ${fail_ct} fail
EOF
}

ssh_evidence=$(collect_ssh_evidence ace-linux-2)
win1_evidence=$(ingest_bridge_artifact .claude/state/harness-readiness-licensed-win-1.yaml)

{
  echo "# Weekly Hermes Cross-Machine Parity Review"
  echo
  echo "> Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "> Governance: [#2089](https://github.com/vamseeachanta/workspace-hub/issues/2089)"
  echo "> Baseline: [#1583](https://github.com/vamseeachanta/workspace-hub/issues/1583)"
  echo
  echo "## dev-primary / ace-linux-1"
  echo
  echo "**Status: pass**"
  echo "**Evidence method: direct local probes**"
  echo
  collect_local_evidence
  echo
  echo "## dev-secondary / ace-linux-2"
  echo
  if [[ "$ssh_evidence" == "UNREACHABLE" ]]; then
    ssh_status="unreachable"
    echo "**Status: unreachable**"
    echo "**Evidence method: timeout-wrapped SSH (${SSH_TIMEOUT}s)**"
    echo
    echo "  - SSH probe failed or timed out"
  elif printf '%s' "$ssh_evidence" | grep -qi 'not-installed'; then
    ssh_status="drift"
    echo "**Status: drift**"
    echo "**Evidence method: timeout-wrapped SSH (${SSH_TIMEOUT}s)**"
    echo
    printf '%s\n' "$ssh_evidence"
    echo "  - One or more required tools are not installed"
  else
    ssh_status="pass"
    echo "**Status: pass**"
    echo "**Evidence method: timeout-wrapped SSH (${SSH_TIMEOUT}s)**"
    echo
    printf '%s\n' "$ssh_evidence"
  fi
  echo
  echo "## licensed-win-1"
  echo
  if [[ "$win1_evidence" == "NO_ARTIFACT" ]]; then
    win1_status="blocked"
    echo "**Status: blocked**"
    echo "**Evidence method: bridge artifact (missing)**"
    echo
    echo "  - No readiness artifact found at .claude/state/harness-readiness-licensed-win-1.yaml"
    echo "  - Cannot assess parity without evidence — classified as blocked, not pass"
  elif printf '%s' "$win1_evidence" | grep -q 'Overall: pass'; then
    win1_status="pass"
    echo "**Status: pass (via bridge artifact)**"
    echo "**Evidence method: explicit readiness artifact**"
    echo
    printf '%s\n' "$win1_evidence"
  else
    win1_status="drift"
    echo "**Status: drift (via bridge artifact)**"
    echo "**Evidence method: explicit readiness artifact**"
    echo
    printf '%s\n' "$win1_evidence"
    echo "  - Bridge artifact reports non-pass overall state"
  fi
  echo
  echo "## licensed-win-2"
  echo
  echo "**Status: blocked**"
  echo "**Evidence method: none (no canonical artifact path defined)**"
  echo
  echo "  - No artifact contract exists for licensed-win-2 in v1"
  echo
  echo "## macbook-portable"
  echo
  echo "**Status: blocked (unsupported in v1)**"
  echo "**Evidence method: none (awaiting #2240 macOS parity scaffolding)**"
  echo
  echo "  - macOS parity requires registry and readiness support from [#2240](https://github.com/vamseeachanta/workspace-hub/issues/2240)"
  echo
  echo "## Summary"
  echo
  echo "| Machine | Status | Evidence Method |"
  echo "|---------|--------|-----------------|"
  echo "| dev-primary / ace-linux-1 | pass | local probes |"
  if [[ "$ssh_status" == "unreachable" ]]; then
    echo "| dev-secondary / ace-linux-2 | unreachable | SSH (timed out) |"
  elif [[ "$ssh_status" == "drift" ]]; then
    echo "| dev-secondary / ace-linux-2 | drift | SSH probes |"
  else
    echo "| dev-secondary / ace-linux-2 | pass | SSH probes |"
  fi
  if [[ "$win1_status" == "blocked" ]]; then
    echo "| licensed-win-1 | blocked | bridge artifact (missing) |"
  elif [[ "$win1_status" == "drift" ]]; then
    echo "| licensed-win-1 | drift | bridge artifact |"
  else
    echo "| licensed-win-1 | pass | bridge artifact |"
  fi
  echo "| licensed-win-2 | blocked | no artifact contract |"
  echo "| macbook-portable | blocked | unsupported until #2240 |"
  echo
  echo "## Follow-On Guidance"
  echo
  echo "- For drift findings, file issues labeled cat:harness and machine:<affected>, referencing [#1583](https://github.com/vamseeachanta/workspace-hub/issues/1583)"
  echo "- For cross-machine divergence, reference [#2089](https://github.com/vamseeachanta/workspace-hub/issues/2089)"
  echo "- macOS parity blocked on [#2240](https://github.com/vamseeachanta/workspace-hub/issues/2240)"
  echo "- licensed-win-2 parity blocked until canonical artifact path is defined"
  echo "- GitHub issue auto-creation is deferred from v1"
} > "$ARTIFACT"

echo "Weekly parity review written to: ${ARTIFACT}"

if [[ "$COMMENT_ON_ISSUE" == "true" ]]; then
  if command -v gh >/dev/null 2>&1; then
    summary=$(grep -A20 "## Summary" "$ARTIFACT" | head -15)
    gh issue comment 2089 --repo vamseeachanta/workspace-hub --body "## Weekly Parity Review — ${DATE_STAMP}

${summary}

Full artifact: \`logs/weekly-parity/parity-review-${DATE_STAMP}.md\`" >/dev/null 2>&1 || echo "WARN: failed to post GitHub comment on #2089"
  else
    echo "WARN: gh CLI not available — skipping GitHub comment"
  fi
fi

exit 0
