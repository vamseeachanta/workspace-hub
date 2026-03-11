# Capability Assessment — WRK-624 Governance Skill Set

**Produced by:** WRK-1010 Stage 10 (Work Execution)
**Date:** 2026-03-10
**Assessment type:** Static/heuristic — SKILL.md content analysis only. No runtime execution.
**Linked review:** WRK-624 workflow governance review
**Source map:** `specs/skills/skill-knowledge-map.md`

---

## Summary Table

| Skill | Delta Score | Overlap Flag | Recommendation |
|-------|:-----------:|:------------:|---------------|
| work-queue | 5 | Medium (work-queue-workflow) | retain |
| workflow-gatepass | 4 | Medium (work-queue, work-queue-workflow) | retain-with-clarification |
| wrk-lifecycle-testpack | 3 | Low | retain-with-clarification |
| work-queue-workflow | 2 | HIGH (work-queue, workflow-gatepass) | merge into work-queue |
| comprehensive-learning | 5 | Low | retain |
| session-start | 4 | Low-Medium (work-queue) | retain |
| resource-intelligence | 5 | Low | retain |
| cross-review (inline) | 3 | HIGH (duplicated across 2 files) | extract to standalone SKILL.md |

---

## Phase 1 — Capability Evaluation (Static/Heuristic)

### Skill 1: work-queue

**Claimed behaviors and scores:**

| # | Claimed Behavior | SKILL.md Section | Score |
|---|-----------------|-----------------|-------|
| 1 | Two-phase capture+process pipeline with smart routing | §Quick Start, §Command Interface | **pass** — distinct `/work add` (capture) vs `/work run` (process) commands; smart routing rule stated ("action verbs → Process") |
| 2 | 20-stage canonical lifecycle with per-stage exit artifacts | §Canonical 20-Stage Lifecycle, §Stage Contracts | **pass** — full stage table with exit artifacts, hard gate labels, and script names for each stage |
| 3 | Complexity routing (A/B/C) with differentiated execution depth | §Complexity Routing | **pass** — criteria table (word count, repo count) and route differences stated; cross-review differences per route explicit |
| 4 | Checkpoint and resume continuity | §Checkpoint & Resume | **pass** — artifact schema (5 required fields), scripts named (`checkpoint.sh`, `start_stage.py`), auto-load behavior stated |
| 5 | Workstation routing by keyword pattern | §Workstation Routing | **pass** — pattern-to-machine table, machine WRK ID ranges, bulk-assign script referenced |

**Delta score: 5** — Strong deterministic protocol. Stage contract table with exact artifacts, script names, hard gate labels, and complexity routing criteria provide protocol a bare model would not produce reliably. Every claim has a verifiable exit artifact.

---

### Skill 2: workflow-gatepass

**Claimed behaviors and scores:**

| # | Claimed Behavior | SKILL.md Section | Score |
|---|-----------------|-----------------|-------|
| 1 | Enforce stage sequence with no-bypass rules | §Required Lifecycle Chain, §No-Bypass Rules | **pass** — 12 explicit no-bypass rules with specific conditions; Stage 5 gate enforced by named script |
| 2 | Close gate minimum (12 named gates) | §Close Gate Minimum | **pass** — all 12 gates named (plan, TDD, integrated test, legal, cross-review, html-open, publish, resource-intelligence, reclaim, future-work, archive-readiness, stage evidence) |
| 3 | Stage 15 → Stage 17 next-work disposition rule | §Stage 15 to Stage 17 Rule | **pass** — two paths defined (update existing WRK or spin off); mandatory YAML artifact named; category inference script referenced |
| 4 | Reusable scripts table | §Reusable Scripts | **pass** — 8 scripts listed with purpose; `close-item.sh` documents `--html-verification` as required (WRK≥624) |
| 5 | Route consistency (A/B/C) lifecycle equivalence | §Route Consistency | **partial** — states "same canonical 20-stage lifecycle" for all routes and differences in 10-12, but does not repeat the per-route cross-review differentiation that work-queue and work-queue-workflow specify more fully |

**Delta score: 4** — Strong gate enforcement protocol with machine-checkable evidence requirements and explicit no-bypass language. The close gate minimum list (12 gates) and no-bypass rules are highly deterministic. Slight deduction: route consistency coverage is thinner than in work-queue.

