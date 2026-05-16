<!-- CONFLICT_MARKER_FORENSIC_FILE_OK -->
<!-- ^ self-exempt from the very hook this plan designs; per-file sentinel per Gemini r2 finding #1 + path-restricted to docs/plans/** in the script's logic. -->

# Plan for #2722: feat(enforcement): pre-commit hook to block unresolved merge-conflict markers across tier-1 repos

> **Status:** adversarial-reviewed (r3+r4 inline patches applied 2026-05-16T22:50Z & T23:05Z)
> **Complexity:** T2
> **Date:** 2026-05-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2722
> **Review artifacts:** `scripts/review/results/2026-05-16-plan-2722-claude.md` (MAJOR, 13 findings) | `scripts/review/results/2026-05-16-plan-2722-codex.md` (MAJOR, 8 findings via `env -u CLAUDECODE` workaround) | `scripts/review/results/2026-05-16-plan-2722-gemini.md` (MAJOR, 8 findings — 4 truly novel)

---

## Resource Intelligence Summary

### Existing repo code

- **`scripts/enforcement/`** (22 scripts as of 2026-05-16T21:30Z) — closest analogs:
  - `check-no-abs-paths.sh` (6468 B) — stage-aware check using `git diff --cached --name-only`; per-file regex; exits 1 on detection with `file:line` citations. **This is the structural template.**
  - `check-harness-file-size.sh` (3561 B) — also stage-aware; similar shape.
  - `check-soul-runtime-drift.sh` (3041 B, landed 2026-05-16 commit `965c124f0`) — drift-detection idiom for vendored-vs-source artifacts.
