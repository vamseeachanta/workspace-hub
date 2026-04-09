# Plan Review Command Pack — 2026-04-09

> Ready-to-run `gh` commands for issues #2059, #2063, #2056
> Generated from execution packs in `docs/plans/claude-followup-2026-04-09/results/`

---

## 1. Move Each Issue to `status:plan-review`

Run these commands **in order** (one per issue). Each adds the label and posts the review comment from the execution pack.

### Issue #2059 — Real Vessel Stability Test Cases

```bash
gh issue edit 2059 --add-label "status:plan-review"
```

```bash
gh issue comment 2059 --body "$(cat <<'EOF'
**Plan review posted** — execution pack prepared at `docs/plans/claude-followup-2026-04-09/results/issue-2059-execution-pack.md`

**Summary**: Test-only implementation (~80-120 lines) adding real vessel stability cases for Sleipnir, Thialf, and Balder to `test_vessel_fleet_adapter.py`. All production source modules are already complete via #1859 and #1850. Conditional minor edit to `ship_data.py` only if monohull form coefficient defaults produce unreasonable GM values for semi-subs.

**Key decisions for review**:
1. Physical reasonableness bounds: GM in [0.5, 50] m — appropriate for large semi-sub crane vessels?
2. Conditional Cb/Cw override: implement only if monohull defaults fail bounds check — agree?
3. Pre-existing `test_register_multiple_vessels` isolation bug is explicitly out of scope

Labeling `status:plan-review`. Please review and approve or request changes.
EOF
)"
```

### Issue #2063 — Drilling Riser Adapter

```bash
gh issue edit 2063 --add-label "status:plan-review"
```

```bash
gh issue comment 2063 --body "$(cat <<'EOF'
## Plan Review: #2063 — Drilling Riser Adapter

Execution pack prepared at `docs/plans/claude-followup-2026-04-09/results/issue-2063-execution-pack.md`.

**Scope**: Add `adapter.py` to `digitalmodel/src/digitalmodel/drilling_riser/` that converts
worldenergydata CSV records (imperial) to SI calculation-ready dicts, following the #1859
`normalize_*_record` / `register_*` pattern. 6 TDD integration tests. No worldenergydata changes.

**Files**: 2 new (`adapter.py`, `test_adapter_integration.py`), 2 modified (`__init__.py`, `conftest.py`).

**Dependencies**: #1859 DONE. No blockers.

**Wave**: 1 (high-confidence batch alongside #2059 and #2056).

Requesting review before `status:plan-approved` label.
EOF
)"
```

### Issue #2056 — Session Governance Phase 2

```bash
gh issue edit 2056 --add-label "status:plan-review"
```

```bash
gh issue comment 2056 --body "$(cat <<'EOF'
## Plan Review: Execution Pack Ready

An execution pack has been prepared for #2056 (Session Governance Phase 2: Wire Runtime Enforcement into Hooks).

**Artifact**: `docs/plans/claude-followup-2026-04-09/results/issue-2056-execution-pack.md`

**Scope summary**:
- Fix tool-call ceiling threshold (500 -> 200) + add hard-stop context injection
- Create error-loop-breaker hook (3x consecutive identical errors -> STOP)
- Flip pre-push review gate default to strict mode
- TDD-first: 3 new test files before any implementation code

**Implementation delta**: ~150 lines new code + ~30 lines modified across 7 modified files and 3 new files.

**Contention note**: `.claude/settings.json` is high-contention; edits are minimal (2 env vars + 1 PostToolUse entry).

**Prerequisite**: #1839 Phase 1 is complete (verified via commit `e69473081`).

Please review and apply `status:plan-approved` when ready to proceed with implementation.

Labels: `status:plan-review`
EOF
)"
```

---

## 2. Move Each Issue to `status:plan-approved` (After User Approval)

After the user reviews and approves each plan, run the corresponding commands below. The label swap removes `plan-review` and adds `plan-approved`.

### Issue #2059

```bash
gh issue edit 2059 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

```bash
gh issue comment 2059 --body "$(cat <<'EOF'
**Plan approved** — execution pack at `docs/plans/claude-followup-2026-04-09/results/issue-2059-execution-pack.md` is cleared for implementation.

Scope: TDD-first test extension for 3 real vessel stability cases. Branch: `feat/2059-vessel-stability-tests`. Single atomic commit.