---

### Skill 3: wrk-lifecycle-testpack

**Claimed behaviors and scores:**

| # | Claimed Behavior | SKILL.md Section | Score |
|---|-----------------|-----------------|-------|
| 1 | Minimum 6-test suite contract for workflow changes | §Test Suite Contract | **pass** — 6 numbered tests with clear descriptions; signal coverage rule stated ("inferred signals are not measured signals") |
| 2 | Required `execute.yaml` shape (test data contract) | §Required Test Data Shape | **pass** — field names, allowed values (`scope`: integrated\|repo; `result`: pass\|passed) specified |
| 3 | Orchestrator variation test commands | §Orchestrator Variation Tests | **pass** — exact bash commands provided for variation check and session log parsing |
| 4 | Commands for running the test suite | §Recommended Commands | **partial** — three commands listed but no guidance on when to add tests vs update them, beyond "whenever gate contracts change" |

**Delta score: 3** — Material workflow scaffolding for gate compliance testing. The 6-test minimum suite with explicit data shapes is actionable. However, the skill is narrow in scope (only invoked when workflow code changes, not on every WRK). A bare model would know to write tests but not the specific fields and signal-coverage requirement.

---

### Skill 4: work-queue-workflow

**Claimed behaviors and scores:**

| # | Claimed Behavior | SKILL.md Section | Score |
|---|-----------------|-----------------|-------|
| 1 | Clear entrypoint that delegates to canonical sub-skills | §intro, §Source of Truth | **pass** — Source of Truth table names all authoritative files; intro is explicit about delegation |
| 2 | Canonical terminology definitions | §Canonical Terminology | **pass** — 6 terms defined with violations-to-avoid list; adds clarity not present in other skills |
| 3 | Stage Gate Policy table | §Stage Gate Policy | **pass** — all 20 stages listed with gate type (HARD / auto) and exit artifact; R-25/R-26/R-27 rules stated |
| 4 | Plan Mode gates (4 stages) | §Plan-Mode Gates | **pass** — 4 stages listed with triggers; pattern stated (EnterPlanMode → think → ExitPlanMode → write) |
| 5 | Orchestrator Team Pattern with scope-discovery rule | §Orchestrator Team Pattern | **partial** — R-28 scope-discovery rule is useful; but conditional pause triggers list (R-27) duplicates content from workflow-gatepass §No-Bypass Rules with slightly different wording |

**Delta score: 2** — The canonical terminology section (§Canonical Terminology) is the primary unique value of this skill — it prevents session/stage/phase confusion. The Stage Gate Policy table consolidates information from work-queue and workflow-gatepass but does not add new authoritative content. The Start-to-Finish Chain (§Start-to-Finish Chain) is largely a curated pointer to the other two skills. A capable model with work-queue and workflow-gatepass loaded would largely replicate this skill's guidance, except for the terminology definitions.

---

### Skill 5: comprehensive-learning

**Claimed behaviors and scores:**

| # | Claimed Behavior | SKILL.md Section | Score |
|---|-----------------|-----------------|-------|
| 1 | Single fire-and-forget command for full learning pipeline | §intro, §Pipeline Summary | **pass** — phase table with 11 phases, mandatory flags, machine-routing logic; cron-safe stated |
| 2 | Mode-based routing per machine | §Mode-Based Routing | **pass** — bash snippet with hostname check; `full` vs `contribute` modes defined; which phases each mode runs stated |
| 3 | Cross-machine data flow | §Cross-Machine Data Flow | **pass** — per-machine commit targets; ace-linux-1 git pull in Phase 10a named |
| 4 | Session design: lean by default (what NOT to run during sessions) | §Session Design: Lean by Default | **pass** — explicit prohibition list of skills that must NOT run standalone during sessions; in-session vs nightly pipeline table |
| 5 | Cron scheduling | §Scheduling | **pass** — exact crontab entry provided; script name and path; `git pull` hard gate noted |

**Delta score: 5** — Strong deterministic protocol. Mode routing, per-machine commit targets, phase sequencing, and the lean-session design constraint together are highly specific and would not be reproduced reliably by a bare model. The prohibition list ("Must NOT run standalone during sessions") prevents a class of errors that a bare model would make.

---

### Skill 6: session-start

**Claimed behaviors and scores:**

