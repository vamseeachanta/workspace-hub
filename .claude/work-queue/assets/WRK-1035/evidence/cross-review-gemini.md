# Cross-Review: Gemini
> WRK-1035 | 2026-03-08

## Verdict: MINOR

---

## Findings

### P2-MINOR — Rolling scope rule creates open-ended WRK with no convergence guarantee
**Plan ref:** §Phase 1 "Rolling scope intake policy"; session-audit-master.md §Addendum — Stage 17 Live Validation Gate

The plan explicitly encodes a rule that new compliance failure patterns discovered during the 7-day
live validation window are rolled INTO WRK-1035 and reset the clock. This is the correct
intent — a hardening WRK should not be closed while known HIGH violations remain — but the written
policy has no convergence guard. If agents continue producing novel compliance failures during the
validation window, WRK-1035 could remain open indefinitely and absorb scope far beyond the 6
phases defined in the plan.

Recommended tightening: cap the rolling intake at patterns that are (a) a direct consequence of
a gate introduced by WRK-1035 itself, or (b) classified HIGH by the same audit methodology
(session-audit-master.md Patterns 1–3). Patterns in the MEDIUM/LOW range discovered during
live validation should be captured as WRK-1039 inputs, not absorbed. Add this boundary
explicitly to the rolling scope rule.

---

### P2-MINOR — Stage 1 exit gate (R-25) proportionality: template overhead for simple WRKs
**Plan ref:** §Phase 1, AC "user-review-capture.yaml template exists"

Requiring a `user-review-capture.yaml` artifact for every WRK adds a creation-time overhead that
scales poorly with Route A (simple) items. Route A WRKs are typically captured and executed
within a single session; the scope is unambiguous at capture time, and there is no multi-stage
planning cycle to drift from. For Route A items, the Stage 1 gate adds ceremony without
meaningfully reducing the retroactive approval risk (which primarily manifests at Stages 5, 7,
and 17 — none of which Route A WRKs routinely reach in complex form).

The plan does include a migration exemption for WRKs created before WRK-1035 deployment. However,
the route-proportionality question is not addressed for future items.

Recommended: allow the gate verifier to emit `n/a` (not FAIL) for Stage 1 when WRK frontmatter
carries `route: A` and the WRK was created after the deployment cutoff. Stage 1 hard-gate status
should be configurable in `stage-gate-policy.yaml` per route, matching the existing conditional-
pause model. This reduces bureaucratic load on the high-volume Route A tail without weakening the
gate on Route B/C where scope drift is the real risk.

---

### P2-MINOR — Phase 3 verifier deployed before Phase 1 gate artifact is used in production
**Plan ref:** §Phase 1 AC "Gate verifier check for user-review-capture.yaml presence at Stage 2
entry added (addressed in Phase 3 — cross-phase dependency noted)"; §Phase 3 gap 14-related check

The plan correctly notes this cross-phase dependency but resolves it by deferring the verifier
check to Phase 3. The risk is that Phase 1 and Phase 2 are implemented and committed, new WRKs
are created after deployment, and those WRKs advance to Stage 2 without a `user-review-capture.yaml`
before Phase 3 is live. There is a window of deployment where the required artifact is documented
but not yet machine-enforced.

Recommended: treat the gap-14 check in Phase 3 as a hard prerequisite for merging Phase 1.
The Phase 1 AC already acknowledges this dependency — make it a blocking dependency in the
Implementation Sequence rather than just a note. Alternatively, ship a minimal verifier stub
for gap 14 as part of Phase 1 so the gate is live from first deployment.

---

### P2-MINOR — 7-day live validation window: daily cron mechanism not fully specified
**Plan ref:** §Addendum — Stage 17 Live Validation Gate; §Phase 6

The audit master specifies that the 7-day validation window requires daily session log analysis
with results written to `assets/WRK-1035/evidence/live-validation/day-N.md`. The plan identifies
`comprehensive-learning` nightly pipeline as the vehicle but does not:
- Define which specific gate checks are run in the daily analysis (all 14 new checks? only
  HIGH-severity patterns 1–3?)
- Specify whether the daily result must be human-reviewed before the clock advances, or whether
  a clean automated run is sufficient to advance the day count
- Name the script that produces `day-N.md` (a new script? a `verify-gate-evidence.py --daily` mode?)
- Define what happens when a violation is found mid-window — is the fix itself gated by the same
  Stage 5/7/17 approval cycle, or does a simpler patch path exist?

Without this specificity, the 7-day window is an intention rather than a verifiable process.
Add a §Live Validation Protocol sub-section to Phase 6 that answers these four questions.

---

### P3-SUGGESTION — 985→400 line pruning for work-queue/SKILL.md: consider going further
**Plan ref:** §Phase 5, work-queue/SKILL.md target ≤400 lines

400 lines is the hard limit from coding-style.md but it is not necessarily the right target for
an agent-consumed skill. The meta-example in session-audit-master.md (§Meta-Example 2: Stage Order
Inversion at 62% Context) shows that a ~980-line skill loaded early in a session had negligible
effective weight at 62% context fill, causing a stage-ordering error. 400 lines halves the token
cost but does not eliminate the context-decay problem.

