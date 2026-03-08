# WRK-1034 — Gemini Independent Plan Draft
## Stage 7 and Stage 17 Hard Gate Enforcement

**Reviewer:** Gemini (independent planning agent)
**Date:** 2026-03-07
**WRK:** WRK-1034

---

## 1. What I Observed in the Stage 5 Implementation

After reading the code closely, Stage 5 enforcement has these structural properties:

- `check_stage5_evidence_gate()` in `verify-gate-evidence.py` is the canonical single-function checker
- It is activated via a separate `stage5-gate-config.yaml` with an `activation` enum (`disabled | canary_plan_cross_review | canary_claim_close | full`)
- The function returns a 3-value tuple: `(True, detail)` for pass, `(False, detail)` for predicate failure, `(None, detail)` for infrastructure failure
- Both `claim-item.sh` and `close-item.sh` call the checker via `--stage5-check WRK-NNN` CLI mode
- The bash wrappers treat exit 1 (predicate fail) and exit 2 (infra fail) as hard blocks — fail-closed
- There is a migration-exemption escape hatch: `evidence/stage5-migration-exemption.yaml` with `approved_by` validated against a `human_authority_allowlist`
- There is also an `emergency_bypass_until` operational override in the config
- The Stage 5 artifacts it checks are TWO documents: `user-review-common-draft.yaml` + `user-review-plan-draft.yaml`, with a cross-artifact `review_cycle_id` consistency check

Stage 7 and Stage 17 are structurally simpler: each requires only ONE artifact (`plan-final-review.yaml` and `user-review-close.yaml` respectively). Stage 17's artifact already exists as a gate in `check_user_review_close_gate()` inside `run_checks()` at the `close` phase — but it is not enforced as a hard-stop CLI gate the way Stage 5 is.

---

## 2. Key Observations and Non-Obvious Risks

### 2.1 Stage 17 artifact partially exists already

`check_user_review_close_gate()` already parses `user-review-close.yaml` and is called in `run_checks()` for phase=close. However:
- It is NOT exposed as a standalone `--stage17-check` CLI entrypoint
- It is NOT called from `close-item.sh` as a fail-closed pre-check
- The decision values accepted are `{approved, accepted, passed}` — the WRK-1034 spec says `approved|passed`, so `accepted` is an extra alias already in place

Risk: if we just add a `--stage17-check` CLI that delegates to the existing function, we get the right behavior. But we must NOT accidentally duplicate the logic — that creates divergence bugs. The canonical check should remain `check_user_review_close_gate()`, and the new CLI mode should call it directly.

### 2.2 Stage 7 artifact field mismatch

The WRK spec says `plan-final-review.yaml` has fields: `confirmed_by`, `confirmed_at`, `decision: passed`. Looking at the actual file in WRK-1034's evidence dir:

```
confirmed_by: ""
confirmed_at:
decision: ""
review_cycle_id: rc-1034-plan-final
```

There is also `check_plan_confirmation()` in the script, which reads the plan HTML artifact (not a YAML file) and checks for `confirmed_by`, `confirmed_at`, `decision: passed`. This is a different artifact (the HTML/MD plan final document) from `plan-final-review.yaml` (the YAML evidence artifact).

Risk: there are now potentially TWO confirmation mechanisms for Stage 7:
1. `check_plan_confirmation()` — checks the plan-final HTML/MD file body for an inline confirmation block
2. A new `check_stage7_evidence_gate()` — would check `evidence/plan-final-review.yaml`

The plan must clarify which is authoritative. My recommendation: `plan-final-review.yaml` should be the YAML evidence artifact (machine-readable, canonical), and `check_plan_confirmation()` on the plan-final HTML is a secondary human-readable signal. The hard gate should require the YAML artifact. If `check_plan_confirmation()` is already in `run_checks()` for `phase=claim`, then the Stage 7 gate should NOT re-validate the HTML — it should check the YAML. Do not conflate them.

### 2.3 The `confirmed_at` vs `reviewed_at` field name divergence

Stage 7 spec uses `confirmed_at`, Stage 17 spec uses `confirmed_at` (or possibly `reviewed_at` — the existing `check_user_review_close_gate()` checks `reviewed_at`, not `confirmed_at`). Before writing any checker, verify the canonical field name for each artifact to avoid baking in a mismatch that makes well-formed artifacts fail the gate.

