#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage:
  add-member.sh <telegram_numeric_id> [--scope acma|doris] [--apply]
  add-member.sh --list
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

env_file="${DECKHAND_ENV_FILE:-$HOME/.hermes/.env}"
scopes_yml="${DECKHAND_SCOPES_YML:-config/deckhand/scopes.yml}"
apply=false
list=false
telegram_id=""
scope=""
python_bin="${DECKHAND_PYTHON:-python3}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      apply=true
      shift
      ;;
    --list)
      list=true
      shift
      ;;
    --scope)
      [[ $# -ge 2 ]] || die "--scope requires a value"
      scope="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      die "unknown option: $1"
      ;;
    *)
      [[ -z "$telegram_id" ]] || die "only one telegram_numeric_id may be provided"
      telegram_id="$1"
      shift
      ;;
  esac
done

read_allowed_users() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  awk -F= '
    $1 == "TELEGRAM_ALLOWED_USERS" {
      value = substr($0, index($0, "=") + 1)
    }
    END {
      if (value != "") print value
    }
  ' "$file"
}

id_in_csv() {
  local id="$1"
  local csv="$2"
  local item
  IFS=',' read -r -a items <<<"$csv"
  for item in "${items[@]}"; do
    item="${item#"${item%%[![:space:]]*}"}"
    item="${item%"${item##*[![:space:]]}"}"
    [[ "$item" == "$id" ]] && return 0
  done
  return 1
}

write_allowed_users() {
  local file="$1"
  local id="$2"
  local current new_value tmp

  current="$(read_allowed_users "$file" || true)"
  if id_in_csv "$id" "$current"; then
    return 0
  fi

  if [[ -z "$current" ]]; then
    new_value="$id"
  else
    new_value="${current},${id}"
  fi

  mkdir -p "$(dirname "$file")"
  tmp="$(mktemp)"
  if [[ -f "$file" ]]; then
    awk -F= -v new_value="$new_value" '
      BEGIN { updated = 0 }
      $1 == "TELEGRAM_ALLOWED_USERS" && index($0, "=") > 0 {
        if (!updated) {
          print "TELEGRAM_ALLOWED_USERS=" new_value
          updated = 1
        }
        next
      }
      { print }
      END {
        if (!updated) print "TELEGRAM_ALLOWED_USERS=" new_value
      }
    ' "$file" >"$tmp"
  else
    printf 'TELEGRAM_ALLOWED_USERS=%s\n' "$new_value" >"$tmp"
  fi
  mv "$tmp" "$file"
}

scope_status() {
  local mode="$1"
  local id="${2:-}"
  local scope_name="${3:-}"
  "$python_bin" - "$mode" "$scopes_yml" "$id" "$scope_name" <<'PY'
import ast
import re
import sys
from pathlib import Path

mode, path_arg = sys.argv[1], sys.argv[2]
telegram_id = sys.argv[3] if len(sys.argv) > 3 else ""
scope_name = sys.argv[4] if len(sys.argv) > 4 else ""
path = Path(path_arg)

if not path.exists():
    print(f"error: scopes file not found: {path}", file=sys.stderr)
    sys.exit(1)

lines = path.read_text(encoding="utf-8").splitlines()
scope_ranges = {}
in_scopes = False
external_scope_allowlist = None

for i, line in enumerate(lines):
    allowlist_match = re.match(r"^poc_external_scope_allowlist:\s*\[(.*)\]\s*$", line)
    if allowlist_match:
        external_scope_allowlist = [
            item.strip().strip("\"'")
            for item in allowlist_match.group(1).split(",")
            if item.strip()
        ]
    if re.match(r"^scopes:\s*$", line):
        in_scopes = True
        continue
    if not in_scopes:
        continue
    if re.match(r"^[A-Za-z0-9_-][A-Za-z0-9_ -]*:\s*$", line):
        in_scopes = False
        continue
    match = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
    if not match:
        continue
    name = match.group(1)
    end = len(lines)
    for j in range(i + 1, len(lines)):
        if re.match(r"^  [A-Za-z0-9_-]+:\s*$", lines[j]) or re.match(r"^[A-Za-z0-9_-][A-Za-z0-9_ -]*:\s*$", lines[j]):
            end = j
            break
    scope_ranges[name] = (i, end)

def parse_ops(text):
    stripped = text.strip()
    if not stripped:
        return []
    try:
        value = ast.literal_eval(stripped)
    except (SyntaxError, ValueError):
        return None
    if not isinstance(value, list):
        return None
    return [str(item) for item in value]

def find_ops(name):
    start, end = scope_ranges[name]
    for index in range(start + 1, end):
        match = re.match(r"^    operators:\s*(.*?)(\s+#.*)?$", lines[index])
        if match:
            return index, parse_ops(match.group(1)), match.group(2) or ""
    return None, [], ""

if mode == "list":
    for name in scope_ranges:
        _, ops, _ = find_ops(name)
        if ops is None:
            print(f"{name}: operators=<unparseable>")
        else:
            print(f"{name}: operators={','.join(ops)}")
    sys.exit(0)

if scope_name not in scope_ranges:
    print(f"error: scope not found in {path}: {scope_name}", file=sys.stderr)
    sys.exit(1)

if external_scope_allowlist is not None and scope_name not in external_scope_allowlist:
    allowed = ", ".join(external_scope_allowlist)
    print(f"error: scope {scope_name} is not allowed for external member onboarding; allowed scopes: {allowed}", file=sys.stderr)
    sys.exit(1)

ops_line, ops, comment = find_ops(scope_name)
if ops is None:
    print(f"error: operators for scope {scope_name} are not an inline list", file=sys.stderr)
    sys.exit(1)

if mode == "contains":
    sys.exit(0 if telegram_id in ops else 2)

if mode == "apply":
    if telegram_id in ops:
        sys.exit(0)
    ops.append(telegram_id)
    rendered = ", ".join(repr(item).replace("'", '"') for item in ops)
    replacement = f"    operators: [{rendered}]{comment}"
    if ops_line is None:
        start, _ = scope_ranges[scope_name]
        lines.insert(start + 1, replacement)
    else:
        lines[ops_line] = replacement
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.exit(0)

print(f"error: unknown mode: {mode}", file=sys.stderr)
sys.exit(1)
PY
}

if "$list"; then
  [[ -z "$telegram_id" && -z "$scope" && "$apply" == false ]] || die "--list cannot be combined with other arguments"
  allowed="$(read_allowed_users "$env_file" || true)"
  count=0
  if [[ -n "$allowed" ]]; then
    IFS=',' read -r -a allowed_items <<<"$allowed"
    for item in "${allowed_items[@]}"; do
      item="${item#"${item%%[![:space:]]*}"}"
      item="${item%"${item##*[![:space:]]}"}"
      [[ -n "$item" ]] && count=$((count + 1))
    done
  fi
  printf 'TELEGRAM_ALLOWED_USERS count: %s\n' "$count"
  scope_status list
  exit 0
fi

[[ -n "$telegram_id" ]] || { usage; exit 1; }
[[ "$telegram_id" =~ ^[0-9]+$ ]] || die "telegram_numeric_id must contain digits only; usernames are not accepted"

allowed="$(read_allowed_users "$env_file" || true)"
allowlist_change=false
if ! id_in_csv "$telegram_id" "$allowed"; then
  allowlist_change=true
fi

operator_change=false
if [[ -n "$scope" ]]; then
  if scope_status contains "$telegram_id" "$scope"; then
    operator_change=false
  else
    rc=$?
    [[ "$rc" -eq 2 ]] || exit "$rc"
    operator_change=true
  fi
fi

if ! "$apply"; then
  if "$allowlist_change"; then
    printf 'would add %s to TELEGRAM_ALLOWED_USERS\n' "$telegram_id"
  fi
  if "$operator_change"; then
    printf 'would add %s to scope %s operators\n' "$telegram_id" "$scope"
  fi
  if ! "$allowlist_change" && ! "$operator_change"; then
    printf 'no changes\n'
  fi
  exit 0
fi

if "$allowlist_change"; then
  write_allowed_users "$env_file" "$telegram_id"
  printf 'added %s to TELEGRAM_ALLOWED_USERS\n' "$telegram_id"
fi

if "$operator_change"; then
  scope_status apply "$telegram_id" "$scope"
  printf 'added %s to scope %s operators\n' "$telegram_id" "$scope"
fi

if ! "$allowlist_change" && ! "$operator_change"; then
  printf 'no changes\n'
fi

printf 'run: hermes gateway restart  (to load the allowlist change)\n'