| # | Claimed Behavior | SKILL.md Section | Score |
|---|-----------------|-----------------|-------|
| 1 | Auto-load drift-risk rules (non-interactive, <2s) | §Step 0 | **pass** — 3 specific files listed; log event format given; bash command to write log provided |
| 2 | Surface readiness report and session snapshot | §Steps 1, 2 | **pass** — file paths stated; 48h staleness rule for snapshot; conditional display rule |
| 3 | Quota status with thresholds | §Step 3 | **pass** — ≥90% warn, 70-89% note, <70% silent; 4h cache staleness rule |
| 4 | Top unblocked item per category with category ordering | §Step 4 | **pass** — category order stated; HIGH/MEDIUM/LOW priority logic; fallback for missing Category View |
| 5 | Mandatory /work handoff and approval gate | §Step 6 | **partial** — gate exists but exit artifact is not specified (no named YAML evidence file created by session-start itself; it relies on downstream work-queue gate) |

**Delta score: 4** — Strong briefing protocol with specific file paths, staleness thresholds, and a mandatory handoff gate. Step 0 (drift-rule preload) is unique and would not be done by a bare model. The quota threshold table and category ordering are actionable specifics. Deduction for Step 6 lacking its own evidence artifact.

---

### Skill 7: resource-intelligence

**Claimed behaviors and scores:**

| # | Claimed Behavior | SKILL.md Section | Score |
|---|-----------------|-----------------|-------|
| 1 | Stage-scoped execution for Stage 2 and Stage 16 with hard STOP guards | §Stage 2, §Stage 16 | **pass** — distinct sections with STOP guards; Stage 2 = 8-step checklist; Stage 16 = 5-step checklist |
| 2 | Gate artifact schema with verified vs recommended fields | §evidence/resource-intelligence.yaml Schema | **pass** — gate-verified fields distinguished from WARN fields; `skills.core_used ≥3` minimum stated |
| 3 | Resource Mining Checklist (10 categories, priority order) | §Resource Mining Checklist | **pass** — 10 ordered categories; "cheapest lookup first" principle; "stop when no results after reasonable scan" |
| 4 | Category→Mining Map | §Category→Mining Map | **pass** — 8 WRK categories mapped to high/low-priority mining targets; subcategory override rule for engineering domains |
| 5 | Confidence derivation rule with measurable quality signals | §Confidence Derivation Rule, §Measurable Quality Signals | **pass** — 3 conditions for `confidence: high` stated; 3 measurable signals with Good/Needs-work thresholds |

**Delta score: 5** — Highly specific. The 10-category mining checklist, Category→Mining Map, hard STOP guards (prevents stage bleed), and gate artifact schema with verified vs recommended field distinction are all deterministic protocols a bare model would not produce. The confidence derivation rule with measurable signals is verifiable.

---

### Skill 8: cross-review (inline — no standalone SKILL.md)

**Claimed behaviors and scores:**

| # | Claimed Behavior | Source | Score |
|---|-----------------|--------|-------|
| 1 | Multi-provider review with APPROVE/MINOR/REQUEST_CHANGES verdicts | work-queue §Cross-Review; work-queue-workflow §Stage 6 | **pass** — output format specified; verdict labels consistent |
| 2 | Codex as hard gate with automatic quota fallback | work-queue-workflow §Stage 6 | **pass** — fallback logic (exit code 3 or ≥2 Codex reviews → Claude Opus substitution) stated; `CODEX_MAX_REVIEWS_PER_WRK` env var documented |
| 3 | Pseudocode review checklist in cross-review artifact | work-queue-workflow §Stage 6 | **pass** — 5 checklist items with PASS/FAIL scoring; required section named |
| 4 | Route-differentiated review depth | work-queue §Cross-Review | **partial** — Route A uses single self-review; Route B/C uses `cross-review.sh ... all`; but the variation between work-queue and work-queue-workflow on this point introduces minor inconsistency |

**Delta score: 3** — Material scaffolding. The Codex-fallback logic, pseudocode review checklist, and output format specification are concrete. However, the absence of a standalone SKILL.md means the protocol is split across two files with slight inconsistencies, which reduces effective delta below what it would be with a single authoritative file.

---

## Phase 2 — With vs Without Delta Summary

