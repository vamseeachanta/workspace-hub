#!/usr/bin/env bash
# test_check_archived_marine_skills.sh — Tests for archived marine skill public-surface checks.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../check-archived-marine-skills.py"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

pass() { TESTS_PASSED=$((TESTS_PASSED + 1)); echo "  PASS: $1"; }
fail() {
  TESTS_FAILED=$((TESTS_FAILED + 1)); echo "  FAIL: $1"
  [[ -n "${2:-}" ]] && echo "        $2"
}
run_test() { TESTS_RUN=$((TESTS_RUN + 1)); echo ""; echo "--- Test ${TESTS_RUN}: $1 ---"; }

make_tmpdir() {
  if [[ -z "${TMPDIR:-}" ]]; then
    echo "TMPDIR must be set for archived marine skill checker tests" >&2
    exit 2
  fi
  mktemp -d "$TMPDIR/archived-marine-check.XXXXXX"
}

test_self_test() {
  run_test "self-test exercises each rule and allowed form"
  if python3 "$SCRIPT_UNDER_TEST" --self-test >/dev/null 2>&1; then
    pass "self-test exits 0"
  else
    fail "self-test failed"
  fi
}

test_flags_synthetic_residue() {
  run_test "synthetic residue is rejected without echoing matched text"
  local td output rc slash backslash
  td="$(make_tmpdir)"
  slash="/"
  backslash="\\"
  {
    printf 'client: Example Name\n'
    printf 'tool: Q:%sexample\n' "$slash"
    printf 'share: %s%sserver%sshare\n' "$backslash" "$backslash" "$backslash"
    printf 'root: %shome%sperson%srepo\n' "$slash" "$slash" "$slash"
    printf 'disk: %smnt%sdisk%srepo\n' "$slash" "$slash" "$slash"
    printf '%s\n' '"Example Name" -> Client A'
  } > "$td/SKILL.md"
  set +e
  output="$(python3 "$SCRIPT_UNDER_TEST" "$td" 2>&1)"
  rc=$?
  set -e
  rm -rf "$td"
  if [[ $rc -eq 0 ]]; then
    fail "synthetic violations were accepted"
    return
  fi
  if [[ "$output" == *"Example Name"* || "$output" == *"server"* || "$output" == *"person"* ]]; then
    fail "output echoed matched text" "$output"
  elif [[ "$output" == *"RULE label_identifier"* && "$output" == *"RULE drive_abs"* && "$output" == *"RULE unc_share"* && "$output" == *"RULE home_path"* && "$output" == *"RULE mount_path"* && "$output" == *"RULE codename_mapping"* ]]; then
    pass "all expected rule names appeared without matched text"
  else
    fail "output missed an expected rule" "$output"
  fi
}

test_public_url_and_signature_pass() {
  run_test "public URL and typed signature parameter pass"
  local td
  td="$(make_tmpdir)"
  {
    printf 'reference: https://example.org/docs\n'
    printf 'def configure(\n'
    printf '    vessel: OrcFxAPI.OrcaFlexObject,\n'
    printf ') -> None:\n'
  } > "$td/SKILL.md"
  if python3 "$SCRIPT_UNDER_TEST" "$td" >/dev/null 2>&1; then
    pass "public URL and typed parameter exit 0"
  else
    fail "public URL or typed parameter was rejected"
  fi
  rm -rf "$td"
}

test_drive_and_share_paths_fail() {
  run_test "drive path and share path are still flagged"
  local td output rc slash backslash
  td="$(make_tmpdir)"
  slash="/"
  backslash="\\"
  {
    printf 'tool: Q:%sexample\n' "$slash"
    printf 'share: %s%sserver%sshare\n' "$backslash" "$backslash" "$backslash"
  } > "$td/SKILL.md"
  set +e
  output="$(python3 "$SCRIPT_UNDER_TEST" "$td" 2>&1)"
  rc=$?
  set -e
  rm -rf "$td"
  if [[ $rc -eq 0 ]]; then
    fail "drive/share paths were accepted"
  elif [[ "$output" == *"RULE drive_abs"* && "$output" == *"RULE unc_share"* ]]; then
    pass "drive and share rules appeared"
  else
    fail "drive/share output missed expected rules" "$output"
  fi
}

