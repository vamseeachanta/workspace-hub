<!-- Canonical layout copy of terminal-1-sesa.md for stream slug 'sesa-lng'. Original launch-record file is preserved at docs/plans/overnight-prompts/2026-04-28-elements-wave/terminal-1-sesa.md. -->

We are in `/mnt/local-analysis/workspace-hub` on branch `main`.

You are Terminal 1 for the overnight Elements planning wave.

## Mission

Plan a bounded curated extraction pass for `workspace-hub#2541`: SESA LNG corpus from Elements.

This is planning-only. Do not implement extraction, do not copy raw files into git/wiki, and do not modify `/mnt/ace`.

## Issue context

Issue: https://github.com/vamseeachanta/workspace-hub/issues/2541
Umbrella: https://github.com/vamseeachanta/workspace-hub/issues/2540
Completed upstream: #2526, #2534, #2535, #2536.

Raw corpus source of record:
`/mnt/ace/doris/62092_sesa`

Wiki domain target:
`lng-projects`

Relevant existing artifacts:
- `.planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md`
- `.planning/intel/elements-to-llm-wiki/elements-wiki-classification.tsv`
- `.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv`
- `.planning/intel/elements-deep-extraction/elements-deep-extraction-report.md`
- `knowledge/wikis/lng-projects/`

## Allowed writes

Only write these paths:
- `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md`
- `.planning/intel/elements-overnight-wave/sesa-candidate-dossier.md`
- `.planning/intel/elements-overnight-wave/sesa-first-tranche.tsv`
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-1-sesa.md`

## Forbidden writes

Do not write to:
- `/mnt/ace/**`
- `knowledge/wikis/**`
- `docs/plans/README.md`
- `scripts/**`
- `.gitignore`
- any Terminal 2/3/4 paths
- unrelated dirty provider scorecard/report files

## Required work

1. Re-read issue #2541 with `gh issue view 2541`.
2. Inspect the candidate TSV and source tree metadata for `/mnt/ace/doris/62092_sesa` using read-only commands only.
3. Group likely high-value files into themes: reference studies, free-span/metocean, material specs/datasheets, subsea valves/TBE, logistics/project deliverables.
4. Produce `sesa-candidate-dossier.md` with evidence-backed observations and risks.
5. Produce `sesa-first-tranche.tsv` with no more than 20 candidate artifacts. Columns: priority, theme, content_kind, bytes, absolute_path, rationale, extraction_method, target_wiki_page, risk_note.
6. Draft the canonical plan file for #2541 with scope, resource intelligence, artifact map, TDD/validation, acceptance criteria, and approval boundary.
7. Write final result summary to `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-1-sesa.md`.
8. Post one concise GitHub comment on #2541 summarizing the result paths and whether it is ready for adversarial review. Do not add `status:plan-approved`.

## Hard boundaries

- Do not run broad PDF extraction.
- Do not process more than small metadata/path samples unless needed for planning.
- Do not copy raw data into git.
- Do not self-approve.
- If uncertain, write the uncertainty in the dossier rather than asking the user.

## Verification

Run:
- `test -s docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md`
- `test -s .planning/intel/elements-overnight-wave/sesa-candidate-dossier.md`
- `test -s .planning/intel/elements-overnight-wave/sesa-first-tranche.tsv`
- `test -s docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-1-sesa.md`

Final response should list files written and any blocker.