Specifically: `check_user_review_close_gate()` at line 367 checks for `("reviewer", "reviewed_at", "decision")`. The WRK spec says Stage 17 fields are `reviewer`, `confirmed_at`, `decision`. These do not match. Either:
- The spec is wrong (use `reviewed_at`), OR
- The existing function has the wrong field name, OR
- Both field names should be accepted (union validation)

This must be resolved before writing tests. Using the wrong field name means every correctly authored artifact will fail the gate, or every malformed one will pass.

### 2.4 Three separate gate config files vs one shared config

The Stage 5 pattern uses a dedicated `stage5-gate-config.yaml`. The naive approach creates `stage7-gate-config.yaml` and `stage17-gate-config.yaml`. This means three separate config files, three separate activation states, three separate `human_authority_allowlist` copies.

Alternative: A single `user-review-gates-config.yaml` with per-stage activation:
```yaml
stages:
  5:
    activation: full
    gate_activation_commit: "..."
  7:
    activation: full
    gate_activation_commit: "..."
  17:
    activation: full
    gate_activation_commit: "..."
human_authority_allowlist: [user, vamsee]
emergency_bypass_until: ""
```

This approach has advantages: single allowlist to maintain, single emergency bypass, no risk of the three configs going out of sync on `human_authority_allowlist`. It also means updating Stage 5's config file, which requires its own change-control note (the file says changes must reference a WRK item — WRK-1034 is the right ref).

Downside: if we consolidate into a new file, we must update `_load_stage5_config()` to look at the new file or keep backward compat. This is additional migration surface.

Recommendation: Start with separate `stage7-gate-config.yaml` and `stage17-gate-config.yaml` that share the same schema as `stage5-gate-config.yaml`. Unification can be a follow-up WRK. This minimizes blast radius. The `human_authority_allowlist` values are identical to Stage 5 so copying them is low-risk.

### 2.5 Migration exemption for in-flight WRKs

Stage 5 has `evidence/stage5-migration-exemption.yaml` for legacy items that predated the gate. When Stage 7 and Stage 17 gates ship with `activation: full`, any WRK that is currently mid-lifecycle (past Stage 7 without a `plan-final-review.yaml`, or past Stage 17 without a `user-review-close.yaml`) will be immediately blocked.

The WRK spec says `activation: full` from day one. This is more aggressive than Stage 5's initial `disabled` state. The risk is real: active WRKs like WRK-1021, WRK-1019, WRK-1023 may be in mid-lifecycle. If Stage 7 gate is active and they lack `plan-final-review.yaml`, `claim-item.sh` will fail for them.

My recommendation: implement parallel migration exemption files `stage7-migration-exemption.yaml` and `stage17-migration-exemption.yaml` with the same schema as the Stage 5 exemption. This gives the user an escape hatch for in-flight WRKs without having to disable the gate globally.

### 2.6 The `--stage7-check` entrypoint must NOT be called in `close-item.sh`

Stage 7 check (plan-final approval) guards Stage 8+ (cross-review, execute, etc.). It logically belongs as a pre-check for `claim-item.sh` (not `close-item.sh`). Stage 17 check belongs as a pre-check for `close-item.sh`. The assignment of gates to scripts is:

- `claim-item.sh`: already checks Stage 5; must also check Stage 7 (plan-final approved before claiming implementation)
- `close-item.sh`: already checks Stage 5; must also check Stage 17 (user review of implementation before closing)

However, there is a sequencing question: if Stage 5 gate blocks and Stage 7 gate also blocks, the agent gets TWO error messages from the same script. The messages must be distinct and actionable, not just "stage N gate failed."

### 2.7 The `--stage5-check` flag name coupling

The existing bash scripts hardcode `--stage5-check` as the CLI flag. If Stage 7 and Stage 17 follow the same pattern, we'll have three different CLI flags: `--stage5-check`, `--stage7-check`, `--stage17-check`. This is fine for now. The alternative would be `--stage-check 5/7/17` but that requires changing existing callers of `--stage5-check`, which breaks backward compatibility. Stick with per-stage flags.

### 2.8 `plan-final-review.yaml` field for `confirmed_by` — human identity validation

Stage 5 validates that the `approved_by` field in exemption artifacts is in the `human_authority_allowlist`. Should Stage 7's gate validate that `confirmed_by` in `plan-final-review.yaml` is in the allowlist? Yes — this is the entire point of the gate. An AI agent writing its own `confirmed_by: claude` would bypass the gate's intent. The checker must validate the identity.

