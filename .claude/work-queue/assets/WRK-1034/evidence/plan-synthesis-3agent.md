# WRK-1034 — 3-Agent Plan Synthesis
**Route B Stage 5 exit artifact — all 3 agents independently planned**

| Agent | Draft file | Key contribution |
|-------|-----------|-----------------|
| Claude | (WRK-1034.md plan section) | Phase 1/2 structure; field names from micro-skill |
| Codex | `evidence/plan-codex-draft.md` | Generic loader + `_validate_exemption()` helper; 17 tests; detailed pseudocode |
| Gemini | `evidence/plan-gemini-draft.md` | Risk analysis; existing soft-gate interaction; union timestamp check; migration exemptions |

---

## Convergence Points (all 3 agree)

- Mirror Stage 5: separate config files per stage, `(True|False|None, detail)` return, exit 0/1/2
- Stage 7 artifact: `evidence/plan-final-review.yaml` — fields `confirmed_by`, `confirmed_at`, `decision=passed`
- Stage 17 artifact: `evidence/user-review-close.yaml` — fields `reviewer`, `confirmed_at|reviewed_at`, `decision=approved|accepted|passed`
- `claim-item.sh` gets Stage 7 guard; `close-item.sh` gets Stage 17 guard (after Stage 5 blocks)
- SKILL.md HARD GATE notices + exit checklists for Stages 7 and 17
- `activation: full` for both new gates

---

## Synthesis Decisions (resolved conflicts)

### D1: Config loader — Codex approach wins
Use `_load_gate_config(workspace_root, filename)` (filename-based, most flexible).
`_load_stage5_config()` becomes a thin wrapper calling it with `"stage5-gate-config.yaml"`.
Avoids triplicating the loader logic.

### D2: `_validate_exemption()` helper — add it (Codex proposal)
Extract exemption-checking logic into `_validate_exemption(exemption_path, wrk_id, human_allowlist)`.
Refactor Stage 5's inline exemption block to use it. Both Stage 7 and Stage 17 share the helper.

### D3: Stage 17 timestamp field — union check (both `reviewed_at` and `confirmed_at`)
Production `user-review-close.yaml` artifacts (WRK-1029, WRK-1031) have BOTH fields.
The existing soft gate (`check_user_review_close_gate()`) checks `reviewed_at`.
Resolution: hard gate checks `confirmed_at` first, falls back to `reviewed_at`. Either non-empty = pass.
This is backward-compatible with all existing artifacts.

### D4: Allowlist enforcement on primary artifact — yes (Codex + Gemini both flag this)
`confirmed_by` in `plan-final-review.yaml` must be in `human_authority_allowlist`.
`reviewer` in `user-review-close.yaml` must be in `human_authority_allowlist`.
An agent writing `confirmed_by: claude` must fail the gate — this is the entire enforcement point.

### D5: Migration exemption files — add support for Stage 7 and Stage 17
Since `activation: full` (not `disabled`), any in-flight WRK at Stage 8+ without `plan-final-review.yaml`
would be blocked. Add `stage7-migration-exemption.yaml` and `stage17-migration-exemption.yaml` support
(same schema as `stage5-migration-exemption.yaml`, checked before the primary artifact).

### D6: Do NOT delegate Stage 17 hard gate to `check_user_review_close_gate()`
The existing soft gate lacks allowlist enforcement. The new hard gate is stricter. Write it
independently; the soft gate and hard gate both read the same artifact but serve different callers.

### D7: Stage 5 config `change_note` — update to reference WRK-1034 (Gemini flag)
The `stage5-gate-config.yaml` header requires change_note + WRK reference for any modification.
This WRK touches the activation flip — update `last_updated` and `change_note`.

---

## Final Plan Steps (synthesized from all 3)

**Phase 1 — Python + config:**
1. Add `_load_gate_config(workspace_root, filename)` generic loader
2. Refactor `_load_stage5_config()` → thin wrapper calling generic loader
3. Add `_validate_exemption(exemption_path, wrk_id, human_allowlist)` helper
4. Add `check_stage7_evidence_gate(wrk_id, assets_dir, workspace_root)`:
   - reads `stage7-gate-config.yaml`, `stage7-migration-exemption.yaml` (if present)
   - checks `plan-final-review.yaml`: `confirmed_by` in allowlist, `confirmed_at` non-empty, `decision=passed`
5. Add `check_stage17_evidence_gate(wrk_id, assets_dir, workspace_root)`:
   - reads `stage17-gate-config.yaml`, `stage17-migration-exemption.yaml` (if present)
   - checks `user-review-close.yaml`: `reviewer` in allowlist, `confirmed_at|reviewed_at` non-empty, `decision=approved|accepted|passed`
6. Add `_run_stage7_check(args)` and `_run_stage17_check(args)` CLI handlers
7. Update `main()`: dispatch `--stage7-check`, `--stage17-check`
8. Create `stage7-gate-config.yaml` (activation=full, owned_by_wrk=WRK-1034, same schema as stage5)
9. Create `stage17-gate-config.yaml` (same)
10. Update `stage5-gate-config.yaml`: check in-flight WRKs → exemptions if needed → flip disabled→full + update change_note/WRK-1034 ref

**Phase 2 — Shell + SKILL:**
11. `claim-item.sh`: Stage 7 guard block after Stage 5 guard (reuse `$STAGE5_CHECKER` variable, prefix STAGE7_)
    Also add `confirmed_at: ""` to bootstrap `user-review-close.yaml` template
12. `close-item.sh`: Stage 17 guard block after Stage 5 guard (prefix STAGE17_)
13. `work-queue/SKILL.md`: HARD GATE + exit checklists for Stages 7 and 17; bump v1.6.4 → v1.7.0

**Tests (17 — exceeds AC-8 minimum of 10):**
Stage 7: disabled bypass (T1), missing artifact (T2), all-fields pass (T3), wrong decision (T4),
agent confirmed_by rejected (T5), confirmed_by missing (T6), missing config→infra fail (T7),
migration exemption valid (T8)
Stage 17: disabled bypass (T9), missing artifact (T10), all-fields pass (T11), wrong decision (T12),
agent reviewer rejected (T13)
CLI: --stage7-check exit 0 (T14), exit 1 (T15); --stage17-check exit 0 (T16), exit 1 (T17)

---

## Open Questions Resolved by User (Stage 5 Q&A)

| Question | Decision |
|----------|----------|
| Gate activation for S5/S7/S17 | `full` — immediate enforcement |
| confirmed_at in bootstrap template | Yes, include `confirmed_at: ""` |
| Stage 7 canonical artifact | `evidence/plan-final-review.yaml` only |

---

## Not in Scope

- Unifying all 3 gate configs into a single file (deferred follow-up WRK)
- Modifying `check_user_review_close_gate()` soft gate logic (too much blast radius)
- Interactive planning enforcement for Route A/B/C 3-agent sessions (tracked as separate gap)
