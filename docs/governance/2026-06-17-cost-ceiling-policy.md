# Decision record — AI provider cost-ceiling policy

- **Date:** 2026-06-17
- **Status:** Accepted (operator decision 2026-06-17)
- **Issue:** [#3192](https://github.com/vamseeachanta/workspace-hub/issues/3192) · **Epic:** [#3058](https://github.com/vamseeachanta/workspace-hub/issues/3058)
- **SSoT for:** provider cost routing intent. Referenced from `config/agents/routing-config.yaml` (`execution_contexts`).

## Context

The operator runs fixed multi-provider budgets (Anthropic Max base + overage, OpenAI, Google AI Pro). Claude API is the most expensive surface and is reserved for interactive development. The prior `routing-config.yaml` named `claude` primary for every tier with no notion of a cost ceiling, and there was an apparent conflict between the policy phrase "agy powers Hermes" and the configs (which all say Hermes runs `gpt-5.5` via the `openai-codex` provider).

## Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | **Claude is the interactive-dev lane only.** | API cost; reserve the premium surface for human-driven work. |
| 2 | **Hermes's backing lane STAYS `gpt-5.5` / `openai-codex`.** The phrase "agy powers Hermes" is **overridden** — agy is a *fallback/delegation* lane, not Hermes's backing model. | All configs + the provider-capabilities strategy note already run Hermes on `gpt-5.5`; no reason to switch its backing model. Resolves the #3192 conflict. |
| 3 | **agy (Antigravity, Gemini-backed) is the cheap fallback / delegation lane.** In routing it resolves to the `gemini` provider token (the capability that exists in `provider-capabilities.yaml`); `agy` is the CLI surface for it. | Keeps the token set consistent with `provider-capabilities.yaml`; a first-class `agy` token is scoped to [#3190](https://github.com/vamseeachanta/workspace-hub/issues/3190). |
| 4 | **Cost ceiling: no Claude for Hermes-context work.** Encoded as `execution_contexts.hermes_batch.forbid: [claude]`. | Hermes batch/docs/delegation must not consume the Claude API budget. |

## Enforcement status — ENFORCED at runtime (cost ceiling), as of #3205

The cost ceiling is **runtime-enforced** (no longer advisory). A single resolver,
`scripts/ai/routing_resolver.py`, is the only place forbid policy is interpreted; it
reads `execution_contexts` from `routing-config.yaml` and is consulted by **every**
executed surface that can spend provider budget:

| Surface | How it consults the resolver |
|---|---|
| `scripts/coordination/routing/lib/tier_router.sh` (`route_by_tier`, reached by **both** `route.sh` and `orchestrate.sh`) | filters candidates + uses a context-aware emergency default (never claude) when `ROUTE_CONTEXT` is set |
| `scripts/coordination/routing/lib/provider_filter.sh` (`filter_available_providers`) | drops forbidden providers from the available set (`--filter --no-fallback`) |
| `scripts/ai/task-dispatcher.py` | `--context` drops forbidden agents from the scored list |
| `scripts/ai/overnight-batch-planner.py` | overnight/overnight-batch issues run in `hermes_batch`; no claude default, and an explicit `agent:claude` is a hard error |

**Invocation:** routers pass `--context hermes_batch` (CLI flag) or set `ROUTE_CONTEXT=hermes_batch` (env). **Fail-closed:** an explicit but *unknown* context (e.g. a typo `hermes-batch`) errors with exit 3 — it never falls through to claude. Provider tokens are CLI-normalized in one place (`openai-codex` → `codex`).

**Scope:** this enforces the **cost ceiling** (the `execution_contexts.*.forbid` lists). It does **not** yet single-source the per-tier routing table (`tiers.*`) — that reconciliation (cost-aligned, codex for cheap tiers) is the deferred follow-up [#3209](https://github.com/vamseeachanta/workspace-hub/issues/3209) under epic [#3058](https://github.com/vamseeachanta/workspace-hub/issues/3058).

**Tests (drive the real surfaces):** `tests/ai/test_routing_resolver.py`, `tests/ai/test_task_dispatcher_cost_ceiling.py`, `tests/ai/test_overnight_planner_cost_ceiling.py`, `tests/coordination/test_tier_router_cost_ceiling.py`, `tests/coordination/test_orchestrate_and_provider_filter_cost_ceiling.py`. `tests/config/test_cost_ceiling_policy.py` continues to assert the config's declared intent.

## Related
- `config/agents/routing-config.yaml` — `execution_contexts` + `routing_resolution_note` reference this doc.
- `config/agents/model-registry.yaml` / `provider-capabilities.yaml` — model IDs; Hermes = `gpt-5.5` (unchanged).
- `docs/governance/2026-06-14-model-parity-decision.md` — sibling decision record (single-registry principle).
