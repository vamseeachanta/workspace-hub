#!/usr/bin/env bash
# populate-hf-token.sh — distribute the permanent Hugging Face API token across
# the SSH-reachable fleet, without ever exposing the token.
#
# WHY: all fleet HF credentials turned out to be hf_oauth_ SESSION tokens, which
# expire by design and silently break every HF publish lane (wh#3598). The fix
# is ONE permanent write token, entered ONCE, then fanned out — and never
# displayed, logged, put in argv, or exported into shell profiles again.
#
# Exposure model (the "never expose it" contract):
#   - Canonical copy = ~/.cache/huggingface/token on THIS machine (mode 600).
#   - Prompt is silent (read -rsp) and happens ONLY when no valid canonical
#     copy exists; otherwise the canonical file is reused — future fan-outs
#     (new machine joins) need no re-entry and no regeneration.
#   - Transport = piped over ssh stdin (never in argv, never in remote env,
#     never in process listings); remote write is umask-077 cat > file.
#   - Output prints ONLY status codes, usernames, and prefix classes.
#   - Shell-profile HF_TOKEN exports are flagged (file:line only — the env var
#     takes precedence over the token file, so a stale export re-breaks
#     everything after a refresh; exports also leak into every process env).
#
# Usage:
#   scripts/fleet/populate-hf-token.sh --check      # report-only fleet health
#   scripts/fleet/populate-hf-token.sh              # distribute + verify
#
# Config: config/fleet-ssh-hosts.yml (ssh aliases; users live in ~/.ssh/config)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HOSTS_YML="$REPO_ROOT/config/fleet-ssh-hosts.yml"
TOKEN_FILE="$HOME/.cache/huggingface/token"
WHOAMI_URL="https://huggingface.co/api/whoami-v2"
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=8)
CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

yaml_list() { # yaml_list <file> <key> — flat "- item" entries under a top-level key
  awk -v key="$2:" '
    $0 == key {on=1; next}
    on && /^[a-z_]+:/ {on=0}
    on && /^ *- / {sub(/^ *- */, ""); print}
  ' "$1"
}
yaml_map() { # yaml_map <file> <key> <name> — value of "  name: value" under key
  awk -v key="$2:" -v want="$3" '
    $0 == key {on=1; next}
    on && /^[a-z_]+:/ {on=0}
    on {gsub(/^ +| +$/,""); split($0, kv, ": "); if (kv[1]==want) print kv[2]}
  ' "$1"
}

classify() { # prefix class only — NEVER the value
  case "$1" in
    hf_oauth*) echo "hf_oauth (EXPIRING session token)" ;;
    hf_*)      echo "hf_ (permanent API token)" ;;
    *)         echo "unknown-format" ;;
  esac
}

whoami_local() { # $1=token → "code:username"
  local out code user
  out=$(curl -s -w '\n%{http_code}' -H "Authorization: Bearer $1" "$WHOAMI_URL")
  code=${out##*$'\n'}
  user=$(printf '%s' "${out%$'\n'*}" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
  echo "$code:${user:-?}"
}

# Remote helpers run everything token-touching ON the remote — nothing comes back
# but a status code / count.
remote_whoami() { # $1=host
  ssh -n "${SSH_OPTS[@]}" "$1" \
    'test -s ~/.cache/huggingface/token && curl -s -o /dev/null -w "%{http_code}" \
       -H "Authorization: Bearer $(tr -d "[:space:]" < ~/.cache/huggingface/token)" \
       '"$WHOAMI_URL"' || echo MISSING' 2>/dev/null || echo UNREACHABLE
}
remote_prefix_class() { # $1=host
  ssh -n "${SSH_OPTS[@]}" "$1" \
    'head -c 9 ~/.cache/huggingface/token 2>/dev/null | grep -q "^hf_oauth" && echo oauth \
     || { head -c 3 ~/.cache/huggingface/token 2>/dev/null | grep -q "^hf_" && echo permanent \
     || echo none; }' 2>/dev/null || echo unreachable
}
remote_env_conflicts() { # $1=host → file:line list, values never printed
  ssh -n "${SSH_OPTS[@]}" "$1" \
    'grep -n "HF_TOKEN" ~/.bashrc ~/.profile ~/.bash_profile 2>/dev/null | cut -d: -f1,2' \
    2>/dev/null || true
}
reach() { # $1=primary → echoes first reachable alias (primary or fallback), or ""
  local host="$1" fb
  if ssh -n "${SSH_OPTS[@]}" "$host" true 2>/dev/null; then echo "$host"; return; fi
  fb=$(yaml_map "$HOSTS_YML" fallbacks "$host")
  if [ -n "$fb" ] && ssh -n "${SSH_OPTS[@]}" "$fb" true 2>/dev/null; then echo "$fb"; return; fi
  echo ""
}

# --- 1. canonical token on THIS machine -------------------------------------
TOKEN=""
if [ -s "$TOKEN_FILE" ]; then
  TOKEN=$(tr -d '[:space:]' < "$TOKEN_FILE")
fi
local_state="absent"
if [ -n "$TOKEN" ]; then
  case "$TOKEN" in
    hf_oauth*) local_state="oauth-session (expires — nonconforming)" ;;
    hf_*)
      res=$(whoami_local "$TOKEN")
      if [ "${res%%:*}" = "200" ]; then
        local_state="VALID permanent token (user=${res#*:})"
      else
        local_state="invalid (whoami ${res%%:*})"
      fi
      ;;
    *) local_state="unknown-format" ;;
  esac
