# Plan for #2408: Workspace-hub-only model-release readiness contract and upgrade playbook

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2408
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2408-claude.md | scripts/review/results/2026-04-20-plan-2408-codex.md | scripts/review/results/2026-04-20-plan-2408-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/standards/CONTROL_PLANE_CONTRACT.md` — defines canonical workspace-hub entrypoints (`AGENTS.md`, `.claude/`, `.codex/`, `.gemini/`) and adapter roles.
- Found: `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — defines cross-provider review expectations that the readiness contract must preserve during model-release changes.
- Found: `config/agents/codex/config.toml`, `config/agents/claude/settings.json`, `config/agents/gemini/settings.json` — concrete provider-config surfaces already managed in workspace-hub.
- Found: `scripts/_core/sync-agent-configs.sh` — concrete config-parity/sync surface relevant to provider/model-release readiness.
- Found: `.claude/rules/README.md`, `.claude/rules/patterns.md`, `.claude/rules/coding-style.md` — live machine-readable/prose governance surfaces the contract must classify explicitly.
- Gap: no workspace-hub-only readiness contract currently defines context-budget handling, truncation-safe artifact design, prompt-pack portability, machine-readable-vs-prose guidance, or provider-upgrade procedure in one canonical place.

### Standards
| Standard | Status | Source |
|---|---|---|
| Control-plane contract | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| AI review routing policy | done | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
| Harness retrieval requirement for `cat:harness` work | done | `docs/plans/README.md` |

### LLM Wiki pages consulted
- Not applicable; this issue is workspace-hub control-plane governance, not domain-wiki content.

### Documents consulted
- Related issue #2399 — broad parent readiness effort; this child exists because review showed the parent was too broad.
- Related issue #2089 — weekly Hermes + AI provider settings review; useful operational context.
- Related issue #1583 — Hermes config parity via repo ecosystem templates; useful for Hermes-facing surfaces.
- `docs/plans/README.md` — for harness issues, required retrieval sources include `config/agents/` and `.claude/rules/`.
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` — documentation-boundary reference for keeping this child scoped to durable guidance rather than transient execution artifacts.

### Gaps identified
- No single workspace-hub-only contract for model-release readiness.
- No explicit workspace-hub upgrade playbook for new provider/model versions.
- No canonical discoverability anchors from existing workspace-hub entrypoints to readiness guidance.
- No explicit contract language for context-budget/truncation-safe design and machine-readable-rules-vs-prose guidance.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-20-issue-2408-workspace-hub-model-release-readiness-contract-and-upgrade-playbook.md |
| Main deliverable package | docs/reports/2026-04-20-issue-2408-workspace-hub-readiness-package.md |
| Standing contract | docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md |
| Upgrade playbook | docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md |
| Contract/anchor tests | tests/docs/test_workspace_hub_model_release_readiness.py |
| Discoverability anchors | AGENTS.md; docs/standards/CONTROL_PLANE_CONTRACT.md; provider adapters remain thin and are referenced, not expanded |
| Plan review — Claude | scripts/review/results/2026-04-20-plan-2408-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-20-plan-2408-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-20-plan-2408-gemini.md |
| Docs updates | docs/plans/README.md |

---

## Deliverable

A workspace-hub-only readiness contract and upgrade playbook, anchored from canonical entrypoints, that defines how this repo adapts safely to future provider/model releases.

---

## Pseudocode

```
inventory workspace_hub control-plane surfaces only: AGENTS.md, provider adapter directories, config/agents, .claude/rules, sync-agent-configs, review-routing policy
extract the readiness dimensions this child must cover: context-budget/truncation safety, machine-readable-vs-prose guidance, prompt-pack portability, discoverability, upgrade procedure
choose one consistent anchor strategy: add discoverability to AGENTS.md and CONTROL_PLANE_CONTRACT.md while keeping provider adapters thin and unchanged except where they already act as canonical pointers
write one cohesive workspace-hub package summarizing current surfaces, gaps, contract boundaries, and explicit out-of-scope tier-1 work
write a standing contract in docs/standards that references but does not supersede CONTROL_PLANE_CONTRACT.md
write a separate upgrade playbook focused on workspace-hub-only release adoption steps
add explicit test file `tests/docs/test_workspace_hub_model_release_readiness.py` covering required dimensions, scope boundary, anchor presence, non-contradiction with CONTROL_PLANE_CONTRACT, and line-count compliance for thin adapters
stop at workspace-hub scope and explicitly defer tier-1 repo ecosystem inventory and Codex adapter-shape changes to sibling/follow-up issues
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/reports/2026-04-20-issue-2408-workspace-hub-readiness-package.md | cohesive summary of workspace-hub surfaces, gaps, and recommendations |
| Create | docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md | standing workspace-hub readiness contract |
| Create | docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md | explicit workspace-hub upgrade playbook |
| Update | AGENTS.md | add discoverability pointer |
| Update | CLAUDE.md | add discoverability pointer |
| Update | GEMINI.md | add discoverability pointer |
| Update | docs/standards/CONTROL_PLANE_CONTRACT.md | anchor readiness contract from canonical control-plane standard |
| Update | docs/plans/README.md | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_contract_covers_context_budget_and_truncation_safety | required dimension is explicit | contract text | named section/requirements present |
| test_contract_covers_machine_readable_vs_prose_guidance | rules-vs-prose dimension is explicit | contract text | named section/requirements present |
| test_contract_covers_prompt_pack_portability | portability dimension is explicit | contract/playbook text | provider/machine portability section present |
| test_upgrade_playbook_separates_provider_vs_repo_drift | playbook handles ownership correctly | playbook text | provider-owned vs repo-owned branches present |
| test_discoverability_anchors_exist_in_workspace_entrypoints | readiness docs are reachable | AGENTS/CLAUDE/GEMINI/control-plane docs | explicit links/references present |
| test_scope_is_workspace_hub_only | issue stays narrowly scoped | package + contract | explicit out-of-scope note for tier-1 ecosystem inventory |

---

## Acceptance Criteria

- [ ] `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` exists
- [ ] `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md` exists
- [ ] `docs/reports/2026-04-20-issue-2408-workspace-hub-readiness-package.md` exists
- [ ] contract explicitly covers context-budget/truncation-safe artifact design
- [ ] contract explicitly covers machine-readable rules/skills vs prose-only guidance
- [ ] contract explicitly covers prompt-pack portability for workspace-hub workflows
- [ ] discoverability anchors exist in the chosen canonical workspace-hub entrypoints
- [ ] package/contract explicitly state that tier-1 ecosystem inventory is out of scope for this issue
- [ ] review artifacts are posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Awaiting review |
| Codex | PENDING | Awaiting review |
| Gemini | PENDING | Awaiting review |

**Overall result:** PENDING

Revisions made based on review:
- none yet

---

## Risks and Open Questions

- **Risk:** root-vs-hidden provider adapter conventions may still contain ambiguity; the contract must describe current workspace-hub reality without inventing a new convention.
- **Risk:** adding too many anchors could violate thin-adapter expectations; the updates should stay minimal and discoverability-focused.
- **Open:** should `CODEX.md` also be introduced as a root thin adapter in workspace-hub, or should this child strictly document current state and defer Codex adapter shape to later work?

---

## Complexity: T2

**T2** — bounded governance/documentation plan focused only on workspace-hub control-plane readiness, with no tier-1 ecosystem inventory or runner implementation.
