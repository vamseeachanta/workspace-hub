# Overnight Elements corpus planning wave — 2026-04-28

## Purpose

Create safe, bounded planning artifacts for the remaining Elements → LLM-wiki corpora after completed issues #2535 and #2536.

This wave is **planning-only**. It must not extract broad raw data, copy raw files into git/wiki, delete staging/source data, or self-approve implementation.

## Issues

| Terminal | Issue | Workstream | Raw corpus | Result artifact |
|---:|---:|---|---|---|
| 1 | #2541 | SESA LNG curated extraction plan | `/mnt/ace/doris/62092_sesa` | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-1-sesa.md` |
| 2 | #2542 | Doris University training taxonomy plan | `/mnt/ace/doris/training` | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-2-doris-university.md` |
| 3 | #2543 | DORIS codes/specs standards metadata plan | `/mnt/ace/doris/codes` | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-3-doris-codes.md` |
| 4 | #2544 | Woodfibre LNG corpus scout plan | `/mnt/ace/acma-projects/31522-woodfibre-lng` | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-4-woodfibre.md` |

Umbrella issue: #2540.

## Shared background

Completed upstream work:
- #2526: Elements copied, verified, and hardlink-merged into `/mnt/ace`; `_from_elements/` retained.
- #2534: retention-gated cleanup remains open; no deletion/release before `2026-05-28` unless explicitly overridden.
- #2535: metadata-first LLM-wiki indexing completed for 8 bucket-level catalogs.
- #2536: first-pass deep extraction completed for suction pile sizing, riser toolbox, and QGIS.

Important files:
- `.planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md`
- `.planning/intel/elements-to-llm-wiki/elements-wiki-classification.tsv`
- `.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv`
- `.planning/intel/elements-deep-extraction/elements-deep-extraction-report.md`
- `scripts/knowledge/llm_wiki.py`
- `scripts/knowledge/tests/test_llm_wiki.py`

## Hard boundaries

- Raw `/mnt/ace` files are the source of record.
- Do not copy raw bulk files into git/wiki raw folders.
- Do not write to `/mnt/ace`.
- Do not delete `_from_elements/` or source drive content.
- Do not run broad OCR/text extraction over entire corpora.
- Do not self-approve implementation; leave plans as drafts / approval candidates.
- Do not stage unrelated dirty provider scorecard/report files.

## Zero-overlap write map

| Terminal | Allowed writes | Forbidden writes |
|---:|---|---|
| 1 | `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md`; `.planning/intel/elements-overnight-wave/sesa-*`; result file T1 | T2/T3/T4 plan/result/intel paths; `/mnt/ace`; wiki raw folders |
| 2 | `docs/plans/2026-04-28-issue-2542-elements-doris-university-training-plan.md`; `.planning/intel/elements-overnight-wave/doris-university-*`; result file T2 | T1/T3/T4 plan/result/intel paths; `/mnt/ace`; wiki raw folders |
| 3 | `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md`; `.planning/intel/elements-overnight-wave/doris-codes-*`; result file T3 | T1/T2/T4 plan/result/intel paths; `/mnt/ace`; wiki raw folders |
| 4 | `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md`; `.planning/intel/elements-overnight-wave/woodfibre-*`; result file T4 | T1/T2/T3 plan/result/intel paths; `/mnt/ace`; wiki raw folders |

All terminals must avoid editing shared files such as `docs/plans/README.md`, wiki indexes, wiki logs, `.gitignore`, and scripts unless explicitly instructed in a later approved implementation wave.

## Morning deliverables

By morning, expect:
- Four child-issue planning dossiers/result files.
- Four draft canonical plan files.
- GitHub comments on #2541-#2544 with links/paths to each result.
- A clear recommendation on which issue(s) are ready for adversarial review / approval next.

## Launch commands

Use one terminal per prompt. From `/mnt/local-analysis/workspace-hub`:

```bash
PROMPT=$(< docs/plans/overnight-prompts/2026-04-28-elements-wave/terminal-1-sesa.md)
claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 20 "$PROMPT" </dev/null | tee docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-1-sesa.log
```

Repeat with terminal-2/3/4 prompt and log paths.
