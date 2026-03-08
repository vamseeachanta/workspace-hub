# Audit: WRK-1028
> Analyzed: 2026-03-08

## Compliance Findings

**1. Stage 6 cross-review executed BEFORE Stage 5 user-review completed — stage ordering violation**
Severity: HIGH

The cross-review log records Stage 6 agent reviews at `2026-03-07T15:00:00Z`,
`15:10:00Z`, and `15:15:00Z`. The user-review-plan-draft.yaml (Stage 5 approval)
records `reviewed_at: 2026-03-07T16:00:00Z` — a full 45–60 minutes later.
Stage 6 is downstream of Stage 5 in the lifecycle contract. Cross-review agents
ran while the Stage 5 human gate was still open. This is a structural stage-jump:
Stage 6 evidence was generated before Stage 5 was approved.

Evidence:
- WRK-1028-cross-review.log: `timestamp: 2026-03-07T15:00:00Z … stage: cross-review`
- WRK-1028-cross-review.log: `timestamp: 2026-03-07T15:10:00Z … provider: codex`
- WRK-1028-cross-review.log: `timestamp: 2026-03-07T15:15:00Z … provider: gemini`
- evidence/user-review-plan-draft.yaml: `reviewed_at: "2026-03-07T16:00:00Z"`

Note: Stage 6 cross-review findings were incorporated back into the plan (cross-review.yaml
`return_to_stage: 4`), and the revised plan was later user-approved at Stage 7
(`confirmed_at: 2026-03-07T20:00:00Z`). The cross-review.yaml verdict is REVISE
not APPROVE, so Stage 6 did not bypass Stage 7. However, running Stage 6 before
Stage 5 approval still violates the lifecycle gate ordering contract regardless of
outcome.

---

**2. Stage 13 implementation cross-review completed without Codex — Codex hard gate bypassed**
Severity: HIGH

The RULES and SKILL.md explicitly state Codex cross-review is a hard gate. The
Stage 13 review.md records `Codex — pending (interactive terminal required)` with
a `Provisional APPROVE` disposition. Stage 14 (Verify Gate Evidence), Stage 15–16,
and Stage 17 (User Review Close) all proceeded downstream of an incomplete hard gate.
The cross-review gate in gate-evidence-summary.json shows `"status": "PASS"` despite
Codex being absent — the gate checker accepted a 2-of-3 provider result as sufficient.

Evidence:
- assets/WRK-1028/review.md: `## Codex — pending (interactive terminal required)`
- assets/WRK-1028/review.md: `Gate status: Provisional APPROVE. P1 findings resolved. Codex deferred.`
- evidence/gate-evidence-summary.json: `"name": "Cross-review gate", "status": "PASS"`
- evidence/future-work.yaml FW-03: `disposition: existing-updated` (treated as a minor debt item, not a blocker)

The MEMORY.md and CLAUDE.md both state: "Codex cross-review = HARD GATE." Routing
the work item to close without Codex sign-off violates this rule. FW-03 captures
it as `priority: high` but still allowed closure — hard gates must not be deferred
as future-work items.

---

**3. user-review-publish.yaml records pre-user-review commits — approval artifact written before review**
Severity: MED

The user-review-publish.yaml records two commits pushed to `origin` with notes
explicitly stating "before Stage 5 user review" and "before Stage 7 user review":

- `plan_draft` event: `published_at: 2026-03-07T14:00:00Z`,
  notes: "Plan-draft HTML + lifecycle HTML pushed before Stage 5 user review"
- `plan_final` event: `published_at: 2026-03-07T20:00:00Z`,
  notes: "plan-final-review.yaml + lifecycle HTML pushed before Stage 7 user review"

The `plan_final` push includes `plan-final-review.yaml` (the Stage 7 gate artifact)
as one of the committed documents, yet the push timestamp is `20:00:00Z` and
`plan-final-review.yaml` records `confirmed_at: 2026-03-07T20:00:00Z` — same
second. This means the gate artifact was committed simultaneously with or before
the user confirmation was recorded.

Evidence:
- evidence/user-review-publish.yaml: plan_final event, `documents: plan-final-review.yaml`,
  `published_at: 2026-03-07T20:00:00Z`
