# Plan for #2722: feat(enforcement): pre-commit hook to block unresolved merge-conflict markers across tier-1 repos

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2722
> **Review artifacts:** `scripts/review/results/2026-05-16-plan-2722-claude.md` | `...-codex.md` | `...-gemini.md` (to be created)

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

Not applicable — enforcement infrastructure issue, no engineering standards involved.

### LLM Wiki pages consulted

Not applicable — no domain-knowledge dependency.

### Documents consulted

- **#2411 7-repo audit** ([issuecomment-4467824635](https://github.com/vamseeachanta/workspace-hub/issues/2411#issuecomment-4467824635)) — surfaced the 3/7 broken state on 2026-05-16. Source of acceptance evidence.
- **Three landed fix PRs**:
  - [worldenergydata#415](https://github.com/vamseeachanta/worldenergydata/pull/415) — `.claude/docs/agents.md` (6 markers); test `tests/test_agent_doc_clean.py`
  - [aceengineer-website#15](https://github.com/vamseeachanta/aceengineer-website/pull/15) — 2 blog files (120 markers); test `tests/python/test_content_clean.py`
  - [assethold#51](https://github.com/vamseeachanta/assethold/pull/51) — `.claude/settings.json` (3 markers); test `tests/test_settings_clean.py`
  - Each test is per-repo and per-file; none would have caught markers in different files (mitigated post-hoc via `feedback_regression_test_broader_than_issue_scope`).
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

    # SKIP if an active merge/rebase/cherry-pick is in progress
    # (legitimate resolution commits stage marker-free content; but if we run
    # mid-conflict, the index may transiently contain unresolved files)
    if [ exists .git/MERGE_MSG OR .git/REBASE_HEAD OR .git/CHERRY_PICK_HEAD ]:
        echo "[check-no-conflict-markers] skipping (active merge/rebase/cherry-pick)"
        exit 0

    # Stage-aware: only check files added/modified/renamed in THIS commit
    STAGED = git diff --cached --name-only --diff-filter=ACMR
    if STAGED is empty: exit 0

    violations = []
    for file in STAGED:
        # Skip if file is gone (deletion) or is the plan/governance doc that
        # legitimately documents marker syntax
        if not exists "$file": continue
        if "$file" matches pattern "docs/governance/**" AND
           grep -q "<!-- CONFLICT_MARKER_FORENSIC_OK -->" "$file": continue
        # Self-exclude: this script itself documents the markers in comments
        if "$file" == "scripts/enforcement/check-no-conflict-markers.sh": continue

        # Strong signal: line beginning with "<<<<<<< " or ">>>>>>> " (note trailing space — git always writes that form)
        # The "=======" alone is a setext-heading false-positive trap; require co-occurrence with either anchor
        lines_lt = grep -n "^<<<<<<< " (staged blob via git show :"$file") || empty
        lines_gt = grep -n "^>>>>>>> " (staged blob via git show :"$file") || empty

        if lines_lt is non-empty OR lines_gt is non-empty:
            violations += "$file:<line>:<marker>" for each match

    if violations is empty: exit 0
    else:
        echo "ERROR: Unresolved merge-conflict markers detected in staged content:"
        for v in violations: echo "  $v"
        echo ""
        echo "To resolve: edit each file, remove the <<<<<<<, =======, >>>>>>> markers,"
        echo "keep the intended content, re-stage, and retry the commit."
        echo "For legitimate forensic documentation, add a"
        echo "<!-- CONFLICT_MARKER_FORENSIC_OK --> sentinel to the file."
        exit 1
```

### Cross-repo installer: `scripts/agents/install-pre-commit-hook-cross-repo.sh`

```
function install_cross_repo():
    WS_ROOT = $(git rev-parse --show-toplevel)  # workspace-hub
    CANONICAL = "$WS_ROOT/scripts/enforcement/check-no-conflict-markers.sh"

    # Tier-1 repo discovery: read from a tracked YAML manifest, NOT hardcoded list
    # (avoids drift when tier-1 set changes; aligns with #2411 inventory)
    TIER1_REPOS = read scripts/agents/tier1-repos.yaml -> .repos[]
    # Initial set per #2411: workspace-hub, digitalmodel, assetutilities,
    # worldenergydata, assethold, aceengineer-website, llm-wiki

    for repo in TIER1_REPOS:
        REPO_PATH = "$HOME/$repo"  OR  "$WS_ROOT/../$repo"  OR  configured base
        if not exists "$REPO_PATH/.git": warn-skip; continue

        # Vendored copy (not symlink — sibling repos may live on machines without WS)
        VENDORED = "$REPO_PATH/scripts/enforcement/check-no-conflict-markers.sh"
        mkdir -p "$REPO_PATH/scripts/enforcement"
        cp "$CANONICAL" "$VENDORED"
        chmod +x "$VENDORED"

        # Wire into pre-commit (idempotent grep-q-then-append pattern)
        PRE_COMMIT = "$REPO_PATH/.git/hooks/pre-commit"
        if not exists PRE_COMMIT: create minimal stub
        if not grep -q "check-no-conflict-markers" PRE_COMMIT:
            insert before final "exit 0":
                # ── Conflict-marker check (workspace-hub#2722) ──
                if [[ -f "$REPO_ROOT/scripts/enforcement/check-no-conflict-markers.sh" ]]; then
                    bash "$REPO_ROOT/scripts/enforcement/check-no-conflict-markers.sh" || exit 1
                fi

        echo "OK: $repo wired"

    # Drift check: workspace-hub canonical vs. each vendored copy
    # Implemented separately in check-pre-commit-hook-drift.sh
```

### Drift check: `scripts/enforcement/check-pre-commit-hook-drift.sh`

```
# Pattern lifted from cadence-helper sync check (install-hooks.sh:158-178)
function check_drift():
    WS_ROOT = $(git rev-parse --show-toplevel)
    CANONICAL = "$WS_ROOT/scripts/enforcement/check-no-conflict-markers.sh"
    CANONICAL_SHA = sha256(CANONICAL)

    for repo in TIER1_REPOS (excluding workspace-hub itself):
        VENDORED = "$repo_path/scripts/enforcement/check-no-conflict-markers.sh"
        if not exists: warn "missing in $repo — run install-pre-commit-hook-cross-repo.sh"; continue
        if sha256(VENDORED) != CANONICAL_SHA:
            echo "DRIFT: $repo has stale vendored copy (expected $CANONICAL_SHA, got <actual>)"
            exit 1

    echo "OK: all vendored copies in sync"
```

### Bootstrap-machine.sh §2.6 (~10 lines)

```
# 2.6. Install conflict-marker pre-commit hook (per #2722)
INSTALL_HOOK="${REPO_ROOT}/scripts/agents/install-pre-commit-hook-cross-repo.sh"
if [[ -x "${INSTALL_HOOK}" ]]; then
    bash "${INSTALL_HOOK}"
fi
```

### Install-hooks.sh wiring (~12 lines in workspace-hub's local install)

Append within existing `Step 2: Wire enforcement-env into pre-commit` chain, before the final `exit 0`:

```
# Wire conflict-marker check
if grep -q "check-no-conflict-markers" "$PRE_COMMIT"; then
    log "OK: conflict-marker check already wired"
else
    sed -i '/^exit 0$/i\
# ── Conflict-marker check (#2722) ──\
if [[ -f "${REPO_ROOT}/scripts/enforcement/check-no-conflict-markers.sh" ]]; then\
  bash "${REPO_ROOT}/scripts/enforcement/check-no-conflict-markers.sh" || exit 1\
fi\
' "$PRE_COMMIT"
fi
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/enforcement/check-no-conflict-markers.sh` | canonical detection script |
| Create | `scripts/agents/install-pre-commit-hook-cross-repo.sh` | propagation across 7 tier-1 repos |
| Create | `scripts/enforcement/check-pre-commit-hook-drift.sh` | drift detection |
| Create | `scripts/agents/tier1-repos.yaml` | canonical tier-1 manifest (avoid hardcoded list) |
| Create | `tests/enforcement/test_check_no_conflict_markers.py` | TDD coverage of detection script |
| Modify | `scripts/memory/bootstrap-machine.sh` | append §2.6 block after §2.5 |
| Modify | `scripts/enforcement/install-hooks.sh` | wire conflict-marker check into workspace-hub pre-commit |
| Update | `docs/plans/README.md` | add this plan row |

---

## TDD Test List

`tests/enforcement/test_check_no_conflict_markers.py` — pytest-driven, exercises the bash script via subprocess against synthetic staged files in a `tmp_path` git fixture.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_clean_file_passes` | normal file with no markers exits 0 | staged file: simple python module | exit 0, no stdout violations |
| `test_lt_anchor_alone_fails` | `<<<<<<< HEAD` at column 0 triggers | staged file with `<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> branch` | exit 1, file:line cited |
| `test_setext_heading_passes` | markdown `=======` underline does NOT trigger | staged file: `# Title\n=======\nbody` | exit 0 (no `<<<<<<<` or `>>>>>>>` co-occurs) |
| `test_shell_banner_passes` | shell-comment banner `# =======` does NOT trigger | staged file with `# ============` block | exit 0 |
| `test_active_merge_skips` | hook exits 0 if `.git/MERGE_MSG` present | dirty index during merge | exit 0, "skipping" message |
| `test_active_rebase_skips` | hook exits 0 if `.git/REBASE_HEAD` present | dirty index during rebase | exit 0 |
| `test_active_cherrypick_skips` | hook exits 0 if `.git/CHERRY_PICK_HEAD` present | dirty index during cherry-pick | exit 0 |
| `test_forensic_whitelist_passes` | `<!-- CONFLICT_MARKER_FORENSIC_OK -->` exempts file | governance doc explaining markers | exit 0 |
| `test_self_exclude_passes` | the check script itself can stage cleanly | staged file: `scripts/enforcement/check-no-conflict-markers.sh` | exit 0 |
| `test_unstaged_marker_ignored` | unstaged file with markers does NOT trigger | working-tree marker, nothing staged | exit 0 (stage-aware) |
| `test_multiple_violations_all_cited` | every match cited, not just first | 2 files each with markers | exit 1, all 4+ violations in stdout |
| `test_deleted_file_skipped` | deletion-diff-filter excludes deleted files | staged deletion of marker-containing file | exit 0 |
| `test_renamed_file_checked` | rename retains content scan | staged rename with markers in content | exit 1 |
| `test_install_idempotent` | running install-pre-commit-hook-cross-repo twice → no double-wiring | call install script twice | hook wired exactly once |
| `test_drift_detected` | modifying vendored copy → drift check exits 1 | tamper with sibling repo's vendored copy | exit 1 with sibling path cited |
| `test_drift_clean_passes` | unmodified copies → exit 0 | fresh install state | exit 0 |

The 16 cases cover happy path + each documented edge case + the install/drift surface. Pytest fixtures use `tmp_path` to construct minimal git repos so the suite is hermetic.

---

## Acceptance Criteria

- [ ] `scripts/enforcement/check-no-conflict-markers.sh` exists and is executable.
- [ ] Stage-aware: only inspects `git diff --cached --name-only --diff-filter=ACMR` files, never the whole tree.
- [ ] Anchored regex: requires `^<<<<<<< ` (trailing space, column 0) OR `^>>>>>>> ` (trailing space, column 0) — does NOT trigger on bare `=======`.
- [ ] Skips during active merge / rebase / cherry-pick (`.git/MERGE_MSG`, `.git/REBASE_HEAD`, `.git/CHERRY_PICK_HEAD`).
- [ ] Forensic whitelist via `<!-- CONFLICT_MARKER_FORENSIC_OK -->` sentinel works in `docs/governance/**`.
- [ ] Self-exclude: the script itself can be modified and committed without false-positive.
- [ ] Reports `file:line:<marker-line>` for every detected violation (not just first).
- [ ] Exit codes: 0 on clean / skip / no-staged-files; 1 on detection.
- [ ] `scripts/agents/install-pre-commit-hook-cross-repo.sh` installs vendored copies into all 7 tier-1 repos (manifest-driven via `scripts/agents/tier1-repos.yaml`).
- [ ] Idempotent: running installer twice produces no duplicate wiring.
- [ ] `scripts/enforcement/check-pre-commit-hook-drift.sh` detects out-of-sync vendored copies.
- [ ] `bootstrap-machine.sh` §2.6 invokes installer on new-machine bootstrap.
- [ ] `install-hooks.sh` wires the check into workspace-hub's own pre-commit (before existing `exit 0` at line 49 — corrected from the dead-code-after-exit-0 pattern).
- [ ] `tests/enforcement/test_check_no_conflict_markers.py` covers all 16 cases listed above, all pass.
- [ ] No regression: `uv run python -m pytest tests/enforcement/` full suite passes (40 existing + 16 new = 56).
- [ ] Empirical validation: hook installed on ≥2 sibling repos (digitalmodel + worldenergydata) and verified to block a deliberately constructed marker-containing commit.
- [ ] Review artifacts posted to `scripts/review/results/2026-05-16-plan-2722-{claude,codex,gemini}.md` (T2 → 3-provider review required per `feedback_always_adversarial_review_scale_depth`).
- [ ] Closing commit references `Closes #2722`.

---

## Adversarial Review Summary

<!-- Filled after Step 4 (review wave) completes. Currently PENDING. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING — review wave in flight.

Revisions made based on review:
- (to be populated after r1/r2/r3 complete)

---

## Risks and Open Questions

- **Risk: hook bypass via `--no-verify`.** Any `git commit --no-verify` skips the hook entirely. Mitigation: `feedback_pre_push_hook_no_verify_for_preservation` documents that commit-level `--no-verify` is banned by the Iron Law; push-level `--no-verify` is permitted for codex-branch preservation. The hook is therefore correctly placed at pre-commit (not pre-push). No additional mitigation needed.
- **Risk: vendored-copy drift.** If a sibling repo modifies its vendored copy independently, drift accumulates. Mitigation: `check-pre-commit-hook-drift.sh` (lifted from cadence-helper pattern at `install-hooks.sh:158-178`); could be hooked into a daily cron or pre-push.
- **Risk: false-positive on setext-heading-only markdown.** Strict anchoring (`^<<<<<<< ` with trailing space) eliminates this — git always writes that exact form.
- **Risk: false-negative if user resolves a conflict but forgets one of the three markers.** A lone `=======` (no `<<<<<<<` or `>>>>>>>` anywhere) will pass. Acceptable: the strongest signal is the anchor pair; the cost of a false-negative here (one stray `=======` line) is far smaller than the false-positive cost (every markdown setext heading triggers).
- **Risk: tier-1 repo discovery drift.** Hardcoded repo list goes stale as tier-1 membership changes. Mitigation: `scripts/agents/tier1-repos.yaml` as single source of truth; `#2411` audit comment is the seed for the initial manifest.
- **Risk: bootstrap-machine.sh §2.6 not idempotent.** If the installer is invoked twice (e.g., bootstrap re-run + manual run), vendored copies are re-overwritten. This is desired behavior for drift recovery; tests `test_install_idempotent` confirms no harm.
- **Open question: should the hook also fire pre-push?** Pre-push is the second line of defense (catches pushes from branches where pre-commit was bypassed). Out of scope for this plan — current scope is pre-commit only; pre-push augmentation could be a follow-on issue.
- **Open question: should LLM-wiki be in the tier-1 manifest?** Per `project_llm_wiki_spunout` (2026-05-05), llm-wiki is a dedicated public repo; #2411 audit included it. Confirming inclusion in tier-1 manifest pending user direction.

---

## Complexity: T2

**T2** — 3 new shell scripts (canonical check, cross-repo installer, drift check) + 1 YAML manifest + 1 pytest test module + 2 modifications to existing infra scripts. Edge cases (active-merge skip, forensic whitelist, self-exclude, setext-heading false-positive guard) add nuance but each is a single conditional. Cross-repo propagation is the most architecturally novel element but follows the well-established cadence-helper sync pattern (`install-hooks.sh:158-178`). Estimated implementation time: 60-90 min including TDD.
