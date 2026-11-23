#!/usr/bin/env bash
# rollout-claude-permissions.sh — OWNER-RUN. Union the canonical Claude permissions from
# workspace-hub origin/main into ~/.claude/settings.json on each machine.
#
# Usage:
#   rollout-claude-permissions.sh [--apply] TARGET...
#     TARGET  local:<hub path>  or  <ssh alias>:<hub path>   (hub path on that machine)
#     --apply write the change (default: dry run, prints the before/after counts and new rules)
#     --ref R read the canonical file from origin ref R (default: main), e.g. a PR branch for review
#
# Per target: `git fetch origin` in the hub (the working tree is not touched, so a dirty or
# diverged checkout is fine), read config/agents/claude/settings.json from origin/<ref>, then
# set permissions.allow and permissions.deny to the UNION of the machine's existing rules and
# the canonical rules (a legacy top-level "deny" in the canonical file is included). Nothing is
# removed; every other key is left alone. A timestamped backup is written before any change.
#
# Agents must not run this with --apply: permission changes are owner-only
# (.claude/rules/workstation-hygiene.md item 6, merge-authorization.md).
set -uo pipefail

APPLY=0; REF=main; TARGETS=(); NEXT_REF=0
for a in "$@"; do
  if [ "$NEXT_REF" = 1 ]; then REF="$a"; NEXT_REF=0; continue; fi
  case "$a" in
    --ref) NEXT_REF=1 ;;
    --apply) APPLY=1 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *:*) TARGETS+=("$a") ;;
    *) echo "bad target: $a (want alias:/hub/path or local:/hub/path)" >&2; exit 2 ;;
  esac
done
[ ${#TARGETS[@]} -gt 0 ] || { sed -n '2,18p' "$0"; exit 2; }

# Runs on the target machine: $1 = hub path, $2 = 1 to apply, $3 = origin ref.
REMOTE=$(cat <<'EOS'
set -uo pipefail
hub="$1"; apply="$2"; ref="$3"; s="$HOME/.claude/settings.json"
command -v jq >/dev/null || { echo "  FAIL: jq not installed"; exit 1; }
git -C "$hub" fetch -q origin "$ref" || { echo "  FAIL: git fetch in $hub"; exit 1; }
canon=$(git -C "$hub" show "origin/$ref:config/agents/claude/settings.json" 2>/dev/null || git -C "$hub" show FETCH_HEAD:config/agents/claude/settings.json) || { echo "  FAIL: canonical file missing"; exit 1; }
[ -f "$s" ] || { mkdir -p "$(dirname "$s")"; echo '{}' > "$s"; echo "  (created empty $s)"; }
new=$(jq --argjson c "$canon" '
  .permissions = ((.permissions // {}) + {
    allow: (((.permissions.allow // []) + ($c.permissions.allow // [])) | unique),
    deny:  (((.permissions.deny  // []) + ($c.permissions.deny  // []) + ($c.deny // [])) | unique)
  })' "$s") || { echo "  FAIL: $s is not valid JSON"; exit 1; }
before=$(jq -c '[(.permissions.allow//[]|length),(.permissions.deny//[]|length)]' "$s")
after=$(printf '%s' "$new" | jq -c '[(.permissions.allow|length),(.permissions.deny|length)]')
before_permissions=$(jq -cS '.permissions // {}' "$s")
after_permissions=$(printf '%s' "$new" | jq -cS '.permissions')
echo "  host=$(hostname) canonical=$(git -C "$hub" rev-parse --short FETCH_HEAD) ref=$ref allow/deny before=$before after=$after"
printf '%s' "$new" | jq -r --slurpfile o "$s" '.permissions.allow - ($o[0].permissions.allow//[]) | .[] | "    + allow " + .'
printf '%s' "$new" | jq -r --slurpfile o "$s" '.permissions.deny - ($o[0].permissions.deny//[]) | length | "    + deny rules added: \(.)"'
if [ "$apply" = 1 ]; then
  if [ "$before_permissions" = "$after_permissions" ]; then echo "  already current"; exit 0; fi
  b="$s.bak-$(date -u +%Y%m%dT%H%M%SZ)"; cp "$s" "$b"
  printf '%s\n' "$new" > "$s.tmp" && jq empty "$s.tmp" && mv "$s.tmp" "$s" && echo "  APPLIED (backup $b)"
else
  echo "  dry run: no change"
fi
EOS
)

rc=0
for t in "${TARGETS[@]}"; do
  host=${t%%:*}; hub=${t#*:}
  echo "== $host"
  if [ "$host" = local ]; then
    printf '%s
' "$REMOTE" | bash -s -- "$hub" "$APPLY" "$REF" || rc=1
  else
    printf '%s\n' "$REMOTE" | ssh -o BatchMode=yes -o ConnectTimeout=15 "$host" "bash -s -- '$hub' '$APPLY' '$REF'" \
      2> >(grep -v -iE 'post-quantum|store now|upgraded|pq\.html' >&2) || rc=1
  fi
done
exit $rc
