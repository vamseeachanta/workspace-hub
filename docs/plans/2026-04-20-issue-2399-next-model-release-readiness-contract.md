# Plan for #2399: Define next-model-release readiness contract for repo ecosystem

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2399
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2399-claude.md | scripts/review/results/2026-04-20-plan-2399-codex.md | scripts/review/results/2026-04-20-plan-2399-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/standards/CONTROL_PLANE_CONTRACT.md` — defines repo entry points, provider adapters, and convergence expectations across repos.
- Found: `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — defines three-agent adversarial review defaults and provider roles for planning and implementation review.
- Found: root `AGENTS.md`, `CLAUDE.md`, `.gemini/GEMINI.md`, and `config/agents/codex/config.toml` — concrete current control-plane entry/config surfaces already in the repo.
- Found: `config/agents/claude/settings.json`, `config/agents/gemini/settings.json`, and `scripts/_core/sync-agent-configs.sh` — concrete parity/config sync surfaces relevant to Hermes/provider readiness and #1583 follow-through.
- Found: `.claude/rules/README.md`, `.claude/rules/patterns.md`, and `.claude/rules/coding-style.md` — live harness-rule surfaces that a `cat:harness` readiness contract must consider.
- Gap: no single contract defines what makes the repo ecosystem resilient to the next model/provider release across prompts, adapters, session logs, tool semantics, eval/smoke coverage, provider/version inventory, and fixture-backed golden-task baselines.

### Standards
| Standard | Status | Source |
|---|---|---|
| Control-plane contract | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| AI review routing policy | done | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
| Current provider settings review cadence | partial | issue #2089 |

### LLM Wiki pages consulted
- No relevant wiki pages; this is control-plane governance and release-readiness work rooted in standards and issue workflow policy.

### Documents consulted
- Related issue #2089 — weekly Hermes + AI provider settings review; useful operational input but not a full readiness contract.
- Related issue #1583 — Hermes config parity via repo ecosystem templates; useful parity baseline and source for Hermes-facing surfaces.
- Related issue #2253 — provider-routing hardening for Gemini confidence; shows provider-specific drift already exists.
- Related issue #2323 — cross-AI plan-review fan-out; identifies a workflow that must remain robust across model changes.
- Existing issue body for #2399 — explicitly requires follow-up issues for the highest-risk gaps discovered and a standing reusable contract.

### Contract-boundary rule
- `docs/standards/CONTROL_PLANE_CONTRACT.md` remains the canonical entry-point/adapter-location standard.
- `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` will define release-readiness checks, smoke battery expectations, version-inventory expectations, and upgrade decision flow.
- The readiness contract must reference the control-plane contract, not supersede it.
- Discoverability is required: the implementation must add explicit pointers to the new readiness surfaces from `AGENTS.md`, `CLAUDE.md`, `.codex/CODEX.md`, `.gemini/GEMINI.md`, and `docs/standards/CONTROL_PLANE_CONTRACT.md` so agents encounter the contract through existing control-plane entry points.
- Scope stop-line: this issue defines the contract, fixture corpus, baseline inventory, and issue creation logic, but does not implement or operate the future smoke runner itself.

### Gaps identified
- No checklist for “model-release ready” status at repo/ecosystem level.
- No golden-task / smoke-eval battery covering planning, review, navigation, and handoff workflows across providers.
- No explicit upgrade playbook separating provider drift from repo-owned fixes.
- No consolidated contract for log/export/schema resilience as models and CLIs evolve.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-20-issue-2399-next-model-release-readiness-contract.md |
| Cohesive main review package | docs/reports/2026-04-20-issue-2399-model-release-readiness-package.md |
| Provider/version baseline inventory | docs/reports/2026-04-20-issue-2399-provider-version-baseline.md |
| Standing contract | docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md |
| Upgrade playbook | docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md |
| Reusable eval battery spec | config/ai/model-release-smoke-battery.yaml |
| Smoke battery runner contract | docs/standards/MODEL_RELEASE_SMOKE_RUNNER_CONTRACT.md |
| Golden-task fixture corpus | tests/fixtures/model_release_battery/ |
| Session/export/log schema fixture inventory | docs/reports/2026-04-20-issue-2399-session-export-log-schema-inventory.md |
| Created follow-up issues summary | docs/reports/2026-04-20-issue-2399-follow-up-issues-created.md |
| Discoverability anchors | AGENTS.md; CLAUDE.md; .codex/CODEX.md; .gemini/GEMINI.md; docs/standards/CONTROL_PLANE_CONTRACT.md |
| Plan review — Claude | scripts/review/results/2026-04-20-plan-2399-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-20-plan-2399-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-20-plan-2399-gemini.md |
| Docs updates | docs/plans/README.md |

