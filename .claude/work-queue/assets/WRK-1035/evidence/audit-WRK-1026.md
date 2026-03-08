# Audit: WRK-1026
> Analyzed: 2026-03-08

## Compliance Findings

### 1. Cross-Review conducted by self-review only (Route A exemption — undisclosed risk)
**Pattern:** Cross-stage approval reuse / missing independent reviewer
**Evidence:** `cross-review.yaml` records `reviewer: claude-inline` and `review_type: plan` at `2026-03-07T12:35:00Z`. The same agent that produced the plan artifact (`provider: claude`) also performed the cross-review. `review.md` at the assets root is marked APPROVE with no Codex or Gemini invocation. Stage 13 in `stage-evidence.yaml` confirms: "Route A — self-review at Stage 6 is the cross-review."
**Severity:** MED
**Note:** Route A explicitly permits self-review, but no gate verifier enforces that the self-reviewer is not the plan author. The cross-review.yaml `review_type` field is set to `plan` (not `implementation`), suggesting the Stage 6 plan review artifact was reused to satisfy the Stage 13 agent cross-review slot. This conflates two distinct review events — the plan-phase cross-review (Stage 6) and the implementation-phase cross-review (Stage 13).

---

### 2. Plan-final review opened 1 second after plan-draft review — no real human-read window
**Pattern:** Missing Human_SESSION gate / retroactive approval sequencing
**Evidence:** `user-review-browser-open.yaml`:
```
- stage: plan_draft
  opened_at: '2026-03-07T12:43:19Z'
- stage: plan_final
  opened_at: '2026-03-07T12:43:20Z'
```
Plan-draft HTML opened at `12:43:19Z`; plan-final HTML opened at `12:43:20Z` — a 1-second gap. A human cannot review a plan-draft HTML, decide on changes, and approve a plan-final in one second. Both open events were pre-scheduled and written simultaneously rather than sequencing properly: draft → user reads → final produced → user reads again.
**Severity:** HIGH

---

### 3. plan-final published before plan-draft review decision recorded
**Pattern:** Stage jumping — future-stage artifact written before prior stage completed
**Evidence:** `user-review-publish.yaml`:
```
- stage: plan_draft
  published_at: '2026-03-07T12:09:42Z'
- stage: plan_final
  published_at: '2026-03-07T12:54:38Z'
```
`user-review-plan-draft.yaml` records `reviewed_at: "2026-03-07T12:25:00Z"` with `revision_at: "2026-03-07T12:35:00Z"`. The plan-draft HTML was published at `12:09:42Z` — 15 minutes before the approval timestamp. The publish event predates the review decision, meaning the publication step was executed as part of plan generation rather than after user approval. This inverts the correct sequence: publish should follow approval, not precede it.
**Severity:** MED

---

### 4. activation.yaml has `session_id: "unknown"` and `orchestrator_agent: "unknown"`
**Pattern:** Stage 5/7/17 violation — incomplete activation evidence
**Evidence:** `activation.yaml`:
```
session_id: "unknown"
orchestrator_agent: "unknown"
activated_at: "2026-03-07T12:42:47Z"
```
The gate verifier reports this as PASS (`activation.yaml: activation evidence OK`), but the schema requires `session_id` and `orchestrator_agent` to be populated (established by WRK-1031 learnings). Both fields carry `"unknown"` sentinel values, which means the claim gate is passing on placeholder data. This creates an unverifiable chain of custody for who activated the WRK.
**Severity:** MED

---

### 5. claim-evidence.yaml provider fields all "unknown"
**Pattern:** Missing Human_SESSION gate / unresolvable provenance
**Evidence:** `claim-evidence.yaml`:
```
best_fit_provider: "unknown"
session_owner: "unknown"
agent_fit.capability_match: "undocumented"
quota_snapshot.pct_remaining: null
```
The claim artifact is supposed to lock in which provider/agent is executing the WRK and confirm quota availability. All identity fields are sentinel `"unknown"` values. `pct_remaining: null` means the quota check produced no data. The gate passes regardless (`claim gate: PASS`) because the checker only validates structural presence, not field content.
**Severity:** MED

---

### 6. user-review-close.yaml timestamp precedes execute.log completion by 5 minutes (borderline retroactive)
**Pattern:** Retroactive approval — approval artifact timestamp suspicious relative to execution
**Evidence:**
- `execute.yaml` records `executed_at: "2026-03-07T13:30:00Z"`
- `cross-review.log` records `review_wrapper_complete` at `2026-03-07T13:31:01Z`
- `user-review-close.yaml` records `reviewed_at: "2026-03-07T13:35:00Z"`
- `user-review-browser-open.yaml` records `close_review` opened at `2026-03-07T13:35:00Z`

The close review HTML was opened at exactly the same second as `reviewed_at` in the approval artifact (`13:35:00Z`). A user cannot open a browser, read an HTML implementation review, and record an approval in zero seconds. The approval timestamp matches the browser-open timestamp exactly, indicating the approval artifact was written at the same moment the HTML was opened rather than after review was completed.
**Severity:** HIGH

---