Transitioning from `status:plan-review` -> `status:plan-approved`.
EOF
)"
```

### Issue #2063

```bash
gh issue edit 2063 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

```bash
gh issue comment 2063 --body "$(cat <<'EOF'
## Plan Approved: #2063

Execution pack reviewed and approved. Implementation may proceed per the TDD task sequence
in the execution pack. Reminder:
- TDD first (write failing tests before adapter code)
- Commit inside `digitalmodel/` submodule, then update pointer in workspace-hub
- Post summary comment on this issue after implementation
- Cross-review required per workspace-hub policy
EOF
)"
```

### Issue #2056

```bash
gh issue edit 2056 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

```bash
gh issue comment 2056 --body "$(cat <<'EOF'
## Plan Approved: Cleared for Implementation

Execution pack reviewed and approved. Implementation may proceed following the TDD-first task sequence defined in the pack.

**Reminder**: Pull latest main and check `.claude/settings.json` for recent changes before starting. Cross-review required after implementation (2-provider minimum).

Labels: remove `status:plan-review`, add `status:plan-approved`
EOF
)"
```

---

## 3. Ordering Recommendation

### Plan-review labeling order (all three, same session)

Apply `status:plan-review` to all three issues in a single pass — order does not matter since no issue depends on another at the review stage.

**Suggested sequence**: #2059, #2063, #2056 (smallest scope first for fastest review turnaround).

### Plan-approved labeling order (after user review)

The user chooses which plans to approve. These issues have **zero file overlap** and can be approved and implemented in parallel. However, if sequencing is preferred:

| Priority | Issue | Rationale |
|----------|-------|-----------|
| 1st | #2059 | Smallest delta (~80-120 lines test-only), highest confidence, zero source risk |
| 2nd | #2063 | Medium delta (~140-190 lines), new adapter module, contained in `digitalmodel/` submodule |
| 3rd | #2056 | Largest delta (~180 lines), touches `.claude/settings.json` (high-contention file), governance hooks |

### Parallel execution safety

All three issues operate in **non-overlapping file domains**:
- #2059: `digitalmodel/tests/naval_architecture/` (+ conditional `ship_data.py`)
- #2063: `digitalmodel/src/digitalmodel/drilling_riser/` + `digitalmodel/tests/drilling_riser/`
- #2056: `.claude/hooks/`, `scripts/enforcement/`, `tests/hooks/`, `.claude/settings.json`

**Parallel implementation is safe.** No merge conflicts expected between any pair.

---

## 4. Command Safety Notes and Rollback

### Safety notes

- **All commands are additive**: `--add-label` and `gh issue comment` do not destroy data
- **Label removal** (`--remove-label`) in Section 2 only removes `status:plan-review` — no other labels are affected
- **Comments are append-only**: GitHub issue comments cannot overwrite existing content
- **No code changes**: This command pack only touches GitHub issue metadata (labels + comments)
- **Idempotent labels**: Running `--add-label` for a label already present is a no-op (safe to re-run)
- **Rate limits**: GitHub CLI respects API rate limits; 6 label edits + 6 comments is well within hourly quota

### Rollback commands

If a label was applied prematurely or to the wrong issue:

```bash
# Remove plan-review from a specific issue
gh issue edit <ISSUE_NUMBER> --remove-label "status:plan-review"

# Remove plan-approved from a specific issue
gh issue edit <ISSUE_NUMBER> --remove-label "status:plan-approved"

# Full rollback — remove both labels from all three issues
for issue in 2059 2063 2056; do
  gh issue edit "$issue" --remove-label "status:plan-review" --remove-label "status:plan-approved" 2>/dev/null
done
```

**Note**: GitHub comments cannot be deleted via `gh issue comment`. If a comment was posted in error, delete it manually from the GitHub web UI (issue page > comment > three-dot menu > Delete).

---

## 5. Morning-Operator Checklist

- [ ] Confirm on latest `main`: `git pull && git log --oneline -3`
- [ ] Run Section 1 commands to label all three issues `status:plan-review`
- [ ] Review each execution pack — check scope, TDD sequence, file lists
- [ ] For each approved plan, run the matching Section 2 commands (`plan-review` -> `plan-approved`)
- [ ] Dispatch implementation agents only for `status:plan-approved` issues (per CLAUDE.md policy)
- [ ] After implementation: verify each agent posted a summary comment on its issue

---

RECOMMENDATION: APPLY AFTER USER CHOOSES APPROVAL ORDER
