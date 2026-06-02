#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage:
  add-member.sh <telegram_numeric_id> [--scope acma|doris] [--operator] [--no-welcome] [--apply]
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
operator=false
welcome=true
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
    --operator)
      operator=true
      shift
      ;;
    --scope)
      [[ $# -ge 2 ]] || die "--scope requires a value"
      scope="$2"
      shift 2
      ;;
    --no-welcome)
      welcome=false
      shift
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

def find_welcome_target(name):
    start, end = scope_ranges[name]
    in_bindings = False
    binding = None
    bindings = []
    for index in range(start + 1, end):
        line = lines[index]
        if re.match(r"^    channel_repo_bindings:\s*(#.*)?$", line):
            in_bindings = True
            continue
        if in_bindings and re.match(r"^    [A-Za-z0-9_-]+:\s*", line):
            break
        if not in_bindings:
            continue
        item_match = re.match(r"^      -\s+([A-Za-z0-9_-]+):\s*(.*?)(?:\s+#.*)?$", line)
        if item_match:
            if binding is not None:
                bindings.append(binding)
            binding = {item_match.group(1): item_match.group(2).strip().strip("\"'")}
            continue
        kv_match = re.match(r"^        ([A-Za-z0-9_-]+):\s*(.*?)(?:\s+#.*)?$", line)
        if binding is not None and kv_match:
            binding[kv_match.group(1)] = kv_match.group(2).strip().strip("\"'")
    if binding is not None:
        bindings.append(binding)
    for candidate in bindings:
        if str(candidate.get("authorize_members", "")).lower() == "true":
            platform = candidate.get("platform")
            channel_id = candidate.get("channel_id")
            if platform and channel_id:
                return platform, channel_id
    return None

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

if mode == "welcome-target":
    target = find_welcome_target(scope_name)
    if target is None:
        sys.exit(2)
    print(f"{target[0]}:{target[1]}")
    sys.exit(0)

print(f"error: unknown mode: {mode}", file=sys.stderr)
sys.exit(1)
PY
}

welcome_target() {
  local scope_name="$1"
  scope_status welcome-target "" "$scope_name"
}

send_welcome() {
  local target="$1"
  local scope_name="$2"
  local msg
  msg="✅ Welcome — you're now authorized for the ${scope_name} channel. Please re-send your request (messages sent before authorization weren't processed)."

  if ! command -v hermes >/dev/null 2>&1; then
    printf 'warning: hermes not found; welcome not sent to %s\n' "$target" >&2
    return 0
  fi
  if ! hermes send --to "$target" "$msg"; then
    printf 'warning: hermes send failed; welcome not sent to %s\n' "$target" >&2
  fi
}

if "$list"; then
  [[ -z "$telegram_id" && -z "$scope" && "$apply" == false && "$operator" == false && "$welcome" == true ]] || die "--list cannot be combined with other arguments"
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
if "$operator" && [[ -z "$scope" ]]; then
  die "--operator requires --scope"
fi

allowed="$(read_allowed_users "$env_file" || true)"
allowlist_change=false
if ! id_in_csv "$telegram_id" "$allowed"; then
  allowlist_change=true
fi

operator_change=false
if "$operator"; then
  if scope_status contains "$telegram_id" "$scope"; then
    operator_change=false
  else
    rc=$?
    [[ "$rc" -eq 2 ]] || exit "$rc"
    operator_change=true
  fi
fi

welcome_target_value=""
welcome_target_found=false
if [[ -n "$scope" ]] && "$welcome"; then
  if welcome_target_value="$(welcome_target "$scope")"; then
    welcome_target_found=true
  else
    rc=$?
    [[ "$rc" -eq 2 ]] || exit "$rc"
  fi
fi

if ! "$apply"; then
  if "$allowlist_change"; then
    printf 'would add %s to TELEGRAM_ALLOWED_USERS\n' "$telegram_id"
  fi
  if "$operator_change"; then
    printf 'would add %s to scope %s operators\n' "$telegram_id" "$scope"
  fi
  if [[ -n "$scope" ]] && "$welcome"; then
    if "$welcome_target_found"; then
      printf 'would welcome: %s\n' "$welcome_target_value"
    else
      printf 'no welcome target for scope %s (no authorize_members group binding); skipping welcome\n' "$scope"
    fi
  fi
  if ! "$allowlist_change" && ! "$operator_change" && { [[ -z "$scope" ]] || ! "$welcome"; }; then
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

if [[ -n "$scope" ]] && "$welcome"; then
  if "$welcome_target_found"; then
    send_welcome "$welcome_target_value" "$scope"
  else
    printf 'no welcome target for scope %s (no authorize_members group binding); skipping welcome\n' "$scope"
  fi
fi

if ! "$allowlist_change" && ! "$operator_change"; then
  printf 'no changes\n'
fi

printf 'run: hermes gateway restart  (to load the allowlist change)\n'
