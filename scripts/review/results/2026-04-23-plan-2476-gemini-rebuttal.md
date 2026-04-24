# Rebuttal — Gemini r1 review of plan #2476 (2026-04-23)

Gemini's MAJOR verdict on plan #2476 is driven by sandbox-overlay divergence, not real evidence gaps. Gemini's sandbox cannot see the sparse-checkout overlay rooted at `/mnt/local-analysis/workspace-hub`, so `glob` calls returned zero matches for every repo-relative path the plan cites. A local `ls -la` under that same repo root shows each flagged file is present and non-empty. The rebuttal below enumerates every "missing" artifact Gemini named in either its r1 findings or the aggregate disagreement summary, pairs it with live `ls -la` output, and assigns a verdict.

## File-existence rebuttal

| Claimed-missing path | `ls -la` result | Verdict |
|---|---|---|
| `knowledge/wikis/engineering/CLAUDE.md` | `-rwxrwxrwx 1 vamsee vamsee 1781 Apr 16 12:05 knowledge/wikis/engineering/CLAUDE.md` | EXISTS — Gemini wrong |
| `knowledge/wikis/engineering/wiki/index.md` | `-rwxrwxrwx 1 vamsee vamsee 12334 Apr 17 09:21 knowledge/wikis/engineering/wiki/index.md` | EXISTS — Gemini wrong |
| `knowledge/wikis/engineering/wiki/log.md` | `-rwxrwxrwx 1 vamsee vamsee 4687 Apr 17 09:23 knowledge/wikis/engineering/wiki/log.md` | EXISTS — Gemini wrong |
| `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` | `-rwxrwxrwx 1 vamsee vamsee 1920 Apr 9 15:45 knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` | EXISTS — Gemini wrong |
| `knowledge/wikis/engineering/wiki/entities/orcaflex-solver.md` | `-rwxrwxrwx 1 vamsee vamsee 3379 Apr 15 02:15 knowledge/wikis/engineering/wiki/entities/orcaflex-solver.md` | EXISTS — Gemini wrong |
| `knowledge/wikis/engineering/wiki/entities/orcawave-solver.md` | `-rwxrwxrwx 1 vamsee vamsee 1959 Apr 9 15:39 knowledge/wikis/engineering/wiki/entities/orcawave-solver.md` | EXISTS — Gemini wrong |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` | `-rwxrwxrwx 1 vamsee vamsee 23360 Feb 23 06:31 digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` | EXISTS — Gemini wrong |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py` | `-rwxrwxrwx 1 vamsee vamsee 26517 Apr 23 16:38 digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py` | EXISTS — Gemini wrong |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py` | `-rwxrwxrwx 1 vamsee vamsee 27563 Apr 15 16:00 digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py` | EXISTS — Gemini wrong |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_to_orcaflex.py` | `-rwxrwxrwx 1 vamsee vamsee 11704 Apr 3 20:11 digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_to_orcaflex.py` | EXISTS — Gemini wrong |
| `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/` | Directory present with `__init__.py`, `cli.py`, `extractor.py`, `post_validator.py`, `builders/` | EXISTS — Gemini wrong |
| `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` | `-rwxrwxrwx 1 vamsee vamsee 10150 Apr 3 20:13 docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` | EXISTS — Gemini wrong |
| `docs/handoffs/2026-04-23-orcawave-orcaflex-semantic-proof-exit-handoff.md` | `-rwxrwxrwx 1 vamsee vamsee 12151 Apr 23 17:19 docs/handoffs/2026-04-23-orcawave-orcaflex-semantic-proof-exit-handoff.md` | EXISTS — Gemini wrong |
| `docs/handoffs/2026-04-24-orcawave-orcaflex-next-wave-closeout.md` | `-rwxrwxrwx 1 vamsee vamsee 4110 Apr 23 20:37 docs/handoffs/2026-04-24-orcawave-orcaflex-next-wave-closeout.md` | EXISTS — Gemini wrong |
| `docs/plans/README.md` | `-rwxrwxrwx 1 vamsee vamsee 55002 Apr 23 21:55 docs/plans/README.md` | EXISTS — Gemini wrong |
| `scripts/knowledge/llm_wiki.py` | `-rwxrwxrwx 1 vamsee vamsee 51131 Apr 16 10:13 scripts/knowledge/llm_wiki.py` | EXISTS — Gemini wrong |

## Secondary findings assessment

Gemini also raised four non-existence findings in its r1 artifact:

1. **Date mismatch (`2026-04-23` header vs `2026-04-24` artifact map):** Real — plan v2 Artifact Map rows still reference `2026-04-24-...` paths while the plan header, filename, and review artifacts are dated `2026-04-23`. This is a genuine internal-consistency defect distinct from the sandbox issue but it will trigger ingestion failures if downstream tooling follows the Artifact Map. Flagged for plan v3 attention regardless of this rebuttal.
2. **`docs/plans/README.md` missing from Artifact Map row:** Real — Files to Change row 6 lists the README modify, but Artifact Map has no corresponding row. Minor packaging defect; file itself exists.
3. **Unexecutable TDD commands (pseudocode placeholders):** Real — the TDD table uses descriptive placeholders ("small Python/YAML parser over changed pages", "Python regex scan", "grep date and slugs", `test -f <page>` without a concrete page list) instead of self-contained shell invocations. Reviewer cannot reproduce the checks without interpreting intent.
4. **`/tmp/wiki-lint-before.txt` static path collision risk:** Weak — CI runs are serialized; collision risk is marginal. Still a MINOR packaging nit if the check is promoted to parallel execution.
5. **"Environment isolation failure" claim about `/mnt/local-analysis/workspace-hub` access:** False — this path is the canonical workspace-hub sparse-overlay root and is directly readable by the primary Claude/Codex dispatchers (verified by `ls -la` above). The constraint Gemini cites is Gemini's own sandbox policy, not a plan defect.

## Conclusion

Gemini MAJOR rebutted on the file-existence axis — no plan edits required to rebut the 16 "missing-file" claims. However, Gemini's non-existence secondary findings (date mismatch, Artifact Map omission of `docs/plans/README.md`, non-executable TDD commands, hardcoded `/tmp` path) are real packaging defects and are independently corroborated by the Claude r1 review (which issued MAJOR with 10 findings, including overlap on Gemini findings #1-3 and #5). Those items stand on their own and must be addressed in a plan v3 revision. See `2026-04-23-plan-2476-disagreement-r2.md` for the aggregate recommendation.