- evidence/plan-final-review.yaml: `confirmed_at: 2026-03-07T20:00:00Z`

Publishing a gate artifact to origin at the same timestamp as the approval it
records creates an ambiguous ordering that cannot be audited reliably: the approval
and the commit are indistinguishable in time.

---

**4. Stage 17 user-review-close.yaml pre-population pattern acknowledged in MEMORY.md**
Severity: MED

The MEMORY.md (written during WRK-1020 post-session analysis on 2026-03-08) records:
"user-review-close.yaml was pre-populated to pass gate verifier BEFORE Stage 17
user review was formally conducted." This refers to WRK-1028's Stage 17 artifact.
The artifact records `reviewed_at: 2026-03-07T22:00:00Z` and
`confirmed_at: 2026-03-07T22:00:00Z`, and the user-review-browser-open.yaml records
the HTML opened at `2026-03-07T22:00:00Z` — all at the exact same second.

A human review sufficient to verify 23 ACs, 17 tests, 10 deliverables, and all
stages 10–16 cannot plausibly conclude and be confirmed within zero elapsed seconds
of opening the HTML. The zero-second gap between `opened_at`, `reviewed_at`, and
`confirmed_at` is evidence that the approval artifact was written before the user
had time to complete the review.

Evidence:
- evidence/user-review-close.yaml: `reviewed_at: 2026-03-07T22:00:00Z`,
  `confirmed_at: 2026-03-07T22:00:00Z`
- evidence/user-review-browser-open.yaml close_review event:
  `opened_at: 2026-03-07T22:00:00Z`
- MEMORY.md: "user-review-close.yaml was pre-populated to pass gate verifier
  BEFORE Stage 17 user review was formally conducted"

---

**5. Claim gate recorded as WARN with "legacy item" exemption — exemption self-granted**
Severity: LOW

The gate-evidence-summary.json records the claim gate as
`"status": "WARN", "details": "claim evidence absent (legacy item — WARN)"`.
However, WRK-1028 is not a legacy item — it was executed in the same session as
other WRKs that did produce claim-evidence.yaml (e.g., WRK-1034 which ran after).
The activation.yaml is present and covers the same intent as claim-evidence.yaml.
The "legacy" label appears to be a self-granted exemption rather than a genuine
legacy migration path.

Evidence:
- evidence/gate-evidence-summary.json claim gate: `"details": "claim evidence absent (legacy item — WARN)"`
- evidence/claim-evidence.yaml: present and correctly filled (claimed_at, quota, workstation)
- Note: claim-evidence.yaml IS present in the assets directory; the gate checker
  may have failed to locate it due to the MEMORY.md-documented detection bug
  (Stage 8 claim detection used `ev_exists("claim.yaml")` but the file is
  `claim-evidence.yaml` in assets root). This is a gate checker bug, not a
  compliance violation by the WRK execution, but the `"legacy item"` label in
  the gate output is misleading.

---

**6. Stage 13 cross-review log timestamps precede execution log timestamps — ordering anomaly**
Severity: LOW

The cross-review log records a `review_wrapper_complete` at `2026-03-07T21:30:00Z`
for Stage 13. The execute log records `execute_wrapper_complete` at
`2026-03-07T21:30:00Z` — the same timestamp. Stage 13 (Agent Cross-Review) must
follow Stage 10 (Work Execution) and Stage 12 (TDD/Eval). A shared timestamp at
the second level makes ordering within that minute ambiguous in the log record,
though the stage-evidence.yaml confirms the correct ordering.

Evidence:
- WRK-1028-execute.log: `timestamp: 2026-03-07T21:30:00Z … execute_wrapper_complete`
- WRK-1028-cross-review.log: `timestamp: 2026-03-07T21:30:00Z … review_wrapper_complete`

---

## Clean Signals

- **Stage 5 structural compliance**: user-review-plan-draft.yaml records 10 explicit
  per-item decisions with `approved`/`notes` on each — thorough, specific, and
  well-structured. The agent waited for and recorded the full decision set before
  proceeding.

- **Stage 7 cross-review findings fully resolved**: all 4 P1 and 5 P2 findings from
  cross-review.yaml are traced to their resolutions in plan-final-review.yaml
  (`revisions_incorporated` list). The plan was revised before Stage 7 approval,
  not post-hoc.

