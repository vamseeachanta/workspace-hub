<!-- Canonical layout copy of terminal-4-woodfibre.md for stream slug 'woodfibre-lng'. Original launch-record file is preserved at docs/plans/overnight-prompts/2026-04-28-elements-wave/terminal-4-woodfibre.md. -->

We are in `/mnt/local-analysis/workspace-hub` on branch `main`.

You are Terminal 4 for the overnight Elements planning wave.

## Mission

Plan a metadata-first scout and bounded extraction candidate pass for `workspace-hub#2544`: Woodfibre LNG corpus.

This is planning-only. Do not implement extraction, do not copy raw files into git/wiki, and do not modify `/mnt/ace`.

## Issue context

Issue: https://github.com/vamseeachanta/workspace-hub/issues/2544
Umbrella: https://github.com/vamseeachanta/workspace-hub/issues/2540
Completed upstream: #2526, #2534, #2535, #2536.

Raw corpus source of record:
`/mnt/ace/acma-projects/31522-woodfibre-lng`

Wiki domain target:
`lng-projects`

Relevant existing artifacts:
- `.planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md`
- `.planning/intel/elements-to-llm-wiki/elements-wiki-classification.tsv`
- `knowledge/wikis/lng-projects/`

## Allowed writes

Only write these paths:
- `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md`
- `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md`
- `.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv`
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-4-woodfibre.md`

## Forbidden writes

Do not write to:
- `/mnt/ace/**`
- `knowledge/wikis/**`
- `docs/plans/README.md`
- `scripts/**`
- `.gitignore`
- any Terminal 1/2/3 paths
- unrelated dirty provider scorecard/report files

## Required work

1. Re-read issue #2544 with `gh issue view 2544`.
2. Build a read-only structure map for `/mnt/ace/acma-projects/31522-woodfibre-lng` from path/file metadata. Avoid opening huge binaries unless only metadata is read.
3. Identify project document families and likely high-value small candidates. Explicitly flag client/confidentiality review needs.
4. Produce `woodfibre-corpus-scout.md` with top-level/second-level structure, file-type/size observations, risks, and recommended extraction strategy.
5. Produce `woodfibre-first-tranche.tsv` with no more than 15 candidate artifacts. Columns: priority, family, content_kind, bytes, absolute_path, rationale, extraction_method, target_wiki_page, confidentiality_risk.
6. Draft the canonical plan file for #2544 with scope, resource intelligence, artifact map, TDD/validation, acceptance criteria, and approval boundary.
7. Write final result summary to `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-4-woodfibre.md`.
8. Post one concise GitHub comment on #2544 summarizing result paths and whether it is ready for adversarial review. Do not add `status:plan-approved`.

## Hard boundaries

- Do not run broad extraction over 1.879 TB.
- Do not copy raw data into git.
- Do not process very large binaries beyond metadata/path/size classification.
- Do not self-approve.
- If uncertain, write the uncertainty in the scout/report rather than asking the user.

## Verification

Run:
- `test -s docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md`
- `test -s .planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md`
- `test -s .planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv`
- `test -s docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-4-woodfibre.md`

Final response should list files written and any blocker.
