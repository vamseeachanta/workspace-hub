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

## Enforcement status — ADVISORY ONLY (important)

This policy is currently **declarative**. The executed routers (`scripts/coordination/routing/lib/tier_router.sh`, `scripts/ai/task-dispatcher.py`) hold their own **hardcoded** routing chains and do **not** parse `routing-config.yaml`. Therefore:

> **Do NOT rely on `execution_contexts` / the cost ceiling to block Claude on Hermes tasks at runtime until the executed-router consolidation lands.**

Consolidating the three drifted routing copies into one executed source is a follow-up under epic [#3058](https://github.com/vamseeachanta/workspace-hub/issues/3058). The guard test (`tests/config/test_cost_ceiling_policy.py`) asserts the config's **declared intent**, not runtime enforcement.

## Related
- `config/agents/routing-config.yaml` — `execution_contexts` + `routing_resolution_note` reference this doc.
- `config/agents/model-registry.yaml` / `provider-capabilities.yaml` — model IDs; Hermes = `gpt-5.5` (unchanged).
- `docs/governance/2026-06-14-model-parity-decision.md` — sibling decision record (single-registry principle).
