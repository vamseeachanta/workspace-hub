# Terminal 2 result — Doris University training corpus plan

> Workstream: workspace-hub#2542 (parent: #2540 overnight Elements wave)
> Wall-clock: 2026-04-28 evening
> Mode: planning-only; no extraction performed; no `/mnt/ace` mutation; no wiki/raw write; no self-approval

## Files written

| Path | Purpose | Bytes (approx) |
|---|---|---:|
| `.planning/intel/elements-overnight-wave/doris-university-taxonomy.md` | Group A–K taxonomy of 564 training files with routing decisions | ~9 KB |
| `.planning/intel/elements-overnight-wave/doris-university-first-tranche.tsv` | 18-row tranche-1 list (priority/topic/content_kind/bytes/path/rationale/method/target/risk) | ~5 KB |
| `docs/plans/2026-04-28-issue-2542-elements-doris-university-training-plan.md` | Canonical plan with scope, resource intel, artifact map, TDD/validation, acceptance criteria, approval boundary | ~12 KB |
| `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-2-doris-university.md` | This file | ~3 KB |

All four paths are within the Allowed-writes list from the Terminal 2 prompt. None of the Forbidden paths (`/mnt/ace/**`, `knowledge/wikis/**`, `docs/plans/README.md`, `scripts/**`, `.gitignore`, sibling-terminal paths, dirty provider files) were touched.

## Key planning outcomes

- **Tranche 1 = 18 artifacts**, well under the 25-artifact ceiling. Composition:
  - 8 canonical curriculum decks (Modules 1.00, 1.01, 1.02, 1.03 — current versions, no `Old Versions/` or `Old Revisions/`)
  - 4 Doris-authored embedded calculations (`Embedded Charts/`)
  - 5 Doris-authored Lunch and Learn PDFs (`ADMIN-FORM-02 - * Lunch and Learn ...`)
  - 1 syllabus snapshot from `Superceeded/` for taxonomy validation
- **Vendor-derivative deny-list applied** to every file under `*/References/` (API 16D/17D/17E/17G/17H/17I, BS EN ISO 13628-5, IEC 60502-1/2, FMC, Duco, OTC, Subsea Engineering Handbook). These are routed citation-only via `wiki/standards/<code-id>.md` per `.claude/rules/calc-citation-contract.md` and #2482.
- **Client-IP packs deferred** (SONANGOL, ENI, DSME, Stat/IFP, Operator Training/Azurite). Plan recommends a separate IP-screening child issue rather than tranche-1 inclusion.
- **Calc-citation precondition recorded**: at least `wiki/standards/api-17e.md` must be created with #2471 frontmatter before the `umbilical-tube-sizing-api-17e` concept page is emitted; conditional on `api-17g.md` or `api-16d.md` for the accumulator-sizing calc.
- **De-duplication strategy explicit**: `draft presentations/...` siblings hash-verified before extraction to avoid double-ingest.

## Adversarial-review readiness

**Ready for adversarial review.** The plan is internally consistent, future-tense throughout, fail-closed on calc citation, and bounds the work to a defensible 18 artifacts. Suggested review angles for whoever runs r3:

1. **Module enumeration completeness** — did the planner miss any `1.04`/`1.05` canonical deck under the top-by-size cut? (Risk #1 in plan.)
2. **Calc-citation completeness** — for each of the 4 embedded charts, is the planned standards-page set sufficient, or are there hidden constants that need additional citations?
3. **Client-IP boundary** — is "DE Presentations/<client>/" the right ALL-IN deferral pattern, or should some client-presentations be split into "methodology" vs "client-data" sub-extractions?
4. **Tranche-1 size** — is 18 too conservative? The 25-cap allows 7 more rows; consider e.g. the 1.01 (Clean) variant deck or the 1.00 V1.2 PDF render.
5. **Standards-page substrate** — the wiki currently has `wiki/standards/` essentially empty; this plan creates a precedent that future calc-extracting plans will inherit. Worth a structural review before approval.

## Caveats / known limitations

- **Source-tree direct listing was unavailable** to Terminal 2 (harness sandbox restricted Bash to the workspace-hub working directory). Taxonomy is built from the 322-row candidate TSV plus the #2535 metadata page, not from a fresh `find /mnt/ace/doris/training`. If the TSV is stale (last regenerated 2026-04-28 19:23 UTC per the domain summary), tranche enumeration will be stale by the same window.
- **Module 1.04+ existence is unverified.** A pre-execution audit of all `1\.0[0-9]` paths in the candidate TSV is the first step in Section 4 of the plan.
- **draft-vs-canonical hash equivalence is unverified.** Hash check is a Section 4 step in the plan, not done here.
- **No new code or scripts were written.** Existing `scripts/knowledge/llm_wiki.py` is sufficient per the #2536 first-pass extraction pattern; no script change is in scope of #2542.
- **No self-approval.** The plan deliberately ends at `status:plan-review`. Per `feedback_never_offer_to_self_label_plan_approved.md`, the user-in-loop gate is load-bearing.

## Verification (per Terminal 2 prompt §Verification)

All four `test -s` checks should pass:

```
test -s docs/plans/2026-04-28-issue-2542-elements-doris-university-training-plan.md
test -s .planning/intel/elements-overnight-wave/doris-university-taxonomy.md
test -s .planning/intel/elements-overnight-wave/doris-university-first-tranche.tsv
test -s docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-2-doris-university.md
```

## Blockers

None. Terminal 2 completed all required work within prompt constraints.