- **`scripts/enforcement/install-hooks.sh`** (10183 B, lines 30-205) — canonical idempotent hook-installer. Uses `grep -q "<sentinel>" "$PRE_COMMIT" && log "already wired" || append`. Operates on **workspace-hub only** — does NOT iterate sibling repos. Pre-existing pre-push wiring (lines 71-178) installs `enforcement-env`, `require-review-on-push`, `require-stage-prompt-drift`, `state-file size guard`, `cadence-helper sync` — same pattern applies to a new conflict-marker check.
- **`scripts/agents/install-soul-runtime.sh`** (87 lines, commit `1c5c11eb7`) — symlink installer for `~/.{hermes,codex}` runtime artifacts. **Does NOT iterate sibling repos** either. Issue body assumed this script handles sibling-repo iteration; correcting: cross-repo install is NEW work, not an extension of existing per-machine symlink logic.
- **Existing conflict-marker check anywhere in scripts/**: NONE (verified via `grep -rln "conflict.marker\|<<<<<<<" scripts/` returns only `scripts/_archive/phase1-setup.sh` — archived). Gap confirmed.
- **Current `.git/hooks/pre-commit` in workspace-hub** (2437 B, lines 1-54): chains encoding → harness-file-size → skill-content → JS-lockfile → plan-approval-gate, then `exit 0` at **line 49**. State-file size guard appended after `exit 0` is DEAD CODE (install-hooks.sh `cat >>` placed it there in error). New conflict-marker check must be wired **before line 49** to actually execute.

### Standards

Engineering-standards: not applicable. Per Codex r2 finding #7, the `cat:harness` label triggers the docs/plans/README.md Harness/Infrastructure retrieval bundle — addressed below.

**Harness/Infrastructure retrieval** (per `docs/plans/README.md` bundle for `cat:harness`):

- **`docs/standards/CONTROL_PLANE_CONTRACT.md`** — read 2026-05-16T22:55Z. Defines durable-vs-transient boundary. The new `scripts/agents/tier1-repos.sh` manifest is a durable control-plane artifact; the new vendored copies in sibling repos are durable per-repo artifacts; the new `.git/hooks/pre-commit` wiring is per-machine transient state (NOT tracked, must be installed via bootstrap).
- **`docs/standards/AI_REVIEW_ROUTING_POLICY.md`** — read 2026-05-16T22:55Z. Three-provider review default policy is the tracked source (per Codex r2 finding #8). Replaces the `feedback_always_adversarial_review_scale_depth` memory citation in §Acceptance Criteria.
- **`config/agents/` settings** — no provider-specific config touched by this plan; cross-provider compatibility verified (hook is bash, no provider-CLI dependency).
- **`.claude/rules/patterns.md`** — Level-3 enforcement gradient (pre-commit hook) is the strongest tier; appropriate for "must-never-miss" defects.
- **`.claude/rules/coding-style.md`** — Path Handling rule: scripts must use `${REPO_ROOT}` / `$(git rev-parse --show-toplevel)`, not hardcoded absolute paths. Applied to the installer's path resolution (single `$WS_ROOT/../$repo` form per Claude r1 finding #5).

### LLM Wiki pages consulted

Not applicable — no domain-knowledge dependency.

### Documents consulted

- **#2411 7-repo audit** ([issuecomment-4467824635](https://github.com/vamseeachanta/workspace-hub/issues/2411#issuecomment-4467824635)) — surfaced the 3/7 broken state on 2026-05-16. Source of acceptance evidence.
- **Three OPEN fix PRs** (verified 2026-05-16T22:50Z via `gh pr view --json state` — all return `OPEN`, NOT merged; r3 correction per Claude finding #1):
  - [worldenergydata#415](https://github.com/vamseeachanta/worldenergydata/pull/415) — `.claude/docs/agents.md` (6 markers); test `tests/test_agent_doc_clean.py`. Mergeability: BLOCKED on baseline-red CI (5/5 main runs red since 2026-05-15, PR-unrelated).
  - [aceengineer-website#15](https://github.com/vamseeachanta/aceengineer-website/pull/15) — 2 blog files (120 markers); test `tests/python/test_content_clean.py`. Mergeability: CLEAN.
  - [assethold#51](https://github.com/vamseeachanta/assethold/pull/51) — `.claude/settings.json` (3 markers); test `tests/test_settings_clean.py`. Mergeability: UNSTABLE on baseline-red `Financial Data Integration` + `Quality Gate` (5/5 main runs red since 2026-05-09, PR-unrelated).
  - Each test is per-repo and per-file; none would have caught markers in different files (mitigated post-hoc via `feedback_regression_test_broader_than_issue_scope`).
  - **Implication for §Acceptance criterion 12** (sibling-repo install validation): the three sibling-repo `main` branches likely still contain the original markers until each PR merges. Installation order matters — install hook on a sibling repo AFTER the fix PR merges, otherwise the hook would block legitimate post-merge work that re-touches the historically-marker-containing files. Captured below.
- **`.claude/rules/patterns.md`** — Level-3 enforcement gradient (pre-commit hook) is the strongest tier; appropriate for "must-never-miss" defects.
- **`feedback_origin_committed_with_unresolved_markers`** memory — documents the exact failure mode (parallel sessions land half-resolved files, `git pull` double-nests markers).
- **`feedback_regression_test_broader_than_issue_scope`** memory — broader-scope tests catch sibling regressions (caught HTML_REPORTING_STANDARDS.md while fixing AI_AGENT_ORCHESTRATION.md).

### Gaps identified

- **No detection layer at commit time** — markers can land on `main` if a parallel session, `git pull` double-nest, or human-resolved file slips through.
- **No cross-repo install mechanism** — `install-hooks.sh` is workspace-hub-only; sibling repos each carry their own `.git/hooks/pre-commit` independently.
- **No canonical hook content distribution model** — choose between symlink-to-workspace-hub (requires workspace-hub on every machine), vendored copy with drift check (cadence-helper pattern), or per-repo independent script (drift inevitable).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-16T22:05Z via `gh issue view`):
- `#2722` — OPEN, labels `status:needs-plan,priority:medium,cat:harness,domain:workflow` — title "feat(enforcement): pre-commit hook to block unresolved merge-conflict markers across tier-1 repos"
- `#2411` — OPEN, audit comment cited
- `#2719` — OPEN, `status:plan-approved` (companion install pattern reference)

**File existence** (`ls -la` 2026-05-16T22:05Z):
- EXISTS: `scripts/enforcement/check-no-abs-paths.sh` (structural template)
- EXISTS: `scripts/enforcement/install-hooks.sh` (installer entry point)
- EXISTS: `scripts/memory/bootstrap-machine.sh` (cross-machine integration point; §2.5 region at lines 106-118)
- EXISTS: `.git/hooks/pre-commit` (locally installed; needs wiring)
- MISSING (this plan creates): `scripts/enforcement/check-no-conflict-markers.sh`
- MISSING (this plan creates): `scripts/agents/install-pre-commit-hook-cross-repo.sh`
- MISSING (this plan creates): `tests/enforcement/test_check_no_conflict_markers.py`

**Line excerpts** (`sed -n N,Mp`):

`.git/hooks/pre-commit:1-13` (proves stage-aware idiom + dead-code-after-exit-0 risk):
```
#!/usr/bin/env bash
# Pre-commit: encoding check only
REPO_ROOT="$(git rev-parse --show-toplevel)"
export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"
...
STAGED_FILES="$(git diff --cached --name-only --diff-filter=ACMR || true)"
[[ -z "$STAGED_FILES" ]] && exit 0
```

`scripts/enforcement/install-hooks.sh:46-66` (proves idempotent grep-q-then-append idiom):
```
PRE_COMMIT="${REPO_ROOT}/.git/hooks/pre-commit"
if [[ -f "$PRE_COMMIT" ]]; then
  if grep -q "enforcement-env" "$PRE_COMMIT" 2>/dev/null; then
    log "OK: enforcement-env already wired into pre-commit"
  else
    ...sed -i insert after PATH export...
```

`scripts/memory/bootstrap-machine.sh:106-118` (proves §2.6 integration point exists):
```
# 2.5. Install SOUL runtime symlinks (per #2719)
...
INSTALL_SOUL="${REPO_ROOT}/scripts/agents/install-soul-runtime.sh"
if [[ -x "${INSTALL_SOUL}" ]]; then
    ...
fi
```

**Gap proofs**:
- `grep -rln "<<<<<<<" scripts/enforcement/ scripts/memory/ scripts/agents/` → returns only test fixtures (in `scripts/enforcement/tests/test_require_review_on_push.sh` as `# ===` banners, NOT conflict markers). No detection script exists.
- `grep -c "<<<<<<<\|=======\|>>>>>>>" .git/hooks/pre-commit` → 0. Current hook does not check markers.

**Reproduction proofs**:

This is a **forward-looking enforcement plan**, not a bug fix. The "failure" being prevented is the recurrence of the 3/7-broken state documented in #2411. Reproduction = verifying the gap (no current check exists) AND that the historical 3 occurrences match what the hook would have blocked:

```
$ grep -rln "^<<<<<<< " scripts/enforcement/ scripts/memory/ scripts/agents/ 2>/dev/null
(empty result — no anchored conflict markers in enforcement scripts)

$ git -C ~/workspace-hub log --oneline --all -- '.claude/docs/agents.md' 'content/blog/AI_AGENT_ORCHESTRATION.md' '.claude/settings.json' | head -3
(sibling repos — not in this tree; commits proven via the 3 PR landings)
```

- Reproduced at: 2026-05-16T22:05Z
- Failure mode observed matches issue claim: **YES** (gap exists; 3 historical occurrences cited; no detection layer; broader-scope TDD tests added per-repo do not generalize).
- Marked **N/A — forward-looking enforcement** for runtime reproduction; the audit + 3 landed fix PRs serve as the empirical evidence.

<!-- Source count: issue body (1) + #2411 audit (2) + 3 landed PRs (3) + install-hooks.sh source (4) + .claude/rules/patterns.md (5) + 2 feedback memories (6, 7). Far above ≥3 minimum. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-16-issue-2722-pre-commit-conflict-marker-hook.md` |
| Detection script | `scripts/enforcement/check-no-conflict-markers.sh` |
| Cross-repo installer | `scripts/agents/install-pre-commit-hook-cross-repo.sh` |
| Drift check (vendored-copy parity) | `scripts/enforcement/check-pre-commit-hook-drift.sh` |
| Tests | `tests/enforcement/test_check_no_conflict_markers.py` |
| Bootstrap integration | `scripts/memory/bootstrap-machine.sh` (new §2.6 block, ~10 lines) |
| Install-hooks integration | `scripts/enforcement/install-hooks.sh` (new wiring block, ~12 lines) |
| Plan review — Claude | `scripts/review/results/2026-05-16-plan-2722-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-16-plan-2722-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-16-plan-2722-gemini.md` |
| Plans index update | `docs/plans/README.md` (new row) |

---

## Deliverable

A workspace-hub-anchored pre-commit hook (`scripts/enforcement/check-no-conflict-markers.sh`) that rejects commits staging files containing unresolved git merge-conflict markers, plus a cross-repo installer that propagates a vendored copy + drift check into all 7 tier-1 repos' `.git/hooks/pre-commit`, with bootstrap-machine integration so new machines pick it up automatically.

---

## Pseudocode

### Detection: `scripts/enforcement/check-no-conflict-markers.sh`

```
function check_no_conflict_markers():
    REPO_ROOT = $(git rev-parse --show-toplevel)
    # Per Gemini r2 #2/#6: use `git rev-parse --git-dir` not `.git/...` —
    # in worktrees `.git` is a file pointing to the actual git dir, not a directory.
    GIT_DIR = $(git rev-parse --git-dir)

    # NOTE: NO active-merge skip. Per Codex r2 finding #1, skipping during
    # active merge/rebase/cherry-pick INVERTS the threat model — the resolution
    # commit is *exactly* the moment the user might leave half-resolved markers.
    # The hook is stage-aware: if a merge is in progress AND the user has
    # cleanly staged the resolution (no markers in staged content), it passes;
    # if the staged content still has markers, it fails — which is the desired
    # behavior. Active-merge state is not interrogated.

    # Stage-aware: only check files added/modified/renamed in THIS commit
    # Per Gemini r2 #8: use NUL-delimited form to handle filenames with spaces
    while IFS= read -r -d '' file; do
        # ...iteration body below...
    done < <(git diff --cached --name-only --diff-filter=ACMR -z)

    # If no staged files: exit 0 (handled by empty-loop fall-through)

    violations = []
    # (inside the iteration body)
    for file in STAGED (NUL-delimited iteration above):
        # Skip deletions (no staged content to scan)
        # `git cat-file -e :"$file"` confirms the staged blob exists
        if not git cat-file -e ":$file" 2>/dev/null: continue

        # Read staged blob ONCE — single source of truth for both
        # marker scan AND sentinel check (per Codex r2 finding #2 +
        # Claude r1 finding #4 — TOCTOU between working-tree sentinel
        # and staged-blob scan was a bypass vector)
        staged_content = $(git show ":$file")

        # ── Path-restricted per-file sentinel (Gemini r2 #1 compromise) ───
        # Allow per-file sentinel ONLY for files in paths where marker syntax
        # is legitimately discussed in prose/code-block form:
        #   docs/plans/**, docs/governance/**, docs/standards/**,
        #   scripts/review/results/**, scripts/review/prompts/**
        # If the file is in one of those paths AND its staged_content
        # contains `<!-- CONFLICT_MARKER_FORENSIC_FILE_OK -->` (markdown HTML
        # comment, hidden when rendered): skip entire file.
        # Rationale: bounds Claude r1 #3 blanket-backdoor concern by
        # restricting per-file exempt to forensic-discussion paths only;
        # hostile commit can't add this sentinel to arbitrary source files.
        if "$file" matches path-prefix-set AND
           grep -q "<!-- CONFLICT_MARKER_FORENSIC_FILE_OK -->" <<< "$staged_content":
            continue  # this file legitimately discusses marker syntax

        # ── Per-line forensic-allowlist sentinel (default) ────────────────
        # Per Claude r1 #3, end-of-line `# CONFLICT_MARKER_FORENSIC_OK` exempts
        # only that line, not the whole file. Matches `scripts/enforcement/
        # check-no-abs-paths.sh:111` prior art.
        # Acceptable end-of-line tags (matched against staged content):
        #   # CONFLICT_MARKER_FORENSIC_OK
        #   // CONFLICT_MARKER_FORENSIC_OK
        #   <!-- CONFLICT_MARKER_FORENSIC_OK -->

        # ── Co-occurrence requirement (Gemini r2 #4) ──────────────────────
        # Markdown 7-level nested blockquote `>>>>>>> ` at column 0 is valid
        # syntax and triggers `^>>>>>>>(\s|$)`. To defeat this false positive,
        # require BOTH `^<<<<<<<` AND `^>>>>>>>` in the same staged blob;
        # markdown blockquotes never co-occur with `<<<<<<<`. Conflict markers
        # always come in {<<<<<<<, =======, >>>>>>>} groups.
        has_lt = grep -q "^<<<<<<<(\s|$)" <<< "$staged_content"
        has_gt = grep -q "^>>>>>>>(\s|$)" <<< "$staged_content"
        if NOT (has_lt AND has_gt): continue  # no conflict-group → no flag

        # Per Claude r1 #8, regex weakened from trailing-space to `(\s|$)`
        # to catch diff3/recursive-merge-driver outputs without trailing space.
        for line in numbered-lines-of staged_content:
            if line matches "^<<<<<<<(\\s|$)" OR line matches "^>>>>>>>(\\s|$)":
                # Per-line sentinel exemption (same staged source!)
                if line ends-with "CONFLICT_MARKER_FORENSIC_OK"
                   OR line ends-with "CONFLICT_MARKER_FORENSIC_OK -->": continue
                violations += "$file:<lineno>:<line-content>"

    if violations is empty: exit 0
    else:
        echo "ERROR: Unresolved merge-conflict markers detected in staged content:"
        for v in violations: echo "  $v"
        echo ""
        echo "To resolve: edit each file, remove the <<<<<<<, =======, >>>>>>> markers,"
        echo "keep the intended content, re-stage, and retry the commit."
        echo "For legitimate forensic documentation lines, append the"
        echo "  # CONFLICT_MARKER_FORENSIC_OK"
        echo "end-of-line tag (or // or <!-- --> variant per file syntax)."
        exit 1
```

**Note on `=======` (the third marker):** intentionally NOT in the trigger set. It appears legitimately as markdown setext H1 underline, shell comment banners (`# ===== section =====`), and ASCII art. Anchored `^<<<<<<< ` / `^>>>>>>> ` are the high-precision signal; if a resolution leaves a stray `=======` alone (no enclosing anchors), the cost is one extra line of noise, not a working-tree corruption. This is documented in §Risks.

### Cross-repo installer: `scripts/agents/install-pre-commit-hook-cross-repo.sh`

```
function install_cross_repo():
    WS_ROOT = $(git rev-parse --show-toplevel)  # workspace-hub
    CANONICAL = "$WS_ROOT/scripts/enforcement/check-no-conflict-markers.sh"

    # Tier-1 repo discovery: tracked manifest. Per Codex r2 finding #4,
    # YAML requires yq (not guaranteed on bootstrap machines). Use shell-
    # source format instead — a plain bash file declaring an array, no
    # parser dependency. The cost is a slight loss of structured-data
    # ergonomics; the gain is bootstrap-time portability.
    #
    # File: scripts/agents/tier1-repos.sh
    # Content example:
    #   TIER1_REPOS=(
    #     "workspace-hub"
    #     "digitalmodel"
    #     "assetutilities"
    #     "worldenergydata"
    #     "assethold"
    #     "aceengineer-website"
    #     "llm-wiki"
    #   )
    source "$WS_ROOT/scripts/agents/tier1-repos.sh"

    for repo in "${TIER1_REPOS[@]}":
        # Path resolution: SINGLE deterministic order (per Claude r1
        # finding #5). On this user's actual layout, siblings live at
        # `/mnt/local-analysis/<repo>` (verified 2026-05-16); ~ is sparse
        # overlay per CLAUDE.md and unsafe as a write target.
        REPO_PATH = "$WS_ROOT/../$repo"  # canonical: sibling of workspace-hub
        if not -d "$REPO_PATH/.git": skip "$repo (not present at canonical path)"; continue

        # Per Codex r2 finding #6: sibling-repo install must persist beyond
        # the local working tree. The vendored copy + hook wiring are
        # tracked artifacts; this function stages them but does NOT commit
        # or push (forbidden — sibling repos require their own plan-approval
        # gate). Instead, leave a clean staging set and prompt the operator
        # to run `cd $REPO_PATH && git diff --cached` for inspection, then
        # commit via that repo's normal workflow.
        # Refuses to overwrite a dirty working tree in the sibling repo.
        if (cd "$REPO_PATH" && git diff --quiet -- scripts/enforcement/ .git/hooks/) returns false:
            echo "WARN: $repo has uncommitted changes in scripts/enforcement/ or .git/hooks/"
            echo "       skipping; resolve dirty state and re-run installer"
            continue

        # Vendored copy (NOT symlink — sibling repos may live on machines without WS)
        VENDORED = "$REPO_PATH/scripts/enforcement/check-no-conflict-markers.sh"
        mkdir -p "$REPO_PATH/scripts/enforcement"
        cp "$CANONICAL" "$VENDORED"
        chmod +x "$VENDORED"

        # Wire into pre-commit. Per Codex r2 finding #3, the stub if
        # created MUST define REPO_ROOT (otherwise the inserted snippet
        # is a no-op). Per Gemini r2 finding #6, locate the hooks dir via
        # `git rev-parse --git-common-dir` rather than the literal
        # `.git/hooks/` — in worktrees, `.git` is a file pointing elsewhere.
        HOOKS_DIR = $(cd "$REPO_PATH" && git rev-parse --git-common-dir)/hooks
        PRE_COMMIT = "$HOOKS_DIR/pre-commit"
        if not -f "$PRE_COMMIT":
            # Create minimal stub with REPO_ROOT defined
            write "$PRE_COMMIT":
                #!/usr/bin/env bash
                REPO_ROOT="$(git rev-parse --show-toplevel)"
                exit 0
            chmod +x "$PRE_COMMIT"

        if not grep -q "check-no-conflict-markers" "$PRE_COMMIT":
            # Insert wiring block BEFORE the final `exit 0`. The block uses
            # `${REPO_ROOT:?}` to fail loudly if the prologue forgot to set it.
            # Linux-only sed -i form per Claude r1 finding #6 — gated below.
            if [[ "$(uname -s)" == "Linux" ]]:
                sed -i '/^exit 0$/i\
\
# ── Conflict-marker check (workspace-hub#2722) ──\
CHECK="${REPO_ROOT:?REPO_ROOT must be set in pre-commit prologue}/scripts/enforcement/check-no-conflict-markers.sh"\
if [[ -f "$CHECK" ]]; then\
  bash "$CHECK" || exit 1\
fi' "$PRE_COMMIT"
            else:
                # macOS/Windows: fall back to python rewrite (BSD sed has
                # different -i semantics; Windows bootstrap uses Git-Bash with
                # MinGW sed which IS GNU). For macOS only, the python path is
                # safer than testing BSD-vs-GNU variant detection.
                python3 -c '...rewrite-with-marker-block...' "$PRE_COMMIT"

        echo "OK: $repo: vendored + wired (call $REPO_PATH and commit normally)"
```

### Drift check: `scripts/enforcement/check-pre-commit-hook-drift.sh`

```
# Inspired by cadence-helper sync check (scripts/sync/sync-cadence-helper.sh
# uses sha256 — verified 2026-05-16 read).
function check_drift():
    WS_ROOT = $(git rev-parse --show-toplevel)
    CANONICAL = "$WS_ROOT/scripts/enforcement/check-no-conflict-markers.sh"
    CANONICAL_SHA = sha256sum(CANONICAL)
    source "$WS_ROOT/scripts/agents/tier1-repos.sh"

    failures = 0
    for repo in "${TIER1_REPOS[@]}" excluding workspace-hub itself:
        REPO_PATH = "$WS_ROOT/../$repo"
        if not -d "$REPO_PATH/.git": continue  # not present is not a drift failure
        VENDORED = "$REPO_PATH/scripts/enforcement/check-no-conflict-markers.sh"
        # Per Codex r2 finding #5: missing-vendored-copy = unprotected repo = FAIL.
        if not -f "$VENDORED":
            echo "FAIL: $repo missing vendored copy — repo unprotected"
            failures = failures + 1
            continue
        if sha256sum("$VENDORED") != CANONICAL_SHA:
            echo "DRIFT: $repo has stale vendored copy"
            failures = failures + 1

    if failures > 0: exit 1
    echo "OK: all tier-1 vendored copies in sync"
```

### Bootstrap-machine.sh §2.6 (~10 lines)

```
# 2.6. Install conflict-marker pre-commit hook (per #2722)
INSTALL_HOOK="${REPO_ROOT}/scripts/agents/install-pre-commit-hook-cross-repo.sh"
if [[ -x "${INSTALL_HOOK}" ]]; then
    bash "${INSTALL_HOOK}"
fi
```

### Install-hooks.sh wiring (~16 lines in workspace-hub's local install)

Append within existing `Step 2: Wire enforcement-env into pre-commit` chain, before the final `exit 0`. **Linux-gated** per Claude r1 finding #6 (BSD sed `-i` differs and breaks on macOS):

```
# Wire conflict-marker check (#2722)
if grep -q "check-no-conflict-markers" "$PRE_COMMIT"; then
    log "OK: conflict-marker check already wired"
elif [[ "$(uname -s)" == "Linux" ]]; then
    sed -i '/^exit 0$/i\
# ── Conflict-marker check (#2722) ──\
if [[ -f "${REPO_ROOT}/scripts/enforcement/check-no-conflict-markers.sh" ]]; then\
  bash "${REPO_ROOT}/scripts/enforcement/check-no-conflict-markers.sh" || exit 1\
fi\
' "$PRE_COMMIT"
    log "OK: wired conflict-marker check into pre-commit"
else
    log "WARN: non-Linux platform ($(uname -s)) — skip auto-wiring; manual install required"
    log "      Add the following block to $PRE_COMMIT before the final 'exit 0':"
    log "      <wire-block-shown-here>"
fi
```

**Dead-code-state disposition** (per Claude r1 finding #13): the existing `.git/hooks/pre-commit` has a dead block at lines 51-54 (state-file size guard after `exit 0`). This plan **explicitly defers** fixing it — out of scope for #2722. Filed as follow-on note in §Risks below. Inserting BEFORE `exit 0` at line 49 sidesteps the issue.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/enforcement/check-no-conflict-markers.sh` | canonical detection script |
| Create | `scripts/agents/install-pre-commit-hook-cross-repo.sh` | propagation across 7 tier-1 repos |
| Create | `scripts/enforcement/check-pre-commit-hook-drift.sh` | drift detection |
| Create | `scripts/agents/tier1-repos.sh` | tier-1 manifest as bash-sourced array (no `yq` dep; per Codex r2 #4) |
| Create | `tests/enforcement/test_check_no_conflict_markers.py` | TDD coverage of detection script (17 cases, see below) |
| Modify | `scripts/memory/bootstrap-machine.sh` | append §2.6 block after §2.5 |
| Modify | `scripts/enforcement/install-hooks.sh` | Linux-gated wiring of conflict-marker check |
| Update | `docs/plans/README.md` | this plan row (already added in initial commit `0e62057d6`) |

---

## TDD Test List

`tests/enforcement/test_check_no_conflict_markers.py` — pytest-driven, exercises the bash script via subprocess against synthetic staged files in a `tmp_path` git fixture.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_clean_file_passes` | normal file with no markers exits 0 | staged file: simple python module | exit 0, no stdout violations |
| `test_canonical_markers_fail` | `<<<<<<< HEAD` + `=======` + `>>>>>>> branch` triggers | staged file with all 3 markers | exit 1, file:line cited |
| `test_lt_anchor_no_trailing_space_fails` | r3 weakened anchor `^<<<<<<<(\\s\|$)` catches no-trailing-space form | staged file with `<<<<<<<\n...` (no space) | exit 1 (Claude r1 #8) |
| `test_setext_heading_passes` | markdown `=======` underline does NOT trigger | staged file: `# Title\n=======\nbody` | exit 0 (no `<<<<<<<` or `>>>>>>>` co-occurs) |
| `test_shell_banner_passes` | shell-comment banner `# =======` does NOT trigger | staged file with `# ============` block | exit 0 |
| `test_stage_aware_during_merge_clean_passes` | during active merge with CLEAN staged content, hook passes (r3 inversion of original test_active_merge_skips per Codex r2 #1) | `.git/MERGE_MSG` exists, staged content has no markers | exit 0 |
| `test_stage_aware_during_merge_marker_fails` | during active merge with marker-staged content, hook FAILS (catches the bypass that Codex r2 #1 surfaced) | `.git/MERGE_MSG` exists, staged content has `<<<<<<<` | exit 1 |
| `test_per_line_sentinel_exempts_line` | end-of-line `# CONFLICT_MARKER_FORENSIC_OK` tag on the marker-bearing line exempts only that line (r3 per-line not per-file, per Claude r1 #3) | staged shell file: `<<<<<<< section # CONFLICT_MARKER_FORENSIC_OK` | exit 0 |
| `test_per_line_sentinel_no_blanket_exempt` | sentinel on one line does NOT exempt another marker line | staged file with sentinel on line A, real marker on line B | exit 1, line B cited |
| `test_sentinel_must_be_staged_not_working_tree` | sentinel only in working tree (not staged) does NOT defeat marker check (r3 TOCTOU fix per Codex r2 #2 + Claude r1 #4) | working tree has sentinel; staged blob has marker without sentinel | exit 1 |
| `test_unstaged_marker_ignored` | unstaged file with markers does NOT trigger | working-tree marker, nothing staged | exit 0 (stage-aware) |
| `test_multiple_violations_all_cited` | every match cited, not just first | 2 files each with markers | exit 1, all 4+ violations in stdout |
| `test_deleted_file_skipped` | deletion-diff-filter excludes deleted files | staged deletion of marker-containing file | exit 0 |
| `test_renamed_file_checked` | rename retains content scan | staged rename with markers in content | exit 1 |
| `test_install_idempotent` | running install-pre-commit-hook-cross-repo twice → no double-wiring | call install script twice | hook wired exactly once |
| `test_install_skips_dirty_sibling` | installer refuses to overwrite a sibling repo with uncommitted changes in scripts/enforcement/ or .git/hooks/ (Codex r2 #6 dirty-worktree handling) | sibling repo has uncommitted local diff | exit 0 with WARN, no overwrite |
| `test_install_creates_stub_with_REPO_ROOT` | installer-created stub defines REPO_ROOT in prologue (Codex r2 #3) | sibling has no pre-commit file | created stub has `REPO_ROOT="$(git rev-parse --show-toplevel)"` |
| `test_drift_detected` | modifying vendored copy → drift check exits 1 | tamper with sibling repo's vendored copy | exit 1 with sibling path cited |
| `test_drift_missing_copy_fails` | missing vendored copy → drift check exits 1 (NOT warn, per Codex r2 #5) | sibling exists but no vendored copy | exit 1 with "missing" cited |
| `test_drift_clean_passes` | unmodified copies → exit 0 | fresh install state | exit 0 |
| `test_markdown_blockquote_passes` | r4: bare `>>>>>>> text` at col 0 (markdown 7-level blockquote) does NOT trigger without `<<<<<<<` co-occurrence (Gemini r2 #4) | staged markdown with `>>>>>>> note` but no `<<<<<<<` | exit 0 |
| `test_co_occurrence_required` | r4: `<<<<<<<` alone without `>>>>>>>` does NOT trigger | staged file with `<<<<<<< x` but no `>>>>>>>` | exit 0 (debatable; documented behavior) |
| `test_filename_with_space_handled` | r4: NUL-delimited iteration handles filenames containing spaces (Gemini r2 #8) | staged file: `my file.py` with markers | exit 1, file:line cited correctly |
| `test_worktree_install_uses_git_dir` | r4: installer resolves hooks dir via `git rev-parse --git-common-dir`, not literal `.git/hooks/` (Gemini r2 #6) | sibling repo is a git worktree (`.git` is a file) | hook wired in actual git-common-dir/hooks |
| `test_per_file_sentinel_restricted_path` | r4: `<!-- CONFLICT_MARKER_FORENSIC_FILE_OK -->` in `docs/plans/x.md` exempts whole file (Gemini r2 #1) | staged plan file with sentinel + markers in fenced code | exit 0 |
| `test_per_file_sentinel_arbitrary_path_rejected` | r4: same sentinel in `src/main.py` does NOT exempt — path-restricted | staged code file with sentinel + real markers | exit 1 (still blocks) |

26 cases (was 20 in r3, +6 in r4) cover happy path + each r3/r4-revised edge case + the install/drift surface. Pytest fixtures use `tmp_path` to construct minimal git repos so the suite is hermetic.

---

## Acceptance Criteria

- [ ] `scripts/enforcement/check-no-conflict-markers.sh` exists and is executable.
- [ ] Stage-aware: only inspects `git diff --cached --name-only --diff-filter=ACMR` files, never the whole tree. NUL-delimited iteration handles filenames with spaces (Gemini r2 #8).
- [ ] Anchored regex: requires `^<<<<<<<(\s|$)` AND `^>>>>>>>(\s|$)` **both present** in same staged blob (co-occurrence requirement per Gemini r2 #4; defeats markdown 7-level blockquote false-positive). Per-line iteration only fires after co-occurrence pre-check passes.
- [ ] Bare `=======` does NOT trigger (false-positive guard for markdown setext + shell comment-banners).
- [ ] Active merge/rebase/cherry-pick is **NOT** skipped — stage-aware scan runs regardless (r3 inversion of original spec per Codex r2 #1). No `.git/MERGE_MSG`/`REBASE_HEAD`/`CHERRY_PICK_HEAD` interrogation (sidesteps Gemini r2 #2 worktree issue moot).
- [ ] Forensic whitelist (default) via **per-line** `# CONFLICT_MARKER_FORENSIC_OK` end-of-line tag (or `//` / `<!-- ... -->` variants), checked against **staged blob** only (single source of truth; defeats TOCTOU bypass per Codex r2 #2 + Claude r1 #4).
- [ ] Per-file sentinel `<!-- CONFLICT_MARKER_FORENSIC_FILE_OK -->` exempts whole file, but ONLY honored in path-restricted set: `docs/plans/`, `docs/governance/`, `docs/standards/`, `scripts/review/results/`, `scripts/review/prompts/` (per Gemini r2 #1; addresses self-blocking-plan-file defect while bounding Claude r1 #3 blanket-backdoor concern).
- [ ] No path-unrestricted self-exclude (per Claude r1 #3 — per-line is the default; per-file is path-restricted).
- [ ] Reports `file:line:<marker-line>` for every detected violation (not just first).
- [ ] Exit codes: 0 on clean / no-staged-files; 1 on detection.
- [ ] `scripts/agents/install-pre-commit-hook-cross-repo.sh` installs vendored copies into all 7 tier-1 repos (manifest-driven via `scripts/agents/tier1-repos.sh` bash-sourced array — no `yq`/`python-yaml` dependency per Codex r2 #4).
- [ ] Installer uses single deterministic path resolution: `$WS_ROOT/../$repo` (per Claude r1 #5).
- [ ] Installer is worktree-safe: resolves sibling hooks dir via `git -C "$REPO_PATH" rev-parse --git-common-dir` (per Gemini r2 #6; `.git` may be a file pointing elsewhere).
- [ ] Installer refuses to overwrite a sibling repo with uncommitted changes in `scripts/enforcement/` or hooks dir; emits WARN and skips (per Codex r2 #6).
- [ ] Created pre-commit stubs include `REPO_ROOT="$(git rev-parse --show-toplevel)"` in prologue (per Codex r2 #3 + Gemini r2 #5).
- [ ] Idempotent: running installer twice produces no duplicate wiring.
- [ ] `scripts/enforcement/check-pre-commit-hook-drift.sh` detects out-of-sync vendored copies AND treats missing vendored copies as FAIL (per Codex r2 #5).
- [ ] `bootstrap-machine.sh` §2.6 invokes installer on new-machine bootstrap.
- [ ] `install-hooks.sh` wires the check into workspace-hub's own pre-commit (before existing `exit 0` at line 49). Linux-gated `sed -i` form; macOS/non-Linux path emits manual-install instructions instead (per Claude r1 #6).
- [ ] `tests/enforcement/test_check_no_conflict_markers.py` covers all 26 cases listed above, all pass.
- [ ] No regression: `uv run python -m pytest tests/enforcement/` passes; new test count is `prior_count + 26` (delta-form, not magic-number total per Claude r1 #2).
- [ ] Sibling-repo install verification (post-merge of fix-PRs #415/#15/#51): `gh pr view 415 -R vamseeachanta/worldenergydata --json state` returns `MERGED` AND `bash scripts/enforcement/check-pre-commit-hook-drift.sh` returns 0 across the tier-1 manifest (closes Claude r1 #1 + #12 unverifiable-sibling-install gap).
- [ ] Review artifacts posted to `scripts/review/results/2026-05-16-plan-2722-{claude,codex,gemini}.md` (T2 → 3-provider default per `docs/standards/AI_REVIEW_ROUTING_POLICY.md`; **all 3 returned MAJOR, true T3 coverage achieved**).
- [ ] Closing commit references `Closes #2722`.

---

## Adversarial Review Summary

| Provider | Verdict | Findings count | Critical/blocking |
|---|---|---|---|
| Claude (r1) | **MAJOR** | 13 | 5 (findings 1, 3, 4, 5, 6) |
| Codex (r2) | **MAJOR** | 8 | 6 (findings 1, 2, 3, 4, 5, 7) |
| Gemini (r2) | **MAJOR** | 8 | 5 (findings 1, 2, 4, 6, 8) — completed AFTER initial UNAVAILABLE snapshot; full T3 coverage achieved |

**Overall result:** MAJOR consensus across all 3 providers — true T3 cross-review. **29 distinct findings, only 3 with non-trivial overlap** (Codex #2 ≈ Claude #4 ≈ Gemini #3 on staged-blob TOCTOU; Codex #3 ≈ Gemini #5 on undefined REPO_ROOT in stub). The 26+ unique findings validate the `feedback_cross_provider_review_payoff` payoff: each provider caught defects the others missed. **r3+r4 inline patches applied** per `feedback_r3_inline_loop_break_pattern` (different defects each round → patch in main, don't dispatch r3+ cycles).

**Revisions made based on review (r3+r4 inline patches, this session)**:

Critical/blocking absorbed:
- (Codex #1) Dropped active-merge/rebase/cherry-pick skip; hook now scans staged content unconditionally → catches half-resolved-resolution commits which were exactly the threat. Pseudocode rewritten; `test_active_merge_skips`/`test_active_rebase_skips`/`test_active_cherrypick_skips` replaced with `test_stage_aware_during_merge_{clean_passes,marker_fails}`.
- (Codex #2 ≈ Claude #4) Forensic-whitelist sentinel now checked against the SAME staged blob as the marker scan; no more working-tree vs staged-blob TOCTOU. Pseudocode `git show ":$file"` reads the blob once into `staged_content`.
- (Claude #1) "3 landed fix PRs" → "3 OPEN fix PRs". Each PR's actual state + mergeability annotated. §Acceptance criterion 12 explicitly tied to post-merge state to avoid blocking legitimate sibling-repo post-merge work.
- (Claude #3) Per-file self-exclude removed; per-line end-of-line `# CONFLICT_MARKER_FORENSIC_OK` sentinel adopted (matches `check-no-abs-paths.sh:111` prior art). Tests updated.
- (Claude #5) Path resolution pinned to single deterministic form: `$WS_ROOT/../$repo`. ~ overlay variant explicitly rejected as unsafe.
- (Claude #6) `install-hooks.sh` sed-i form Linux-gated; macOS path emits manual-install instructions instead of attempting BSD-incompatible syntax.
- (Codex #3) Installer-created pre-commit stub now defines `REPO_ROOT` in prologue; wiring uses `${REPO_ROOT:?}` parameter-expansion form to fail loudly if unset.
- (Codex #4) Manifest format changed from `.yaml` (requires `yq`) to `.sh` (bash-source array; no parser dep). Bootstrap-machine portability preserved.
- (Codex #5) Drift check missing-vendored-copy: warn → FAIL. Unprotected repo treated as drift failure, not informational.
- (Codex #6) Installer skips dirty siblings with WARN rather than overwriting; explicit handoff to operator for cd-and-commit.
- (Codex #7) Standards section "N/A" replaced with explicit `cat:harness` Control Plane + AI_REVIEW_ROUTING_POLICY + config/agents/ + .claude/rules/ retrieval.
- (Codex #8) `feedback_always_adversarial_review_scale_depth` citation replaced with `docs/standards/AI_REVIEW_ROUTING_POLICY.md` (tracked durable policy doc).

MINOR absorbed:
- (Claude #2) Magic-number "40+16=56" replaced with delta-form invariant `prior_count + 20` (also reflects test-count bump from 16 → 20 cases above).
- (Claude #7) "#2411 7-repo audit" wording re-cited as "#2411 audit comment ([issuecomment-4467824635])" — issue vs comment scope distinguished.
- (Claude #8) Anchor regex weakened from trailing-space-required to `^<<<<<<<(\s|$)` to catch diff3/recursive merge-driver no-space outputs.
- (Claude #9) Globstar / `docs/governance/**` ambiguity moot: the per-line sentinel pattern replaces the docs/governance-path-exemption rule entirely. No path-based filtering, no globstar concern.
- (Claude #11) `docs/plans/README.md` row format pinned (already added in initial commit `0e62057d6`; reference confirms the format).
- (Claude #12) Sibling-repo install verification command added to Acceptance (`gh pr view ... && check-drift.sh`).
- (Claude #13) Dead-code state in existing `.git/hooks/pre-commit` (lines 51-54) explicitly DEFERRED — out of scope for #2722, captured in §Risks as follow-on.

Gemini r2 findings absorbed in r4 (this session, post-r3):
- (Gemini #1, CRITICAL) Plan file itself contains `^<<<<<<<` in pseudocode and would be self-blocked by the new hook. Added `<!-- CONFLICT_MARKER_FORENSIC_FILE_OK -->` HTML comment at top of THIS plan file. Hook gains a **path-restricted per-file sentinel**: docs files in `docs/plans/`, `docs/governance/`, `docs/standards/`, `scripts/review/results/`, `scripts/review/prompts/` may carry this sentinel to exempt the entire file. Bounds Claude r1 #3 blanket-backdoor concern by path-restriction.
- (Gemini #2, CRITICAL) `.git/MERGE_MSG` / `.git/REBASE_HEAD` checks fail in git worktrees where `.git` is a *file* pointing to the real git dir. Note: moot for this plan because the r3 patch DROPPED the active-merge skip entirely (Codex #1). Worktree correctness is preserved by the drop; we no longer interrogate `.git/MERGE_MSG` at all.
- (Gemini #3, dup of Codex #2/Claude #4) Working-tree state leakage on whitelist — already absorbed in r3.
- (Gemini #4, HIGH) Markdown 7-level nested blockquote `>>>>>>>` at column 0 IS valid CommonMark syntax. My `OR` trigger (`has_lt OR has_gt`) false-positives on legitimate markdown. **Strengthened** trigger to require BOTH `<<<<<<<` AND `>>>>>>>` in same staged blob — conflict markers always come in groups; markdown blockquotes never co-occur with `<<<<<<<`. Per-line iteration only enters loop if co-occurrence pre-check passes.
- (Gemini #5, dup of Codex #3) Undefined `$REPO_ROOT` in stub — already absorbed.
- (Gemini #6, CRITICAL) Installer's `$REPO_PATH/.git/hooks/pre-commit` fails for git-worktree siblings. **Patched** to use `git -C "$REPO_PATH" rev-parse --git-common-dir`/hooks.
- (Gemini #7, pseudocode-formality) `sha256(CANONICAL)` was pseudocode shorthand; real impl uses `sha256sum`. Pseudocode clarified.
- (Gemini #8, HIGH) Bare `for file in STAGED` word-splits on filenames with spaces/newlines. **Patched** to NUL-delimited form `while IFS= read -r -d ''` reading `git diff --cached --name-only -z`.

Discounted / disagree:
- (Claude #10) "Pattern lifted from cadence-helper" — checked the actual source at `scripts/sync/sync-cadence-helper.sh` 2026-05-16T22:55Z; it DOES use `sha256sum` exactly as my plan stated. The claim was correct and verified; finding withdrawn. Wording softened from "lifted from" to "inspired by ... verified 2026-05-16 read" to remove the strong-implication phrasing while preserving the technical correctness.

---

## Risks and Open Questions

- **Risk: hook bypass via `--no-verify`.** Any `git commit --no-verify` skips the hook entirely. Mitigation: `feedback_pre_push_hook_no_verify_for_preservation` documents that commit-level `--no-verify` is banned by the Iron Law; push-level `--no-verify` is permitted for codex-branch preservation. The hook is therefore correctly placed at pre-commit (not pre-push). No additional mitigation needed.
- **Risk: vendored-copy drift.** If a sibling repo modifies its vendored copy independently, drift accumulates. Mitigation: `check-pre-commit-hook-drift.sh` (sha256-equivalence pattern verified against `scripts/sync/sync-cadence-helper.sh`); could be hooked into a daily cron or pre-push.
- **Risk: false-positive on setext-heading-only markdown.** Anchored `^<<<<<<<(\s|$)` / `^>>>>>>>(\s|$)` (after r3 weakening) requires the left/right anchors, which never appear as natural markdown/shell content. False-positive risk is negligible.
- **Risk: false-negative if user resolves a conflict but forgets one of the three markers.** A lone `=======` (no `<<<<<<<` or `>>>>>>>` anywhere) will pass. Accepted: the strongest signal is the anchor pair; the cost of one stray `=======` line is far smaller than the false-positive cost (every markdown setext heading + every shell comment-banner triggers).
- **Risk: tier-1 repo discovery drift.** Hardcoded repo list goes stale as tier-1 membership changes. Mitigation: `scripts/agents/tier1-repos.sh` as single source of truth; `#2411` audit comment is the seed for the initial manifest.
- **Risk: bootstrap-machine.sh §2.6 not idempotent.** If the installer is invoked twice (e.g., bootstrap re-run + manual run), vendored copies are re-overwritten. This is desired behavior for drift recovery; tests `test_install_idempotent` confirms no harm. Dirty-sibling-skip per Codex r2 #6 prevents the bad case (overwriting uncommitted local work).
- **Risk (follow-on, deferred):** existing workspace-hub `.git/hooks/pre-commit` has dead code at lines 51-54 (state-file size guard inserted after `exit 0` at line 49 by a prior `install-hooks.sh` `cat >>` bug). #2722 wires its check BEFORE line 49 so it executes; the dead block remains unaddressed. **Deferred** — out of scope for this issue; should be filed as a separate cleanup ticket post-merge. (Per Claude r1 #13.)
- **Risk (deferred to follow-on):** the active-merge inversion fix means the hook fires during legitimate conflict-resolution flows — desirable when staged content has markers, but may surface false-positives if the user has `[merge "ours-driver"]` or other custom drivers that emit non-standard markers. Acceptable for v1; surface real-world incidents as follow-on issues if they occur.
- **Open question: should the hook also fire pre-push?** Pre-push is the second line of defense (catches pushes from branches where pre-commit was bypassed). Out of scope for this plan — current scope is pre-commit only; pre-push augmentation could be a follow-on issue.
- **Open question: should LLM-wiki be in the tier-1 manifest?** Per `project_llm_wiki_spunout` (2026-05-05), llm-wiki is a dedicated public repo; #2411 audit included it. Confirming inclusion in tier-1 manifest pending user direction.
- **Open question: macOS path for `install-hooks.sh` auto-wiring.** Current plan is Linux-gated `sed -i`; macOS gets manual-install instructions printed. Adequate for current user base (ace-linux-1/ace-linux-2 primary); revisit if macOS bootstrap becomes a regular path. (Per Claude r1 #6.)

---

## Complexity: T2

**T2** — 3 new shell scripts (canonical check, cross-repo installer, drift check) + 1 bash-sourced manifest + 1 pytest test module (20 cases) + 2 modifications to existing infra scripts. Edge cases (stage-aware-during-merge, per-line forensic sentinel via staged-blob source, setext-heading false-positive guard, BSD-sed gating, dirty-sibling skip) add nuance but each is a single conditional. Cross-repo propagation is the most architecturally novel element but follows the verified sha256-drift idiom from `scripts/sync/sync-cadence-helper.sh`. Estimated implementation time: 90-120 min including TDD + sibling-repo install validation (revised upward from initial 60-90 estimate to absorb r3-driven test count growth 16 → 20 + dirty-sibling installer logic + Linux-gating).