---

## Deliverable

A standing repo-ecosystem readiness contract plus reusable smoke-battery and highest-risk follow-up issue drafts for adopting future model/provider releases safely.

---

## Pseudocode

```
inventory provider-sensitive workflow surfaces across the repo ecosystem: workspace-hub plus tier-1 repo adapters, prompt-pack files, session logs/exports, review flows, handoff flows, tool semantics, `config/agents/*`, and `.claude/rules/*`
group observed failure modes into repo-owned drift vs provider-owned drift
write one cohesive main review package that contains the ecosystem inventory, gap analysis, and release-readiness recommendations in a single reviewable artifact
write a standing readiness contract in `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` that explicitly references but does not replace `CONTROL_PLANE_CONTRACT.md`
write a separate upgrade playbook in `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md`
encode a reusable golden-task / smoke battery spec in `config/ai/model-release-smoke-battery.yaml`
define the execution path and schema contract for that battery in `docs/standards/MODEL_RELEASE_SMOKE_RUNNER_CONTRACT.md`
commit a fixture-backed golden-task corpus under `tests/fixtures/model_release_battery/` with expected outcomes/baselines for planning, adversarial review, repo navigation, code modification discipline, and session handoff integrity
write a schema fixture inventory for session/export/log surfaces using real known artifact types and paths
run a gap analysis against current ecosystem surfaces and rank the highest-risk gaps with an explicit threshold/rubric
for each highest-risk gap above threshold:
    create a follow-up GitHub issue via `gh issue create` and record it in a created-issues summary artifact
outline upgrade workflow: detect release, run eval battery, classify failures, patch repo-owned surfaces, document provider-specific exceptions, record provider/version baseline
add discoverability anchors in AGENTS/provider adapters/control-plane standard so the new readiness contract is reachable from canonical entry points, including `.codex/CODEX.md`
write cohesive package, contract, playbook, battery spec, runner contract, fixture corpus, schema inventory, provider baseline, and created-issues summary
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/reports/2026-04-20-issue-2399-model-release-readiness-package.md | cohesive main review package combining ecosystem inventory, gap analysis, and readiness recommendations |
| Create | docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md | standing reusable contract for future release waves |
| Create | docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md | explicit major-release adoption playbook |
| Create | docs/standards/MODEL_RELEASE_SMOKE_RUNNER_CONTRACT.md | defines runner/schema/execution path for smoke battery |
| Create | config/ai/model-release-smoke-battery.yaml | reusable provider-agnostic eval battery spec |
| Create | tests/fixtures/model_release_battery/ | fixture-backed golden-task corpus with expected outcomes |
| Create | docs/reports/2026-04-20-issue-2399-provider-version-baseline.md | current provider/version baseline for future upgrade comparisons |
| Create | docs/reports/2026-04-20-issue-2399-session-export-log-schema-inventory.md | schema-bearing fixture inventory for session/export/log surfaces |
| Create | docs/reports/2026-04-20-issue-2399-follow-up-issues-created.md | records the actual follow-up issues created for highest-risk gaps |
| Update | AGENTS.md | add discoverability pointer to readiness contract and playbook |
| Update | CLAUDE.md | add discoverability pointer for Claude entry path |
| Create or Update | .codex/CODEX.md | add Codex discoverability anchor and normalize missing adapter doc if absent |
| Update | .gemini/GEMINI.md | add discoverability pointer for Gemini entry path |
| Update | docs/standards/CONTROL_PLANE_CONTRACT.md | anchor the new readiness contract from the canonical control-plane standard |
| Update | docs/plans/README.md | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_main_package_covers_required_sections | cohesive package contains ecosystem inventory + gap analysis + recommendations | main package markdown | required section headers present |
| test_fixture_corpus_contains_golden_tasks_with_expected_outcomes | evaluation corpus is real, not prose-only | `tests/fixtures/model_release_battery/` | fixtures + expected outputs for 5 workflow classes |
| test_contract_defines_readiness_dimensions | readiness is explicit and auditable | standing contract | named dimensions/checklist |
| test_upgrade_playbook_separates_provider_vs_repo_drift | playbook handles ownership correctly | upgrade playbook | explicit provider-owned vs repo-owned branches |
| test_smoke_battery_schema_matches_runner_contract | eval battery is consumable by a runner | yaml battery + runner contract | matching schema/fields |
| test_prompt_pack_portability_is_covered | portability is not omitted | standing contract + playbook | provider/machine portability section present |
| test_session_export_log_schema_inventory_uses_real_fixtures | schema resilience is evidence-backed | fixture inventory | known artifact types/paths enumerated |
| test_discoverability_anchors_reference_new_contract | new surfaces are reachable from canonical entry points | AGENTS/CLAUDE/CODEX/GEMINI/control-plane docs | explicit links/references present |
| test_follow_up_issues_are_created_for_high_risk_gaps | top gaps become actionable follow-ups | ranked risk list | created issue references with severity/ownership |
| test_contract_boundary_with_control_plane_is_explicit | standards do not overlap ambiguously | contract text | references CONTROL_PLANE_CONTRACT without superseding it |

---

## Acceptance Criteria

- [ ] A standing contract exists at `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md`
- [ ] A reusable eval battery spec exists at `config/ai/model-release-smoke-battery.yaml`
- [ ] A smoke battery runner contract exists at `docs/standards/MODEL_RELEASE_SMOKE_RUNNER_CONTRACT.md`
- [ ] An upgrade playbook exists at `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md`
- [ ] A cohesive main package exists at `docs/reports/2026-04-20-issue-2399-model-release-readiness-package.md`
- [ ] A provider/version baseline inventory exists at `docs/reports/2026-04-20-issue-2399-provider-version-baseline.md`
- [ ] A session/export/log schema fixture inventory exists at `docs/reports/2026-04-20-issue-2399-session-export-log-schema-inventory.md`
- [ ] A golden-task fixture corpus exists at `tests/fixtures/model_release_battery/` with expected outcomes for the 5 required workflow classes
- [ ] A created-follow-up-issues summary exists at `docs/reports/2026-04-20-issue-2399-follow-up-issues-created.md`
- [ ] The contract defines readiness dimensions and a checklist for repo/ecosystem use
- [ ] The cohesive main package covers ecosystem inventory, gap analysis, and readiness recommendations across workspace-hub and tier-1 repos
- [ ] The upgrade playbook separates provider drift from repo-owned remediation responsibilities
- [ ] The smoke battery spec is consumable via the runner contract
- [ ] The contract/playbook explicitly cover prompt-pack portability across providers and machines
- [ ] The schema fixture inventory uses real known artifact types/paths for session/export/log resilience
- [ ] The highest-risk gaps produce actual follow-up GitHub issues, not only drafts
- [ ] `AGENTS.md`, `CLAUDE.md`, `.codex/CODEX.md`, `.gemini/GEMINI.md`, and `docs/standards/CONTROL_PLANE_CONTRACT.md` all contain discoverability anchors to the new readiness surfaces
- [ ] The readiness contract explicitly references but does not supersede `CONTROL_PLANE_CONTRACT.md`
- [ ] Review artifacts are posted to `scripts/review/results/`

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

- **Risk:** the contract could become too abstract if it does not anchor to concrete workflow surfaces already known to drift.
- **Risk:** provider-specific release quirks could be mistaken for repo defects, causing unnecessary repo churn.
- **Open:** should the first readiness battery optimize for breadth across many workflows or depth on the highest-value workflows only?

---

## Complexity: T2

**T2** — bounded governance/architecture plan producing a reusable contract and eval framework without immediate implementation code.
