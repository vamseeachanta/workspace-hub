# Archived Skill: `documentation-contract-plan-hardening`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/documentation-contract-plan-hardening`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/documentation-contract-plan-hardening`
Consolidation date: 2026-04-29

---

---
name: documentation-contract-plan-hardening
description: Harden a documentation/contract plan before adversarial review by mapping every issue-scope requirement to independent acceptance criteria and tests, especially for routing/indexing contracts.
version: 1.0.0
category: workspace-hub-learned
tags: [planning, adversarial-review, documentation, contract, routing, indexing]
---

# Documentation Contract Plan Hardening

Use when drafting a plan for a docs/standards/contract issue where the deliverable is a policy/contract/checklist rather than runtime code.

## Why this exists

In issue #2460 (tier-1 indexing and code-placement contract), all three adversarial reviewers returned MAJOR because the plan looked reasonable at a high level but failed a stricter standard:
- issue-required surfaces were bundled into generic "section presence" tests
- code-placement requirements cited `DATA_PLACEMENT.md` but were not independently testable
- a legacy-reference ban was specified as a vague negative test with no concrete forbidden pattern
- daily freshness linkage existed in prose but not as a dedicated validation target
- the plan relied on a local report artifact that was not clearly canonical on the repo's main branch

## Core rule

For documentation-contract plans, every correctness-critical scope item from the issue body must map to:
1. a named artifact section in the contract/checklist
2. an independent acceptance criterion
3. an independent test or validation check

If multiple issue-scope requirements are compressed into one generic test, adversarial reviewers will (correctly) call the plan under-specified.

## Hardening checklist before review

### 1. Build a scope-to-test matrix

Create a table in your notes before finalizing the plan:

| Issue requirement | Planned artifact section | Acceptance criterion | Test/validation |
|---|---|---|---|
| operator maps required | contract section "Required routing surfaces" | contract explicitly requires `docs/maps/<repo>-operator-map.md` | `test_contract_requires_operator_maps` |
| machine-readable registry | contract section "Required routing surfaces" | contract requires one canonical registry per repo | `test_contract_requires_registry` |
| code/tests/docs routing table | checklist + contract section | contract/checklist define routing-table semantics | `test_contract_requires_routing_table` |
| repo vs `/mnt/ace/data` placement | code-placement section | contract encodes data-placement rule | `test_contract_encodes_data_placement_rule` |
| daily freshness | freshness section | contract states cadence and follow-through issue | `test_contract_defines_daily_freshness_and_links_followup` |

Do not proceed until each issue-scope bullet has its own row.

### 2. Treat cited baseline docs as obligations, not decoration

If the plan cites a baseline document such as:
- `docs/standards/CONTROL_PLANE_CONTRACT.md`
- `docs/standards/FILE_STRUCTURE_TAXONOMY.md`
- `docs/standards/DATA_PLACEMENT.md`

then the plan must say exactly what rule from that document becomes part of the new contract and how that rule will be tested.

Bad:
- "DATA_PLACEMENT.md must be incorporated"

Good:
- "The contract must restate the repo-vs-`/mnt/ace/data` decision rule and checklist rows must verify whether each tier-1 repo's routing guidance points large/generated outputs off-repo."
- plus a dedicated acceptance criterion and test.

### 3. Avoid vague negative tests for legacy references

If you need to retire a legacy pattern, do NOT write a test like:
- `test_contract_avoids_legacy_pattern`

unless the plan defines:
- the exact forbidden string(s) or regex
- the allowed migration/retirement wording
- which files the guard applies to

Better pattern:
- one test for required positive retirement language
- one test for forbidden legacy references

Example split:
- `test_contract_declares_legacy_product_doc_conventions_retired`
- `test_contract_does_not_recommend_<exact_legacy_pattern>`

### 4. Distinguish canonical repo evidence from local attestation

If a plan cites a local artifact that may not exist on the canonical branch yet (for example a newly generated report in a dirty working tree), say so explicitly.

Use one of these two patterns:

1. **Canonical evidence pattern**
- artifact exists on tracked branch / repo state expected by reviewers
- safe to cite as repo truth

2. **Local attestation pattern**
- artifact exists only locally right now
- use it as planning input, but acknowledge that implementation must either:
  - land the artifact canonically, or
  - remove dependence on it before approval

If you don't disambiguate this, reviewers may flag the plan as coupled to unpublished state.

### 5. For contract/checklist pairs, test both discoverability and linkage

When the deliverable includes both a contract doc and a checklist doc, include tests for:
- contract exists
- checklist exists
- contract links checklist
- checklist references contract or derived authority
- docs index links both from a trusted discovery surface

Otherwise the checklist can become an orphan artifact.

### 6. Name artifacts to match issue scope

If the issue title says "indexing and code-placement contract" but the planned file is named only `INDEXING_CONTRACT`, reviewers may treat that as scope loss.

Either:
- include the full scope in the filename, or
- state explicitly in the plan that the contract file covers both topics despite the shorter filename

## Recommended validation pattern for docs-contract issues

Prefer many small assertions over one umbrella test.

Bad:
- `test_contract_contains_required_sections`

Better:
- `test_contract_requires_agents_md`
- `test_contract_requires_readme`
- `test_contract_requires_docs_readme`
- `test_contract_requires_operator_map`
- `test_contract_requires_machine_readable_registry`
- `test_contract_requires_routing_table`
- `test_contract_encodes_data_placement_rule`
- `test_contract_declares_daily_freshness_rule`
- `test_contract_links_followup_issue_2465`

## When to use this skill

Use before sending any documentation/contract plan to Codex/Gemini/Claude for adversarial review, especially when:
- the issue is in `cat:documentation` or `cat:harness`
- the deliverable is a contract, policy, checklist, or governance doc
- the issue body has a bulleted scope that can be converted into testable requirements
- local reports or freshly generated artifacts are being cited as planning evidence

## Outcome goal

A reviewer should be able to point at each issue-scope bullet and immediately see:
- where it lands in the deliverable
- which acceptance criterion covers it
- which dedicated validation proves it

If not, the plan is still too soft for adversarial review.