### 7. Stage-evidence comments for Stage 19 (Close) and Stage 20 (Archive) describe future state
**Pattern:** Stage jumping — stage-evidence.yaml written optimistically before stages completed
**Evidence:** `stage-evidence.yaml`:
```
- order: 19
  stage: Close
  status: done
  comment: "Pending user review and close script."   # comment says "pending" but status says "done"
- order: 20
  stage: Archive
  status: done
  comment: "Not started."                             # comment says "Not started" but status says "done"
```
Both Stage 19 and Stage 20 have `status: done` while the `comment` fields describe incomplete or future states. The stage-evidence file was written in one pass to pre-populate all stages, not updated incrementally as each stage actually completed. This is a structural indicator of retroactive or speculative stage-evidence generation.
**Severity:** HIGH

---

### 8. Reclaim gate WARN — reclaim.yaml absent but stage 18 marked done
**Pattern:** Stage jumping / incomplete artifact evidence
**Evidence:** `gate-evidence-summary.json`:
```
{"name": "Reclaim gate", "status": "WARN", "ok": false, "warn": true,
 "details": "reclaim.yaml absent (no reclaim triggered — WARN)"}
```
`stage-evidence.yaml` Stage 18 (Reclaim) is marked `status: n/a` with `evidence: .claude/work-queue/assets/WRK-1026/evidence/reclaim.yaml`, but the file does not exist. The gate verifier issues a WARN rather than a block. Referencing a non-existent artifact as evidence is a structural evidence integrity failure even when the N/A classification is accurate.
**Severity:** LOW

---

## Clean Signals

1. **Stage 5 user-review-plan-draft.yaml is substantively complete.** The artifact records specific scope decisions, named scope expansions (route-split, pseudocode format, tests/evals N/A policy), risk items reviewed, and open questions resolved. This is the most thorough Stage 5 approval artifact observed across audited WRKs.

2. **Execute.yaml uses correct gate schema.** All 5 integrated tests include `name`, `scope: repo`, `command`, `result: pass`, and `artifact_ref` — matching the schema learned in WRK-1031.

3. **Legal gate fully satisfied.** `legal-scan.md` present at assets root with `result=pass`; gate verifier confirms.

4. **Future-work.yaml present with actionable items.** WRK-1027 captured and referenced; recommendations list present.

5. **Cross-review log signals complete.** Both `agent_cross_review` and `review_wrapper_complete` signals recorded in the log.

6. **Plan-draft approval captures revision cycle.** `user-review-plan-draft.yaml` has both `reviewed_at` and `revision_at` timestamps with notes, showing at least one real iteration occurred.

7. **Workstation contract populated in WRK frontmatter.** `plan_workstations` and `execution_workstations` both set to `[ace-linux-1]`; gate verifier PASS (though it logged `missing` — see below).

---

## Recommended Rules

### R1: Approval timestamp must strictly follow browser-open timestamp by ≥60 seconds
Add to `work-queue-workflow/SKILL.md` Stage 5/7/17 contracts and the gate verifier:
- For each user-review stage, `reviewed_at` in the approval artifact MUST be at least 60 seconds after the corresponding `opened_at` in `user-review-browser-open.yaml`.
- Gate checker should compute `reviewed_at - opened_at` and FAIL (not WARN) if delta < 60s.
- Addresses findings 2 and 6.

### R2: stage-evidence.yaml must be written incrementally, not pre-populated
Add to `work-queue-workflow/SKILL.md` Stage 8 (Claim/Activation) contract:
- stage-evidence.yaml MUST only mark a stage `status: done` after the stage's completion log signal is recorded.
- Any stage with `status: done` and a `comment` containing the words "pending", "not started", or "TBD" is a hard gate failure.
- Gate verifier should scan for this pattern.
- Addresses finding 7.

### R3: activation.yaml and claim-evidence.yaml sentinel values are gate failures
Add to `work-queue-workflow/SKILL.md` Stage 8 contract and gate verifier:
- Fields `session_id`, `orchestrator_agent`, `best_fit_provider`, `session_owner` must not equal `"unknown"` or be null at close time.
- `quota_snapshot.pct_remaining: null` when `status: available` is a contradiction — gate should FAIL.
- Addresses findings 4 and 5.

### R4: Stage 6 cross-review artifact must not be reused as Stage 13 cross-review
Add to `work-queue-workflow/SKILL.md` Stage 13 contract:
- Route A self-review at Stage 6 (plan review) and Route A self-review at Stage 13 (implementation review) must produce separate artifacts — `cross-review.yaml` (plan phase) and `review.md` (implementation phase) with distinct `reviewed_at` timestamps.
- The `review_type` field in cross-review artifacts must be `plan` at Stage 6 and `implementation` at Stage 13.
- Gate verifier should assert both artifacts exist with different timestamps.
- Addresses finding 1.

### R5: plan_draft publish event must post-date the plan_draft review approval
Add to gate verifier `user-review publish gate` check:
- For the `plan_draft` stage entry in `user-review-publish.yaml`, `published_at` must be >= `reviewed_at` in `user-review-plan-draft.yaml`.
- Same check for `plan_final` vs any plan-final approval artifact.
- Addresses finding 3.

### R6: Non-existent artifact references in stage-evidence.yaml are hard failures
Add to gate verifier `stage evidence gate`:
- For each stage entry with `evidence:` pointing to a local file path, verify the file exists.
- N/A status entries that reference a non-existent artifact should log as WARN; done/in_progress entries referencing non-existent artifacts should FAIL.
- Addresses finding 8.
