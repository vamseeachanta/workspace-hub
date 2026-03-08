# Cross-Review: Claude
> WRK-1035 | 2026-03-08

## Verdict: MINOR

---

## Findings

### P2-MINOR — Phase 3 Gap 3: elapsed-time threshold is inconsistent between plan and audit
**Plan section:** Phase 3, Priority 1, gap 3 (browser-open to approval elapsed time)

The plan mandates ≥ 300s for ALL hard-gate stages (Stages 5, 7, and 17) — consistent with
the Stage 5 user decision recorded in session-audit-master.md (§Stage 5 User Decisions, item 1:
"300s for ALL hard-gate stages"). However the gate verifier implementation spec in Phase 3 also
states "≥ 300 seconds for all human-gate stages (Stages 5, 7, and 17)" correctly. The problem
is that R-03 in session-audit-master.md still says "≥ 60 seconds for plan stages (5, 7)" —
that older threshold was overridden by the Stage 5 user decision but is still present in the
rules appendix of the audit report. The plan correctly uses 300s, but the threshold in T15/T16
tests (described only as "plan stage") is ambiguous: a reader implementing T15 from the test
table alone might apply 60s rather than 300s. The test description should make explicit that
300s applies to all three human-gate stages. Low implementation risk but potential for
miscalibrated test fixtures.

**Recommended fix:** In the test table for T15/T16, add "(≥ 300s, same threshold as all
human-gate stages)" to remove the ambiguity. Also add a note in Phase 3 text that R-03's
60s threshold is superseded by the Stage 5 user decision.

---

### P2-MINOR — Phase 2: `claim-item.sh` sentinel fix is described in the Risks section but not in the Phase 2 file list
**Plan section:** Phase 2, Files to change; Risks section

The Risks section explicitly states "Phase 2 must also update `claim-item.sh` to read
`$CLAUDE_SESSION_ID` env variable as primary source; block claim with diagnostic if env var
also absent rather than writing sentinel. This is a scope addition to Phase 2 (low risk —
shell-level only)." The session-audit-master.md Open Questions confirm "RESOLVED: Include in
Phase 2 scope."

However, `claim-item.sh` does not appear in the Phase 2 "Files to change" list. It appears
only in the resource-intelligence.yaml file_inventory under gaps. If an implementer reads Phase
2 linearly, they may miss this file. The `close-item.sh` change is in Phase 2's file list;
`claim-item.sh` is not.

**Recommended fix:** Add `scripts/work-queue/claim-item.sh` to the Phase 2 "Files to change"
block with the specific changes (read `$CLAUDE_SESSION_ID`, block on unresolvable session ID
rather than writing "unknown"). This is already resolved in spirit — it just needs to appear
explicitly in the phase deliverable list so no test for it is missing. Currently no test
(T5–T10) covers the claim-item.sh sentinel block path.

---

### P2-MINOR — Phase 4: checkpoint schema enforcement acceptance criteria is incomplete
**Plan section:** Phase 4, Acceptance Criteria; session-audit-master.md §Addendum Checkpoint Schema

The session-audit-master.md Addendum (§Checkpoint Schema + /wrk-resume Deprecation) adds three
requirements to Phase 4 scope: (1) `exit_stage.py` validates checkpoint.yaml before allowing
stage exit; (2) `/work run` auto-loads checkpoint; (3) `/wrk-resume` becomes diagnostic-only.
The plan body for Phase 4 mentions `/wrk-resume` under Phase 5 (adding version field, reading
stage-evidence) but does not include the checkpoint schema validation or `/work run`
auto-load-checkpoint as Phase 4 acceptance criteria items. The "Implication: Phase 4 scope
addition — add to Phase 4 acceptance criteria" note from the audit addendum was not actioned
in the final plan text.

No test covers checkpoint schema enforcement at stage exit. T31–T39 cover stage start/end
script behaviour but none test the checkpoint.yaml validation path.

**Recommended fix:** Add to Phase 4 acceptance criteria:
- `exit_stage.py` validates checkpoint.yaml schema before stage exit; blocks on missing
  or invalid checkpoint
