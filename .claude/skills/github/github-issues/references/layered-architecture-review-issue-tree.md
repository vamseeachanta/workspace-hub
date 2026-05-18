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

## Client/project data-cycle decomposition

When the user asks for feature/issues to review the data, execution, and report layers for a client or private project, split the tree by stable decision boundaries rather than by every artifact type:

1. Umbrella: client/project data-cycle readiness and governance across data → execution → report/output surfaces.
2. Source/archive posture: freeze or deprecate any legacy raw-data repo/path that should stop receiving new source material; specify local-only/archive behavior and write-guard expectations.
3. Private knowledge target: define the private/local llm-wiki or readable-raw-data target separately from the public wiki; mark planned targets as planned if not yet created.
4. Promotion ledger: require raw → readable/private-wiki → public/sanitized promotion records with confidence/completeness scoring and revision triggers as models improve.
5. Output/report scaffolding: govern raw outputs, client-facing HTML, limited PDFs, dashboards/chatbots, and evidence packs as first-class data products with manifests and residency metadata.

This decomposition keeps the user-review surface small while preserving the key architectural contracts. If the user only asked to “create GH feature/issues,” stop after creating/verifying issues unless they also asked for plan artifacts; do not silently escalate to implementation or plan-review state.

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

## Local archive path conflict handling

If the user asks to move or localize a client/project raw-data repo into a mounted archive path, treat a pre-existing destination directory as a safety boundary, not as permission to merge:

1. Verify both source and destination state before acting: git/non-git status, remote/branch for the source clone, top-level destination inventory, and approximate sizes.
2. If the destination already exists and is materially larger or non-git, designate it as a candidate canonical archive only after recording evidence; do not overwrite, rename, merge, or delete either side in the same issue-creation pass.
3. Create/update an issue for the archive/freeze decision that requires a uniqueness comparison before retirement of the old clone.
4. Post a GitHub comment capturing the observed paths, sizes, git status, and the explicit non-action taken. This prevents later agents from assuming the move completed or from retrying destructively.
5. Keep private wiki/readable-source repo creation separate from raw archive movement. The wiki scaffold can proceed when its target is empty/new, but raw archive retirement remains gated on comparison and user approval.

## Parent contract execution pattern

When the umbrella architecture issue becomes explicitly approved for execution, keep the implementation bounded to the cross-layer contract. Do not absorb the child issue details for each layer.

Recommended contract artifacts:

- A concise architecture contract document defining the shared lifecycle, surface codes, and child-issue consumption boundaries.
- A structured fixture or machine-readable matrix for source classes and enforcement fields.
- A generated human-readable markdown matrix for reviewer consumption.
- Tests that enforce the contract instead of only checking that docs exist.

For data/execution/report/chatbot architecture contracts, include these fields in the structured matrix when applicable:

- `source_class`
- `owner`
- `canonical_path` or source ID
- `layer`
- `level`
- `allowed_artifacts`
- `forbidden_artifacts`
- `retention_expectations`
- `publication_rules`
- `public_posture`
- `promotion_gate`
- `input_residency`
- `output_residency`
- `report_chatbot_eligibility`

Test patterns that caught real drift:

1. Required schema: fail if any source row omits a contract field, especially `input_residency` / `output_residency`.
2. Seed coverage: assert all expected source classes exist so the parent contract does not silently drop raw data, private staging, public wiki, execution, or report artifacts.
3. Fail-closed posture: private/restricted rows must forbid public outputs unless an explicit gate exists.
4. Universal public eligibility gate: any row, including public or mixed rows, that mentions a public destination (`public report`, `public llm-wiki`, public chatbot/export surface) must have `gate` in the promotion gate text.
5. Row-keyed markdown drift: parse the generated markdown table by `source_class` and compare each rendered row to the fixture in exact column order. Do not use global string-presence checks; they miss swapped cells, duplicated values, and missing row-specific fields.
6. Contract wording: assert the contract names the lifecycle transitions and architecture surfaces (`A-DATA`, `A-EXEC`, `A-REPORT`, and curated learning/corpus tier where used).

Reviewer lesson: if one provider review is unavailable because of startup/tooling issues, document the failed review artifact and proceed only with targeted validation plus another substantive review path. Do not convert an unavailable review into a negative claim about the provider.

## Adversarial MAJOR hardening pattern

When adversarial review of a layered data/execution/report issue returns `MAJOR`, treat it as a new RED-GREEN pass, not as prose cleanup:

1. Convert each repeated reviewer finding into targeted tests before changing the architecture docs. Examples from data/execution/report governance:
   - schemas must use `additionalProperties: false` where the contract is closed;
   - schemas must reject inline raw/private payload keys such as `raw_data`, `data_dump`, `client_payload`, and `source_text`;
   - promotion/publication gates must be closed enums, not prose strings;
   - report claim entries must bind to source IDs, artifact IDs, source class, sanitization gate, promotion gates, and evidence references;
   - backlog issue commands that use `--body-file` must point at real tracked body files;
   - markdown command fences must be balanced.
2. Run the hardened tests and preserve the failing output as the RED checkpoint.
3. Patch schema/docs/fixtures until the targeted tests pass. Keep fixture changes contract-shaped; do not relax tests to match loose prose.
4. Create every referenced follow-up issue body file before declaring the issue backlog validated. Missing body files are a release-blocking artifact defect because future `gh issue create --body-file ...` commands will fail.
5. Rerun targeted tests, then broader architecture tests, diff whitespace checks, and legal/security scans before commit.
6. Rerun adversarial review after GREEN. A previous `3x MAJOR` review is not resolved merely because local targeted tests passed.
7. If tool/time limits interrupt mid-hardening, explicitly report the work as incomplete and list the exact remaining body files/tests. Do not commit, close, or move labels while the RED/GREEN loop is unresolved.

## Gate handling

- Treat these as planning/governance issues, not implementation.
- Keep the plan future-tense and avoid claiming the inventory is complete before the user's source pass.
- Use issue comments for traceability, but state clearly when plans are draft and not approval-ready.
- Do not self-apply `status:plan-approved`; do not move to `status:plan-review` before adversarial review is actually complete.
- If the user asks for a re-review batch and to mark the plans for their review, run the adversarial reviews first, preserve every provider artifact, then move to `status:plan-review` even when verdicts are `MAJOR`. In that case the comment must preserve the `MAJOR` verdicts verbatim and say “awaiting user decision / not approved / no implementation until explicit approval.”
- If the user explicitly approves the plan with architecture notes, patch those notes into the plan artifact before flipping labels. Example note classes from data/execution/report architecture: confusing symlink aliases must be marked non-canonical and slated for cleanup, active sibling repo placement must be evaluated rather than silently moved, and newly named private wiki targets must be added as private targets.

## Verification

After creation/update, verify:

- issue URLs, titles, and labels render correctly;
- parent/child links resolve;
- plan files are committed and pushed if created;
- issue comments include the correct plan paths and gate state;
- approved parent contract implementation has targeted tests, legal/security scan, review artifacts, commit/push evidence, and issue closeout evidence;
- unrelated dirty worktree state was not swept into the commit.