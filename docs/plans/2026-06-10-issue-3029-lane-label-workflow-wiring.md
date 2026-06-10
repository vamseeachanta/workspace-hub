# Plan for #3029: Wire lane: labels into dispatch routing + planning template + planning skill

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-06-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3029
> **Client:** N/A
> **Project:** (none)
> **Review artifacts:** scripts/review/results/2026-06-10-plan-3029-claude.md | ...-codex.md

---

## Resource Intelligence Summary

Sources consulted:

1. **`scripts/dispatch/route.py:151-157`** — Found provider resolution is `existing_ai or assign.get("provider") or defaults.get("provider")` where `existing_ai = existing_label_value(labels, "ai:")`; `provider_explicit = bool(existing_ai or assign.get("provider"))`. No `lane:` read anywhere in the file. The `existing_label_value(labels, prefix)` helper (route.py:68) already does prefix extraction and is directly reusable for `lane:`.
2. **`.claude/memory/kanban/routing-rules.yaml:30-66`** — Confirmed the provider vocabulary is `claude`, `codex`, `hermes`, `gemini` with `ai:<provider>` label values; `codex` and `claude` are `tier: workhorse, auto_routable: true`; hermes shares `codex_pool`; gemini is `auto_routable: false` (manual `ai:gemini` only). Comment at line 66: "A human-set ai:/machine: label on the issue always overrides." Lane values (`codex`, `claude`) are an exact subset of provider names — no mapping table needed.
3. **Live GitHub state (verified 2026-06-10 in #3028)** — Confirmed 0 `ai:` labels exist on any open workspace-hub issue, while 1,790 open issues across 26 repos carry exactly one `lane:codex`/`lane:claude` label. The router's only currently-available provider signal on issues is `lane:`, which it cannot see.
4. **`docs/plans/_template-issue-plan.md:1-9`** — Confirmed header fields `Client:`/`Project:` exist (per #2778) but no Lane/Provider field.
5. **`.claude/skills/coordination/issue-planning-mode/SKILL.md` Steps 1-4** — Confirmed no instruction to verify/assign a `lane:` label at plan time; Step 4 ("Post and Label") handles only `status:` labels.
6. **`tests/dispatch/test_route_glob.py`** — Found the established hermetic test pattern: import `route.py` via `importlib.util` and call pure functions with explicit args; run via `uv run --with pyyaml pytest`. The provider-resolution block is currently inline in a loop (not a pure function), so testing it requires a small extraction.
7. **`.claude/memory/agents.md` (commit `5ce951be2`)** — The governing "Compute lane assignment (plan-time)" rule this issue operationalizes; quota-gate enforcement is explicitly out of scope here (filed as #3030).

Gaps (to build from scratch):
- A pure `resolve_provider(labels, assign, defaults) -> (provider, provider_explicit)` function in route.py (extraction of the existing inline logic + lane awareness) so the precedence is unit-testable.
- `tests/dispatch/test_route_lane.py` covering the new precedence.
- Template and skill text additions.

## Proposed Changes

### Step 1 — Tests first (TDD, red)

Create `tests/dispatch/test_route_lane.py` (hermetic, importlib pattern from `test_route_glob.py`) pinning the **revised precedence `ai:` > rule provider > `lane:` > default** (per r2 MAJOR-1 resolution — lane is a plan-time *preference*, not an override):

1. `lane:codex`, no `ai:` label, no rule provider → provider `codex`, `provider_explicit=False`.
2. `ai:claude` + `lane:codex` → provider `claude` (`ai:` dispatch-time override wins).
3. **Live-rule fixture (r2 MINOR-1):** card with `needs:cross-review` + `lane:claude` → provider `codex` (the routing-rules.yaml:90-92 rule outranks lane; existing routing intent preserved).
4. No `ai:`/`lane:` labels → rule `assign.provider`, else default (existing behavior bit-identical).
5. `lane:gemini` (not in {codex, claude}) → ignored, falls through to rule/default. Lane vocabulary is fixed to the two workhorse providers.
6. **Label-write guard (r2 MAJOR-2/MINOR-2):** a lane-resolved card passed through `labels_for()` emits NO `ai:` label (`provider_explicit` stays `False` for lane-derived providers — lane is non-sticky and remains re-classifiable; matches the `labels_for` docstring "ai: only when a rule/human chose a non-default provider").
7. A lane-resolved provider flows through `apply_wip` identically to a rule/default-resolved one (`apply_wip` consumes `provider`, not `provider_explicit` — route.py:210-223; pool/WIP caps and auto_routable apply unchanged).

### Step 2 — route.py change (green)

- Extract the inline provider block (route.py:152-157) into `resolve_provider(labels, assign, defaults)`; behavior-preserving except for the new `lane:` step.
- Inside: `existing_lane = existing_label_value(labels, "lane:")`, accepted only if in `{"codex", "claude"}`.
- **Precedence (revised per r2):** `existing_ai or assign.get("provider") or accepted_lane or defaults.get("provider")`.
- **`provider_explicit` is UNCHANGED:** `bool(existing_ai or assign.get("provider"))` — lane never sets it, so `labels_for()` never materializes `ai:` labels from lane (resolves r2 MAJOR-2; Acceptance Criterion 4 now holds literally). Lane stays a live, re-classifiable signal.
- Code comment at the lane step will state the authority model (r1 M2): lane labels are plan-time preferences (agent-or-human-set during the human-gated planning stage), weaker than both the human-set `ai:` override and specific routing rules (routing-rules.yaml:66, 90-92), stronger only than the catch-all default.
- Call site updated; `--apply` write behavior is untouched by construction.

### Step 3 — Plan template field

Add to `docs/plans/_template-issue-plan.md` header block (after `Project:`):

```
> **Lane:** lane:claude | lane:codex   <!-- plan-time AI provider lane per .claude/memory/agents.md "Compute lane assignment"; must match the issue's lane: label — reclassify the label if planning changed the scope -->
```

### Step 4 — Planning skill step

In `.claude/skills/coordination/issue-planning-mode/SKILL.md`:
- Step 2 (Draft Plan): add item — "Set the **Lane:** header field and verify the issue carries exactly one matching `lane:codex`/`lane:claude` label (heavy compute → codex; orchestration/review/light → claude, per the compute-lane rule in `.claude/memory/agents.md`). If planning changed the scope class, relabel the issue. Note: a human/dispatch-set `ai:` label outranks lane — if one is present and now wrong, reconcile it explicitly."
- Step 4 (Post and Label): add to the label-time checklist — "issue carries exactly one `lane:` label consistent with the plan's Lane: field."

### Step 5 — Verification

- `uv run --with pyyaml pytest tests/dispatch/test_route_lane.py tests/dispatch/test_route_glob.py` — new tests pass, glob tests unchanged.
- `python scripts/dispatch/route.py` dry-run executes without error against current boards.
- `scripts/legal/legal-sanity-scan.sh` passes.

## Acceptance Criteria

1. Router resolves provider with precedence `ai:` > rule provider > `lane:` (codex/claude only) > default; covered by passing unit tests including the live `needs:cross-review` fixture and the unknown-lane guard.
2. Existing routing behavior for cards without `lane:` labels is bit-identical (regression-pinned by test 4 and the untouched glob suite); existing rules (incl. `needs:cross-review → codex`) are never inverted by lane.
3. Plan template carries the Lane field; planning skill instructs lane verification at draft and at label time.
4. No change to `--apply` write behavior: `provider_explicit` semantics unchanged, lane never materializes `ai:` labels (pinned by test 6).

## Adversarial Review Resolution (r3, inline)

- **r1 (Claude, inline): MINOR** — `scripts/review/results/2026-06-10-plan-3029-claude.md`. M1 (lane→`ai:` materialization) and M3 (apply_wip consumer) were superseded by the sharper r2 analysis; M2 (authority-model comment) retained in Step 2.
- **r2 (Codex, dispatched): MAJOR** — `scripts/review/results/2026-06-10-plan-3029-codex.md`. Both MAJORs verified against the repo and **resolved by adopting codex's suggested design**: (1) precedence demoted to `ai:` > rule > `lane:` > default so the live `needs:cross-review → codex` rule (routing-rules.yaml:90-92) is never inverted; (2) `provider_explicit` left untouched so lane never produces sticky `ai:` labels, honoring the `labels_for` docstring contract. Both MINORs resolved as new tests 3 and 6. Per the r3 inline-loop-break pattern, these patches are applied inline without a fresh r3 dispatch; the r2 artifact records the pre-revision verdict.

## Risks / Notes

- **Vocabulary drift**: lane labels are exactly `lane:codex`/`lane:claude` (created 2026-06-10 across 26 repos); the `{codex, claude}` whitelist in route.py guards against future lane values silently becoming providers. If a `lane:gemini` is ever wanted, it must be added deliberately (gemini is `auto_routable: false` — auto-routing it via lane would violate routing-rules.yaml intent).
- **Layering with #3030**: the quota gate will need the lane-aware path introduced here; interface kept as one pure function to make that insertion local.
- **Hermes**: hermes draws from codex_pool but has no lane label value; unaffected — hermes assignment continues to come from rules/`ai:hermes` only.

## Out of Scope

- Codex weekly-quota preflight (<10% suspension) — #3030.
- Backfilling `ai:` labels; relabeling any existing issues.
- kanban board/loader changes.