fi
echo "ace-linux-1 (local canonical): $local_state"

if [ "$CHECK_ONLY" -eq 0 ] && [[ "$local_state" != VALID* ]]; then
  echo
  echo "No valid permanent token on this machine. Create ONE permanent WRITE token"
  echo "at https://huggingface.co/settings/tokens (classic or fine-grained; NOT a"
  echo "browser-login hf_oauth session token). You will not need to do this again."
  read -rsp "Paste token (input hidden): " TOKEN; echo
  case "$TOKEN" in
    hf_oauth*) echo "REFUSED: that is an hf_oauth session token — it will expire again."; exit 1 ;;
    hf_*) : ;;
    *) echo "REFUSED: unrecognized token format ($(classify "$TOKEN"))."; exit 1 ;;
  esac
  res=$(whoami_local "$TOKEN")
  [ "${res%%:*}" = "200" ] || { echo "REFUSED: whoami returned ${res%%:*}."; exit 1; }
  umask 077
  mkdir -p "$(dirname "$TOKEN_FILE")"
  printf '%s\n' "$TOKEN" > "$TOKEN_FILE"
  echo "Stored canonical copy (mode 600). user=${res#*:}"
fi

# local env-conflict check (file:line only)
conf=$(grep -n "HF_TOKEN" ~/.bashrc ~/.profile ~/.bash_profile 2>/dev/null | cut -d: -f1,2 || true)
[ -n "$conf" ] && echo "WARN local shell-profile HF_TOKEN export (env overrides the token file — remove/comment it):" && echo "$conf" | sed 's/^/  /'

# --- 2. fan out over SSH -----------------------------------------------------
echo
printf '%-14s %-12s %-10s %-9s %s\n' MACHINE REACHED WHOAMI PREFIX ENV-CONFLICT
while IFS= read -r host; do
  [ -z "$host" ] && continue
  alias_used=$(reach "$host")
  if [ -z "$alias_used" ]; then
    printf '%-14s %-12s %-10s %-9s %s\n' "$host" UNREACHABLE - - -
    continue
  fi
  if [ "$CHECK_ONLY" -eq 0 ]; then
    tr -d '[:space:]' < "$TOKEN_FILE" | ssh "${SSH_OPTS[@]}" "$alias_used" \
      'umask 077; mkdir -p ~/.cache/huggingface; cat > ~/.cache/huggingface/token; printf "\n" >> ~/.cache/huggingface/token'
  fi
  code=$(remote_whoami "$alias_used")
  pclass=$(remote_prefix_class "$alias_used")
  envc=$(remote_env_conflicts "$alias_used")
  printf '%-14s %-12s %-10s %-9s %s\n' "$host" "$alias_used" "$code" "$pclass" "${envc:-none}"
done < <(yaml_list "$HOSTS_YML" ssh_hosts)

# --- 3. machines with no remote-exec channel --------------------------------
manual=$(yaml_list "$HOSTS_YML" manual_hosts)
if [ -n "$manual" ]; then
  echo
  echo "No SSH channel (do on-box, PowerShell):"
  echo '  New-Item -ItemType Directory -Force "$env:USERPROFILE\.cache\huggingface" | Out-Null'
  echo '  Read-Host -AsSecureString "HF token" | ConvertFrom-SecureString -AsPlainText | Set-Content "$env:USERPROFILE\.cache\huggingface\token" -NoNewline'
  echo "$manual" | sed 's/^/  - /'
fi

echo
echo "Done. Verify any machine later with: $0 --check"
