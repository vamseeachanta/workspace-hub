#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SCRIPT="$ROOT/scripts/ai/gh_quirk.sh"

bash -n "$SCRIPT"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir "$tmp/bin"
cat >"$tmp/bin/gh" <<'EOF'
#!/usr/bin/env bash
echo "gh should not run during dry-run" >&2
exit 99
EOF
chmod +x "$tmp/bin/gh"

PATH="$tmp/bin:$PATH" "$SCRIPT" --dry-run log \
  --repo vamseeachanta/workspace-hub \
  --area codex \
  --symptom "dry-run symptom" \
  --cause "dry-run cause" \
  --fix "dry-run fix" \
  --doc "scripts/ai/gh_quirk.sh" \
  --session "test-session" >"$tmp/log.out"

grep -F "gh label create quirk" "$tmp/log.out" >/dev/null
grep -F "gh issue list --repo vamseeachanta/workspace-hub --state all --label quirk" "$tmp/log.out" >/dev/null
grep -F "gh issue create --repo vamseeachanta/workspace-hub" "$tmp/log.out" >/dev/null
grep -F "## Symptom" "$tmp/log.out" >/dev/null

PATH="$tmp/bin:$PATH" "$SCRIPT" --dry-run list \
  --repo vamseeachanta/workspace-hub >"$tmp/list.out"
grep -F "gh issue list --repo vamseeachanta/workspace-hub --state all --label quirk" "$tmp/list.out" >/dev/null

PATH="$tmp/bin:$PATH" "$SCRIPT" --dry-run close \
  --repo vamseeachanta/workspace-hub \
  --number 123 \
  --fixed-by abc1234 \
  --doc .claude/README.md >"$tmp/close.out"
grep -F "gh issue comment 123 --repo vamseeachanta/workspace-hub --body-file -" "$tmp/close.out" >/dev/null
grep -F "gh issue close 123 --repo vamseeachanta/workspace-hub --reason completed" "$tmp/close.out" >/dev/null

echo "ok - gh_quirk.sh dry-run"