- `/work run` reads checkpoint.yaml for the active WRK before calling `start_stage.py`
- `/wrk-resume` behaviour description updated to diagnostic-only (no stage execution)
Add T39b (or renumber) covering `exit_stage.py` checkpoint validation block.

---

### P3-SUGGESTION — Phase 3: modularised `verify-gate-evidence.py` file-size risk not gated by a test
**Plan section:** Phase 3, Risks; Open Questions (RESOLVED item 3)

The plan correctly identifies the 1208-line `verify-gate-evidence.py` as a modularisation
candidate and resolves to split into `checks/timestamp.py`, `checks/identity.py`,
`checks/structure.py` with the main file as a dispatcher ≤ 150 lines. This is well-reasoned.
However there is no line-count test analogous to T40–T43 for the refactored
`verify-gate-evidence.py` itself. After adding 14 new check functions plus the dispatcher
refactor, there is no automated guard preventing the main file from growing back above the
400-line hard limit. The same enforcement applied to skills should apply to the 1208-line
Python file.

**Recommended fix:** Add T47b (or renumber): `verify-gate-evidence.py` (main dispatcher) ≤ 200
lines after refactor. Each `checks/*.py` sub-module ≤ 400 lines.

---

### P3-SUGGESTION — Phase 1 + Phase 3: migration exemption cutoff uses time-based description but plan resolves to ID-based
**Plan section:** Phase 1 Acceptance Criteria; Risks; Open Questions (RESOLVED item 7)

The Open Questions section correctly resolves: "WRK-ID-based exemption (≤ WRK-1035). More
stable than time-based; avoids timezone ambiguity." However the Risks section still describes
the exemption as "all WRKs with `created_at` before `2026-03-09T00:00:00Z`" (time-based). The
Phase 3 backward-compatibility note also says "apply only to WRKs being closed or verified
AFTER this WRK is deployed" without specifying the ID-based cutoff. The implementation will
need to choose one mechanism; if an implementer follows the Risks prose rather than the
Open Questions resolution, they implement the wrong approach.

**Recommended fix:** Remove the time-based cutoff from the Risks section and replace with
"WRK-ID ≤ WRK-1035 are exempt from new timestamp ordering and sentinel value checks." Ensure
consistency with the already-resolved Open Questions entry.

---

### P3-SUGGESTION — Phase 6: 7-day live validation cron integration is under-specified
**Plan section:** Phase 6 Acceptance Criteria; session-audit-master.md §Stage 17 Live Validation Gate

The live validation protocol (7 consecutive clean days, `day-N.md` artefacts in
`assets/WRK-1035/evidence/live-validation/`) is documented in the audit addendum and partially
referenced in Phase 6. However the plan does not specify: (a) which script performs the daily
analysis run and how it is invoked, (b) whether `comprehensive-learning` nightly pipeline needs
a new Phase entry for WRK-1035 violation scanning, (c) who or what resets the 7-day clock when
a HIGH violation is found, (d) what constitutes a "clean day" (zero HIGH-severity violations in
both session logs AND gate verifier output for ALL WRKs run that day, or only WRK-1035 itself).

The rolling-scope rule ("new patterns rolled INTO WRK-1035, not spun off") combined with a
7-day reset means WRK-1035 could remain open indefinitely if violations recur. This is
intentional per the user instruction, but the acceptance criterion at Stage 17 should define
the terminal condition precisely enough to be evaluated without ambiguity.

**Recommended fix:** Add to Phase 6 acceptance criteria:
- A `scripts/work-queue/live-validation-check.sh` or equivalent daily script that runs the
  new gate verifier checks against all same-day session logs and writes `day-N.md`
- A definition of "clean day": zero HIGH-severity violations in gate verifier output for
  any WRK closed or verified during that day
- Wire into `comprehensive-learning-nightly.sh` as a conditional step (active only while
  WRK-1035 Stage 17 is open)

---

### P3-SUGGESTION — Phase 5: `wrk-lifecycle-testpack/SKILL.md` pruning candidate not actioned
**Plan section:** Phase 5, Files to change; resource-intelligence.yaml file_inventory

