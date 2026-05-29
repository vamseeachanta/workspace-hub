#!/usr/bin/env bash
# TDD — #2841 Phase C: weekly consistency check renders a matrix + upserts ONE rolling
# `consistency-drift` issue on FAIL (never duplicates), creates the label before use,
# opens no issue when clean, and exits non-zero on FAIL.
#
# gh is mocked via GH_CMD; the real consistency checks are bypassed with the
# CONSISTENCY_SELFTEST_FAILS seam so matrix/upsert/exit logic is deterministic.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel)"
CHECK="${REPO_ROOT}/scripts/cron/consistency-weekly-check.sh"

fail=0
chk() { if eval "$2"; then echo "  PASS: $1"; else echo "  FAIL: $1"; fail=$((fail+1)); fi; }

WORK="$(mktemp -d)"; trap 'rm -rf "${WORK}"' EXIT
MOCK_LOG="${WORK}/gh-calls.log"

# Mock gh: logs every call; `issue list` returns the contents of $MOCK_EXISTING (a
# number if an open drift issue exists, else empty).
cat > "${WORK}/gh" <<'MOCK'
#!/usr/bin/env bash
echo "$*" >> "${MOCK_LOG}"
case "$1 $2" in
  "label list") echo "" ;;
  "label create") : ;;
  "issue list") cat "${MOCK_EXISTING:-/dev/null}" 2>/dev/null ;;
  "issue create") echo "https://github.test/issues/999" ;;
  "issue edit") : ;;
  *) : ;;
esac
exit 0
MOCK
chmod +x "${WORK}/gh"
export MOCK_LOG
run() { GH_CMD="${WORK}/gh" PATH="${WORK}:${PATH}" "$@"; }

# 1) clean run → matrix written, NO issue created, exit 0
: > "${MOCK_LOG}"
run env CONSISTENCY_SELFTEST_FAILS=0 bash "${CHECK}" >/dev/null 2>&1; rc=$?
chk "clean run exits 0"                       "[ ${rc} -eq 0 ]"
chk "clean run writes a matrix file"          "ls ${REPO_ROOT}/docs/orchestrator-consistency/*-matrix.md >/dev/null 2>&1"
chk "clean run opens NO issue"                "! grep -q 'issue create' '${MOCK_LOG}'"

# 2) drift run, no existing issue → creates exactly one, exits non-zero, label first
: > "${MOCK_LOG}"
export MOCK_EXISTING=/dev/null
run env CONSISTENCY_SELFTEST_FAILS=2 bash "${CHECK}" >/dev/null 2>&1; rc=$?
chk "drift run exits non-zero"                "[ ${rc} -ne 0 ]"
chk "drift run creates an issue"              "grep -q 'issue create' '${MOCK_LOG}'"
chk "label ensured before issue create"       "[ \$(grep -n 'label' '${MOCK_LOG}' | head -1 | cut -d: -f1) -le \$(grep -n 'issue create' '${MOCK_LOG}' | head -1 | cut -d: -f1) ]"

# 3) drift run WITH an existing open issue → edits, does NOT create a duplicate
: > "${MOCK_LOG}"
echo "4242" > "${WORK}/existing.txt"; export MOCK_EXISTING="${WORK}/existing.txt"
run env CONSISTENCY_SELFTEST_FAILS=1 bash "${CHECK}" >/dev/null 2>&1
chk "existing-issue drift updates (edit)"     "grep -q 'issue edit 4242' '${MOCK_LOG}'"
chk "existing-issue drift does NOT duplicate" "! grep -q 'issue create' '${MOCK_LOG}'"

echo "---"
if [ "${fail}" -gt 0 ]; then echo "FAILED: ${fail}"; exit 1; fi
echo "ALL PASS"
