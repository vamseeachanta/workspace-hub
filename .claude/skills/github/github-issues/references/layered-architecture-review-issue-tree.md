# Layered Architecture Review Issue Trees

Use when the user asks to create GitHub feature/issues to review broad system layers such as data, execution, compute, outputs, reports, dashboards, PDFs, or chatbots.

## Pattern

1. Create one umbrella issue for the cross-layer architecture review.
2. Create child issues for each independently reviewable layer, usually:
   - Data layer: raw sources, private/local raw data, public knowledge repos, promotion boundaries, confidentiality boundaries.
   - Execution layer: input contracts, tools/code execution, compute/runtime placement, provenance/evidence manifests.
   - Report layer: raw outputs, client-facing HTML, limited PDFs, dashboards, chatbot/query surfaces, export boundaries.
3. Link children from the umbrella and link the umbrella from each child.
4. For workspace-hub gated work, draft one plan artifact per issue under `docs/plans/` and add plan-index rows.
5. Post a GitHub comment on each issue with the draft plan path, commit, and current gate state.
6. If the user says they will personally review/add sources, stop at draft-plan state. Do not run adversarial plan review or apply `status:plan-review` until that source-curation pass is complete.

## Source inventory seed checklist

Seed the issue/plan inventory with enough concrete classes for the user to refine:

- `/mnt` workspace/control-plane data and mounted local-analysis paths.
- Tier-1 repo checkouts and repo-owned data folders.
- Public/API data sources such as world-energy or standards/literature sources.
- Private/client/project data; mark private by default unless explicitly public.
- Raw-like LLM/wiki staging and public wiki content as separate classes.
- Execution artifacts: manifests, logs, provenance, evidence bundles, generated intermediate files.
- Report artifacts: raw outputs, HTML deliverables, limited PDFs, dashboards, chatbot/query surfaces.

Before writing durable paths into the issue body, verify likely aliases and non-existent targets. For example, if both `/mnt/ace-data` and `/mnt/ace` are mentioned, resolve whether one is a symlink alias; if private wiki targets are planned but not created, label them planned targets rather than existing repos. Capture path corrections explicitly so the future plan does not canonize stale names.

For AI-agent data-governance issues, also use `references/data-governance-usage-level-matrix.md`. Include the four canonical usage levels (`raw-data`, `readable-raw-data`, `llm-wiki-private`, `llm-wiki-public`), promotion gates, source-class/citation rules, and fail-closed checker expectations. Keep private/client and public llm-wiki routes distinct.

## Decision propagation and output residency

When the user adds a cross-cutting architecture decision after the issue tree exists, update the umbrella issue and every affected child issue immediately before asking for approval or re-review. Do not leave the decision stranded in only the latest chat response or one GitHub comment.

For data/execution/report architecture reviews, explicitly model outputs as governed data with the same residency discipline as inputs:

- Client/private inputs produce client/private raw outputs, reports, chatbot indexes, and curated learnings unless explicitly sanitized and promoted.
- Domain-private inputs produce domain-private outputs and domain-private llm-wiki/corpus updates.
- Public inputs or sanitized derivatives may produce public llm-wiki/public-facing artifacts only after a promotion gate.
- Execution manifests should carry both `input_residency` and `output_residency` metadata, plus source-class/citation separation where applicable.

Use a lifecycle model instead of a one-way pipeline when reports or chatbots can generate durable knowledge:

```text
inputs → execution → reports/chatbots → curated output learnings → appropriate llm-wiki/corpus tier
```

A plan is not approval-ready if this lifecycle/residency decision is only present in a comment but missing from the plan artifacts and affected child issue scopes.

## Gate handling

- Treat these as planning/governance issues, not implementation.
- Keep the plan future-tense and avoid claiming the inventory is complete before the user's source pass.
- Use issue comments for traceability, but state clearly when plans are draft and not approval-ready.
- Do not self-apply `status:plan-approved`; do not move to `status:plan-review` before adversarial review is actually complete.
- If the user asks for a re-review batch and to mark the plans for their review, run the adversarial reviews first, preserve every provider artifact, then move to `status:plan-review` even when verdicts are `MAJOR`. In that case the comment must preserve the `MAJOR` verdicts verbatim and say “awaiting user decision / not approved / no implementation until explicit approval.”

## Verification

After creation/update, verify:

- issue URLs, titles, and labels render correctly;
- parent/child links resolve;
- plan files are committed and pushed if created;
- issue comments include the correct plan paths and gate state;
- unrelated dirty worktree state was not swept into the commit.