Similarly for Stage 17: `reviewer` in `user-review-close.yaml` must be in the allowlist.

This is NOT currently done in `check_user_review_close_gate()` — it only checks that the field is non-empty. This is a pre-existing gap that WRK-1034 should close for Stage 17. Stage 7 should enforce it from the start.

### 2.9 Empty string vs missing field in YAML

In `plan-final-review.yaml` (WRK-1034's own artifact): `confirmed_by: ""` (empty string). The current `check_user_review_close_gate()` implementation checks `not str(data.get(key, "")).strip()` — this catches both missing and empty-string cases correctly. Stage 7 checker must use the same pattern.

### 2.10 `review_cycle_id` field

`plan-final-review.yaml` has a `review_cycle_id` field. Should Stage 7 gate validate it? The Stage 5 pattern uses `review_cycle_id` to check cross-artifact consistency across TWO artifacts. Stage 7 only has one artifact, so there is nothing to cross-check. The field can be recorded for audit but should not be a hard validation requirement. Do NOT add a gate that blocks because `review_cycle_id` is empty — it adds no security value for a single-artifact check.

---

## 3. Proposed Implementation Approach

### Phase A: Python checker functions (verify-gate-evidence.py)

1. Add `_load_stage7_config(workspace_root)` — mirrors `_load_stage5_config()`, reads `stage7-gate-config.yaml`
2. Add `check_stage7_evidence_gate(wrk_id, assets_dir, workspace_root)`:
   - Load and check `stage7-gate-config.yaml` activation
   - Check `evidence/stage7-migration-exemption.yaml` if present
   - Check `evidence/plan-final-review.yaml` for fields: `confirmed_by` (non-empty, in allowlist), `confirmed_at` (non-empty), `decision == "passed"`
   - Return `(True/False/None, detail)` tri-state
3. Add `_load_stage17_config(workspace_root)` — mirrors above, reads `stage17-gate-config.yaml`
4. Add `check_stage17_evidence_gate(wrk_id, assets_dir, workspace_root)`:
   - Load and check `stage17-gate-config.yaml` activation
   - Check `evidence/stage17-migration-exemption.yaml` if present
   - Delegate field checks to the existing `check_user_review_close_gate()` logic, PLUS add allowlist validation for the `reviewer` field
   - Return tri-state
5. Add `_run_stage7_check(args)` CLI handler — mirrors `_run_stage5_check()`
6. Add `_run_stage17_check(args)` CLI handler
7. Update `main()` to dispatch `--stage7-check` and `--stage17-check`

Note: do NOT modify `check_user_review_close_gate()` directly since it is called in `run_checks()` for regular gate summary. Instead, add allowlist-aware logic only in the new `check_stage17_evidence_gate()` wrapper.

### Phase B: Gate config YAML files

Create `scripts/work-queue/stage7-gate-config.yaml`:
- Same schema as `stage5-gate-config.yaml`
- `owned_by_wrk: WRK-1034`
- `activation: full` (immediate enforcement per spec)
- Same `human_authority_allowlist: [user, vamsee]`
- `gate_activation_commit: ""` (to be filled at first live activation)

Create `scripts/work-queue/stage17-gate-config.yaml` — same structure.

Update `stage5-gate-config.yaml`:
- `last_updated` and `change_note` to reference WRK-1034 (per the file's own change-control requirement)
- `activation` remains as-is (do not change Stage 5's activation state in this WRK)

### Phase C: Shell script guards

In `claim-item.sh` (after the Stage 5 check block, before quota check):
- Add Stage 7 guard with same pattern: check for `--stage7-check`, capture exit code, fail-closed on 1 or 2
- Error messages must be specific: "Complete Stage 7 plan-final review and evidence before claiming"

In `close-item.sh` (after the Stage 5 check block):
- Add Stage 17 guard with same pattern
- Error messages: "Complete Stage 17 implementation review and evidence before closing"

### Phase D: SKILL.md updates

The SKILL.md for `work-queue-workflow` needs:
- HARD GATE notices at Stage 7 and Stage 17 sections (matching the style of any existing Stage 5 notice)
- Exit checklist for Stage 7: must have `evidence/plan-final-review.yaml` with `confirmed_by` (human), `confirmed_at`, `decision: passed`
- Exit checklist for Stage 17: must have `evidence/user-review-close.yaml` with `reviewer` (human), `confirmed_at`/`reviewed_at` (resolve the field name question first), `decision: approved|passed`

### Phase E: Tests (10+ required)

Proposed test cases:

1. Stage 7 gate passes when `plan-final-review.yaml` has all required fields with valid human identity
2. Stage 7 gate fails when `plan-final-review.yaml` is missing entirely
3. Stage 7 gate fails when `confirmed_by` is empty string
4. Stage 7 gate fails when `confirmed_by` is an agent identity not in allowlist
5. Stage 7 gate fails when `decision` is not "passed" (e.g., "pending")
6. Stage 7 gate passes when `stage7-migration-exemption.yaml` is present with valid `approved_by`
7. Stage 7 gate fails when migration exemption has `approved_by` not in allowlist
8. Stage 17 gate passes when `user-review-close.yaml` has all valid fields
9. Stage 17 gate fails when `user-review-close.yaml` is missing
10. Stage 17 gate fails when `reviewer` is an agent identity not in allowlist
11. Stage 17 gate fails when `decision` is not in `{approved, passed}` (verify `accepted` handling)
12. Stage 7 gate returns `(True, ...)` when `stage7-gate-config.yaml` has `activation: disabled`
13. Stage 7 gate returns `(None, ...)` infrastructure failure when config file is absent (fail-closed)

---

## 4. Concerns About "Mirror Stage 5" Approach

The naive copy-paste approach would miss:

1. **The existing `check_user_review_close_gate()` function** — it already handles Stage 17 artifact parsing. Ignoring it and writing duplicate logic creates two different implementations that can silently diverge.

2. **The allowlist validation gap** — Stage 5 enforces allowlist at the exemption level. Stages 7 and 17 need it at the primary artifact level (the `confirmed_by`/`reviewer` fields). Simply mirroring Stage 5 would omit this.

3. **The field name discrepancy** (`confirmed_at` vs `reviewed_at` in Stage 17) — a naive copy would pick one without resolving which the existing artifact uses.

4. **The dual-artifact cross-check in Stage 5** — Stage 5 checks two artifacts and cross-validates `review_cycle_id`. Stages 7 and 17 are single-artifact, so the cross-check is not applicable. A naive mirror would add a spurious cross-artifact check.

5. **Migration exemption for in-flight WRKs** — Stage 5 shipped with `activation: disabled`. Shipping Stages 7 and 17 with `activation: full` without migration exemption support would block all currently active WRKs.

6. **The `plan-final-review.yaml` vs plan-final HTML confusion** — `check_plan_confirmation()` already reads inline YAML blocks in the HTML/MD plan file. The new Stage 7 checker must NOT call `check_plan_confirmation()` to avoid double-counting or conflating two different artifacts.

---

## 5. Open Questions for User Approval

1. Should the Stage 7 gate validate that `confirmed_by` is in `human_authority_allowlist`? (Recommended: yes — otherwise an agent can self-confirm.)

2. Should Stage 17's `check_stage17_evidence_gate()` add allowlist validation for `reviewer` that the existing `check_user_review_close_gate()` lacks? (Recommended: yes — add it only in the new hard-gate path, not in the existing `run_checks()` path to avoid breaking existing close-phase reports for items that lack reviewer identity.)

3. Canonical field name for Stage 17: is it `confirmed_at` (spec) or `reviewed_at` (existing function)? Should both be accepted?

4. Single consolidated gate config file vs three separate files? (Recommendation above: separate files for now.)

5. Should `activation: full` for Stage 7 and Stage 17 be effective immediately, or should it start as `canary_claim_close` to shake out in-flight WRKs first?

---

## 6. Risk Summary

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Field name mismatch blocks valid artifacts | Medium | High | Resolve `confirmed_at` vs `reviewed_at` before writing tests |
| In-flight WRKs immediately blocked by `activation: full` | High | Medium | Add migration exemption support; consider canary mode first |
| Duplicate logic for Stage 17 vs existing close gate | Medium | Medium | Delegate to existing function, add allowlist check as wrapper |
| Agent self-confirmation via `confirmed_by: claude` | High (intentional attack) | High | Enforce `human_authority_allowlist` on primary artifact fields |
| Stage 5 config `change_note` not updated | Low | Low | Update as part of WRK-1034 change control |
