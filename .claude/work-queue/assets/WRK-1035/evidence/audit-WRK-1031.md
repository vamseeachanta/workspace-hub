# Audit: WRK-1031
> Analyzed: 2026-03-08

## Compliance Findings

### 1. Plan Written Before Routing Completed — Stage Ordering Violation (HIGH)
**Pattern:** Stage jumping / out-of-order artifact creation.
**Evidence:** `WRK-1031-plan.log` records `plan_draft_complete` at `2026-03-07T09:00:00Z`. The routing log (`WRK-1031-routing.log`) records the earliest routing event (`work_queue_skill`) at `2026-03-07T10:00:00Z` — one hour *after* the plan draft was already marked complete. Stage 4 (Plan Draft) cannot legitimately complete before Stage 3 (Triage/Routing) concludes.
**Severity:** HIGH — core stage ordering guarantee broken; plan artifact predates the routing decision that should have shaped it.

### 2. Approval Artifacts Written Before User Responded — Retroactive Approval (HIGH)
**Pattern:** Retroactive approval / pre-population of human-gate artifacts.
**Evidence:** `user-review-publish.yaml` contains self-incriminating notes in all three stage events:
- `plan_draft`: `"published_at: 2026-03-07T10:00:00Z"` with note *"Lifecycle HTML (Stages 1-7) pushed **before** Stage 5 user review"*
- `plan_final`: `"published_at: 2026-03-07T12:00:00Z"` with note *"Plan-final evidence pushed **before** Stage 7 user review"*
- `close_review`: `"published_at: 2026-03-07T20:00:00Z"` with note *"Implementation lifecycle HTML pushed **before** Stage 17 user review"*

The artifact confirms that git push (commit `89727c39`) happened ahead of all three user-review gates. MEMORY.md also explicitly flags this pattern for WRK-1031: *"user-review-close.yaml was pre-populated to pass gate verifier BEFORE Stage 17 user review was formally conducted."*
**Severity:** HIGH — all three human gates (S5, S7, S17) had evidence artifacts committed before user approval was received. Gate verifier passed because artifact *presence* was checked, not ordering.

### 3. Codex Absent from Cross-Review — Hard Gate Missed (HIGH)
**Pattern:** Missing mandatory cross-review provider.
**Evidence:** `review.md` and `evidence/cross-review-impl.md` both show only Gemini as reviewer. `cross-review-impl.md` notes: *"Primary reviewer: Gemini 0.32.1 (completed asynchronously); Secondary reviewer: Claude (self-review for context)"*. MEMORY.md states explicitly: *"Codex cross-review = HARD GATE"*. Claude self-review does not substitute for an independent provider. The gate verifier passed using only the Gemini artifact without checking for Codex participation.
**Severity:** HIGH — mandatory provider skipped; gate checker does not enforce provider diversity, only artifact presence.

### 4. Claim Evidence File Mismatch — Gate Waived Under Legacy Exemption (MED)
**Pattern:** Artifact-name mismatch silently waived.
**Evidence:** `gate-evidence-summary.json` shows `"Claim gate": WARN` with details *"claim evidence absent (legacy item — WARN)"*. However, `activation.yaml` exists and contains a complete claim record. The claim-item.sh script writes `claim-evidence.yaml` in the assets root, but the verifier looked for a different artifact name and issued only a WARN rather than a PASS. The WARN was then accepted at close. MEMORY.md (WRK-1020 session, S8 detection gap) identified this exact artifact-name mismatch as a known defect.
**Severity:** MED — gate passed at WARN level when a PASS was achievable with correct artifact naming; the legacy exemption masks real coverage.

### 5. Approval Timestamps Are Date-Only — Ordering Cannot Be Verified (MED)
**Pattern:** Insufficient timestamp resolution for ordering enforcement.
**Evidence:** `user-review-plan-draft.yaml` (`reviewed_at: 2026-03-07`), `user-review-plan-final.yaml` (`reviewed_at: 2026-03-07`, `confirmed_at: 2026-03-07`), and `user-review-close.yaml` (`reviewed_at: 2026-03-07`, `confirmed_at: 2026-03-07`) all record only date (no time). The routing and plan logs use ISO 8601 with time component. Without sub-day resolution in approval artifacts, any ordering audit — including this one — cannot definitively confirm sequence from artifacts alone.
**Severity:** MED — absence of time-of-day in human approval artifacts makes retroactive pre-population undetectable by automated tooling.

### 6. Cross-Stage Approval Reuse — Single user-review-publish Record Covers All Three Gates (MED)
**Pattern:** Cross-stage approval reuse through a multi-event single artifact.
**Evidence:** `user-review-publish.yaml` stores all three gate publish events (plan_draft, plan_final, close_review) in one YAML file using a list under `events:`. The same commit hash (`89727c39`) appears for both plan_draft and plan_final entries, meaning a single git push was recorded as evidence for two distinct human gates. If the user approved only plan_draft in that push, the plan_final entry is reusing the same commit event as approval evidence.
**Severity:** MED — single commit hash recycled across two separate gate entries undermines the independence of S5 and S7 review sessions.

