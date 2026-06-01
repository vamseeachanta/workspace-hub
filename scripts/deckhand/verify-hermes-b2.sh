#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd "$script_dir/../.." && pwd -P)"
shim_dir="${HOME}/.hermes/deckhand/shims"
sample_path="$shim_dir:${PATH:-}"
resolver_env=(
  "PYTHONPATH=$repo_root/src${PYTHONPATH:+:$PYTHONPATH}"
  "HERMES_SESSION_USER_ID=${DECKHAND_VERIFY_USER_ID:-8748731589}"
  "HERMES_SESSION_PLATFORM=${DECKHAND_VERIFY_PLATFORM:-telegram}"
  "HERMES_SESSION_CHAT_ID=${DECKHAND_VERIFY_CHAT_ID:-8748731589}"
  "HERMES_SESSION_THREAD_ID=${DECKHAND_VERIFY_THREAD_ID:-}"
)

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

pass() {
  echo "PASS: $*"
}

[[ -d "$shim_dir" ]] || fail "shim dir missing: $shim_dir"
pass "shim dir exists: $shim_dir"

if PATH="$sample_path" command -v git >/tmp/deckhand-verify-command-v-git.$$ 2>/dev/null; then
  git_path="$(cat /tmp/deckhand-verify-command-v-git.$$)"
  rm -f /tmp/deckhand-verify-command-v-git.$$
else
  rm -f /tmp/deckhand-verify-command-v-git.$$
  fail "git is not resolvable on sample terminal PATH"
fi
[[ "$git_path" == "$shim_dir/git" ]] || fail "sample PATH resolves git to $git_path, expected $shim_dir/git"
pass "sample PATH resolves git to shim"

for tool in gh hub; do
  if [[ -x "$shim_dir/$tool" ]]; then
    resolved="$(PATH="$sample_path" command -v "$tool" || true)"
    [[ "$resolved" == "$shim_dir/$tool" ]] || fail "sample PATH resolves $tool to $resolved, expected $shim_dir/$tool"
    pass "sample PATH resolves $tool to shim"
  else
    fail "missing executable shim: $shim_dir/$tool"
  fi
done

pat_env="$(env "${resolver_env[@]}" python3 -m deckhand.shim_resolve || true)"
[[ -n "$pat_env" ]] || fail "resolver returned no pat_env for test identity"
[[ "$pat_env" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || fail "resolver returned invalid pat_env name"
pass "resolver returned pat_env name for test identity: $pat_env"

[[ -z "${GH_TOKEN:-}" ]] || fail "GH_TOKEN is set in ambient environment"
pass "GH_TOKEN is absent from ambient environment"

echo "Deckhand B2 read-only verification complete."
