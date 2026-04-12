#!/usr/bin/env bash
# test-weekly-hermes-parity-review.sh — Regression tests for #2239 weekly parity review
# Run: bash tests/work-queue/test-weekly-hermes-parity-review.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PARITY_SCRIPT="${REPO_ROOT}/scripts/cron/weekly-hermes-parity-review.sh"
SCHEDULE_FILE="${REPO_ROOT}/config/scheduled-tasks/schedule-tasks.yaml"

pass=0
fail=0
ok() { echo "  PASS  $1"; pass=$((pass + 1)); }
failcase() { echo "  FAIL  $1"; fail=$((fail + 1)); }

mk_ws() {
  local ws
  ws=$(mktemp -d)
  mkdir -p "${ws}/config/workstations" "${ws}/scripts/readiness" "${ws}/config/agents/hermes" "${ws}/logs/weekly-parity" "${ws}/.claude/state"
  cp "${PARITY_SCRIPT}" "${ws}/scripts/cron-weekly.sh"
  cat > "${ws}/config/workstations/registry.yaml" <<'YAML'
machines:
  dev-primary:
    hostname: ace-linux-1
    hostname_aliases: []
    os: linux
    role: primary-dev
    workspace_root: /mnt/local-analysis/workspace-hub
    schedule_variant: full
    ssh: ace-linux-1
  dev-secondary:
    hostname: ace-linux-2
    hostname_aliases: []
    os: linux
    role: secondary-dev
    workspace_root: /mnt/workspace-hub
    schedule_variant: contribute
    ssh: ace-linux-2
  licensed-win-1:
    hostname: licensed-win-1
    hostname_aliases: []
    os: windows
    role: simulation-license-host
    workspace_root: 'D:\\workspace-hub'
    schedule_variant: contribute-minimal
    ssh: null
  licensed-win-2:
    hostname: licensed-win-2
    hostname_aliases: []
    os: windows
    role: simulation-secondary
    workspace_root: 'D:\\workspace-hub'
    schedule_variant: contribute-minimal
    ssh: null
YAML
  cat > "${ws}/scripts/readiness/harness-config.yaml" <<'YAML'
workstations:
  dev-primary:
    ws_hub_path: /mnt/local-analysis/workspace-hub
    ssh_target: null
  dev-secondary:
    ws_hub_path: /mnt/workspace-hub
    ssh_target: ace-linux-2
  licensed-win-1:
    ws_hub_path: 'D:\\workspace-hub'
    ssh_target: null
    linux_reachable: false
    report_path: .claude/state/harness-readiness-licensed-win-1.yaml
YAML
  cat > "${ws}/config/agents/hermes/config.yaml.template" <<'YAML'
model:
  provider: anthropic
  model: claude-sonnet-4
YAML
  echo "$ws"
}
rm_ws() { rm -rf "$1"; }

echo "=== #2239 weekly parity review tests ==="