test_fenced_configuration_label_still_fails() {
  run_test "fenced configuration label with non-codename value is flagged"
  local td output rc
  td="$(make_tmpdir)"
  {
    printf '```yaml\n'
    printf 'client: Example Name\n'
    printf '```\n'
  } > "$td/SKILL.md"
  set +e
  output="$(python3 "$SCRIPT_UNDER_TEST" "$td" 2>&1)"
  rc=$?
  set -e
  rm -rf "$td"
  if [[ $rc -eq 0 ]]; then
    fail "fenced configuration label was accepted"
  elif [[ "$output" == *"RULE label_identifier"* ]]; then
    pass "fenced configuration label was flagged"
  else
    fail "fenced configuration label missed expected rule" "$output"
  fi
}

test_fenced_configuration_codename_passes() {
  run_test "fenced configuration label with codename passes"
  local td
  td="$(make_tmpdir)"
  {
    printf '```yaml\n'
    printf 'client: Client A\n'
    printf '```\n'
  } > "$td/SKILL.md"
  if python3 "$SCRIPT_UNDER_TEST" "$td" >/dev/null 2>&1; then
    pass "fenced codename label exits 0"
  else
    fail "fenced codename label was rejected"
  fi
  rm -rf "$td"
}

test_allowlist_uses_repo_relative_key_for_absolute_subtree() {
  run_test "absolute subtree path uses repository-relative allowlist key"
  local repo_root abs_subtree
  repo_root="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
  abs_subtree="$repo_root/.claude/_archive/2026-10-09-l8/.claude/skills/engineering/marine-offshore"
  if python3 "$SCRIPT_UNDER_TEST" "$abs_subtree" >/dev/null 2>&1; then
    pass "absolute subtree exits 0"
  else
    fail "absolute subtree path was rejected"
  fi
}

test_default_subtree_resolves_from_repo_root() {
  run_test "default subtree resolves from repository root outside cwd"
  local repo_root td output rc
  repo_root="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
  td="$(make_tmpdir)"
  set +e
  output="$(
    REPO_ROOT="$repo_root" SCRIPT_UNDER_TEST="$SCRIPT_UNDER_TEST" OFFROOT="$td" python3 - <<'PY'
import importlib.util
import os
from pathlib import Path

script = Path(os.environ["SCRIPT_UNDER_TEST"])
spec = importlib.util.spec_from_file_location("archived_marine_check", script)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def run_from(cwd: str) -> tuple[int, int]:
    seen = []
    original_scan = module.scan

    def recording_scan(root):
        paths = module.iter_files(root)
        seen.append(len(paths))
        return original_scan(root)

    module.scan = recording_scan
    old_cwd = os.getcwd()
    try:
        os.chdir(cwd)
        rc = module.main([])
    finally:
        os.chdir(old_cwd)
        module.scan = original_scan
    return rc, seen[-1] if seen else -1


repo_root = os.environ["REPO_ROOT"]
root_rc, root_count = run_from(repo_root)
offroot_rc, offroot_count = run_from(os.environ["OFFROOT"])
print(f"root_rc={root_rc} root_count={root_count}")
print(f"offroot_rc={offroot_rc} offroot_count={offroot_count}")
if root_rc != 0 or offroot_rc != 0 or root_count <= 0 or root_count != offroot_count:
    raise SystemExit(1)
PY
  )"
  rc=$?
  set -e
  rm -rf "$td"
  if [[ $rc -eq 0 ]]; then
    pass "default subtree scans the same files outside cwd"
  else
    fail "default subtree did not resolve from repository root" "$output"
  fi
}

test_allowed_forms_pass() {
  run_test "codename, placeholder, neutral description, and structured examples pass"
  local td
  td="$(make_tmpdir)"
  {
    printf 'client: Client A\n'
    printf 'vessel: Vessel A\n'
    printf 'operator: a semi-submersible operator\n'
    printf 'project: <project-name>\n'
    printf 'vessel: { length: 300.0 }\n'
  } > "$td/SKILL.md"
  if python3 "$SCRIPT_UNDER_TEST" "$td" >/dev/null 2>&1; then
    pass "allowed forms exit 0"
  else
    fail "allowed forms were rejected"
  fi
  rm -rf "$td"
}

test_self_test
test_flags_synthetic_residue
test_public_url_and_signature_pass
test_drive_and_share_paths_fail
test_fenced_configuration_label_still_fails
test_fenced_configuration_codename_passes
test_allowlist_uses_repo_relative_key_for_absolute_subtree
test_default_subtree_resolves_from_repo_root
test_allowed_forms_pass

echo ""
echo "=================================="
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "=================================="

[[ $TESTS_FAILED -gt 0 ]] && exit 1
exit 0