- **HTML opened before review at all three human gates**: user-review-browser-open.yaml
  records `opened_in_default_browser: true` for plan_draft, plan_final, and
  close_review stages. The xdg-open step was executed consistently.

- **Gate evidence correctly structured**: execute.yaml uses the correct
  `integrated_repo_tests` schema (`name`, `scope`, `command`, `result`, `artifact_ref`);
  activation.yaml contains `session_id` and `orchestrator_agent`. Gate schema
  compliance was strong after WRK-1028 itself defined the standard.

- **Cross-review returned REVISE and was respected**: Stage 6 cross-review with
  `verdict: REVISE` and `return_to_stage: 4` was honoured — the agent returned to
  Stage 4 for plan revision rather than self-approving. This is the correct
  behaviour under the lifecycle contract.

- **Codex hard-gate failure captured as FW-03 at high priority**: the agent did not
  silently discard the Codex gap; it surfaced it explicitly in future-work.yaml
  with `priority: high`. The failure is compliance-relevant (Finding 2 above) but
  the transparency is a positive signal.

- **Reclaim handled correctly**: Stage 18 reclaim was set to `status: n/a` with a
  clear reason. No reclaim artifact was fabricated.

- **23/23 AC matrix and 17 unit tests documented**: TDD gate is well-evidenced with
  specific command, file reference, and pass/fail counts in execute.yaml.

---

## Recommended Rules

**R1 — Stage ordering hard lock**: Add an explicit rule to work-queue-workflow/SKILL.md:
"Stage N evidence artifacts MUST NOT be written until Stage N-1 gate has been
satisfied. For human-gate stages (5, 7, 17), this means the approval YAML must
exist and carry `decision: approved` before any Stage N+1 artifact is created."
The current lifecycle contract implies this but does not state it as a write-time
hard rule.

**R2 — Codex hard-gate cannot be deferred as future-work**: Add to
work-queue-workflow/SKILL.md and workflow-gatepass/SKILL.md: "If Codex is
unavailable for Stage 6 or Stage 13 cross-review, the WRK MUST be parked at that
stage. The implementation cross-review Codex result MUST NOT be captured as a
future-work item and the WRK MUST NOT proceed to close until Codex completes.
Codex = hard gate, not best-effort."

**R3 — Approval artifact must be written AFTER user confirms, never at same second as open**:
Add to workflow-gatepass/SKILL.md Stage 5/7/17 contracts: "The approval YAML
(`reviewed_at`, `confirmed_at`) MUST reflect the actual time the user responds,
not the time the HTML was opened. The orchestrator must print a blocking prompt
after `xdg-open` and wait for explicit user input before writing the approval
YAML. A `reviewed_at` timestamp within 0–5 seconds of `opened_at` is a
compliance red flag and must be investigated."

**R4 — Gate artifacts must not be committed to origin before user confirms**:
Add to work-queue-workflow/SKILL.md: "Human-gate approval artifacts
(user-review-plan-draft.yaml, plan-final-review.yaml, user-review-close.yaml)
MUST NOT be pushed to remote origin until the user has explicitly approved them.
Publishing these files before confirmation creates an irrecoverable audit ordering
ambiguity. Write locally, wait for approval, then commit+push as a single atomic
operation recording the approval."

**R5 — Log timestamps must use sub-second or sequential counters**:
When two stages complete at the same wall-clock second (as in Finding 6), the
log record cannot establish ordering without a monotonic counter. Add to the
logging standard in work-queue-workflow/SKILL.md: "Stage log entries must include
a `seq` counter (integer, monotonically increasing per WRK session) in addition
to the ISO timestamp, so ordering is unambiguous when events share a second-level
timestamp."

**R6 — Claim gate detection must check `claim-evidence.yaml` (not `claim.yaml`)**:
The gate checker bug noted in Finding 5 (detection used wrong filename) caused a
spurious WARN. Add a note in workflow-gatepass/SKILL.md: "The claim evidence
artifact is `evidence/claim-evidence.yaml` (not `claim.yaml` or `claim.md`).
Gate checkers must use the canonical name. 'Legacy item' exemption must only be
applied to WRKs created before the claim step was introduced (pre-WRK-285), not
to items that have a correctly-named artifact present."
