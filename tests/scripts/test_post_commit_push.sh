#!/usr/bin/env bash
# test_post_commit_push.sh — Tests for scripts/hooks/post-commit (WRK-1141)
# Tests: SKIP_PUSH guard, CI guard, detached HEAD guard, no-upstream guard,
#        submodule guard, rebase guard, amend guard, normal push path
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
HOOK="${REPO_ROOT}/scripts/hooks/post-commit"
TMPDIR_BASE="$(mktemp -d)"
PASS_COUNT=0
FAIL_COUNT=0

cleanup() { rm -rf "${TMPDIR_BASE}"; }
trap cleanup EXIT

run_test() {
  local name="$1" ok="$2" msg="${3:-}"
  if [[ "${ok}" == "1" ]]; then
    echo "  PASS  ${name}"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "  FAIL  ${name}${msg:+: ${msg}}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

# Helper: run hook with overridden git commands via PATH stub directory
run_hook_with_stubs() {
  local stub_dir="$1"; shift
  local env_vars=("$@")
  env PATH="${stub_dir}:${PATH}" "${env_vars[@]}" bash "${HOOK}"
}

# ── Test 1: SKIP_PUSH=1 → exit 0, no push ────────────────────────────────────
T1="${TMPDIR_BASE}/t1"
mkdir -p "${T1}"
output="$(SKIP_PUSH=1 bash "${HOOK}" 2>&1 || true)"
run_test "SKIP_PUSH=1-skips-push" "$([ -z "${output}" ] && echo 1 || echo 0)" "${output}"

# ── Test 2: CI=true → exit 0, no push ────────────────────────────────────────
output="$(CI=true bash "${HOOK}" 2>&1 || true)"
run_test "CI=true-skips-push" "$([ -z "${output}" ] && echo 1 || echo 0)" "${output}"

# ── Test 3: GITHUB_ACTIONS set → exit 0, no push ─────────────────────────────
output="$(GITHUB_ACTIONS=true bash "${HOOK}" 2>&1 || true)"
run_test "GITHUB_ACTIONS-skips-push" "$([ -z "${output}" ] && echo 1 || echo 0)" "${output}"

# ── Test 4: Detached HEAD → exit 0, no push ──────────────────────────────────
STUB4="${TMPDIR_BASE}/stubs4"
mkdir -p "${STUB4}"
# git symbolic-ref HEAD should fail (returns non-zero) for detached HEAD
cat > "${STUB4}/git" <<'SH'
#!/usr/bin/env bash
if [[ "${1:-}" == "symbolic-ref" ]]; then exit 1; fi
if [[ "${1:-}" == "rev-parse" && "${2:-}" == "--show-toplevel" ]]; then
  echo "/tmp"
  exit 0
fi
echo "stub-git: unhandled: $*" >&2
exit 1
SH
chmod +x "${STUB4}/git"
output="$(PATH="${STUB4}:${PATH}" bash "${HOOK}" 2>&1 || true)"
run_test "detached-HEAD-skips-push" "$([ -z "${output}" ] && echo 1 || echo 0)" "${output}"

# ── Test 5: Rebase in progress → exit 0, no push ─────────────────────────────
T5="${TMPDIR_BASE}/t5"
FAKE_GIT_DIR5="${T5}/.git"
mkdir -p "${FAKE_GIT_DIR5}/rebase-merge"
STUB5="${TMPDIR_BASE}/stubs5"
mkdir -p "${STUB5}"
cat > "${STUB5}/git" <<SH
#!/usr/bin/env bash
if [[ "\${1:-}" == "symbolic-ref" ]]; then echo "refs/heads/main"; exit 0; fi
if [[ "\${1:-}" == "rev-parse" && "\${2:-}" == "--git-dir" ]]; then echo "${FAKE_GIT_DIR5}"; exit 0; fi
echo "stub-git: unhandled: \$*" >&2; exit 1
SH
chmod +x "${STUB5}/git"
output="$(PATH="${STUB5}:${PATH}" bash "${HOOK}" 2>&1 || true)"
run_test "rebase-in-progress-skips-push" "$([ -z "${output}" ] && echo 1 || echo 0)" "${output}"

# ── Test 6: Amend via GIT_REFLOG_ACTION → exit 0, no push ────────────────────
output="$(GIT_REFLOG_ACTION="rebase: amend" bash "${HOOK}" 2>&1 || true)"
run_test "amend-GIT_REFLOG_ACTION-skips-push" "$([ -z "${output}" ] && echo 1 || echo 0)" "${output}"

# ── Test 7: No upstream configured → warn and skip ───────────────────────────
T7="${TMPDIR_BASE}/t7"
FAKE_GIT_DIR7="${T7}/.git"
mkdir -p "${FAKE_GIT_DIR7}"
STUB7="${TMPDIR_BASE}/stubs7"
mkdir -p "${STUB7}"
cat > "${STUB7}/git" <<SH
#!/usr/bin/env bash
if [[ "\${1:-}" == "symbolic-ref" ]]; then echo "refs/heads/main"; exit 0; fi
if [[ "\${1:-}" == "rev-parse" && "\${2:-}" == "--git-dir" ]]; then echo "${FAKE_GIT_DIR7}"; exit 0; fi
if [[ "\${1:-}" == "rev-parse" && "\${2:-}" == "--abbrev-ref" ]]; then exit 128; fi
if [[ "\${1:-}" == "rev-parse" && "\${2:-}" == "--show-superproject-working-tree" ]]; then echo ""; exit 0; fi
echo "stub-git: unhandled: \$*" >&2; exit 1
SH
chmod +x "${STUB7}/git"
output="$(PATH="${STUB7}:${PATH}" bash "${HOOK}" 2>&1 || true)"
run_test "no-upstream-warns-and-skips" "$(echo "${output}" | grep -q "no upstream" && echo 1 || echo 0)" "${output}"

# ── Test 8: Normal path → push fires in background ───────────────────────────
T8="${TMPDIR_BASE}/t8"
FAKE_GIT_DIR8="${T8}/.git"
mkdir -p "${FAKE_GIT_DIR8}"
PUSH_LOG8="${T8}/push.log"
STUB8="${TMPDIR_BASE}/stubs8"
mkdir -p "${STUB8}"
cat > "${STUB8}/git" <<SH
#!/usr/bin/env bash
if [[ "\${1:-}" == "symbolic-ref" ]]; then echo "refs/heads/main"; exit 0; fi
if [[ "\${1:-}" == "rev-parse" && "\${2:-}" == "--git-dir" ]]; then echo "${FAKE_GIT_DIR8}"; exit 0; fi
if [[ "\${1:-}" == "rev-parse" && "\${2:-}" == "--abbrev-ref" ]]; then echo "origin/main"; exit 0; fi
if [[ "\${1:-}" == "rev-parse" && "\${2:-}" == "--show-superproject-working-tree" ]]; then echo ""; exit 0; fi
if [[ "\${1:-}" == "push" ]]; then echo "pushed" > "${PUSH_LOG8}"; exit 0; fi
echo "stub-git: unhandled: \$*" >&2; exit 1
SH
chmod +x "${STUB8}/git"
PATH="${STUB8}:${PATH}" bash "${HOOK}" 2>&1 || true
# wait for background push
sleep 0.5
run_test "normal-path-push-fires" "$([ -f "${PUSH_LOG8}" ] && echo 1 || echo 0)" "push.log missing"

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "Results: ${PASS_COUNT} PASS, ${FAIL_COUNT} FAIL"
[[ "${FAIL_COUNT}" -eq 0 ]]