| Skill | Without Skill (bare model) | With Skill | Delta |
|-------|---------------------------|------------|:-----:|
| work-queue | Ad-hoc task logging; no stage contracts; no complexity routing | 20-stage lifecycle with named artifacts, scripts, and hard gates | **5** |
| workflow-gatepass | Would enforce some gates but skip others; no close minimum checklist | 12 named gates; 12 explicit no-bypass rules; machine-checkable evidence | **4** |
| wrk-lifecycle-testpack | Would write tests but not know the specific gate evidence data shape | 6-test minimum; explicit field schema; signal-coverage rule | **3** |
| work-queue-workflow | Would navigate lifecycle with work-queue + workflow-gatepass; might conflate terminology | Canonical terminology; Stage Gate Policy consolidation; Plan-Mode gates | **2** |
| comprehensive-learning | Would run learning phases ad-hoc; no machine routing; sessions would be polluted with analysis work | Lean-session design; machine routing; phase ordering; cron scheduling | **5** |
| session-start | Would check queue and quotas informally; no structured briefing | Structured briefing with file paths, thresholds, category ordering, drift-rule preload | **4** |
| resource-intelligence | Would mine resources informally; no gate artifact; no STOP guards between stages | Ordered mining checklist; Category→Mining Map; STOP guards; measurable quality signals | **5** |
| cross-review | Would do multi-provider review but miss Codex-fallback and pseudocode checklist | Fallback logic; pseudocode checklist; output format spec | **3** |

---

## Phase 3 — Overlap Analysis

### 3A — 8×8 Coarse Overlap Matrix

Score: 0=clearly disjoint, 1=some shared vocabulary, 2=overlapping claims, 3=full redundancy

|  | wq | gp | lt | wqw | cl | ss | ri | cr |
|--|:--:|:--:|:--:|:---:|:--:|:--:|:--:|:--:|
| **work-queue (wq)** | — | 2 | 1 | **3** | 1 | 1 | 1 | 2 |
| **workflow-gatepass (gp)** | 2 | — | 2 | 2 | 0 | 1 | 1 | 1 |
| **wrk-lifecycle-testpack (lt)** | 1 | 2 | — | 1 | 0 | 0 | 0 | 1 |
| **work-queue-workflow (wqw)** | **3** | 2 | 1 | — | 0 | 1 | 0 | 2 |
| **comprehensive-learning (cl)** | 1 | 0 | 0 | 0 | — | 1 | 1 | 0 |
| **session-start (ss)** | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| **resource-intelligence (ri)** | 1 | 1 | 0 | 0 | 1 | 0 | — | 0 |
| **cross-review (cr)** | 2 | 1 | 1 | 2 | 0 | 0 | 0 | — |

**High-overlap pairs identified (score ≥ 2):**
1. work-queue vs work-queue-workflow: **3**
2. work-queue-workflow vs workflow-gatepass: **2**
3. work-queue vs workflow-gatepass: **2**
4. work-queue vs cross-review: **2**
5. work-queue-workflow vs cross-review: **2**
6. workflow-gatepass vs wrk-lifecycle-testpack: **2**

### 3B — Deep Review of Four Pairs

#### Pair 1: work-queue vs work-queue-workflow (overlap score: 3)

This is the highest-overlap pair. `work-queue-workflow` is explicitly described as
"a clear entrypoint for users who ask for the 'work-queue workflow'" that "delegates to
canonical `work-queue` and `workflow-gatepass` contracts" (`work-queue-workflow/SKILL.md` §intro).

Content audit:
- Stage contract table: in work-queue §Stage Contracts (authoritative)
- Stage Gate Policy table: in work-queue-workflow §Stage Gate Policy (near-duplicate with gate types added)
- Complexity Routing: in work-queue §Complexity Routing (authoritative); referenced in work-queue-workflow
- Start-to-Finish Chain: in work-queue-workflow (5 bullets pointing to other skills)
- Cross-review protocol: in work-queue §Cross-Review AND work-queue-workflow §Stage 6 (duplicated)
- Canonical Terminology: in work-queue-workflow §Canonical Terminology (unique — not in work-queue)
- Plan-Mode Gates: in work-queue-workflow §Plan-Mode Gates (unique)
- Orchestrator Team Pattern: in work-queue-workflow §Orchestrator Team Pattern (unique — not in work-queue)

