#!/usr/bin/env bash
# ABOUTME: Paths that maintenance sweeps must never delete, even when untracked (#3826).
#
# WHY THIS EXISTS. Two scheduled paths treated "untracked" as "regenerable":
# repo-housekeeping.sh ran `git clean -fd` with no exclusions, and
# return-to-main-guard.sh classified untracked as churn and `git stash -u`d it on
# a 30-minute cron. That equation is false for a small, high-value class, and it
# destroyed .planning/plan-approved/3787.md TWICE -- a file whose own body
# documents the mechanism that destroyed it.
#
# An approval marker records a USER-IN-LOOP DECISION. It is not derivable from
# the repo, no agent may re-issue one, and its loss is invisible: a missing gate
# looks exactly like work that was never approved.
#
# Note the shape of the original defect. repo-housekeeping.sh already built
# `-e` excludes from SECRET_GLOBS so git-ignored secrets survived `git clean -fdx`
# -- the denylist existed, but was applied to the LOWER-risk path while untracked
# authored work went unprotected eleven lines above. This file is that same idea,
# put on the path that needed it.
#
# The list is deliberately short. Every entry is a class authored by a person and
# reconstructable by nobody. Generated dashboards, reports, logs and state
# snapshots are NOT here and must keep being swept -- a denylist that swallows
# everything would strand sessions off main, which is the problem #3187 fixed.
#
# Bash `*` matches `/`, so each glob covers arbitrary nesting.

NEVER_CLEAN_GLOBS=(
  '.planning/plan-approved/*'   # approval-gate evidence -- the reason this exists
  '.planning/*.md'              # plans, research, retrospectives
  'docs/plans/*'                # authored plans
  'docs/session-handoffs/*'     # handoffs; often a session's only record
  'scripts/*'                   # a script is never build output
  '.claude/rules/*'             # operating rules
  '.claude/skills/*'            # skills
)

# never_clean_match <path> -> 0 if the path is protected, 1 otherwise.
never_clean_match() {
  local path="$1" glob
  for glob in "${NEVER_CLEAN_GLOBS[@]}"; do
    # shellcheck disable=SC2053  # glob match is intended, not string equality
    [[ "${path}" == ${glob} ]] && return 0
  done
  return 1
}

# never_clean_untracked <repo_root> -> prints protected UNTRACKED paths, one per
# line; returns 0 if any were found, 1 if none.
#
# NUL-delimited iteration: a path containing a space or newline must not split
# into fragments that individually miss every glob and let the file through.
never_clean_untracked() {
  local repo="$1" path found=1
  while IFS= read -r -d '' path; do
    if never_clean_match "${path}"; then printf '%s\n' "${path}"; found=0; fi
  done < <(git -C "${repo}" ls-files --others --exclude-standard -z 2>/dev/null)
  return "${found}"
}
