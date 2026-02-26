# Session knowledge — 2026-02-26 OrcaFlex close-out

## Completed this session

| WRK | Title | Deliverable |
|-----|-------|-------------|
| WRK-314 | OrcaFlex run scripts | `run_orcaflex.py` for A01, C10, E08, K01, L01 |
| WRK-315 | OrcFxAPI legacy migration | run scripts ported from OrcFxAPI to orcawave |
| WRK-316 | OrcaWave skill updates | skills capabilities arrays populated |
| WRK-317 | OrcaWave L01 run script | `run_orcawave_diffraction_improved.py` |
| WRK-318 | OrcaWave L02–L06 run scripts | `run_orcawave.py` × 5 examples |
| WRK-319 | OrcaWave QA suite | `orcawave_example_qa.py` + `QA_REPORT.md` |
| WRK-328 | ORCAFLEX_MODELS.md | 326-line per-model engineering cards, 14 letter groups |

## Handed to Codex

| WRK | Title | Status |
|-----|-------|--------|
| WRK-320 | OrcaWave skills capabilities arrays | in_progress 80% |
| WRK-321 | OrcaWave HTML report stub sections | in_progress 40% |

## Key decisions

- ORCAFLEX_MODELS.md: first draft 478 lines (over 400 limit); condensed to 326 by consolidating F01 variants into comparison table, removing inter-sub-section dividers, merging Notable/Expected inline
- digitalmodel: pushed directly to origin/main after stash-pop conflict resolution (accepted remote benchmark_plotter.py with +1543 lines)
- workspace-hub: WRK-470 (Windows-illegal filename `Exit code:` on origin/main) still blocks full sync; used branch workflow to deliver session changes via PR

## Blocker still open

**WRK-470**: `.claude/work-queue/pending/Exit code:` on origin/main has `:` in filename — illegal on Windows. Local main is 206 commits behind and cannot pull. Must be deleted from remote by a Linux/Mac machine or GitHub web UI.