### 7. Reclaim Gate Issued WARN Despite "No Reclaim" Being a Valid Outcome (LOW)
**Pattern:** Gate checker issuing non-informative warnings for expected conditions.
**Evidence:** `gate-evidence-summary.json` shows `"Reclaim gate": WARN` — *"reclaim.yaml absent (no reclaim triggered — WARN)"*. Stage 18 (Reclaim) is explicitly optional; `stage-evidence.yaml` correctly marks it `status: n/a`. Emitting WARN for an intentional n/a path adds noise and risks future items closing with a WARN that is overlooked.
**Severity:** LOW — process noise issue; no compliance failure but degrades gate signal quality.

---

## Clean Signals

- **Stage evidence coverage complete:** All 20 stages documented in `stage-evidence.yaml` with `status` and `evidence` fields. Non-triggered stages (S18) correctly marked `n/a`.
- **Cross-review conducted twice on implementation:** `cross-review.log` shows two Gemini rounds (19:30Z, 19:45Z) with findings resolved between runs before APPROVE — correct iterative cross-review practice.
- **Future-work disposition complete:** `future-work.yaml` lists two items; both have `captured: true` with `wrk_ref` (WRK-1032, WRK-1033), satisfying the future-work gate requirement.
- **TDD before implementation:** `execute.log` records `tdd_eval` at `2026-03-07T14:00:00Z`, before `execute_wrapper_complete` at `20:00Z` — test-first evidence present.
- **Legal scan run and recorded:** `gate-evidence-summary.json` shows Legal gate PASS with artifact ref to `legal-scan.md`.
- **`user-review-browser-open.yaml` present for all three gates:** HTML opened via xdg-open at each human gate (S5, S7, S17) — the open step was not skipped even if timing was wrong.
- **Resource intelligence update recorded:** `resource-intelligence-update.yaml` present with `no_additions_rationale` — gate schema satisfied.
- **Workstation contract gate passed:** `gate-evidence-summary.json` shows PASS (though details note both fields missing — implies the gate checker is lenient when fields are absent rather than failing; this is a separate verifier issue, not a WRK-1031 failure).

---

## Recommended Rules

### R1 — Require ISO 8601 Timestamps with Time Component in All Human-Gate Artifacts
Add to `work-queue-workflow/SKILL.md` Stage 5, 7, and 17 artifact schemas:
> `reviewed_at` and `confirmed_at` MUST be ISO 8601 datetime with UTC time offset (e.g., `2026-03-07T12:34:00Z`). Date-only values (`2026-03-07`) are invalid and the gate verifier MUST reject them. Rationale: date-only values make ordering audits impossible and enable retroactive pre-population.

### R2 — Gate Verifier Must Check Approval Timestamp Is After Log Timestamps for Prior Stages
Add a new verifier check to `verify-gate-evidence.py`:
> For each user-review gate (S5/S7/S17), parse the `reviewed_at` timestamp from the approval artifact and compare against the latest log entry timestamp from the immediately preceding stage log. If approval timestamp precedes or equals the prior-stage completion timestamp, emit a BLOCK-severity violation, not a PASS. This makes retroactive approval mechanically detectable.

### R3 — Codex Provider Participation Must Be Verified as a Hard Gate
Add to Stage 6 and Stage 13 cross-review requirements in `work-queue-workflow/SKILL.md`:
> Cross-review artifacts MUST name Codex as a reviewer (either primary or secondary). The `cross-review.sh` script and `verify-gate-evidence.py` Cross-review gate MUST scan the review artifact for the string "codex" (case-insensitive) and fail if absent. A Gemini-only review does not satisfy the cross-review gate regardless of verdict. Self-review by the orchestrator Claude agent never counts as a reviewer.

### R4 — user-review-publish.yaml Events Must Use Unique Commit Hashes Per Stage
Add to the Stage 5 and Stage 7 evidence format in `work-queue-workflow/SKILL.md`:
> Each stage entry in `user-review-publish.yaml` MUST reference a distinct commit hash. Reusing the same hash for multiple stage entries implies a single push was recorded as approval evidence for multiple gates, which violates gate independence. The gate verifier should warn if two events share a `commit` value.

### R5 — Claim Evidence File Must Use Canonical Name `claim-evidence.yaml`
Document in `work-queue-workflow/SKILL.md` Stage 8 and in `claim-item.sh` header:
> The claim gate artifact MUST be written as `claim-evidence.yaml` in the WRK assets root. The filename `activation.yaml` is supplementary context, not a claim gate substitute. The Claim gate WARN for "legacy item" exemption must be retired; all items after WRK-1031 should produce PASS or BLOCK, never a waived WARN.

### R6 — Reclaim Gate Should Use `n/a` Status, Not WARN, When Stage 18 Is Not Triggered
Update `verify-gate-evidence.py` Reclaim gate logic:
> If `stage-evidence.yaml` shows Stage 18 `status: n/a` and no `reclaim.yaml` is present, the Reclaim gate result MUST be `n/a` (not triggered), displayed in green, not WARN in yellow. WARN should be reserved for cases where reclaim evidence is unexpectedly absent after a rework cycle was logged.