`resource-intelligence.yaml` explicitly lists `wrk-lifecycle-testpack/SKILL.md` (83 lines,
version 1.0.1) with 6 identified gaps — including no Stage 1 gate tests, no timestamp ordering
tests, no Codex keyword tests, no sentinel value tests. The plan defers this to WRK-1045 to
avoid scope creep. This is a reasonable call, but the skill-creator scorecard mandated by Phase
5 should include `wrk-lifecycle-testpack/SKILL.md` in the evaluation (it is the test contract
skill directly governing the 47 tests being added). It is listed in `resource-intelligence.yaml`
`skills.core_used` and has identified gaps. If it scores below 60/100 on utility it becomes a
merge/retire candidate whose deferral to WRK-1045 would need explicit justification.

**Recommended fix:** Add `wrk-lifecycle-testpack/SKILL.md` to the Phase 5 skill-creator
scorecard evaluation (read-only evaluation, no line-count test — the skill is 83 lines and
already within bounds). Document the scorecard result and carry the update recommendation
into WRK-1045 with a cross-reference.

---

## What is solid

- **All 6 phases are coherently sequenced.** The dependency graph (Phase 1 → Phase 3 gap 14;
  Phase 1/2/4 must complete before Phase 5 SKILL edits) is explicit, implementable, and
  avoids the multi-file merge-conflict trap by deferring all SKILL.md edits to a single pass.

- **All 14 gate verifier gaps are addressed in Phase 3.** The gap numbering is consistent
  between session-audit-master.md, resource-intelligence.yaml, and the plan. Priority 1/2
  partition is sound (retroactive approval checks first, structural checks second).

- **Phase 4 start_stage.py / exit_stage.py scope is well-bounded.** The "pre-work: review
  current scope before writing code" instruction is correct — it prevents over-engineering.
  The WAIT instruction output for human-gate stages, stale artifact scan, prior-stage artifact
  prerequisite check, and HTML regeneration are all independently testable and non-overlapping
  with Phase 3 verifier work.

- **Phase 5 pruning criteria are clear and binary.** The two-rule taxonomy (redundant → delete,
  script-enforced → one-line reference note) removes the ambiguity that causes reference-file
  dumping. The note that `references/` is not a content dump is explicit and will prevent the
  most common pruning anti-pattern.

- **47 tests are sufficient for the scoped deliverables.** Each phase has dedicated test files,
  each test maps to a specific check or behaviour, and the test table is machine-readable. The
  integration eval section (post-implementation human-run) correctly supplements unit tests
  with live gate self-verification on WRK-1035 itself.

- **Risks section is comprehensive and actionable.** The six risks (retroactive verification of
  archived WRKs, Codex deadlock on ace-linux-1, sentinel value blocking, SKILL cross-reference
  breakage, Stage 1 gate for existing pending WRKs, verifier file size) are each paired with a
  specific mitigation. No material risk is identified here that is absent from the plan.

- **Phase 2 close-item.sh shell-level blocking is the right architectural layering.** Shell exit
  1 before invoking verify-gate-evidence.py means the most critical ordering invariants are
  enforced even if the Python verifier is bypassed or broken. Redundancy here is a feature.

- **Phase 6 orchestrator team pattern correctly subordinates spawn-team.sh to on-demand
  TaskCreate.** The clarification that spawn-team.sh is a convenience tool, not a required
  entrypoint, and that TeamCreate is optional (not mandated) accurately reflects the user
  decision in session-audit-master.md §Stage 5 User Decisions item 5.

- **Phases 5 and 6 SKILL.md edits are correctly mandated as a single-pass operation.** The
  sequencing note prevents the line-budget double-counting problem that would occur if Phase 5
  pruning and Phase 6 additions were applied in separate editing passes.

- **Out of Scope section is complete.** WRK-1039 through WRK-1045 are all listed with rationale.
  The rolling-scope rule and 7-day live validation window are correctly captured as Stage 17
  conditions rather than Phase 6 deliverables.