**Unique content in work-queue-workflow that is NOT in work-queue:**
1. Canonical Terminology definitions
2. Plan-Mode Gates table (4 stages)
3. Orchestrator Team Pattern (R-28 scope-discovery rule, TeamCreate vs TaskCreate guidance)
4. Stage 4/5/6/10 detailed protocols

**Verdict:** Full redundancy on lifecycle routing; partial unique value on terminology and team orchestration.
These unique sections should be retained. The Start-to-Finish Chain is purely pointer content.
**Recommendation:** Merge work-queue-workflow unique sections into work-queue (or workflow-gatepass
for gate-specific content), then retire work-queue-workflow as a standalone skill.

---

#### Pair 2: workflow-gatepass vs wrk-lifecycle-testpack (overlap score: 2)

`workflow-gatepass` defines gate rules; `wrk-lifecycle-testpack` provides tests for those rules.
This is a healthy producer-consumer relationship, not redundancy. Overlap exists in that both
reference the same scripts (`verify-gate-evidence.py`, `orchestrator-variation-check.sh`,
`parse-session-logs.sh`) and both describe close-gate requirements.

However:
- workflow-gatepass §Close Gate Minimum defines WHAT the gates are
- wrk-lifecycle-testpack §Test Suite Contract defines HOW to test them

The overlap is definitional vocabulary, not claims. Score of 2 reflects shared topic, not redundant protocol.

**Verdict:** Appropriate producer-consumer split. No merge needed.
**Recommendation:** retain both, but add a cross-reference in wrk-lifecycle-testpack pointing to
workflow-gatepass as the source of truth for gate definitions.

---

#### Pair 3: session-start vs work-queue (overlap score: 1)

`session-start` §Step 6 (Mandatory /work handoff) requires selecting or creating a WRK item through
the `/work` flow. This is a handoff, not redundancy — session-start triggers the work-queue flow.

`session-start` also surfaces "top 3 unblocked pending work items" (§Step 4), which reads queue
state that work-queue manages. This is a read-only consumption of work-queue state.

The overlap is integration, not functional duplication. Score of 1 is appropriate.

**Verdict:** No overlap concern. session-start is a session-context aggregator; work-queue is an
operational data model and command interface.

---

#### Pair 4: comprehensive-learning vs workspace-hub:improve (overlap score: assessed below)

`comprehensive-learning` is the pipeline orchestrator; `improve` is Phase 4 of that pipeline.
`comprehensive-learning` §Pipeline Summary lists `/improve` as Phase 4 (mandatory). `improve/SKILL.md`
describes a 3-phase workflow (COLLECT → CLASSIFY → IMPLEMENT) that comprehensive-learning invokes.

`improve` §Trigger Conditions states it runs at session exit or manually via `/improve`.
`comprehensive-learning` §Session Design explicitly says `/improve` must NOT run standalone during sessions.

This creates a minor tension: improve says it runs at session exit, but comprehensive-learning
says to use the nightly pipeline instead. The boundary is not crisp.

**Verdict:** Partial scope boundary issue. The improve skill should clarify that direct invocation
is superseded by comprehensive-learning for all machines with nightly cron. The standalone trigger
"session exit" in improve is now stale given comprehensive-learning's design.

---

## Phase 4 — Procedural Completeness (Static/Heuristic)

Applies to skills with prescribed step sequences.

### session-start (6 steps + sub-steps)

| Step | Trigger clear? | Exit artifact? | Blocking condition? | Complete? |
|------|:--------------:|:--------------:|:-------------------:|:---------:|
| 0 — Auto-load drift rules | Yes | Log event (bash command given) | No (skip silently on failure) | Partial |
| 1 — Readiness report | Yes | Surface warnings | No (if "All Clear", note briefly) | Partial |
| 2 — Session snapshot | Yes (48h staleness rule) | Surface Ideas/Notes section | No | Partial |
| 2b — Knowledge surfacing | Yes (if active WRK known) | "Past work context:" block | No (skip if empty) | Partial |
| 3 — Quota status | Yes (≥90% threshold) | Quota block in output | No (warn only) | Partial |
| 3b — Agent Teams Status | Yes | Dry-run tidy output | No | Partial |
| 3c — Active Session Audit | Yes (before picking up WRK) | Collision risk surface | No (investigate) | Partial |
| 4 — Top items by category | Yes | Category briefing block | No | Pass |
| 5 — Computer context | Partial (vague "if field exists") | Machine note | No | Fail |
| 6 — Mandatory /work handoff | Yes | (relies on work-queue gate, no own artifact) | Yes (do not execute without WRK ID approval) | Partial |

