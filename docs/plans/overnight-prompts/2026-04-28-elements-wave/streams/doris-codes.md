<!-- Canonical layout copy of terminal-3-doris-codes.md for stream slug 'doris-codes'. Original launch-record file is preserved at docs/plans/overnight-prompts/2026-04-28-elements-wave/terminal-3-doris-codes.md. -->

We are in `/mnt/local-analysis/workspace-hub` on branch `main`.

You are Terminal 3 for the overnight Elements planning wave.

## Mission

Plan a standards-aware metadata promotion pass for `workspace-hub#2543`: DORIS Codes and Specs.

This is planning-only. Do not implement extraction, do not copy raw standards files into git/wiki, and do not modify `/mnt/ace`.

## Issue context

Issue: https://github.com/vamseeachanta/workspace-hub/issues/2543
Umbrella: https://github.com/vamseeachanta/workspace-hub/issues/2540
Related standards issue: #2227
Completed upstream: #2526, #2534, #2535, #2536.

Raw corpus source of record:
`/mnt/ace/doris/codes`

Wiki domain target:
`engineering-standards`

Relevant existing artifacts:
- `.planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md`
- `.planning/intel/elements-to-llm-wiki/elements-wiki-classification.tsv`
- `knowledge/wikis/engineering-standards/`

## Allowed writes

Only write these paths:
- `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md`
- `.planning/intel/elements-overnight-wave/doris-codes-standards-inventory-plan.md`
- `.planning/intel/elements-overnight-wave/doris-codes-standards-families.tsv`
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-3-doris-codes.md`

## Forbidden writes

Do not write to:
- `/mnt/ace/**`
- `knowledge/wikis/**`
- `docs/plans/README.md`
- `scripts/**`
- `.gitignore`
- any Terminal 1/2/4 paths
- unrelated dirty provider scorecard/report files

## Required work

1. Re-read issue #2543 and related issue #2227 with `gh issue view`.
2. Inspect source tree metadata for `/mnt/ace/doris/codes` using read-only commands only. Avoid expensive full-content scans.
3. Infer standards families from path/name metadata: API, ASME, ASTM, DNV, ISO, NORSOK, OCIMF, CSA, ABS, IEC, etc. Include uncertainty.
4. Produce `doris-codes-standards-inventory-plan.md` with a safe metadata-only promotion strategy and licensing/copyright guardrails.
5. Produce `doris-codes-standards-families.tsv` with columns: family, approximate_count_or_sample_count, representative_paths, proposed_wiki_target, license_risk, extraction_policy.
6. Draft the canonical plan file for #2543 with scope, resource intelligence, artifact map, TDD/validation, acceptance criteria, and approval boundary.
7. Write final result summary to `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-3-doris-codes.md`.
8. Post one concise GitHub comment on #2543 summarizing result paths and whether it is ready for adversarial review. Do not add `status:plan-approved`.

## Hard boundaries

- Do not OCR or text-extract standards.
- Do not copy raw standards into git/wiki.
- Do not claim authoritative licensing status; classify risk conservatively.
- Do not self-approve.
- If uncertainty remains, write it in the plan instead of asking the user.

## Verification

Run:
- `test -s docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md`
- `test -s .planning/intel/elements-overnight-wave/doris-codes-standards-inventory-plan.md`
- `test -s .planning/intel/elements-overnight-wave/doris-codes-standards-families.tsv`
- `test -s docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-3-doris-codes.md`

Final response should list files written and any blocker.