Phase 5 correctly identifies that artifact checklists enforced by scripts should be removed rather
than migrated. If that principle is applied consistently, the residual content (stage-contract
table condensed, routing rules, file placement map, cross-references) is likely achievable in
200–250 lines — well under 400. The 400-line ceiling should be treated as an upper bound, not a
target. A target of 250 lines for this skill would substantially reduce the context-decay risk
documented in the audit.

---

### P3-SUGGESTION — WRK-1040 nomenclature findings not fully integrated into Phase 4 scope
**Plan ref:** §Out of Scope "WRK-1040 Nomenclature canonicalisation"; WRK-1040-findings.md

WRK-1040 findings flag that `human_session` in stage contract YAMLs and `start_stage.py` is a
confusing term (a stage invocation type named after a WRK session concept). The finding
explicitly recommends this be captured as a discrete sub-task of WRK-1035 rather than a separate
WRK, yet the plan places the full rename in WRK-1040's scope and Phase 4 (which modifies
`start_stage.py`) makes no mention of the `human_session` → `human_gate` rename.

This creates a risk: Phase 4 extends `start_stage.py`'s WAIT instruction logic using the current
`human_session` invocation type match; WRK-1040 later renames the field; Phase 4 logic breaks
silently. Recommend either (a) including the `human_session` rename in Phase 4's pre-work scope
review and applying it in that pass, or (b) explicitly noting in Phase 4 that `start_stage.py`
must match `human_session` and this will be renamed by WRK-1040 — making the dependency
trackable.

---

### P3-SUGGESTION — Elapsed-time threshold inconsistency between plan and audit
**Plan ref:** §Phase 3, gap 3 "≥ 300s for all human-gate stages (5, 7, and 17)";
session-audit-master.md R-03 "≥ 60 seconds for plan stages (5, 7) and ≥ 300 seconds for Stage 17"

The audit master (R-03) specifies different thresholds: 60 seconds for Stages 5 and 7, 300 seconds
for Stage 17. The plan's Phase 3 gap 3 implementation spec uses 300 seconds uniformly for all
three. The session-audit-master.md §Stage 5 User Decisions confirms 300s for ALL hard-gate stages
as the resolved decision. However the discrepancy between R-03 as written and the user decision
means R-03 in the audit is now incorrect — it will mislead any future agent reading the audit
without reading the §Stage 5 User Decisions addendum.

Recommend adding a brief errata note to R-03 in `session-audit-master.md` (or striking through
"60 seconds" and noting "superseded by Stage 5 User Decision 1: 300s uniform"), so the canonical
source and the plan are consistent. This avoids a future agent implementing 60s for Stages 5/7
based on R-03 alone.

---

## What is solid

- Root-cause identification is accurate and specific: the audit traces retroactive approval
  fabrication, Codex bypass, and sentinel values to concrete tooling gaps (verifier checks
  presence not ordering, no wait enforcement before artifact write, claim-item.sh fallback to
  "unknown"). The plan addresses each root cause at the enforcement layer, not just the
  documentation layer.

- Phase sequencing is well-designed. Phase 1 (policy) → Phase 2 (skill contracts + shell
  guards) → Phase 3 (verifier hardening) → Phase 4 (stage scripts) → Phase 5 (pruning) →
  Phase 6 (orchestrator pattern) follows a logical dependency chain. The note that Phase 5/6
  SKILL.md edits must be applied in a single pass to avoid merge conflicts is a valuable
  operational detail.

- 47-test suite with named scenarios per gap is proportionate and complete. The test table maps
  each test ID to file, scenario, and expected outcome — reviewable without reading the
  implementation.

- The Phase 3 verifier modularisation decision (`checks/timestamp.py`, `checks/identity.py`,
  `checks/structure.py`) addresses the risk of pushing a 1208-line file further past readable
  size. Keeping the main file as a dispatcher at ≤150 lines is the correct architectural move.

- Migration exemption strategy (WRK-ID-based rather than time-based) is the right choice.
  Time-based cutoffs are vulnerable to timezone ambiguity; WRK-ID ordering is deterministic and
  already available in frontmatter.

- Out-of-scope delineation is disciplined. WRK-1039, WRK-1041, WRK-1042, WRK-1043, WRK-1044
  are explicitly named with rationale, preventing scope creep through the back door of vague
  "out of scope" statements.

- Phase 5 pruning rules are clear and non-ambiguous: redundant content deleted outright (not
  moved to references/); content converted to scripts replaced with a one-line reference note.
  This prevents references/ from becoming a dump directory.

- The Risks section is thorough. The Codex/ace-linux-1 deadlock risk, the sentinel rejection
  surfacing real failures, and the work-queue/SKILL.md cross-reference risk are all identified
  with concrete mitigations. The `--since-wrk` flag proposal for backward compatibility is
  pragmatic and avoids retroactive failure of archived WRKs.

- WRK-1040 nomenclature changes were completed in parallel and the findings document clearly
  separates what was fixed from what requires WRK-1035 coordination. The `human_session`
  breaking-change identification is accurate.
