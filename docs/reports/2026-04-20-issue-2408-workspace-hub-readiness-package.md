# Workspace-Hub Model-Release Readiness Package (#2408)

> Cohesive summary of the workspace-hub-only control-plane surfaces, the readiness gaps that motivated this issue, the shape of the contract and playbook delivered under #2408, and the work explicitly deferred to follow-up issues.
>
> Date: 2026-04-20 | Issue: [#2408](https://github.com/vamseeachanta/workspace-hub/issues/2408)

---

## Why this package exists

Issue #2399 (parent) was reviewed as too broad: it mixed workspace-hub governance, tier-1 ecosystem inventory, and provider-entrypoint-shape normalization in a single change. #2408 is the narrow child scoped strictly to **workspace-hub control-plane readiness**: a standing contract and an operational upgrade playbook, anchored from the two canonical discoverability surfaces (`AGENTS.md` and `docs/standards/CONTROL_PLANE_CONTRACT.md`).

---

## Scope

### In scope

- `AGENTS.md`
- `docs/standards/CONTROL_PLANE_CONTRACT.md`
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` (consulted, not modified)
- Root provider entry surfaces `CLAUDE.md`, `GEMINI.md` (audited only — verified ≤ 20 lines)
- Provider adapter directories `.claude/`, `.codex/`, `.gemini/` (referenced only)
- `config/agents/claude/`, `config/agents/codex/`, `config/agents/gemini/`
- `scripts/_core/sync-agent-configs.sh`
- `.claude/rules/coding-style.md`, `.claude/rules/patterns.md`, `.claude/rules/README.md`

### Out of scope

The following work is deliberately deferred and **will not** be performed under #2408:

- **Tier-1 ecosystem inventory.** Downstream repos (digitalmodel, assethold, assetutilities, worldenergydata, etc.) have their own readiness posture; harmonizing them is a separate effort.
- **Provider-entrypoint-shape normalization.** Whether `CLAUDE.md` / `GEMINI.md` / `.codex/*` share a common shape is a separate effort. #2408 audits their line-count compliance only.
- Runner/evaluation harness implementation.
- Model-choice or AI review routing changes (owned by `AI_REVIEW_ROUTING_POLICY.md`).

Any reader of this package who discovers they need one of the out-of-scope deliverables should open a sibling issue rather than extend #2408.

---

## Surface inventory (workspace-hub)

| Surface | Role | Status |
|---|---|---|
| `AGENTS.md` | canonical workflow contract + readiness anchor | updated under #2408 |
| `docs/standards/CONTROL_PLANE_CONTRACT.md` | adapter topology + readiness cross-reference | updated under #2408 |
| `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` | five-dimension readiness contract | created under #2408 |
| `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md` | provider-owned vs repo-owned drift playbook | created under #2408 |
| `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | cross-provider review routing | unchanged; referenced |
| `CLAUDE.md`, `GEMINI.md` | thin provider-entry adapters | audited only; within line limit |
| `.claude/rules/coding-style.md` | 20-line harness rule (source of truth) | unchanged; referenced |
| `.claude/rules/patterns.md` | enforcement-tier gradient | unchanged; referenced |
| `config/agents/` + `scripts/_core/sync-agent-configs.sh` | provider-config drift reconciliation | unchanged; referenced by the playbook |

---

## Workspace-Hub Gap Summary

The following gaps existed in the workspace-hub control plane before #2408 and are the concrete motivation for the contract/playbook delivered here.

1. **No single workspace-hub contract for model-release readiness.** Readiness posture was implicit in scattered references inside `CONTROL_PLANE_CONTRACT.md`, `.claude/rules/`, and `AGENTS.md`. A new provider release had no canonical checklist to satisfy.
2. **No workspace-hub upgrade playbook.** Engineers had to re-derive provider-owned vs repo-owned drift handling each release. Error-prone, especially when a single PR mixed the two.
3. **No cross-file discoverability-anchor policy.** A new artifact could be created under `docs/standards/` without `AGENTS.md` or `CONTROL_PLANE_CONTRACT.md` pointing to it; the artifact then rotted.
4. **No explicit context-budget / truncation-safety contract.** Adapters (e.g., `CLAUDE.md`) were capped at 20 lines by `.claude/rules/coding-style.md`, but no contract explained why truncation safety matters for adapter-sized artifacts specifically.
5. **No explicit machine-readable-vs-prose contract.** Enforcement-tier gradient existed in `.claude/rules/patterns.md`, but there was no model-release-facing rule saying "machine-readable by default; prose only where a rule has no binary shape."
6. **No prompt-pack portability contract.** Provider-specific prompts leaked machine-local assumptions. There was no rule governing fail-closed behavior when a prompt ran on a provider without the required capability.

Each gap maps 1-to-1 to a dimension in `MODEL_RELEASE_READINESS_CONTRACT.md`.

---

## Strategy choice

Three canonical-doc strategies were considered:

1. **Embed readiness into `AGENTS.md` and `CONTROL_PLANE_CONTRACT.md` directly.** Rejected — would push AGENTS.md past the 20-line adapter limit.
2. **Write readiness inside each provider adapter (`CLAUDE.md`, `GEMINI.md`, `.codex/*`).** Rejected — provider adapters are thin audit-only surfaces under #2408; also duplicates content across providers.
3. **Strict canonical-doc strategy: update only `AGENTS.md` (one-line pointer) and `CONTROL_PLANE_CONTRACT.md` (cross-reference), create the contract and playbook as sibling standards.** **Chosen.**

Strategy 3 keeps provider entry surfaces thin, leaves `AI_REVIEW_ROUTING_POLICY.md` as the sole owner of review routing, and lets readers of `AGENTS.md` discover the readiness contract within the 20-line adapter budget.

---

## What was delivered under #2408

- `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` — standing contract covering five readiness dimensions.
- `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md` — step-by-step playbook split by provider-owned vs repo-owned drift.
- `tests/docs/test_workspace_hub_model_release_readiness.py` — executable checks for each dimension, anchor policy, scope, non-contradiction, and line-count compliance (limit sourced from `.claude/rules/coding-style.md`).
- `AGENTS.md` — adds the canonical readiness pointer within the 20-line budget by consolidating two Policy bullets.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — adds the cross-reference to both new standards.
- This package.

---

## What was not delivered (and why not)

- **No changes to `CLAUDE.md` / `GEMINI.md` / `.codex/**`.** Provider-entrypoint-shape normalization is out of scope for #2408; audit-only verification that they remain thin is the correct scope.
- **No tier-1 repo changes.** Tier-1 ecosystem inventory is out of scope for #2408.
- **No new enforcement hooks or scripts.** The readiness contract states the rules; enforcement promotion from prose → micro-skill → script → hook is tracked against `.claude/rules/patterns.md` and can happen in follow-up issues.
- **No new routing or review-policy changes.** Those are owned by `AI_REVIEW_ROUTING_POLICY.md`.

---

## Validation

- `uv run pytest tests/docs/test_workspace_hub_model_release_readiness.py -v` — targeted readiness suite passing; current run evidence belongs in the issue closeout comment.
- Manual audit: `CLAUDE.md`, `GEMINI.md`, `AGENTS.md` each remain ≤ 20 lines (limit sourced from `.claude/rules/coding-style.md`).
- Non-contradiction audit: new docs reference only the adapter paths defined in `CONTROL_PLANE_CONTRACT.md` (`AGENTS.md`, `.claude/`, `.codex/`, `.gemini/`) and introduce no new adapter roots.

---

## Residual risk

- The readiness contract is prose-with-tests; enforcement has not been promoted to pre-commit hooks. Future issues may convert dimensions 1–4 into script-tier or hook-tier enforcement per `.claude/rules/patterns.md`.
- Adapter line limits live in `.claude/rules/coding-style.md`. If that rule is ever rewritten without the `"CLAUDE.md, MEMORY.md, AGENTS.md, GEMINI.md must not exceed N lines"` phrasing, the line-limit test will fail loudly — this is intended (the test treats the policy file as the source of truth).
