# Decision record — Evidence-threshold approval evolution (graduate routine approvals off the user-gate)

- **Date:** 2026-06-28
- **Status:** PROPOSED — requires owner approval (the agent never self-approves this policy)
- **Issue:** [#3296](https://github.com/vamseeachanta/workspace-hub/issues/3296) · **Epic:** [#3290](https://github.com/vamseeachanta/workspace-hub/issues/3290) (Theme D — owner orchestration overhead)
- **Implements:** the `agents.md` "Autonomous gate evolution" rule.
- **Evaluator:** `scripts/governance/evidence_threshold_eligibility.py` (pure, fail-closed, **shadow-mode only**).
- **Ledger:** `docs/governance/evidence-threshold/` (append-only JSON audit records).

## Context

`agents.md` records the owner intent: *"hard gates remain in force until metrics prove agent rigor is consistently safe; over time, shift routine plan/review/execution/verification cycles from user-managed approval to evidence-threshold approval so the owner focuses on ideas, GTM throughput, and customer/prospect artifacts."*

This policy converts that one-line intent into a concrete metric + threshold + eligibility scheme, plus a small advisory evaluator. **It does not relax any gate today.** The binding constraint is the SOUL must-fire rule *"Never self-label `status:plan-approved`. The user-in-loop approval gate is load-bearing."* The pilot therefore runs in **shadow mode**: the evaluator computes and records an eligibility verdict; the human still applies the label. True auto-apply is a later, separately-approved graduation phase whose **hard precondition is amending that SOUL must-fire rule** (owner decision D5).

This is a deliberate evolution of the `scripts/workflow/completeness_score.py` (#2798) pattern: class is auto-derived from changed files (not caller-selectable), and malformed input is rejected. The one intentional divergence is the failure direction (see "Fail-closed posture" below).

## Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | **Issue class is DERIVED, never caller-supplied.** `classify(changed_files, labels)` maps the change to a class; `evaluate_eligibility` has no `issue_class` parameter. | Closes the "declare a load-bearing change eligible" gaming vector (mirrors `completeness_score.classify()`). |
| 2 | **Load-bearing signals win, checked first.** A change touching any load-bearing file/label can never down-classify into an eligible bucket. | Cross-cutting changes stay manual. |
| 3 | **Eligible set is small and explicit; everything else fails closed to manual.** Unknown class → INELIGIBLE. | Conservative by construction. |
| 4 | **Malformed/missing/non-finite/out-of-domain metric → INELIGIBLE (fail closed), never a raised exception.** Validation runs INSIDE `normalize_metrics`, BEFORE any normalization arithmetic, for every metric direction. | A shadow advisory gate's safe state is "keep the human-in-loop gate." A raise could be swallowed by a caller and mis-default toward graduation. |
| 5 | **All metrics normalized to higher-is-better [0,1] before the threshold loop.** Lower-is-better and count-lower-better metrics are converted first. | Prevents evaluating lower-is-better metrics backwards. |
| 6 | **Shadow mode only. The verdict vocabulary has no `auto_apply` mode** (`mode ∈ {shadow, manual}`). | The evaluator recommends/records; it never applies `status:plan-approved`. |
| 7 | **Auto-apply (a future phase) names amending the SOUL never-self-approve must-fire rule as a HARD PRECONDITION.** | Auto-apply cannot ship until the owner amends that rule; the shadow phase preserves it unchanged. |

## Rigor metrics

Computed over a trailing window of **eligible-class** issues. Each metric declares a normalization direction and a raw domain that is validated **before** any normalization arithmetic, then is normalized to a higher-is-better [0,1] score before the threshold comparison.

| Metric | Direction | Raw domain | Normalization | Proposed threshold (normalized) | Notes |
|---|---|---|---|---|---|
| `adversarial_review_approve_rate` | higher_is_better | [0,1] | `v = raw` | ≥ 0.90 | fraction of plans where all required providers returned APPROVE (no MAJOR) on first pass, read from `scripts/review/results/`. |
| `post_merge_revert_rate` | rate_lower_better | [0,1] | `v = 1 - raw` | ≥ 0.95 | fraction of merged eligible-class issues reopened/reverted/bug-followed within N days. **Externally grounded** — depends on real reopens the agent cannot fake. |
| `completeness_gate_pass_rate` | higher_is_better | [0,1] | `v = raw` | ≥ 0.90 | fraction of opted-in closes passing #2798 at/above threshold on first computation. |
| `reproduction_compliance_rate` | higher_is_better | [0,1] | `v = raw` | ≥ 0.90 | fraction of plans with a valid Step-1.5 reproduction citation or a justified `N/A`. |
| `plan_revision_rounds` | count_lower_better | [best, best+span] = [1, 5] | `v = clamp(1 - (raw-best)/span)` | ≥ 0.50 | mean MAJOR-driven re-draft rounds before approval. |

- **Rolling window / minimum sample (proposed, owner decides at approval):** trailing window over the most recent eligible-class issues; `min_sample = 20`. Below `min_sample` → INELIGIBLE ("insufficient sample"). Window length count-based vs days-based is an open owner-input item.
- The numeric thresholds and window above are **proposals**; the owner sets the final numbers at approval.

## Issue-class taxonomy

**Eligible (routine, low blast radius):**
- `docs-typo-index` — single-file docs / index / README typo (pilot class — already a safe-path in `plan-approval-gate.sh`).
- `test-only-additive` — pure additive test changes, no source.
- `low-risk-config` — non-CI, non-schema config edits.

**Ineligible / load-bearing (ALWAYS manual, regardless of metrics):**
- `ci-workflow` — `.github/workflows/`, `.github/actions/`.
- `schema-contract` — `schema/`, `*.schema.json`, registry files.
- `security-legal` — `.legal-*`, `scripts/legal/`, secrets.
- `outward-facing` — client-shared reports, public sites, `client:*` label.
- `engineering-calc` — source packages (`src/`, `packages/`).
- `harness-enforcement` — `scripts/enforcement/`, SOUL, `agents.md`, `config/agents/`, `gate:*` label.
- `gate-self-modification` — `.claude/hooks/`, `plan-approval-gate`.

**Default:** any unmatched class → `unknown` → INELIGIBLE (fail closed to manual).

## Deterministic classifier

`classify(changed_files, labels)`:
1. For each changed file (in order), return the first load-bearing class matched (priority-ordered per the table above).
2. Else, if any label carries a load-bearing signal (`gate:*` → `harness-enforcement`; `client:*` → `outward-facing`), return that class.
3. Else, if **all** changed files satisfy an eligible bucket predicate (all-docs → `docs-typo-index`; all-tests → `test-only-additive`; all-low-risk-config → `low-risk-config`), return that bucket.
4. Else `unknown`.

The class is read from authoritative sources by a thin CLI wrapper (git for changed files, `gh` for labels) — never passed in pre-classified by the agent.

## Fail-closed posture (deliberate divergence from `completeness_score.py`)

`completeness_score.py` *raises* `CompletenessError` on an out-of-range/NaN metric — correct for a scoring module whose only valid response to bad input is to halt the score. This evaluator instead **fails closed to INELIGIBLE (stays manual)** on a missing/None/non-finite/out-of-domain metric of **any** direction. The validation lives **inside `normalize_metrics`, before any arithmetic** (`1.0 - raw`, `(raw - best)/span`), and returns `(None, bad_metric_name)` rather than raising — so a malformed lower-is-better/count metric cannot raise a `TypeError` before the conservative verdict is produced. A post-normalization range guard remains as defense-in-depth.

## Evidence ledger / audit trail

Each shadow-eligible decision produces an append-only JSON record (see `docs/governance/evidence-threshold/README.md`) containing: `reviewed_commit_sha`, `plan_path`, `review_artifact_paths`, `issue_class`, `raw_metric_snapshot`, `normalized_metric_snapshot`, `thresholds`, `window_bounds`, `sample_size`, `decision`, `decided_at_utc`, `mode: "shadow"`. This makes every (shadow) auto-approval reconstructable.

**Scope boundary (D6):** this ledger is **governance-internal audit only**. It does NOT define the envelope-determinism fields (`input_hash`, `result_hash`, `provenance.code_version`) owned by #3282/#3283, nor the deckhand routing / `result:` registry descriptor owned by #3282/#3295.

## Kill-switch and rollback

- **Kill-switch:** `config.kill_switch_on = True` → every verdict is INELIGIBLE ("kill-switch engaged"), returning the pilot class to fully manual immediately.
- **Rollback:** disable the kill-switch path is the kill-switch itself; for an opted-in class, removing the opt-in label also returns it to manual. No gate or label flow is modified by the shadow pilot.

## Graduation phases

1. **Shadow (this policy):** evaluator computes + records a verdict; the human applies the label. SOUL must-fire rule preserved unchanged. Pilot scoped to ONE eligible class — proposed `docs-typo-index` (lowest blast radius).
2. **Owner-authorized auto-apply (future, separate approval):** HARD PRECONDITION = the owner amends the SOUL never-self-approve must-fire rule. Only then may an eligibility verdict drive label application, behind an opt-in label + server-side authority (mirroring `.github/workflows/completeness-gate.yml`). **Out of scope here.**

## Pilot scope and risks

- Pilot class: `docs-typo-index` (single eligible class), with the ledger audit trail and the kill-switch + label-removal rollback.
- **Pilot may be inert:** eligible-class issue volume may be too low to reach `min_sample` for a long time (fail-safe to manual). Surfaced so the owner isn't surprised the pilot rarely fires.
- **Metric gaming:** thresholds computed from agent-produced artifacts can be inflated. Mitigations: class is derived not caller-supplied; malformed inputs fail closed; `post_merge_revert_rate` is externally grounded.

## Enforcement status — SHADOW (advisory) only

The evaluator is a pure module with no gate wiring. It does **not** modify `plan-approval-gate.sh`, `completeness-gate.yml`, `agents.md`, `SOUL.runtime.md`, or any `status:*` label flow. Tests: `tests/governance/test_evidence_threshold_eligibility.py`.

## Related
- `agents.md` — the "Autonomous gate evolution" rule this policy implements.
- `config/agents/claude/SOUL.runtime.md` — the never-self-approve must-fire rule (the binding constraint; amendment is the auto-apply precondition).
- `scripts/workflow/completeness_score.py` / `.claude/rules/completeness-before-close.md` (#2798) — the derived-class + fail-closed precedent this evolves.
- `.github/workflows/completeness-gate.yml` — the opt-in label + server-side authority shape a future auto-apply phase would reuse.
