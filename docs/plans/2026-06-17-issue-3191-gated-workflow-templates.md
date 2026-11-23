# Plan for #3191: Gated workflow templates (issue→plan→approve→implement→review→close) + cross-provider review workflow

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3191
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-17-plan-3191-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/workflows/` holds 5 YAMLs + a README, in **two informal schema dialects**:
  - **`metadata`/`config`/`steps`** — `pytest-validation.yaml`, `aggregation.yaml`, `checkpoint.yaml` (step keys: name, agent, parallel, command, output_file, success_criteria, depends_on, on_failure; has worker_contract + error_handling).
  - **`name`/`description`/`phases`** — `standard-development.yaml`, `data-analysis.yaml` (phase keys: description, delegation{tool, subagent_type, load_agent}, actions, output).
- Found: `standard-development.yaml` already encodes a 6-phase TDD flow but is **Claude-only** (hard-codes `tool: Task`, `subagent_type`, `@.claude/agent-library/...`) and has **no gates, no status labels, no approval point, no per-tier review depth** — exactly the gap.
- Found: `scripts/review/plan-review-fanout.sh` — real, provider-portable cross-review fan-out (Claude+Codex+Gemini, parallel, per-provider UNAVAILABLE degradation, writes `scripts/review/results/<date>-plan-<NNNN>-<provider>.md`). The review-workflow YAML must encode THIS invocation, not invent one.
- Found: `scripts/review/validate-review-output.sh` classifies an artifact VALID|NO_OUTPUT|SKIPPED_NETWORK|INVALID_OUTPUT — usable as a consensus input.
- Gap: no template encodes the gate chain as data (status labels, approval point, tier→review-depth).

### Standards
Not applicable (harness/governance).

### LLM Wiki pages consulted
None — workspace-hub-internal (`.claude/` out of scope of `wiki-sibling-routing.md`). Hence Client: N/A.

### Documents consulted
- `AGENTS.md` (lines 5–7) — canonical gate chain + "Reviews: APPROVE|MINOR|MAJOR".
- `config/agents/claude/SOUL.runtime.md` (Hard Gates 1–5) — tier→depth **T1=1 / T2=2 / T3=3 providers**; 3-agent default; never self-label plan-approved.
- `.claude/rules/completeness-before-close.md` — opt-in `gate:completeness`; thresholds code 90 / evidence 80; owner-only verified label.
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` + `config/ai-tools/provider-routing-policy.yaml` — authoritative machine-readable router (reference it, don't re-encode).
- `scripts/automation/validate_yaml.py` — existing validator, but enforces a `module/execution/inputs/outputs/logging` schema that NO workflow YAML matches → NOT a workflow validator (do not reuse).

### Gaps identified
- No canonical workflow YAML schema (two undocumented divergent dialects; no JSON Schema/validator).
- No gate-encoding template; no dry-run runner.
- Provider-neutrality gap (phase-dialect YAMLs hard-code Claude tooling).
- **Epic linkage discrepancy:** #3191 says "Parent epic #3058" but #3058's body lists only #3059–#3062. Flag at approval; do not assume linkage.

### Evidence
Issue #3191 OPEN (labels priority:medium, machine:multi, domain:harness, lane:claude). #3058 OPEN, body lists #3059–#3062 only. Files verified present/missing as listed above. `find -iname '*workflow*schema*'` → empty (no schema exists). N/A reproduction (authoring issue).
Distinct sources consulted: 8 (issue + AGENTS.md + SOUL + 3 rules + AI-review policy + existing workflow YAMLs/fanout).

---

## Approach / Deliverable
Three provider-neutral, gate-chain-encoding templates under `.claude/workflows/` + a JSON Schema they conform to + a pytest validation suite + a README "Instantiating a gated flow" section.

- **`issue-gate-chain.yaml`** (extends the `metadata/config/steps` dialect) — ordered gates mirroring AGENTS.md: issue → resource_intel → plan(`status:plan-review`, artifact path) → adversarial_review_plan(depth from tiers, runner `plan-review-fanout.sh`) → user_approval(`status:plan-approved`, actor USER_ONLY, self_approve: forbidden) → implement_tdd(precondition `status:plan-approved`, tests_before_code) → adversarial_review_code → completeness_gate(applies_when_label `gate:completeness`, verifier COMPLETENESS_OWNERS) → close(reason completed). `config.tiers` encodes T1→[claude], T2→[claude,codex], T3→[claude,codex,gemini].
- **`tdd-implementation.yaml`** — provider-neutral rewrite of `standard-development.yaml`'s shape: test_first → implement → refactor → review, integrating completeness-before-close.
- **`cross-provider-review-workflow.yaml`** — encodes the `plan-review-fanout.sh` fan-out + 3-agent default + `on_provider_unavailable: continue_and_record` degradation; references `provider-routing-policy.yaml`, doesn't re-encode assignments.
- **`schema/workflow.schema.json`** — draft-07 (matching the repo's `Draft7Validator` precedent); `kind: gated-workflow` discriminator scopes it to these templates (avoids colliding with legacy dialects / the module-config schema).

These are Level-0/1 (prose/data) on the `patterns.md` enforcement gradient — templates, NOT enforcement. Enforcement stays in `plan_approval_gate_check.py` / `completeness-gate.yml`; the plan must not over-claim that landing them enforces gates.

## Files to change
| Action | Path |
|---|---|
| Create | `.claude/workflows/schema/workflow.schema.json` |
| Create | `.claude/workflows/issue-gate-chain.yaml` |
| Create | `.claude/workflows/tdd-implementation.yaml` |
| Create | `.claude/workflows/cross-provider-review-workflow.yaml` |
| Create | `tests/workflow/test_gated_workflow_templates.py` |
| Modify | `.claude/workflows/README.md` (schema + gate-chain + instantiation sections) |
| Update | `docs/plans/README.md` (index) |
(`validate_yaml.py` NOT modified — its schema is for module configs, not workflows.)

## TDD test list (pytest, schema-validation lane — no new engine)
each-template-valid-yaml; each-matches-schema (`Draft7Validator`); gate-chain-ordered-set == AGENTS.md sequence; user_approval USER_ONLY + self_approve forbidden; status-labels ⊆ canonical set; tier depths T1/T2/T3 = 1/2/3; review-workflow references real `plan-review-fanout.sh` (exists on disk); review default 3-agent; degradation field present; tdd tests-before-code ordering; completeness gate opt-in (thresholds 90/80); provider-neutrality (no `Task`/`subagent_type`/`@.claude/agent-library` tokens); inline source citations present. Tests written red first.

## Risks / open questions
- Three YAML shapes in one dir → README documents which schema applies; `kind:` discriminator scopes the new schema.
- Templates encode but don't enforce → position as Level-0/1; cross-ref real enforcers.
- Provider-routing drift → reference `provider-routing-policy.yaml`, single source of truth.
- **RESOLVED (operator 2026-06-17):** templates-as-data (Level-0/1) accepted — enforcement stays in the existing gates (`plan_approval_gate_check.py`/`completeness-gate.yml`); these templates encode but do not enforce. #3191 now listed under #3058 (epic body updated).
- **Open:** `tdd-implementation.yaml` supersede vs coexist with `standard-development.yaml`? Recommend coexist.

## Adversarial review (T2 plan-stage) — DONE, findings folded in
1 adversarial lens run 2026-06-17 (NON-APPROVE; 3 MAJOR + 4 MINOR). Resolutions:
- **MAJOR — schema has no real validation entry point** (discriminator is naming-only; `validate_yaml.py` rejects these by design). FIX: the pytest suite IS the entry point — a fixture loads `schema/workflow.schema.json` and validates ONLY files with `kind: gated-workflow` (legacy dialects skipped). `validate_yaml.py` untouched.
- **MAJOR — provider-neutrality must be scoped per-template.** FIX: all THREE new templates must be neutral; `tdd-implementation.yaml` is a provider-neutral REWRITE of `standard-development.yaml`'s shape (legacy left in place, marked deprecated). Neutrality test is per-template (incl. example blocks).
- **MAJOR — README migration story missing.** FIX: README gets a "Choosing a workflow template" decision table covering all 8 files (5 legacy + 3 new), marking `standard-development.yaml`/`data-analysis.yaml` deprecated for new work.
- **MINOR — jsonschema is a dev-only dep** (pyproject `dependency-groups.dev`). FIX: tests run under `uv run --group dev pytest ...`; documented in TDD section + acceptance.
- **MINOR — fanout-reference test must verify the YAML actually calls the real path**, not just that the path exists. FIX: test extracts the runner field from the YAML and asserts it resolves to `scripts/review/plan-review-fanout.sh`.
- **MINOR — tier mapping is reference data**, not hardcoded per template (tier is assigned by the human at plan-review). FIX: `config.tiers` documented as lookup-only; templates don't force a tier.
- **MINOR — future-tense:** reframe Resource-Intel "Found:" as "currently exists" to avoid implying the plan authored existing files.
Cross-provider (Codex/Gemini) review via `plan-review-fanout.sh` still recommended at code stage.

## Acceptance criteria
Mirror issue #3191: 3 gate-chain templates schema-valid + provider-agnostic + inline-cited; review-workflow references real fanout + 3-agent default + degradation; tier depths exact; user_approval USER_ONLY; README instantiation section; tests pass; review artifacts posted.
