# Terminal 1 — SESA LNG curated extraction plan (issue #2541)

> **Run:** 2026-04-28 overnight Elements wave, Terminal 1
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2541
> **Outcome:** plan-review (NOT plan-approved); ready for adversarial review
> **Permission boundary respected:** no writes to `/mnt/ace/**`, `knowledge/wikis/**`, `docs/plans/README.md`, `scripts/**`, `.gitignore`, or any Terminal 2/3/4 paths.

## Files written

| Path | Bytes (approx) | Purpose |
|---|---:|---|
| `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md` | ~13 KB | Canonical plan with resource intelligence, artifact map, scope, pseudocode, TDD, acceptance criteria, risks |
| `.planning/intel/elements-overnight-wave/sesa-candidate-dossier.md` | ~9 KB | Evidence-backed theme groupings, dedup observations, uncertainties |
| `.planning/intel/elements-overnight-wave/sesa-first-tranche.tsv` | ~6 KB | 20-artifact bounded shortlist (header + 20 rows) |
| `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-1-sesa.md` | this file | Result summary |

## What was decided

- **Tranche size:** 20 artifacts (at the issue's hard cap), ~276 MB total raw across 5 themes.
- **Theme coverage** — every theme listed in #2541 acceptance criteria is represented:
  - reference-studies: 6 artifacts (G-ITE-10046/10008/10010/10024/10033/10042)
  - free-span / metocean: 6 artifacts (G-ITE-10029, L-MCA-10025 .docx + .pdf, L-LYO-10033/10032, L-MCA-10022)
  - material-specs: 2 artifacts (L-HDS-10016 baseline + DORIS markup)
  - subsea-valves-TBE: 3 artifacts (PIETRO trunnion brochure, RMT VM catalogue, ASTM compliance matrix .pptx)
  - logistics/deliverables: 3 artifacts (San Antonio Este logistics base description, Q-PRO-10066 deliverable, KOM presentation)
- **Standards explicitly excluded:** DNV-ST-F101, API 6DSS, ASME B16.5, ASTM A351/A182/A276 — they belong in `wiki/standards/` per `.claude/rules/calc-citation-contract.md`.
- **CAD (.dwg, 18 files), email (.msg, 4 files), .db (6 files) deferred** to follow-up tranches.
- **Canonical-path heuristics documented:** Old/ and JWhipple/ shadow copies excluded; latest dated transmittal folder wins; .pdf preferred over .doc/.docx for content; Rev JRA preferred when present.

## What was deliberately NOT done

- No raw bulk data copied into git/wiki.
- No `pdftotext`, `pandoc`, or other extraction was executed against any SESA file. All inspection was metadata-only via the candidate TSV.
- No edits to `/mnt/ace`.
- No `status:plan-approved` label applied (user-in-loop gate is intact).
- Plan reviewers are NOT pre-authorized — adversarial review must run before user approval.

## Open questions surfaced for plan review (not resolved)

1. Are LYOS / MKII / Hilli three competing FLNG vessel options, or is one of them a topside identifier?
2. Is the SESA project freely citeable inside the workspace-hub wiki, or does vendor brochure text need a redistribution policy first?
3. Should Rev JRA review-markup PDFs be merged into base-rev source pages, or kept as separate review pages?
4. Is there a private DORIS wiki page documenting the GSM-AO numbering scheme that would obviate a redocumentation concept page?

## Verification (commands run)

- `gh issue view 2541` — OPEN, title matches, all referenced issues (#2540 umbrella, #2526/#2534/#2535/#2536) cited.
- `Grep ^[a-z]+\tlng-projects\tdoris-62092-sesa\t deep-extraction-candidates.tsv` → 347 SESA candidate rows confirmed.
- `Grep . sesa-first-tranche.tsv -c` → 21 lines (header + 20 rows) confirmed.
- File-existence post-write: all four required output paths exist and are non-empty.

## Status / next action

- Issue #2541 stays at **plan-review**.
- Recommend adversarial review next (Claude + Codex + Gemini against the plan) before user approves.
- Implementation phase should be a *separate follow-up issue* with its own plan; this plan only authorizes the *shape* of that future work.

## No blockers

Terminal 1 ran clean. No blockers, no dependency on Terminals 2-4.
