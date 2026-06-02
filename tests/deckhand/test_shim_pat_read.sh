#!/usr/bin/env bash
# Tests the shims' read_pat_value(): dedicated secrets file takes precedence
# over ~/.hermes/.env, falls back to .env, and fails closed when absent.
# The function is extracted from the live shim source so the test tracks the
# real implementation (no copy).
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
shim="$repo_root/scripts/deckhand/shims/git"

# Extract the read_pat_value function body from the shim and load it.
fn="$(awk '/^read_pat_value\(\) \{/{f=1} f{print} f&&/^\}/{exit}' "$shim")"
[[ -n "$fn" ]] || { echo "FAIL: could not extract read_pat_value from $shim"; exit 1; }
eval "$fn"

pass=0; fail=0
check() { # desc expected actual
  if [[ "$2" == "$3" ]]; then echo "  ok: $1"; pass=$((pass+1));
  else echo "  FAIL: $1 (expected '$2' got '$3')"; fail=$((fail+1)); fi
}

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
export HOME="$tmp"
mkdir -p "$HOME/.hermes/deckhand"

# 1. fallback to .env when no secrets file exists
printf 'DECKHAND_PAT_ACMA=from_env\n' > "$HOME/.hermes/.env"
check "fallback to .env" "from_env" "$(read_pat_value DECKHAND_PAT_ACMA; echo)"

# 2. secrets.env takes precedence over .env
printf 'DECKHAND_PAT_ACMA=from_secrets\n' > "$HOME/.hermes/deckhand/secrets.env"
check "secrets.env precedence over .env" "from_secrets" "$(read_pat_value DECKHAND_PAT_ACMA; echo)"

# 3. key only in secrets.env
printf 'DECKHAND_PAT_DORIS=doris_secret\n' >> "$HOME/.hermes/deckhand/secrets.env"
check "key only in secrets.env" "doris_secret" "$(read_pat_value DECKHAND_PAT_DORIS; echo)"

# 4. fail-closed: key absent everywhere -> non-zero, empty
val="$(read_pat_value DECKHAND_PAT_MISSING)"; rc=$?
check "missing key returns non-zero" "1" "$rc"
check "missing key emits nothing" "" "$val"

# 5. quoted values are unwrapped
printf 'DECKHAND_PAT_Q="quoted_val"\n' > "$HOME/.hermes/deckhand/secrets.env"
check "quoted value unwrapped" "quoted_val" "$(read_pat_value DECKHAND_PAT_Q; echo)"

# 6. malformed pat_env name rejected (fail-closed)
read_pat_value 'bad name' >/dev/null 2>&1; check "invalid key name -> non-zero" "1" "$?"

echo "--- $pass passed, $fail failed ---"
[[ "$fail" -eq 0 ]]
