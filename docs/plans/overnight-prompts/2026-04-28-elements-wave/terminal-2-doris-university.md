We are in `/mnt/local-analysis/workspace-hub` on branch `main`.

You are Terminal 2 for the overnight Elements planning wave.

## Mission

Plan a bounded extraction and taxonomy pass for `workspace-hub#2542`: Doris University training corpus.

This is planning-only. Do not implement extraction, do not copy raw files into git/wiki, and do not modify `/mnt/ace`.

## Issue context

Issue: https://github.com/vamseeachanta/workspace-hub/issues/2542
Umbrella: https://github.com/vamseeachanta/workspace-hub/issues/2540
Completed upstream: #2526, #2534, #2535, #2536.

Raw corpus source of record:
`/mnt/ace/doris/training`

Wiki domain target:
`engineering` with Doris/training context.

Relevant existing artifacts:
- `.planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md`
- `.planning/intel/elements-to-llm-wiki/elements-wiki-classification.tsv`
- `.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv`
- `knowledge/wikis/engineering/`

## Allowed writes

Only write these paths:
- `docs/plans/2026-04-28-issue-2542-elements-doris-university-training-plan.md`
- `.planning/intel/elements-overnight-wave/doris-university-taxonomy.md`
- `.planning/intel/elements-overnight-wave/doris-university-first-tranche.tsv`
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-2-doris-university.md`

## Forbidden writes

Do not write to:
- `/mnt/ace/**`
- `knowledge/wikis/**`
- `docs/plans/README.md`
- `scripts/**`
- `.gitignore`
- any Terminal 1/3/4 paths
- unrelated dirty provider scorecard/report files

## Required work

1. Re-read issue #2542 with `gh issue view 2542`.
2. Inspect the candidate TSV and source tree metadata for `/mnt/ace/doris/training` using read-only commands only.
3. Build a training taxonomy from file paths/types/sizes. Separate reusable engineering training from client/project-specific material.
4. Produce `doris-university-taxonomy.md` with topic groups, evidence examples, risks, and proposed wiki target structure.
5. Produce `doris-university-first-tranche.tsv` with no more than 25 candidate artifacts. Columns: priority, topic, content_kind, bytes, absolute_path, rationale, extraction_method, target_wiki_page, risk_note.
6. Draft the canonical plan file for #2542 with scope, resource intelligence, artifact map, TDD/validation, acceptance criteria, and approval boundary.
7. Write final result summary to `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-2-doris-university.md`.
8. Post one concise GitHub comment on #2542 summarizing the result paths and whether it is ready for adversarial review. Do not add `status:plan-approved`.

## Hard boundaries

- Do not run broad PPT/PDF extraction.
- Do not process more than small metadata/path samples unless needed for planning.
- Do not copy raw data into git.
- Do not self-approve.
- If uncertain, write the uncertainty in the taxonomy/report rather than asking the user.

## Verification

Run:
- `test -s docs/plans/2026-04-28-issue-2542-elements-doris-university-training-plan.md`
- `test -s .planning/intel/elements-overnight-wave/doris-university-taxonomy.md`
- `test -s .planning/intel/elements-overnight-wave/doris-university-first-tranche.tsv`
- `test -s docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-2-doris-university.md`

Final response should list files written and any blocker.
