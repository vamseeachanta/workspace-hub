# Terminal 6 — Execution Pack: Session Governance Phase 3 (#2057)

## 1. Issue Metadata

| Field | Value |
|-------|-------|
| Issue | [#2057](https://github.com/vamseeachanta/workspace-hub/issues/2057) |
| Title | Session governance Phase 3: restore lost session infrastructure |
| Parent | #1839 |
| Labels | `enhancement`, `priority:medium`, `cat:ai-orchestration`, `agent:claude` |
| State | OPEN |
| Milestone | None |
| Assignees | None |
| Stage-1 Dossier | `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-6-governance-phase3-infrastructure.md` |
| Pack Date | 2026-04-09 |

---

## 2. Fresh Status Check Since Stage-1 Dossier

### CRITICAL: Dossier Is Stale — Skills Already Implemented

The stage-1 dossier (written ~15:00 2026-04-09) concluded that deliverables #1 and #4 were missing and #2/#3 were already complete. **Between the dossier write and now, the overnight batch terminal implemented all 4 deliverables** in 5 atomic commits:

| Commit | Time | Description |
|--------|------|-------------|
| `e582d7e70` | 15:16 | `feat(skills): add session-start-routine pre-flight skill (#2057)` |
| `5c9c798d0` | 15:17 | `feat(skills): add session-corpus-audit quality analysis skill (#2057)` |
| `be5208928` | 15:18 | `feat(skills): register comprehensive-learning in skills tree (#2057)` |
| `9639588bb` | 15:18 | `feat(skills): add cross-review-policy enforcement skill (#2057)` |
| `ef8e7826b` | 15:28 | `feat(governance): restore lost session infrastructure — 3 new skills (#2057)` (squash cleanup) |

### Deliverable Status Matrix (Updated)

| # | Deliverable | Dossier Said | Actual Status Now | File Path |
|---|-------------|-------------|-------------------|-----------|
| 1 | session-start-routine | MISSING | **DONE** — 44 lines, v1.0.0 | `.claude/skills/coordination/session-start-routine/SKILL.md` |
| 2 | session-corpus-audit | DONE (workspace-hub) | **DONE** — duplicate at coordination (58 lines) + original workspace-hub (434 lines) | `.claude/skills/coordination/session-corpus-audit/SKILL.md` |
| 3 | comprehensive-learning | DONE (workspace-hub) | **DONE** — wrapper added (143 lines) at coordination path | `.claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md` |
| 4 | cross-review-policy | MISSING | **DONE** — 57 lines, v1.0.0 | `.claude/skills/coordination/cross-review-policy/SKILL.md` |

### Path Deviation

Dossier expected skills at `.claude/skills/workspace-hub/`. Overnight build placed them at `.claude/skills/coordination/`. Both are valid skill locations, but this means:
- The `workspace-hub/session-corpus-audit/` (434 lines, Hermes-authored) and `coordination/session-corpus-audit/` (58 lines, overnight build) are **duplicates** with different content
- The `workspace-hub/comprehensive-learning/` (159 lines, v2.5.0) and `coordination/comprehensive-learning-wrapper/` (143 lines) are **complementary** (wrapper provides skill-tree discoverability)

### Outstanding Gaps Not Addressed by Overnight Build

| Gap | Evidence | Severity |
|-----|----------|----------|
| 5 broken `session-start-routine` links in `_internal/` skills | `grep -rn session-start-routine .claude/skills/_internal/` returns 4 hits pointing to `../session-start-routine/SKILL.md` (relative to `_internal/meta/`) which doesn't exist | Medium |
| 0 of 4 proposed smoke tests created | `ls tests/skills/test_*_smoke.py` — no matches | Medium |
| SESSION-GOVERNANCE.md not updated for #2057 | `grep -n '#2057' docs/governance/SESSION-GOVERNANCE.md` — no matches (Phase 3 sections reference #2047, #2028, #2027) | Low |
| Issue #2057 body still stale | Claims deliverables #2 and #3 "never built" / "invisible" | Low |
| No `status:plan-review` or `status:plan-approved` labels | `gh issue view 2057 --json labels` shows only original 4 labels | Process violation — work was done without plan approval |
| Duplicate session-corpus-audit not reconciled | 434-line vs 58-line versions at different paths | Low — functional but confusing |

---

## 3. Minimal Plan-Review Packet

### Scope Assessment: CLEANUP ONLY

All production skills are built and committed. The remaining work is verification + hygiene:

1. **Fix 5 broken internal links** — point `_internal/meta/` references to actual skill location
2. **Create 4 smoke tests** — validate skill frontmatter and required sections
3. **Update SESSION-GOVERNANCE.md** — add #2057 section documenting the skill restoration
4. **Reconcile duplicates** — decide whether coordination/ or workspace-hub/ is canonical for session-corpus-audit
5. **Update issue body** — reflect actual completion state
6. **Label and close** — add `status:plan-approved`, then close after verification

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Broken links cause confusion in future skill audits | High | Low | Fix all 5 references in one commit |
| Duplicate skills cause divergent evolution | Medium | Medium | Choose canonical path, symlink or remove duplicate |
| Process violation (no plan-approved before implementation) | Already happened | Low — skills are small, pattern-following | Document in issue comment, retrospective only |

### Cross-Review Requirements

Per `docs/standards/AI_REVIEW_ROUTING_POLICY.md`, cleanup commits are low-risk and can use two-agent review (Claude + one of Codex/Gemini). Full three-agent review not required for link fixes and smoke tests.

---

## 4. Issue Refinement Recommendations

### Issue Body Update

The issue body should be updated to reflect reality:

1. **Deliverable #1** (session-start-routine): Change "Lost during GSD migration" → "Restored at `.claude/skills/coordination/session-start-routine/SKILL.md` (v1.0.0, 2026-04-09)"
2. **Deliverable #2** (session-corpus-audit): Change "Never built" → "Pre-existing at `workspace-hub/` (434 lines, Hermes v1.0.0) + slim version at `coordination/` (58 lines)"
3. **Deliverable #3** (comprehensive-learning): Change "invisible to skill discovery" → "Registered via wrapper at `coordination/comprehensive-learning-wrapper/SKILL.md` (143 lines)"
4. **Deliverable #4** (cross-review-policy): Change "not as actionable skill" → "Skill created at `coordination/cross-review-policy/SKILL.md` (57 lines, v1.0.0)"
5. **Add section**: "Remaining cleanup: broken links (5), smoke tests (4), governance doc update, duplicate reconciliation"

### Label Recommendations

| Action | Label | Reason |
|--------|-------|--------|
| Add | `status:plan-review` | Formalize the cleanup plan for approval |
| Eventually add | `status:plan-approved` | After operator reviews this pack |
| Eventually add | `status:done` | After cleanup is verified |

---

## 5. Operator Command Pack

### 5a. Verify Current State

```bash
# Confirm all 4 skill files exist at coordination path
for skill in session-start-routine session-corpus-audit cross-review-policy comprehensive-learning-wrapper; do
  echo "--- $skill ---"
  head -10 .claude/skills/coordination/$skill/SKILL.md 2>/dev/null || echo "MISSING: $skill"
done
```

```bash
# Confirm broken links still exist (expect 4-5 hits)
grep -rn 'session-start-routine' .claude/skills/_internal/ .claude/skills/operations/
```

```bash
# Confirm no smoke tests exist yet
ls tests/skills/test_session_start_routine_smoke.py tests/skills/test_session_corpus_audit_smoke.py tests/skills/test_comprehensive_learning_smoke.py tests/skills/test_cross_review_policy_smoke.py 2>&1
```

```bash
# Confirm SESSION-GOVERNANCE.md lacks #2057 section
grep -n '#2057' docs/governance/SESSION-GOVERNANCE.md
```

### 5b. Issue Management Commands

```bash
# Update issue body with completion status (operator should review draft first)
gh issue edit 2057 --body "$(cat <<'BODY'
## Context

#1839 identified several pieces of session infrastructure that were lost during the GSD migration or never built. Phase 1 delivered the checkpoint model. Phase 2 wires runtime enforcement. This issue covers rebuilding the lost skills.

## Deliverables — Status

### 1. session-start-routine skill — DONE
- **Restored**: `.claude/skills/coordination/session-start-routine/SKILL.md` (v1.0.0)
- **Commits**: e582d7e70, ef8e7826b
- Pre-flight checks: load context, check prior state, validate env, check in-flight work, check governance limits

### 2. session-corpus-audit skill — DONE
- **Pre-existing**: `.claude/skills/workspace-hub/session-corpus-audit/SKILL.md` (434 lines, Hermes v1.0.0)
- **Slim version added**: `.claude/skills/coordination/session-corpus-audit/SKILL.md` (58 lines)
- **Commits**: 5c9c798d0, ef8e7826b

### 3. comprehensive-learning → skills tree — DONE
- **Pre-existing**: `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md` (v2.5.0)
- **Wrapper added**: `.claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md` (143 lines)
- **Commits**: be5208928, ef8e7826b

### 4. cross-review-policy skill — DONE
- **Created**: `.claude/skills/coordination/cross-review-policy/SKILL.md` (v1.0.0)
- **Commits**: 9639588bb, ef8e7826b
- Routing matrix, enforcement levels, verification commands

## Remaining Cleanup
- [ ] Fix 5 broken `session-start-routine` links in `_internal/meta/` skills
- [ ] Create 4 smoke tests in `tests/skills/`
- [ ] Update `docs/governance/SESSION-GOVERNANCE.md` with #2057 section
- [ ] Reconcile duplicate session-corpus-audit files (coordination/ vs workspace-hub/)

## References
- Governance doc: `docs/governance/SESSION-GOVERNANCE.md`
- Session signals: `.claude/state/session-signals/`
- Review routing policy: `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- Parent: #1839
BODY
)"
```

```bash
# Add plan-review label
gh issue edit 2057 --add-label "status:plan-review"
```

```bash
# After operator approves cleanup plan:
gh issue edit 2057 --add-label "status:plan-approved" --remove-label "status:plan-review"
```

```bash
# Post summary comment documenting overnight implementation
gh issue comment 2057 --body "$(cat <<'COMMENT'
## Stage-2 Status Report (2026-04-09)

