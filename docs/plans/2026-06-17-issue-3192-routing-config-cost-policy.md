# Plan for #3192: Reconcile routing-config.yaml with operator cost policy (Hermes→agy, Claude dev-only)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3192
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-17-plan-3192-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `config/agents/routing-config.yaml` (111 lines) — `tiers.{SIMPLE,STANDARD,COMPLEX,REASONING}.primary` all `claude`; `agents.hermes` declares `provider: openai-codex`, `models.primary: gpt-5.5`.
- Found: `config/agents/model-registry.yaml` (v2.2) — `latest_models` (claude_primary opus-4-8[1m], gemini_primary gemini-2.5-pro, openai_primary gpt-5.5) + work_queue_routing.
- Found: `config/agents/provider-capabilities.yaml` (v1.3) — `providers.hermes.model_ids.primary: gpt-5.5`; strategy note: "Hermes runs gpt-5.5 via the openai-codex provider (NOT a Claude wrapper)".
- **Consumer reality (load-bearing):** the tier→provider mapping is **advisory/documentary, NOT executed.** Verified: `scripts/coordination/routing/lib/tier_router.sh:10` assigns `ROUTING_CONFIG=` but never reads it — routing chains are hardcoded bash arrays (and already disagree with the YAML, e.g. SIMPLE primary=codex in bash vs claude in YAML). `scripts/ai/task-dispatcher.py` loads the YAML but only reads `tiers.*.description`; provider preference comes from a hardcoded dict. `scripts/coordination/routing/route.sh` prints a hardcoded table that disagrees with both. `scripts/dispatch/route.py` (#3030 lane dispatcher) doesn't reference routing-config at all.
- Gap: NO single executed source of truth for tier routing — three drifted copies (YAML, tier_router.sh arrays, task-dispatcher dict).

### Standards / LLM Wiki
Not applicable / none — harness governance config.

### Documents consulted
Issue #3192 (cost policy + 3-part scope); epic #3058 (convert manual checks → standing invariants → motivates a written SSoT + guard test, not just a config edit); `docs/governance/2026-06-14-model-parity-decision.md` (decision-record format + single-registry principle); `scripts/agents/set-antigravity-default-model.sh` (proves **agy = Antigravity CLI, Gemini-backed** → "agy" resolves to provider `gemini`); `scripts/enforcement/model-id-baseline.txt:934` (records routing-config gpt-5.5 line — editing Hermes block may move it); `tests/config/test_routing_config_observed_behavior.py` (asserts SIMPLE/STANDARD primary==claude — contradicts the new policy, must change).

### Gaps identified
- No `docs/governance/*cost*` doc exists — SSoT must be written from scratch.
- routing-config has no cost-policy header and no "execution context" notion separate from tier.
- No test enforces the cost ceiling → config can silently drift back (the #3058 failure mode).
- **Unresolved policy/config conflict (surface, don't silently fix):** policy says "agy (Gemini) powers Hermes" but all configs + strategy note say Hermes runs gpt-5.5 via openai-codex. Treat as a deliberate operator redefinition; record for HITL confirmation.

### Evidence
#3192 OPEN; #3058 OPEN. Files verified. Gap proofs: `grep -rli "cost ceiling|cost policy" docs/` empty; `grep -c routing-config scripts/dispatch/route.py` → 0; tier_router.sh has no YAML parser. N/A reproduction (governance/config divergence, shown statically; old test currently passes encoding the OLD policy). Sources: 8.

---

## Approach / Deliverable
**OPERATOR DECISION (2026-06-17): Hermes's backing lane STAYS `gpt-5.5`/openai-codex** — the original policy phrase "agy powers Hermes" is overridden; agy is the cheap *fallback / delegation* lane, NOT Hermes's backing model. So no change to `agents.hermes.provider` (remains openai-codex) and the model-id baseline line stays put — the conflict is RESOLVED, not just flagged.

A cost-ceiling-honoring `routing-config.yaml` that separates **execution context** from **tier**: `hermes_batch` → **primary `openai-codex` (gpt-5.5)**, fallback `agy`, **forbid `claude`** (cost ceiling), `cost_ceiling: true`; `interactive_dev` → primary claude, fallback [codex, agy]; `cross_review` unchanged (claude). Backed by a governance SSoT (`docs/governance/2026-06-17-cost-ceiling-policy.md`) referenced from the config header; model-registry + provider-capabilities reconciled; a regression-guard test that fails if a cost-ceiling context ever names Claude.

- Add `header.cost_ceiling_policy` + `policy_summary` ("Claude reserved for interactive dev; Hermes = gpt-5.5/openai-codex; agy = cheap fallback/delegation lane; NO Claude for Hermes-context — cost ceiling"); add `execution_contexts` as above; repoint tiers to contexts; add `routing_resolution_note` stating the maps are advisory today.
- **Scope boundary (deliberate):** this changes the declarative/advisory config + governance ONLY. Rewiring the 3 hardcoded executed routers to actually parse routing-config (collapsing the drifted copies into one executed SSoT) is larger → follow-up under #3058. The `routing_resolution_note` makes the advisory status explicit so no one believes the ceiling is runtime-enforced when it isn't.

## Files to change
Create: `docs/governance/2026-06-17-cost-ceiling-policy.md`, `tests/config/test_cost_ceiling_policy.py`.
Modify: `config/agents/routing-config.yaml`, `config/agents/provider-capabilities.yaml`, `config/agents/model-registry.yaml` (comment cross-ref, no model-ID churn), `tests/config/test_routing_config_observed_behavior.py` (replace the all-claude assertion), `docs/plans/README.md`. Update if flagged: `scripts/enforcement/model-id-baseline.txt:934`.

## TDD test list
cost-ceiling-context-DECLARES-forbid-claude (declaration, not runtime enforcement); **hermes-context-primary-is-openai-codex**; **hermes-context-fallback-is-gemini** (agy = the Antigravity Gemini CLI surface → resolves to the `gemini` provider token, which exists in provider-capabilities); interactive-dev-primary-is-claude; cost-policy-reference-resolves (governance doc exists + declares the ceiling); cross-review-unchanged; simple-standard-context-honors-ceiling (replaces the old all-claude assertion — asserts SIMPLE/STANDARD primary is no longer hardcoded claude); provider-caps-hermes-aligned (provider-capabilities hermes.primary == routing-config agents.hermes.models.primary == gpt-5.5). Red first.

## Risks / open questions (HITL-critical)
- **Advisory vs enforced:** is it acceptable to ship a "cost ceiling" the runtime routers don't read? The plan scopes executed-router rewiring to a #3058 follow-up; `routing_resolution_note` keeps it honest. **Confirm acceptable.**
- **Hermes-backing conflict: RESOLVED (operator 2026-06-17)** — Hermes backing stays gpt-5.5/openai-codex; agy is the fallback/delegation lane only. `agents.hermes.provider` unchanged; line-934 baseline unaffected.
- **agy↔gemini taxonomy:** use `agy` as a first-class token (→ Antigravity Gemini surface) or reuse `gemini`? Keep consistent with set-antigravity-default-model.sh.
- **Test inversion:** flipping `test_simple_and_standard_route_to_claude` (tied to #1730) — confirm no other suite depends on it.

## Adversarial review (T2 plan-stage) — DONE, findings folded in
1 adversarial lens run 2026-06-17 (NON-APPROVE; 2 CRITICAL + 2 HIGH + 3 MED/LOW). Resolutions:
- **CRITICAL — test name inversion** (`hermes-context-primary-is-agy` contradicted the design). FIXED in TDD list: primary = openai-codex, fallback = gemini.
- **CRITICAL — advisory honesty.** FIX: the `routing_resolution_note` is a prominent top-of-file YAML comment reading "**This cost ceiling is ADVISORY ONLY — NOT enforced by tier_router.sh / task-dispatcher.py (they hold hardcoded chains). Do NOT rely on it to block Claude on Hermes tasks until the executed-router consolidation lands (#3058 follow-up).**" Guard test renamed to assert the config's *declared intent*, not runtime enforcement.
- **HIGH — agy↔gemini taxonomy.** RESOLVED: routing-config uses the **`gemini`** provider token (exists in provider-capabilities); agy is documented as the Antigravity Gemini *CLI surface* that resolves to `gemini`. (First-class `agy` token is #3190's concern; #3192 doesn't reference a non-existent provider.)
- **HIGH — baseline line 934.** FIX: do NOT claim "unaffected" — adding header/execution_contexts shifts lines; run the change, and if the hash moves, regenerate via `check-model-id-sourcing.sh --update-baseline` and commit it in the same PR.
- **MED — test inversion spec** + **before/after YAML diff** included in the implementation; new assertion specified (SIMPLE/STANDARD primary no longer hardcoded claude). Only one dependent of the old test (none external) — safe.
- **MED — governance ADR** `docs/governance/2026-06-17-cost-ceiling-policy.md` records the operator decision (Hermes stays openai-codex; agy = fallback; "agy powers Hermes" overridden) with the authority/date, referenced from the routing-config header.
Cross-provider (Codex/Gemini) review via `plan-review-fanout.sh` recommended at code stage.

## Acceptance criteria
Mirror issue #3192: execution contexts reflect Hermes→agy / Claude dev-only / agy fallback; cost-ceiling contexts forbid Claude; governance SSoT written + referenced; model-registry + provider-capabilities reconciled with Claude-on-Hermes flags; Hermes-backing conflict recorded for HITL; tests pass (incl. inverted guard); no regression; routing_resolution_note documents advisory status + deferred executed-router consolidation; model-id baseline clean/updated; review artifacts posted.
