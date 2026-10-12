#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
SCRIPT_UNDER_TEST="${REPO_ROOT}/scripts/operations/rollout-claude-permissions.sh"
FIXTURE="${SCRIPT_DIR}/fixtures/claude-settings-duplicate-deny-missing-canonical.json"

TMPDIR="${TMPDIR:-/tmp}"
WORK_DIR="$(mktemp -d "${TMPDIR%/}/rollout-claude-permissions.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

origin_repo="${WORK_DIR}/origin"
hub_repo="${WORK_DIR}/hub"
home_dir="${WORK_DIR}/home"
settings="${home_dir}/.claude/settings.json"

mkdir -p "${origin_repo}/config/agents/claude" "$(dirname "$settings")"
cat >"${origin_repo}/config/agents/claude/settings.json" <<'JSON'
{
  "permissions": {
    "allow": [],
    "deny": [
      "Bash(existing-canonical-deny:*)",
      "Bash(missing-canonical-deny:*)"
    ]
  }
}
JSON

git -C "$origin_repo" init -q -b main
git -C "$origin_repo" add config/agents/claude/settings.json
git -C "$origin_repo" \
  -c user.name="Test User" \
  -c user.email="test@example.invalid" \
  commit -q -m "fixture"

git clone -q "$origin_repo" "$hub_repo"
cp "$FIXTURE" "$settings"

output="$(HOME="$home_dir" bash "$SCRIPT_UNDER_TEST" --apply "local:${hub_repo}")"

if grep -q "already current" <<<"$output"; then
  echo "FAIL: duplicate-count fixture was reported already current" >&2
  echo "$output" >&2
  exit 1
fi

jq -e '
  (.permissions.deny | index("Bash(missing-canonical-deny:*)")) != null
  and (.permissions.deny | length) == 2
' "$settings" >/dev/null

echo "PASS: duplicate deny plus missing canonical deny writes the missing rule"