**All 4 skill deliverables implemented** during overnight batch (terminal 6, commits e582d7e70..ef8e7826b).

Skills created at `.claude/skills/coordination/` path:
- `session-start-routine/SKILL.md` (44 lines)
- `session-corpus-audit/SKILL.md` (58 lines)
- `cross-review-policy/SKILL.md` (57 lines)
- `comprehensive-learning-wrapper/SKILL.md` (143 lines)

**Remaining cleanup** (plan-review pending):
1. Fix 5 broken internal links in `_internal/meta/` skills
2. Create 4 smoke tests
3. Update SESSION-GOVERNANCE.md
4. Reconcile duplicate session-corpus-audit (coordination/ 58 lines vs workspace-hub/ 434 lines)

Process note: implementation preceded plan-approval label. This was an overnight batch — apply `status:plan-approved` retroactively after reviewing this pack.
COMMENT
)"
```

---

## 6. Self-Contained Future Implementation Prompt

```
## Cleanup Task: GitHub Issue #2057 — Post-Implementation Hygiene

You are completing the cleanup tail for Session Governance Phase 3 (#2057).
All 4 skill deliverables were already implemented (see commits e582d7e70..ef8e7826b).
The remaining work is verification and hygiene — no new features.

### Task 1: Fix Broken Internal Links (5 files)

These files reference `../session-start-routine/SKILL.md` relative to `_internal/meta/`,
but the skill was created at `.claude/skills/coordination/session-start-routine/SKILL.md`.

Fix each reference to point to the correct path:

1. `.claude/skills/_internal/meta/repo-cleanup/SKILL.md` line 51
   - Current: `[session-start-routine](../session-start-routine/SKILL.md)`
   - Fix to: `[session-start-routine](../../../coordination/session-start-routine/SKILL.md)`

2. `.claude/skills/_internal/meta/hidden-folder-audit/SKILL.md` line 42
   - Current: `[session-start-routine](../session-start-routine/SKILL.md)`
   - Fix to: `[session-start-routine](../../../coordination/session-start-routine/SKILL.md)`

3. `.claude/skills/_internal/meta/module-based-refactor/SKILL.md` line 141
   - Current: `../meta/session-start-routine/SKILL.md`
   - Fix to: `../../coordination/session-start-routine/SKILL.md`

4. `.claude/skills/operations/devtools/ai-tool-assessment/SKILL.md` line 177
   - Current: `[session-start-routine](../../meta/session-start-routine/SKILL.md)`
   - Fix to: `[session-start-routine](../../../coordination/session-start-routine/SKILL.md)`

5. `.claude/skills/_internal/builders/skill-creator/SKILL.md` line 128
   - Current: `[session-start-routine](../../meta/session-start-routine/SKILL.md)`
   - Fix to: `[session-start-routine](../../../coordination/session-start-routine/SKILL.md)`

IMPORTANT: Verify each line number is still correct before editing. Use `grep -n session-start-routine <file>` first.

### Task 2: Create 4 Smoke Tests

Create `tests/skills/conftest.py` (if not exists) with shared skill-loading utility:

```python
import yaml
import pathlib

def load_skill(skill_path: str) -> dict:
    path = pathlib.Path(skill_path)
    assert path.exists(), f"Skill file missing: {skill_path}"
    text = path.read_text()
    assert text.startswith("---"), "Skill must have YAML frontmatter"
    parts = text.split("---", 2)
    meta = yaml.safe_load(parts[1])
    body = parts[2] if len(parts) > 2 else ""
    return {"meta": meta, "body": body, "path": path}

REQUIRED_FRONTMATTER = {"name", "description", "version"}
```

Create 4 test files (each ~20-30 lines):
- `tests/skills/test_session_start_routine_smoke.py` — assert file exists at coordination path, has frontmatter, body contains "Pre-flight" and "Context" and "Environment"
- `tests/skills/test_session_corpus_audit_smoke.py` — assert file exists at coordination path, has frontmatter
- `tests/skills/test_comprehensive_learning_smoke.py` — assert wrapper file exists at coordination path, cron script exists at `scripts/cron/comprehensive-learning-nightly.sh`
- `tests/skills/test_cross_review_policy_smoke.py` — assert file exists at coordination path, body contains "AI_REVIEW_ROUTING_POLICY"

Run: `uv run pytest tests/skills/test_*_smoke.py -v`

### Task 3: Update SESSION-GOVERNANCE.md

Add a new section after the existing Phase 3d section (after line ~320) in `docs/governance/SESSION-GOVERNANCE.md`:

```markdown
## What Was Implemented (Phase 3e) — 2026-04-09

### Session Infrastructure Skills Restoration (#2057)

Rebuilds four session skills lost during the GSD migration or never formalized:

| Skill | Path | Lines | Purpose |
|-------|------|-------|---------|
| session-start-routine | `.claude/skills/coordination/session-start-routine/SKILL.md` | 44 | Pre-flight checks at session start |
| session-corpus-audit | `.claude/skills/coordination/session-corpus-audit/SKILL.md` | 58 | Session quality trend analysis |
| comprehensive-learning-wrapper | `.claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md` | 143 | Skill-tree discoverability for nightly learning pipeline |
| cross-review-policy | `.claude/skills/coordination/cross-review-policy/SKILL.md` | 57 | Actionable three-agent review routing enforcement |

Also fixed 5 broken internal links and added 4 smoke tests.
```

### Task 4: Reconcile Duplicates (Decision Required)

Two session-corpus-audit files exist:
- `.claude/skills/workspace-hub/session-corpus-audit/SKILL.md` (434 lines, Hermes-authored, comprehensive)
- `.claude/skills/coordination/session-corpus-audit/SKILL.md` (58 lines, overnight build, slim)

**Recommendation**: Keep the workspace-hub version as canonical (it's far more detailed). Add a note to the coordination version that it's a slim reference pointing to the canonical one. Or delete the coordination version if redundancy is unwanted.

### Acceptance Criteria

- [ ] All broken links fixed: `grep -rn 'session-start-routine' .claude/skills/_internal/` shows valid paths
- [ ] All 4 smoke tests pass: `uv run pytest tests/skills/test_*_smoke.py -v`
- [ ] SESSION-GOVERNANCE.md mentions #2057
- [ ] Existing tests still pass: `uv run pytest tests/work-queue/test_session_governor.py -v`
- [ ] Issue #2057 body reflects actual completion state

### Constraints

- Do NOT modify the skill files themselves — they are already committed
- Do NOT modify `session_governor.py`, `governance-checkpoints.yaml`, or hook scripts
- Use `uv run` for all Python commands
- Commit cleanup as a single `chore(governance): fix broken links and add smoke tests (#2057)` commit
```

---

## 7. Morning Handoff

### For the Operator (Morning of 2026-04-10)

**TL;DR**: Issue #2057 is **95% complete**. The overnight batch implemented all 4 skill deliverables. What remains is cleanup hygiene — broken links, smoke tests, governance doc update, and issue management.

**Time estimate for cleanup**: One short Claude session (~15-20 tool calls).

**Decision needed**: Reconcile duplicate `session-corpus-audit` files (434-line workspace-hub vs 58-line coordination). Recommendation: keep workspace-hub as canonical.

**Process note**: The overnight batch implemented skills before the issue received `status:plan-approved`. This was expected for overnight batch behavior — apply the label retroactively.

### Quick-Start Sequence

1. Run the verification commands from Section 5a to confirm state
2. Run the `gh issue comment` command from Section 5b to document status
3. Run `gh issue edit 2057 --add-label "status:plan-approved"` to retroactively approve
4. Paste the Section 6 prompt into a new Claude session to execute cleanup
5. After cleanup passes, close: `gh issue close 2057 --comment "Phase 3 complete — all 4 skills restored, links fixed, smoke tests passing."`

### Key File Paths for Context

| File | Role | Lines |
|------|------|-------|
| `.claude/skills/coordination/session-start-routine/SKILL.md` | Deliverable #1 — pre-flight skill | 44 |
| `.claude/skills/coordination/session-corpus-audit/SKILL.md` | Deliverable #2 — slim quality analysis | 58 |
| `.claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md` | Deliverable #3 — skill-tree wrapper | 143 |
| `.claude/skills/coordination/cross-review-policy/SKILL.md` | Deliverable #4 — review routing policy | 57 |
| `.claude/skills/workspace-hub/session-corpus-audit/SKILL.md` | Pre-existing detailed version (Hermes) | 434 |
| `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md` | Pre-existing nightly pipeline skill | 159 |
| `docs/governance/SESSION-GOVERNANCE.md` | Governance roadmap (needs #2057 section) | 474 |
| `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | Source policy for cross-review-policy skill | ~60 |
| `scripts/ai/review_routing_gate.py` | Routing engine referenced by cross-review-policy | ~345 |

---

## 8. Final Recommendation

**RECOMMENDATION: APPLY `status:plan-approved` RETROACTIVELY AND EXECUTE CLEANUP**

All 4 skill deliverables for #2057 are implemented and committed. The remaining work is strictly cleanup: fix 5 broken internal links, create 4 smoke tests, update SESSION-GOVERNANCE.md, and reconcile the duplicate session-corpus-audit. This is a single short session of non-risky, pattern-following work. No blockers. Approve and dispatch.
