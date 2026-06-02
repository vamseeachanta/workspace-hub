#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
script="$repo_root/scripts/deckhand/add-member.sh"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

env_file="$tmpdir/hermes.env"
scopes_yml="$tmpdir/scopes.yml"

write_scopes() {
  cat >"$scopes_yml" <<'EOF'
schema_version: 2

scopes:
  acma:
    operators: ["111"]
    repositories:
      - example/acma
  doris:
    operators: []
    repositories:
      - example/doris
  ecosystem:
    operators: []
    repositories:
      - example/ecosystem

origin_bound_default:
  enabled: true

poc_external_scope_allowlist: [acma, doris]
EOF
}

assert_contains() {
  local needle="$1"
  local file="$2"
  if ! grep -Fq "$needle" "$file"; then
    printf 'expected %s to contain: %s\n' "$file" "$needle" >&2
    printf 'actual:\n' >&2
    sed -n '1,160p' "$file" >&2
    exit 1
  fi
}

assert_not_contains() {
  local needle="$1"
  local file="$2"
  if grep -Fq "$needle" "$file"; then
    printf 'expected %s not to contain: %s\n' "$file" "$needle" >&2
    printf 'actual:\n' >&2
    sed -n '1,160p' "$file" >&2
    exit 1
  fi
}

run_script() {
  DECKHAND_ENV_FILE="$env_file" DECKHAND_SCOPES_YML="$scopes_yml" "$script" "$@"
}

write_scopes
printf 'OTHER_ENV=do-not-print\n' >"$env_file"
if run_script alice >"$tmpdir/non_numeric.out" 2>"$tmpdir/non_numeric.err"; then
  printf 'expected non-numeric id to fail\n' >&2
  exit 1
fi
assert_contains "digits only" "$tmpdir/non_numeric.err"

write_scopes
printf 'OTHER_ENV=do-not-print\nTELEGRAM_ALLOWED_USERS=111\n' >"$env_file"
run_script 222 --scope acma >"$tmpdir/dry_run.out"
assert_contains "would add 222 to TELEGRAM_ALLOWED_USERS" "$tmpdir/dry_run.out"
assert_contains "would add 222 to scope acma operators" "$tmpdir/dry_run.out"
assert_not_contains "222" "$env_file"
assert_not_contains '"222"' "$scopes_yml"

run_script 222 --scope acma --apply >"$tmpdir/apply.out"
assert_contains "added 222 to TELEGRAM_ALLOWED_USERS" "$tmpdir/apply.out"
assert_contains "added 222 to scope acma operators" "$tmpdir/apply.out"
assert_contains "run: hermes gateway restart  (to load the allowlist change)" "$tmpdir/apply.out"
assert_contains "TELEGRAM_ALLOWED_USERS=111,222" "$env_file"
assert_contains 'operators: ["111", "222"]' "$scopes_yml"
if [[ "$(grep -c '^TELEGRAM_ALLOWED_USERS=' "$env_file")" -ne 1 ]]; then
  printf 'expected one TELEGRAM_ALLOWED_USERS line\n' >&2
  exit 1
fi

run_script 222 --scope acma --apply >"$tmpdir/idempotent.out"
assert_contains "no changes" "$tmpdir/idempotent.out"
if [[ "$(grep -o '222' "$env_file" | wc -l)" -ne 1 ]]; then
  printf 'expected allowlist id to appear once\n' >&2
  exit 1
fi
if [[ "$(grep -o '"222"' "$scopes_yml" | wc -l)" -ne 1 ]]; then
  printf 'expected scope operator id to appear once\n' >&2
  exit 1
fi

run_script --list >"$tmpdir/list.out"
assert_contains "TELEGRAM_ALLOWED_USERS count: 2" "$tmpdir/list.out"
assert_contains "acma: operators=111,222" "$tmpdir/list.out"
assert_not_contains "do-not-print" "$tmpdir/list.out"

if run_script 333 --scope ecosystem >"$tmpdir/ecosystem.out" 2>"$tmpdir/ecosystem.err"; then
  printf 'expected disallowed scope to fail\n' >&2
  exit 1
fi
assert_contains "not allowed for external member onboarding" "$tmpdir/ecosystem.err"

printf 'ok\n'
