#!/usr/bin/env bash
# test_resync_skill_links.sh — SANDBOXED tests for scripts/skills/resync-skill-links.sh (#3251).
#
# CONTRACT: every test builds a throwaway ecosystem under `mktemp -d` and points the script at it
# via WORKSPACE_HUB. It NEVER scans the real workspace-hub ecosystem or any parent dir, and writes
# NOTHING under the real .claude/state/. The outer script intentionally does NOT use `set -e` so
# expected-failure tests don't abort the run.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RESYNC="${REPO_ROOT}/scripts/skills/resync-skill-links.sh"
PROPAGATE_SRC="${REPO_ROOT}/scripts/propagate-ecosystem.sh"

PASS=0; FAIL=0
pass() { echo "PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAIL: $1"; FAIL=$((FAIL + 1)); }
assert_eq()       { [[ "$2" == "$3" ]] && pass "$1" || fail "$1 (expected '$3', got '$2')"; }
assert_contains() { case "$2" in *"$3"*) pass "$1";; *) fail "$1 (missing '$3' in: $2)";; esac; }
assert_file()     { [[ -f "$2" ]] && pass "$1" || fail "$1 (no file $2)"; }

test_failed_sandbox_assignments() {
  local assignments line result count=0
  assignments="$(grep -E '^[[:space:]]*hub="\$\(new_sandbox' "${BASH_SOURCE[0]}")" || return 1
  while IFS= read -r line; do
    # Execute only the source assignment line. All possible inline dependencies
    # are non-writing stubs; no original test body or real setup is executed.
    bash -c 'new_sandbox() { return 1; }; add_repo() { exit 97; };
      cp() { exit 97; }; mkdir() { exit 97; }; eval "$1"; exit 97' _ "$line"
    result=$?; count=$((count + 1))
    assert_eq "failed_sandbox_assignment_$count" "$result" "1"
  done <<< "$assignments"
  [[ "$count" -gt 0 ]]
}

if [[ "${SANDBOX_FAILURE_CHECK_ONLY:-0}" == 1 ]]; then
  test_failed_sandbox_assignments || exit 1
  [[ "$FAIL" == 0 ]]; exit $?
fi

TEST_PARENT="$(mktemp -d)" || exit 1
cleanup() {
  [[ -n "$TEST_PARENT" && "$TEST_PARENT" != / && -d "$TEST_PARENT" ]] || return
  rm -rf -- "$TEST_PARENT"
}
trap cleanup EXIT
test_failed_sandbox_assignments || exit 1

# new_sandbox [template_dirs...] — echoes <sbx>/wshub. Templates default to "meta" so workflows +
# guidelines slots resolve to TEMPLATE-ABSENT (keeps single-cell classify tests isolated).
new_sandbox() {
  local sbx hub tdir
  sbx="$(mktemp -d "$TEST_PARENT/case.XXXXXX")" || return 1
  hub="$sbx/wshub"
  mkdir -p "$hub/.claude/skills/_internal" "$hub/scripts"
  mkdir -p "$hub/scripts/lib" "$hub/scripts/skills"
  cp "$REPO_ROOT/scripts/lib/reparse_guard.sh" "$hub/scripts/lib/" || return 1
  cp "$REPO_ROOT/scripts/skills/native_skill_root.py" "$hub/scripts/skills/" || return 1
  local templates=("$@"); [[ ${#templates[@]} -eq 0 ]] && templates=("meta")
  for tdir in "${templates[@]}"; do
    mkdir -p "$hub/.claude/skills/_internal/$tdir"
    printf -- '---\nname: %s\n---\nshared %s template body\n' "$tdir" "$tdir" \
      > "$hub/.claude/skills/_internal/$tdir/SKILL.md"
  done
  echo "$hub"
}

# add_repo <hub> <name> [nested|flat] — create an empty ecosystem repo with .claude/skills/
add_repo() {
  local hub="$1" name="$2" loc="${3:-nested}" base
  if [[ "$loc" == "flat" ]]; then base="$(dirname "$hub")/$name"; else base="$hub/$name"; fi
  mkdir -p "$base/.claude/skills"
  echo "$base"
}

link_healthy()  { ln -s "$1/.claude/skills/_internal/$3" "$2/.claude/skills/$3"; } # hub repo shared
link_dangling() { ln -s "$1/.claude/skills/_internal/does-not-exist-$3" "$2/.claude/skills/$3"; }
make_flattened(){ printf 'IntxLNK\1../../wshub/.claude/skills/_internal/%s' "$3" > "$2/.claude/skills/$3"; }
make_modified() { mkdir -p "$2/.claude/skills/$3"; printf -- '---\nname: %s\n---\nLOCALLY EDITED body\n' "$3" > "$2/.claude/skills/$3/SKILL.md"; }
make_matching() { mkdir -p "$2/.claude/skills/$3"; cp "$1/.claude/skills/_internal/$3/SKILL.md" "$2/.claude/skills/$3/SKILL.md"; }

run_report() {
  # run_report <hub> [extra args...] — report mode, fixed machine label; echoes the state JSON
  local hub="$1"; shift
  WORKSPACE_HUB="$hub" EQ_MACHINE="test-box" EQ_SKILL_LINK_ALLOWLIST="" \
    bash "$RESYNC" "$@" >/dev/null 2>&1
  cat "$hub/.claude/state/skill-link-health-test-box.json" 2>/dev/null
}

jget() { # jget <json> <key> -> integer/string value (naive but sufficient for the flat shape)
  printf '%s' "$1" | grep -o "\"$2\": *[^,}]*" | head -1 | sed 's/.*: *//; s/^"//; s/"$//'
}

if [[ "${NATIVE_ADMISSION_ONLY:-0}" != 1 && "${CODEX_ONLY_ONLY:-0}" != 1 ]]; then
# ── T1: classify HEALTHY ────────────────────────────────────────────────────
hub="$(new_sandbox meta)" || exit 1
r="$(add_repo "$hub" repo-healthy nested)"; link_healthy "$hub" "$r" meta
json="$(run_report "$hub")"
assert_eq "test_classify_healthy" "$(jget "$json" healthy)" "1"

# ── T2: classify MISSING ────────────────────────────────────────────────────
hub="$(new_sandbox meta)" || exit 1
add_repo "$hub" repo-missing flat >/dev/null
json="$(run_report "$hub")"
assert_eq "test_classify_missing" "$(jget "$json" missing)" "1"

# ── T3: classify DANGLING ───────────────────────────────────────────────────
hub="$(new_sandbox meta)" || exit 1
r="$(add_repo "$hub" repo-dangling nested)"; link_dangling "$hub" "$r" meta
json="$(run_report "$hub")"
assert_eq "test_classify_dangling" "$(jget "$json" dangling)" "1"

# ── T4: classify FLATTENED ──────────────────────────────────────────────────
hub="$(new_sandbox meta)" || exit 1
r="$(add_repo "$hub" repo-flattened flat)"; make_flattened "$hub" "$r" meta
json="$(run_report "$hub")"
assert_eq "test_classify_flattened" "$(jget "$json" flattened)" "1"

# ── T5: classify MODIFIED-REAL-DIR ──────────────────────────────────────────
hub="$(new_sandbox meta)" || exit 1
r="$(add_repo "$hub" repo-modified nested)"; make_modified "$hub" "$r" meta
json="$(run_report "$hub")"
assert_eq "test_classify_modified_real_dir" "$(jget "$json" modified_real_dir)" "1"

# A real dir matching the template classifies HEALTHY (not MODIFIED).
hub="$(new_sandbox meta)" || exit 1
r="$(add_repo "$hub" repo-realmatch nested)"; make_matching "$hub" "$r" meta
json="$(run_report "$hub")"
assert_eq "test_classify_matching_real_dir_healthy" "$(jget "$json" healthy)" "1"

# ── T6: classify TEMPLATE-ABSENT (guidelines/workflows have no _internal template) ──
hub="$(new_sandbox meta)" || exit 1
r="$(add_repo "$hub" repo-ta nested)"; link_healthy "$hub" "$r" meta
json="$(run_report "$hub")"
# 1 repo x 3 shared dirs: meta=HEALTHY, workflows+guidelines=TEMPLATE-ABSENT
assert_eq "test_classify_template_absent" "$(jget "$json" template_absent)" "2"

# ── T7: state JSON shape + counts sum to repos x dirs ───────────────────────
hub="$(new_sandbox meta)" || exit 1
r1="$(add_repo "$hub" repo-h nested)"; link_healthy "$hub" "$r1" meta
r2="$(add_repo "$hub" repo-m flat)"   # all missing/template-absent
r3="$(add_repo "$hub" repo-d nested)"; link_dangling "$hub" "$r3" meta
json="$(run_report "$hub")"
for k in machine audited_at platform repos_total healthy missing dangling flattened \
         modified_real_dir template_absent repairable unexpected_missing_repos worst_state schema_version; do
  assert_contains "test_state_json_has_key_$k" "$json" "\"$k\""
done
assert_eq "test_state_json_schema_version" "$(jget "$json" schema_version)" "1"
rt="$(jget "$json" repos_total)"
sum=$(( $(jget "$json" healthy) + $(jget "$json" missing) + $(jget "$json" dangling) \
      + $(jget "$json" flattened) + $(jget "$json" modified_real_dir) + $(jget "$json" template_absent) ))
assert_eq "test_state_json_counts_sum" "$sum" "$(( rt * 3 ))"
assert_eq "test_state_json_repairable" "$(jget "$json" repairable)" \
  "$(( $(jget "$json" missing) + $(jget "$json" dangling) + $(jget "$json" flattened) ))"
assert_eq "test_state_json_worst_dangling" "$(jget "$json" worst_state)" "DANGLING"

# ── T8: report writes state ONLY under the sandbox (real .claude/state untouched) ──
REAL_STATE="${REPO_ROOT}/.claude/state"
before="$(ls "$REAL_STATE"/skill-link-health-* 2>/dev/null | wc -l)"
hub="$(new_sandbox meta)" || exit 1; add_repo "$hub" repo-x nested >/dev/null
run_report "$hub" >/dev/null
after="$(ls "$REAL_STATE"/skill-link-health-* 2>/dev/null | wc -l)"
assert_eq "test_state_written_under_sandbox_only_real_untouched" "$after" "$before"
assert_file "test_state_written_under_sandbox" "$hub/.claude/state/skill-link-health-test-box.json"

# ── T9: report mode makes no filesystem changes to links ────────────────────
hub="$(new_sandbox meta)" || exit 1
r="$(add_repo "$hub" repo-missing nested)"
run_report "$hub" >/dev/null
if [[ ! -e "$r/.claude/skills/meta" ]]; then pass "test_report_mode_makes_no_changes"
else fail "test_report_mode_makes_no_changes (report created a link)"; fi

# ── T10: allowlist suppresses a MISSING repo from unexpected_missing_repos ───
hub="$(new_sandbox meta)" || exit 1
add_repo "$hub" repo-allowed nested >/dev/null
json="$(WORKSPACE_HUB="$hub" EQ_MACHINE="test-box" EQ_SKILL_LINK_ALLOWLIST="repo-allowed" \
        bash "$RESYNC" >/dev/null 2>&1; cat "$hub/.claude/state/skill-link-health-test-box.json")"
assert_eq "test_allowlist_suppresses_missing" "$(jget "$json" unexpected_missing_repos)" "[]"
# Without the allowlist the same repo IS unexpected.
json2="$(run_report "$hub")"
assert_contains "test_unexpected_missing_without_allowlist" "$json2" "repo-allowed"

# ── T11: --apply repairs MISSING + DANGLING (needs propagate copied into sandbox) ──
hub="$(new_sandbox meta)" || exit 1
cp "$PROPAGATE_SRC" "$hub/scripts/propagate-ecosystem.sh"
r1="$(add_repo "$hub" repo-missing nested)"
r2="$(add_repo "$hub" repo-dangling nested)"; link_dangling "$hub" "$r2" meta
WORKSPACE_HUB="$hub" EQ_MACHINE="test-box" EQ_SKILL_LINK_ALLOWLIST="" \
  bash "$RESYNC" --apply >/dev/null 2>&1
json="$(cat "$hub/.claude/state/skill-link-health-test-box.json")"
assert_eq "test_apply_repairs_missing_and_dangling" "$(jget "$json" repairable)" "0"
if [[ -L "$r1/.claude/skills/meta" ]]; then pass "test_apply_created_symlink"
else fail "test_apply_created_symlink (no symlink at repo-missing/meta)"; fi

# ── T12: --apply never clobbers a MODIFIED-REAL-DIR ─────────────────────────
hub="$(new_sandbox meta)" || exit 1
cp "$PROPAGATE_SRC" "$hub/scripts/propagate-ecosystem.sh"
add_repo "$hub" repo-missing nested >/dev/null   # gives a repairable cell so apply runs
r="$(add_repo "$hub" repo-mod nested)"; make_modified "$hub" "$r" meta
WORKSPACE_HUB="$hub" EQ_MACHINE="test-box" EQ_SKILL_LINK_ALLOWLIST="" \
  bash "$RESYNC" --apply >/dev/null 2>&1
if [[ -d "$r/.claude/skills/meta" && ! -L "$r/.claude/skills/meta" ]] \
   && grep -q "LOCALLY EDITED" "$r/.claude/skills/meta/SKILL.md"; then
  pass "test_apply_skips_modified_real_dir"
else fail "test_apply_skips_modified_real_dir (modified dir was altered)"; fi

# ── T13: guard blocks --apply when propagate is unavailable ─────────────────
hub="$(new_sandbox meta)" || exit 1   # no propagate copied in
add_repo "$hub" repo-missing nested >/dev/null
out="$(WORKSPACE_HUB="$hub" EQ_MACHINE="test-box" EQ_SKILL_LINK_ALLOWLIST="" \
       bash "$RESYNC" --apply 2>&1)"
rc=$?
assert_contains "test_apply_guard_blocks" "$out" "guard blocked"
assert_eq "test_apply_guard_exit_zero" "$rc" "0"
if [[ ! -e "$hub/repo-missing/.claude/skills/meta" ]]; then pass "test_apply_guard_no_changes"
else fail "test_apply_guard_no_changes (link created despite guard)"; fi

# ── T14: --apply --dry-run is a no-op ───────────────────────────────────────
hub="$(new_sandbox meta)" || exit 1
cp "$PROPAGATE_SRC" "$hub/scripts/propagate-ecosystem.sh"
r="$(add_repo "$hub" repo-missing nested)"
out="$(WORKSPACE_HUB="$hub" EQ_MACHINE="test-box" EQ_SKILL_LINK_ALLOWLIST="" \
       bash "$RESYNC" --apply --dry-run 2>&1)"
assert_contains "test_dry_run_under_apply_message" "$out" "dry-run"
if [[ ! -e "$r/.claude/skills/meta" ]]; then pass "test_dry_run_under_apply_is_noop"
else fail "test_dry_run_under_apply_is_noop (dry-run created a link)"; fi

# ── T15: fail-closed on an unrecognized Windows host (no silent default label) ──
hub="$(new_sandbox meta)" || exit 1
out="$(WORKSPACE_HUB="$hub" EQ_OS_OVERRIDE="windows" EQ_HOST_OVERRIDE="some-unknown-box" \
       bash "$RESYNC" 2>&1)"
rc=$?
assert_eq "test_machine_label_fail_closed_windows_rc" "$rc" "1"
assert_contains "test_machine_label_fail_closed_windows_msg" "$out" "unknown Windows host"

# ── T16: --machine override + EQ_MACHINE drive the state filename ────────────
hub="$(new_sandbox meta)" || exit 1; add_repo "$hub" repo-x nested >/dev/null
WORKSPACE_HUB="$hub" bash "$RESYNC" --machine custom-label >/dev/null 2>&1
assert_file "test_machine_arg_override" "$hub/.claude/state/skill-link-health-custom-label.json"

# ── T17: WORKTREE excluded (.git file → /worktrees/), SUBMODULE + clone KEPT ──
# The worktree-skip must drop only worktrees, never genuine submodules (whose .git is ALSO a file).
hub="$(new_sandbox meta)" || exit 1
add_repo "$hub" real-clone nested >/dev/null                                # no .git ⇒ a real target
wt="$hub/wt-checkout"; mkdir -p "$wt/.claude/skills"
printf 'gitdir: /somewhere/.git/worktrees/wt-checkout\n' > "$wt/.git"        # worktree ⇒ EXCLUDED
sm="$hub/a-submodule"; mkdir -p "$sm/.claude/skills"
printf 'gitdir: ../.git/modules/a-submodule\n' > "$sm/.git"                  # submodule ⇒ KEPT
json="$(run_report "$hub")"
assert_eq "test_worktree_excluded_submodule_kept" "$(jget "$json" repos_total)" "2"
fi
snapshot_adapter() {
  local path="$1"
  if command -v cygpath >/dev/null 2>&1; then path="$(cygpath -m "$path")" || return 1; fi
  uv run --no-project --quiet python -B - "$path" <<'PY'
import json, os, stat, sys
try:
    info = os.lstat(sys.argv[1])
except FileNotFoundError:
    print('{"state":"absent"}')
else:
    attributes = getattr(info, "st_file_attributes", 0)
    target = os.readlink(sys.argv[1]) if stat.S_ISLNK(info.st_mode) or attributes & 0x400 else None
    print(json.dumps([info.st_dev, info.st_ino, info.st_mode, attributes, target]))
PY
}
if [[ "${CODEX_ONLY_ONLY:-0}" != 1 ]]; then
for variant in absent existing; do
  hub="$(new_sandbox meta)" || exit 1
  cp "$PROPAGATE_SRC" "$hub/scripts/propagate-ecosystem.sh"
  r="$(add_repo "$hub" native-owner nested)"
  mkdir -p "$r/.agents/skills" "$r/.codex" "$r/.gemini"
  printf 'native payload' > "$r/.agents/skills/sentinel"
  # Preserve an existing foreign Gemini directory; native guard must not alter it.
  mkdir -p "$r/.gemini/skills"
  printf 'foreign payload' > "$r/.gemini/skills/sentinel"
  [[ "$variant" == existing ]] && printf 'legacy pointer' > "$r/.codex/skills"
  out="$(bash "$hub/scripts/propagate-ecosystem.sh" --skills-only --only native-owner 2>&1)"
  assert_contains "native_${variant}_disposition" "$out" "native skills preserved"
  assert_eq "native_${variant}_payload" "$(cat "$r/.agents/skills/sentinel")" "native payload"
  assert_eq "native_${variant}_gemini" "$(cat "$r/.gemini/skills/sentinel")" "foreign payload"
  if [[ "$variant" == absent ]]; then
    [[ ! -e "$r/.codex/skills" && ! -L "$r/.codex/skills" ]] && pass native_absent || fail native_absent
  else
    assert_eq native_existing "$(cat "$r/.codex/skills")" "legacy pointer"
  fi
done
for reply in 'native:3' 'absent:2' 'garbage:0' 'missing:0' 'runner:127' 'file:2'; do
  hub="$(new_sandbox meta)" || exit 1
  cp "$PROPAGATE_SRC" "$hub/scripts/propagate-ecosystem.sh"
  r="$(add_repo "$hub" blocked-owner nested)"
  mkdir -p "$r/.codex" "$r/.gemini/skills"
  printf 'preserve' > "$r/.codex/skills"
  if [[ "$reply" == file:* ]]; then
    printf 'not a directory' > "$r/.agents"
  elif [[ "$reply" == runner:* ]]; then
    mkdir -p "$hub/bins"
    printf '#!/usr/bin/env bash\nexit 127\n' > "$hub/bins/uv"
    chmod +x "$hub/bins/uv"
  elif [[ "$reply" == missing:* ]]; then
    rm -- "$hub/scripts/skills/native_skill_root.py"
  else
    printf "print('%s')\nraise SystemExit(%s)\n" "${reply%:*}" "${reply#*:}" > "$hub/scripts/skills/native_skill_root.py"
  fi
  for mode in default codex_only; do
    args=(--skills-only --only blocked-owner)
    [[ "$mode" == codex_only ]] && args=(--codex-only --only blocked-owner)
    out="$(PATH="$hub/bins:$PATH" bash "$hub/scripts/propagate-ecosystem.sh" "${args[@]}" 2>&1)"; result=$?
    assert_contains "blocked_${reply}_${mode}_disposition" "$out" "Codex classification blocked"
    [[ "$result" != 0 ]] && pass "blocked_${reply}_${mode}_exit" || fail "blocked_${reply}_${mode}_exit"
  done
  assert_eq "blocked_${reply}_preserved" "$(cat "$r/.codex/skills")" "preserve"
done
hub="$(new_sandbox meta)" || exit 1
cp "$PROPAGATE_SRC" "$hub/scripts/propagate-ecosystem.sh"
r="$(add_repo "$hub" indirect-owner nested)"
mkdir -p "$r/.agents/skills"
out="$(WORKSPACE_HUB="$hub" EQ_MACHINE=test-box EQ_SKILL_LINK_ALLOWLIST="" bash "$RESYNC" --apply 2>&1)"
assert_contains indirect_native_disposition "$out" "native skills preserved"
[[ ! -e "$r/.codex/skills" && ! -L "$r/.codex/skills" ]] && pass indirect_native_absent || fail indirect_native_absent
gemini_before="$(snapshot_adapter "$r/.gemini/skills")" || { fail dry_run_gemini_snapshot_before; exit 1; }
out="$(bash "$hub/scripts/propagate-ecosystem.sh" --skills-only --dry-run 2>&1)"
assert_contains dry_run_native_disposition "$out" "native skills preserved"
gemini_after="$(snapshot_adapter "$r/.gemini/skills")" || { fail dry_run_gemini_snapshot_after; exit 1; }
assert_eq dry_run_gemini_identity_type_target_unchanged "$gemini_after" "$gemini_before"
fi
snapshot_fixture() {
  local root="$1" entry
  ( cd "$root" || exit 1
    declare -F snapshot_adapter >/dev/null || { echo 'snapshot_adapter undefined' >&2; exit 1; }
    while IFS= read -r -d '' entry; do
      if [[ -L "$entry" ]]; then printf 'L %s %s\n' "$entry" "$(readlink "$entry")"
      elif [[ -f "$entry" ]]; then printf 'F %s ' "$entry"; sha256sum "$entry" | cut -d' ' -f1
      else printf 'D %s\n' "$entry"; fi
    done < <(find . -path ./.git -prune -o -print0 | sort -z)
    local adapter; adapter="$(snapshot_adapter "$root/.gemini/skills")" || exit 1
    printf 'A .gemini/skills %s\n' "$adapter"
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then git status --porcelain=v1 --untracked-files=all; fi
  )
}
make_stale_gemini_link() {
  local root="$1" target link
  target="$root/.gemini/stale-target"; link="$root/.gemini/skills"
  mkdir -p "$target"
  if command -v cygpath >/dev/null 2>&1; then
    MSYS2_ARG_CONV_EXCL='*' cmd.exe /c mklink /J \
      "$(cygpath -w "$link")" "$(cygpath -w "$target")" >/dev/null
  else ln -s stale-target "$link"; fi
}
declare -F snapshot_adapter >/dev/null && pass codex_only_snapshot_helper_defined \
  || { fail codex_only_snapshot_helper_defined; exit 1; }
for dry in ordinary dry_run; do
  original="$(new_sandbox meta)" || exit 1; moved="$TEST_PARENT/codex only $dry"
  hub="$original"
  cp "$PROPAGATE_SRC" "$hub/scripts/propagate-ecosystem.sh"; rm -rf "$hub/.claude/skills/_internal"
  r="$(add_repo "$hub" selected-owner nested)"; other="$(add_repo "$hub" other-owner nested)"
  mkdir -p "$r/.agents/skills" "$r/.codex" "$r/.gemini" "$other/.agents/skills"
  for n in one two three four five six; do printf '%s' "$n" > "$r/.agents/skills/$n"; done
  printf parked > "$r/.codex/skills"; make_stale_gemini_link "$r"
  printf '{"preserve":true}\n' > "$r/.claude/settings.json"; printf sibling > "$other/.agents/skills/sentinel"
  mv "$(dirname "$original")" "$moved"; hub="$moved/wshub"
  r="$hub/selected-owner"; other="$hub/other-owner"
  git -C "$r" init -q; git -C "$r" add .
  before="$(snapshot_fixture "$r")" || { fail "codex_only_${dry}_selected_before"; exit 1; }
  other_before="$(snapshot_fixture "$other")" || { fail "codex_only_${dry}_sibling_before"; exit 1; }
  args=(--codex-only --verbose --only selected-owner); [[ "$dry" == dry_run ]] && args+=(--dry-run)
  out="$(cd "$TEST_PARENT" && bash "$hub/scripts/propagate-ecosystem.sh" "${args[@]}" 2>&1)"; result=$?
  assert_eq "codex_only_${dry}_rc" "$result" 0
  assert_eq "codex_only_${dry}_single_event" "$(grep -c 'selected-owner native skills preserved; Codex adapter untouched' <<< "$out")" 1
  selected_after="$(snapshot_fixture "$r")" || { fail "codex_only_${dry}_selected_after"; exit 1; }
  sibling_after="$(snapshot_fixture "$other")" || { fail "codex_only_${dry}_sibling_after"; exit 1; }
  assert_eq "codex_only_${dry}_selected_unchanged" "$selected_after" "$before"
  assert_eq "codex_only_${dry}_sibling_unchanged" "$sibling_after" "$other_before"
done

expect_codex_only_failure() {
  local name="$1" hub="$2"; shift 2
  local before after out result; before="$(snapshot_fixture "$hub")" || { fail "codex_only_${name}_snapshot_before"; return; }
  out="$(bash "$hub/scripts/propagate-ecosystem.sh" "$@" 2>&1)"; result=$?
  [[ "$result" != 0 ]] && pass "codex_only_${name}_rc" || fail "codex_only_${name}_rc"
  after="$(snapshot_fixture "$hub")" || { fail "codex_only_${name}_snapshot_after"; return; }
  assert_eq "codex_only_${name}_unchanged" "$after" "$before"
}
hub="$(new_sandbox meta)" || exit 1; cp "$PROPAGATE_SRC" "$hub/scripts/propagate-ecosystem.sh"; add_repo "$hub" target nested >/dev/null
expect_codex_only_failure missing "$hub" --codex-only
expect_codex_only_failure empty "$hub" --codex-only --only
expect_codex_only_failure option_value "$hub" --codex-only --only --dry-run
expect_codex_only_failure path_value "$hub" --codex-only --only ../target
expect_codex_only_failure repeated "$hub" --codex-only --only target --only target
expect_codex_only_failure hooks_first "$hub" --hooks-only --codex-only --only target
expect_codex_only_failure hooks_last "$hub" --codex-only --only target --hooks-only
expect_codex_only_failure unmatched "$hub" --codex-only --only absent
add_repo "$hub" duplicate flat >/dev/null; add_repo "$hub" duplicate nested >/dev/null
expect_codex_only_failure duplicate "$hub" --codex-only --only duplicate

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "================================"
echo "PASS: $PASS  FAIL: $FAIL"
echo "================================"
[[ $FAIL -eq 0 ]]