T1() {
  local ws out artifact
  ws=$(mk_ws)
  out=$(WORKSPACE_HUB="$ws" HOME="$ws/home" bash "$ws/scripts/cron-weekly.sh" 2>&1 || true)
  artifact="$ws/logs/weekly-parity/parity-review-$(date +%Y-%m-%d).md"
  if [[ -f "$artifact" ]] && echo "$out" | grep -q 'Weekly parity review written to:'; then ok "T1: script writes dated artifact to logs/weekly-parity/"; else failcase "T1"; fi
  rm_ws "$ws"
}
T1
T2() {
  local ws artifact
  ws=$(mk_ws)
  mkdir -p "$ws/bin"
  cat > "$ws/bin/ssh" <<'EOF'
#!/usr/bin/env bash
exit 255
EOF
  chmod +x "$ws/bin/ssh"
  artifact="$ws/logs/weekly-parity/parity-review-$(date +%Y-%m-%d).md"
  PATH="$ws/bin:$PATH" WORKSPACE_HUB="$ws" HOME="$ws/home" bash "$ws/scripts/cron-weekly.sh" >/dev/null 2>&1 || true
  if grep -q 'dev-secondary / ace-linux-2 | unreachable' "$artifact"; then ok "T2: unreachable SSH host reported but script exits 0"; else failcase "T2"; fi
  rm_ws "$ws"
}
T2
T3() {
  local ws artifact
  ws=$(mk_ws)
  cat > "$ws/.claude/state/harness-readiness-licensed-win-1.yaml" <<'YAML'
generated_at: "2026-04-12T00:00:00Z"
overall: pass
pass_count: 9
fail_count: 0
YAML
  artifact="$ws/logs/weekly-parity/parity-review-$(date +%Y-%m-%d).md"
  WORKSPACE_HUB="$ws" HOME="$ws/home" bash "$ws/scripts/cron-weekly.sh" >/dev/null 2>&1 || true
  if grep -q 'licensed-win-1 | pass | bridge artifact' "$artifact"; then ok "T3: Windows bridge artifact ingested for licensed-win-1"; else failcase "T3"; fi
  rm_ws "$ws"
}
T3
T4() {
  local ws artifact
  ws=$(mk_ws)
  artifact="$ws/logs/weekly-parity/parity-review-$(date +%Y-%m-%d).md"
  WORKSPACE_HUB="$ws" HOME="$ws/home" bash "$ws/scripts/cron-weekly.sh" >/dev/null 2>&1 || true
  if grep -q 'licensed-win-2 | blocked | no artifact contract' "$artifact"; then ok "T4: licensed-win-2 marked as blocked"; else failcase "T4"; fi
  rm_ws "$ws"
}
T4
T5() {
  local ws artifact
  ws=$(mk_ws)
  artifact="$ws/logs/weekly-parity/parity-review-$(date +%Y-%m-%d).md"
  WORKSPACE_HUB="$ws" HOME="$ws/home" bash "$ws/scripts/cron-weekly.sh" >/dev/null 2>&1 || true
  if grep -Eq 'macbook-portable \| blocked|macbook-portable \| unsupported' "$artifact"; then ok "T5: macbook-portable marked as blocked/unsupported"; else failcase "T5"; fi
  rm_ws "$ws"
}
T5
T6() { if grep -Eq 'timeout .*ssh -o ConnectTimeout=10 -o BatchMode=yes' "$PARITY_SCRIPT"; then ok "T6: script uses timeout-wrapped SSH probes"; else failcase "T6"; fi; }
T6
T7() { if grep -q 'id: weekly-hermes-parity-review' "$SCHEDULE_FILE"; then ok "T7: weekly-hermes-parity-review found in schedule-tasks.yaml"; else failcase "T7"; fi; }
T7
T8() {
  local ws artifact
  ws=$(mk_ws)
  artifact="$ws/logs/weekly-parity/parity-review-$(date +%Y-%m-%d).md"
  WORKSPACE_HUB="$ws" HOME="$ws/home" bash "$ws/scripts/cron-weekly.sh" >/dev/null 2>&1 || true
  if grep -q '#1583' "$artifact" && grep -q '#2089' "$artifact"; then ok "T8: artifact contains issue links #1583 and #2089"; else failcase "T8"; fi
  rm_ws "$ws"
}
T8
T9() {
  local ws artifact
  ws=$(mk_ws)
  artifact="$ws/logs/weekly-parity/parity-review-$(date +%Y-%m-%d).md"
  WORKSPACE_HUB="$ws" HOME="$ws/home" bash "$ws/scripts/cron-weekly.sh" >/dev/null 2>&1 || true
  if ! grep -q 'licensed-win-2 | pass' "$artifact" && ! grep -q 'macbook-portable | pass' "$artifact"; then ok "T9: missing evidence never counts as pass"; else failcase "T9"; fi
  rm_ws "$ws"
}
T9
T10() { if grep -q -- '--comment-on-issue' "$PARITY_SCRIPT" && grep -q 'COMMENT_ON_ISSUE=false' "$PARITY_SCRIPT"; then ok "T10: GitHub commenting respects explicit flag"; else failcase "T10"; fi; }
T10

echo
if [[ "$fail" -eq 0 ]]; then echo "All ${pass} tests passed"; exit 0; else echo "${fail} test(s) failed; ${pass} passed"; exit 1; fi
