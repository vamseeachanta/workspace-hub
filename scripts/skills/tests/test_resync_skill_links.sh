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

SANDBOXES=()
cleanup() { for d in "${SANDBOXES[@]:-}"; do [[ -n "$d" && -d "$d" ]] && rm -rf "$d"; done; }
trap cleanup EXIT

# new_sandbox [template_dirs...] — echoes <sbx>/wshub. Templates default to "meta" so workflows +
# guidelines slots resolve to TEMPLATE-ABSENT (keeps single-cell classify tests isolated).
new_sandbox() {
  local sbx hub tdir
  sbx="$(mktemp -d)"; SANDBOXES+=("$sbx")
  hub="$sbx/wshub"
  mkdir -p "$hub/.claude/skills/_internal" "$hub/scripts"
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

# ── T1: classify HEALTHY ────────────────────────────────────────────────────
hub="$(new_sandbox meta)"
r="$(add_repo "$hub" repo-healthy nested)"; link_healthy "$hub" "$r" meta
json="$(run_report "$hub")"
assert_eq "test_classify_healthy" "$(jget "$json" healthy)" "1"

# ── T2: classify MISSING ────────────────────────────────────────────────────
hub="$(new_sandbox meta)"
add_repo "$hub" repo-missing flat >/dev/null
json="$(run_report "$hub")"
assert_eq "test_classify_missing" "$(jget "$json" missing)" "1"

# ── T3: classify DANGLING ───────────────────────────────────────────────────
hub="$(new_sandbox meta)"
r="$(add_repo "$hub" repo-dangling nested)"; link_dangling "$hub" "$r" meta
json="$(run_report "$hub")"
assert_eq "test_classify_dangling" "$(jget "$json" dangling)" "1"

# ── T4: classify FLATTENED ──────────────────────────────────────────────────
hub="$(new_sandbox meta)"
r="$(add_repo "$hub" repo-flattened flat)"; make_flattened "$hub" "$r" meta
json="$(run_report "$hub")"
assert_eq "test_classify_flattened" "$(jget "$json" flattened)" "1"

# ── T5: classify MODIFIED-REAL-DIR ──────────────────────────────────────────
hub="$(new_sandbox meta)"
r="$(add_repo "$hub" repo-modified nested)"; make_modified "$hub" "$r" meta
json="$(run_report "$hub")"
assert_eq "test_classify_modified_real_dir" "$(jget "$json" modified_real_dir)" "1"

# A real dir matching the template classifies HEALTHY (not MODIFIED).
hub="$(new_sandbox meta)"
r="$(add_repo "$hub" repo-realmatch nested)"; make_matching "$hub" "$r" meta
json="$(run_report "$hub")"
assert_eq "test_classify_matching_real_dir_healthy" "$(jget "$json" healthy)" "1"

# ── T6: classify TEMPLATE-ABSENT (guidelines/workflows have no _internal template) ──
hub="$(new_sandbox meta)"
r="$(add_repo "$hub" repo-ta nested)"; link_healthy "$hub" "$r" meta
json="$(run_report "$hub")"
# 1 repo x 3 shared dirs: meta=HEALTHY, workflows+guidelines=TEMPLATE-ABSENT
assert_eq "test_classify_template_absent" "$(jget "$json" template_absent)" "2"

# ── T7: state JSON shape + counts sum to repos x dirs ───────────────────────
hub="$(new_sandbox meta)"
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
hub="$(new_sandbox meta)"; add_repo "$hub" repo-x nested >/dev/null
run_report "$hub" >/dev/null
after="$(ls "$REAL_STATE"/skill-link-health-* 2>/dev/null | wc -l)"
assert_eq "test_state_written_under_sandbox_only_real_untouched" "$after" "$before"
assert_file "test_state_written_under_sandbox" "$hub/.claude/state/skill-link-health-test-box.json"

# ── T9: report mode makes no filesystem changes to links ────────────────────
hub="$(new_sandbox meta)"
r="$(add_repo "$hub" repo-missing nested)"
run_report "$hub" >/dev/null
if [[ ! -e "$r/.claude/skills/meta" ]]; then pass "test_report_mode_makes_no_changes"
else fail "test_report_mode_makes_no_changes (report created a link)"; fi

# ── T10: allowlist suppresses a MISSING repo from unexpected_missing_repos ───
hub="$(new_sandbox meta)"
add_repo "$hub" repo-allowed nested >/dev/null
json="$(WORKSPACE_HUB="$hub" EQ_MACHINE="test-box" EQ_SKILL_LINK_ALLOWLIST="repo-allowed" \
        bash "$RESYNC" >/dev/null 2>&1; cat "$hub/.claude/state/skill-link-health-test-box.json")"
assert_eq "test_allowlist_suppresses_missing" "$(jget "$json" unexpected_missing_repos)" "[]"
# Without the allowlist the same repo IS unexpected.
json2="$(run_report "$hub")"
assert_contains "test_unexpected_missing_without_allowlist" "$json2" "repo-allowed"

# ── T11: --apply repairs MISSING + DANGLING (needs propagate copied into sandbox) ──
hub="$(new_sandbox meta)"
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
hub="$(new_sandbox meta)"
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
hub="$(new_sandbox meta)"   # no propagate copied in
add_repo "$hub" repo-missing nested >/dev/null
out="$(WORKSPACE_HUB="$hub" EQ_MACHINE="test-box" EQ_SKILL_LINK_ALLOWLIST="" \
       bash "$RESYNC" --apply 2>&1)"
rc=$?
assert_contains "test_apply_guard_blocks" "$out" "guard blocked"
assert_eq "test_apply_guard_exit_zero" "$rc" "0"
if [[ ! -e "$hub/repo-missing/.claude/skills/meta" ]]; then pass "test_apply_guard_no_changes"
else fail "test_apply_guard_no_changes (link created despite guard)"; fi

# ── T14: --apply --dry-run is a no-op ───────────────────────────────────────
hub="$(new_sandbox meta)"
cp "$PROPAGATE_SRC" "$hub/scripts/propagate-ecosystem.sh"
r="$(add_repo "$hub" repo-missing nested)"
out="$(WORKSPACE_HUB="$hub" EQ_MACHINE="test-box" EQ_SKILL_LINK_ALLOWLIST="" \
       bash "$RESYNC" --apply --dry-run 2>&1)"
assert_contains "test_dry_run_under_apply_message" "$out" "dry-run"
if [[ ! -e "$r/.claude/skills/meta" ]]; then pass "test_dry_run_under_apply_is_noop"
else fail "test_dry_run_under_apply_is_noop (dry-run created a link)"; fi

# ── T15: fail-closed on an unrecognized Windows host (no silent default label) ──
hub="$(new_sandbox meta)"
out="$(WORKSPACE_HUB="$hub" EQ_OS_OVERRIDE="windows" EQ_HOST_OVERRIDE="some-unknown-box" \
       bash "$RESYNC" 2>&1)"
rc=$?
assert_eq "test_machine_label_fail_closed_windows_rc" "$rc" "1"
assert_contains "test_machine_label_fail_closed_windows_msg" "$out" "unknown Windows host"

# ── T16: --machine override + EQ_MACHINE drive the state filename ────────────
hub="$(new_sandbox meta)"; add_repo "$hub" repo-x nested >/dev/null
WORKSPACE_HUB="$hub" bash "$RESYNC" --machine custom-label >/dev/null 2>&1
assert_file "test_machine_arg_override" "$hub/.claude/state/skill-link-health-custom-label.json"

# ── T17: WORKTREE excluded (.git file → /worktrees/), SUBMODULE + clone KEPT ──
# The worktree-skip must drop only worktrees, never genuine submodules (whose .git is ALSO a file).
hub="$(new_sandbox meta)"
add_repo "$hub" real-clone nested >/dev/null                                # no .git ⇒ a real target
wt="$hub/wt-checkout"; mkdir -p "$wt/.claude/skills"
printf 'gitdir: /somewhere/.git/worktrees/wt-checkout\n' > "$wt/.git"        # worktree ⇒ EXCLUDED
sm="$hub/a-submodule"; mkdir -p "$sm/.claude/skills"
printf 'gitdir: ../.git/modules/a-submodule\n' > "$sm/.git"                  # submodule ⇒ KEPT
json="$(run_report "$hub")"
assert_eq "test_worktree_excluded_submodule_kept" "$(jget "$json" repos_total)" "2"

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "================================"
echo "PASS: $PASS  FAIL: $FAIL"
echo "================================"
[[ $FAIL -eq 0 ]]