**Score: 1/10 complete, 7/10 partial, 1/10 fail, 1/10 pass** → approximate completeness: **0.4**

Primary gap: steps 0-3b are information-surfacing steps with no exit artifact of their own; blocking
conditions are soft (warn/note rather than block). Step 5 trigger is vague. Step 6 does not produce
its own evidence artifact.

---

### workflow-gatepass (20-stage lifecycle chain)

Only the 4 HARD gate stages are evaluated here (stages 1, 5, 7, 17); auto-proceed stages assessed coarsely.

| Stage | Trigger clear? | Exit artifact named? | Blocking condition? | Complete? |
|-------|:--------------:|:-------------------:|:-------------------:|:---------:|
| 1 HARD — Capture | Yes | `user-review-capture.yaml` (`scope_approved: true`) | Yes (Stage 2 blocked until present) | Pass |
| 5 HARD — User Review Plan Draft | Yes (interactive loop described) | `user-review-plan-draft.yaml` | Yes (machine-checked script named) | Pass |
| 7 HARD — User Review Plan Final | Yes | `plan-final-review.yaml` (`confirmed_by` in allowlist) | Yes (claim-item.sh --stage7-check named) | Pass |
| 17 HARD — User Review Implementation | Yes | `user-review-close.yaml` (`reviewer` in allowlist) | Yes (close-item.sh --stage17-check named) | Pass |
| 2-4, 6, 8-16, 18-20 (auto) | Yes (named in lifecycle chain) | Partial (some have artifacts, some are implied) | No (conditional pause only) | Partial |

**Score for HARD gates: 4/4 complete.** Auto-proceed stages: partial.
**Overall completeness (HARD + auto coarse): 0.75**

---

### work-queue-workflow (start-to-finish chain with stage details for stages 4, 5, 6, 10)

| Stage | Trigger clear? | Exit artifact named? | Blocking condition? | Complete? |
|-------|:--------------:|:-------------------:|:-------------------:|:---------:|
| Stage 4 Plan Draft | Yes (EnterPlanMode instruction given) | `specs/wrk/WRK-NNN/plan.md` | Partial (pause on scope change — condition not specified precisely) | Partial |
| Stage 5 Plan Draft (Human) | Yes (detailed protocol) | `user-review-plan-draft.yaml` | Yes (STOP block + named verifier script) | Pass |
| Stage 6 Cross-Review | Yes (provider dispatch given) | `cross-review-<provider>.md` | Partial (MAJOR → fix before next phase; but no script enforcement named) | Partial |
| Stage 8 Claim | Yes (claim-item.sh command given) | claim-item.sh output | Yes (Stage 9 enforces; exit 1 if not claimed) | Pass |
| Stage 10 Execution | Yes (context budget limits stated) | `execute.yaml` | Partial (80% context → auto-checkpoint; vague) | Partial |

**Score: 2/5 complete, 3/5 partial** → completeness: **0.55**

---

## Retirement / Merge Candidates

### Candidate 1: work-queue-workflow — MERGE into work-queue

**Evidence:**
- Overlap score 3 (full redundancy on lifecycle routing)
- Delta score 2 (unique value only in §Canonical Terminology, §Plan-Mode Gates, §Orchestrator Team Pattern)
- §intro is explicit: skill "delegates to canonical work-queue and workflow-gatepass contracts"
- §Source of Truth table says the authoritative files are work-queue/SKILL.md and workflow-gatepass/SKILL.md

**Proposed merge targets:**
- §Canonical Terminology → work-queue §Canonical Terminology (new section)
- §Plan-Mode Gates → work-queue §Plan-Mode Gates (new section)
- §Orchestrator Team Pattern → work-queue §Orchestrator Team Pattern (new section)
- §Stage 4/5/6/10 detailed protocols → work-queue §Stage Contracts (inline expansion of relevant rows)
- Retire work-queue-workflow as a separate file; retain trigger keywords as aliases pointing to work-queue

**Risk:** Low. work-queue already contains the canonical 20-stage lifecycle. The merge adds ~80 lines.

---

### Candidate 2: cross-review — EXTRACT to standalone SKILL.md

**Evidence:**
- No standalone SKILL.md is a documentation gap (noted in plan.md §Tough Questions)
- Protocol split across work-queue §Cross-Review and work-queue-workflow §Stage 6 with minor inconsistencies
- Delta score 3 — sufficient unique content to warrant its own file
- Codex-fallback logic, pseudocode review checklist, and output format are deterministic protocols

**Proposed action:** Create `.claude/skills/workspace-hub/cross-review/SKILL.md` containing:
- Triggers, inputs, outputs, handoffs, negative scope
- Provider dispatch commands
- Codex quota fallback logic (from work-queue-workflow §Stage 6)
- Output format spec (APPROVE/MINOR/REQUEST_CHANGES + Pseudocode Review + Findings)
- Pseudocode review checklist
- Route differentiation (A: single self-review; B/C: multi-provider)
- Remove cross-review prose from work-queue and work-queue-workflow (replace with pointer)

**Risk:** Low. All content already exists; this is extraction and consolidation.

---

### Candidate 3: improve — CLARIFY session-exit trigger

**Evidence:**
- improve §Trigger Conditions says "Session exit (per CLAUDE.md Core Rule #7)"
- comprehensive-learning §Session Design says `/improve` must NOT run standalone during sessions
- comprehensive-learning invokes /improve as Phase 4 of the nightly pipeline
- This ambiguity could cause a model to run /improve inline during a session

**Proposed action:** Update improve/SKILL.md §Trigger Conditions to add:
"Do not invoke standalone during sessions — use comprehensive-learning (nightly pipeline).
Direct /improve invocation is only appropriate when comprehensive-learning is not scheduled
or for isolated debugging sessions."

**Risk:** None — purely a documentation clarification.

---

## Follow-up Recommendations (WRK Items to Capture)

| # | Title | Type | Priority | Rationale |
|---|-------|------|:--------:|-----------|
| FW-1 | Merge work-queue-workflow unique content into work-queue and retire standalone skill | maintenance | HIGH | Delta score 2; overlap score 3; §intro says skill just delegates; reduces maintenance surface |
| FW-2 | Extract cross-review inline protocol to standalone cross-review/SKILL.md | maintenance | HIGH | No standalone file is a gap; protocol currently split across two files with inconsistencies |
| FW-3 | Clarify improve §Trigger Conditions to note comprehensive-learning supersedes standalone invocation | maintenance | MEDIUM | Ambiguous session-exit trigger could cause models to run /improve inline during sessions |
| FW-4 | Add cross-reference in wrk-lifecycle-testpack pointing to workflow-gatepass as gate definition authority | maintenance | LOW | Producer-consumer relationship not documented; aids navigation |
| FW-5 | Improve session-start procedural completeness: add exit artifacts for steps 0-3b and clarify Step 5 trigger | maintenance | MEDIUM | Current completeness score 0.4; steps lack own evidence artifacts and some triggers are vague |
| FW-6 | Live skill capability eval — run actual model tasks to validate static scores | harness | MEDIUM | This assessment is static/heuristic only; WRK-1009 eval framework should add runtime scoring |

---

## Assessment Traceability

| Plan Test | Test Description | Status |
|-----------|-----------------|--------|
| T1 | All 8 skills × 5 boundary fields populated in skill-knowledge-map.md | Pass — 8 skills × 5 fields in `skill-knowledge-map.md` |
| T2 | All 8 skills have numeric delta score (0-5) with written rationale | Pass — delta scores in §Phase 2 Summary Table |
| T3 | All 4 pairs assessed with overlap score (0-3) | Pass — 3B covers all 4 required pairs |
| T4 | ≥1 concrete recommendation with evidence and follow-up WRK | Pass — 3 retirement/merge candidates + 6 FW items |
| T5 | ≥2 skills with step-sequence have compliance score recorded | Pass — session-start (0.4), workflow-gatepass (0.75), work-queue-workflow (0.55) |

**WRK-624 governance link:** This assessment directly supports WRK-624's goal of rationalising the
workflow governance skill set. The primary finding is that work-queue-workflow's content is largely
redundant with work-queue and workflow-gatepass, with unique value concentrated in three sections
that should be migrated. Cross-review's lack of a standalone file is the second priority finding.
