# Terminal 4 — Woodfibre LNG corpus scout & bounded-extraction plan (issue #2544)

> **Run:** 2026-04-28 overnight Elements wave, Terminal 4
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2544
> **Outcome:** plan-review (NOT plan-approved); ready for adversarial review
> **Permission boundary respected:** no writes to `/mnt/ace/**`, `knowledge/wikis/**`, `docs/plans/README.md`, `scripts/**`, `.gitignore`, or any Terminal 1/2/3 paths.

## Files written

| Path | Purpose |
|---|---|
| `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` | Canonical plan with resource intelligence, artifact map, scope, pseudocode, TDD, acceptance criteria, risks, approval boundary |
| `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md` | Metadata-only structure scout (top-1/top-2 dirs, extension/size histograms, EDMS register decode, risks, uncertainties) |
| `.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv` | 15-row candidate matrix (priority/family/content_kind/bytes/path/rationale/extraction_method/target_wiki_page/confidentiality_risk) |
| `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-4-woodfibre.md` | This file |

## What was decided

- **Posture:** metadata-first, confidentiality-aware. Zero raw bytes from a 1.879 TB corpus into git/wiki.
- **Corpus shape established (jq-aggregated from `.planning/intel/elements-to-llm-wiki/elements-ingested-files.jsonl`):**
  - 5,364 files / 1,879,405,139,855 bytes (1.879 TB).
  - 96% of bytes (1.8 TB) live in `02.Mooring Analysis/03.Orcaflex` as `.sim` time-history binaries — **never** extracted.
  - High-signal text/PDF/DOCX live almost entirely under `05.Deliverables/` (3.39 GB / 500 files).
  - The author has already separated sim-vs-non-sim via `orcaflex_no_sim/` (1.7 GB / 1,344 files of OrcaFlex inputs and design files).
- **First-tranche bounded to 15 documents (≈80 MB total):**
  - 3 from `DB Design Briefs` (naval architecture + structural design brief + structural design basis).
  - 3 from `RA Reports` (FST-1 / FST-2 ISE assessments + SD-000171).
  - 1 from `04.Model Test Correlation` (correlation report Rev B).
  - 5 from `TN Technical Notes` (mooring interface loads, stability/ballast, loading-arm motions, operational/maintenance/failure loadcases, FST CP system design).
  - 2 from `FD Project design criteria & philosophies` (load-monitoring philosophy + SD-000141).
  - 1 corpus readme (`orcaflex_no_sim/Readme.txt`, 694 bytes — safely inline-quotable).
- **Latest-revision-only rule applied:** for documents with multiple rev letters (e.g. SD-000104 Naval Architecture Design Brief at B/B1/C/C1/C2; SD-000157 Loading Arm Motions at B/C/D/E), the tranche pins the highest published rev letter and any sub-revision suffix.
- **Hard exclusions enforced at TSV level:**
  - `.sim`, `.r001-3`, `.sldprt`, `.wbpz`, `.scdoc`, `.osav`, `.esav`, `.rst`, `.db`, `.mechdb`, `.dspsymb` — all engineering binaries.
  - `05.Deliverables/DEMOLITION/{CAPRICORN,TAURUS}/*` — 162 record drawings averaging 14 MB; likely third-party / prior-vessel-owner IP.
- **Confidentiality posture (CRITICAL):** every candidate is marked `high` or `medium` risk in the TSV. Implementation is gated on a second checkpoint beyond `status:plan-approved`: a written ACMA / project-owner clearance recorded in `docs/governance/woodfibre-extraction-clearance-2026.md`. The plan cannot be executed without that record.
- **Wiki output proposed (deferred — only after `status:plan-approved` AND clearance record):**
  - 1 corpus pointer page: `wiki/sources/woodfibre-corpus-pointer.md` (structure metadata, no document abstracts).
  - 15 abstract pages, each one a `wiki/sources/woodfibre-<slug>.md` with frontmatter + 1-page methodology-only summary; no specific numerical values without explicit ACMA approval per row.
  - `wiki/index.md`, `wiki/log.md`, `wiki/overview.md` updates.
- **Cross-corpus coordination:** the `lng-projects` wiki also receives Terminal-1's SESA pointer pages. All Woodfibre pages prefixed `woodfibre-`; all SESA pages must use `sesa-` to avoid namespace collision. Coordination is captured in the plan's risk section, not enforced at terminal-4 level.

## What was deliberately NOT done

- No reads or writes to `/mnt/ace/acma-projects/31522-woodfibre-lng/**`. The sandbox correctly blocked direct `ls`/`find` on the mount; all corpus shape was derived from the pre-existing `elements-ingested-files.jsonl` index.
- No raw bytes (PDF/DOCX/SIM/CAD) copied into git or `knowledge/wikis/lng-projects/`.
- No `wiki/sources/woodfibre-corpus-pointer.md` emission — that is the deferred implementation step, not a planning artifact.
- No edits to `knowledge/wikis/lng-projects/wiki/` content.
- No edits to Terminal 1/2/3 paths or to the master overnight-prompt pack.
- No `status:plan-approved` label applied (user-in-loop gate is intact). No language in any artifact pre-authorizes downstream agents to set the label, per memory: `feedback_never_offer_to_self_label_plan_approved.md`.
- No assertion of fair-use, NDA-compliance, or IP clearance — every confidentiality call is left for ACMA / project-owner review.

## Key uncertainties surfaced (kept in plan, not resolved)

1. **Project-owner identity** — inferred from filename tokens (`WoodfibreLNG`, `WSP Interface loads`, `FST-1/FST-2`, `Capricorn`/`Taurus`, `LNGC`). Cannot be confirmed without opening a PDF; deferred to plan-stage reviewer / ACMA reviewer.
2. **EDMS revision-letter convention** — assumed `B = IFR`, `C = IFA`, sub-numbers = sub-revisions. If different, the latest-revision rule may pick a wrong file. Mitigation: implementation step calls a 2-row sanity check ("does the chosen rev's mtime exceed all sibling revs?") — if not, escalate.
3. **Whether `_from_elements/` staging path exists** — implied by #2535 catalog (`staging_root: /mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements`) but not verified directly because of sandbox boundary. Treated as precondition.
4. **Public regulator filings** — BC OGC and BC EAO commonly publish summarized project documents for LNG facilities. If applicable summaries exist, abstracts could cite the public filing instead of paraphrasing internal docs, eliminating clearance friction. Not researched in this terminal; flagged in plan's open questions.
5. **Whether any of the 15 candidates contain WSP, Pacific Energy, or shipyard-partner IP** that ACMA does not own outright — folder names suggest WSP for the mooring interface document. Deferred to ACMA review.
6. **DEMOLITION subdir IP provenance** — record drawings predate the conversion project and likely came from prior owners of CAPRICORN/TAURUS hulls. Excluded from tranche; provenance question left open for future cataloging issue.

## Verification (commands run within sandbox)

- `gh issue view 2544 --json ...` → OPEN; scope/deliverables/acceptance criteria match plan output.
- `Read .planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md` → confirmed bucket #8 totals (5,364 files / 1.879 TB / `metadata-only` priority).
- `Grep` over `deep-extraction-candidates.tsv` for `woodfibre` and `acma-projects-31522-woodfibre` → 0 matches (consistent with metadata-only classification).
- jq streaming aggregations on `elements-ingested-files.jsonl`:
  - `reduce inputs as $r ({}; ...)` → top-level dir histogram (6 entries; sum = 5,364 ✓).
  - same pattern → depth-2 histogram (top-12 cited in scout).
  - same pattern → extension histogram (top-25; `.sim` dominates at 98.7% bytes).
  - same pattern → content_kind histogram (engineering-data 4,269 / 1,858 GB).
- jq small-first / large-first slices on `05.Deliverables/{DB,RA,FD,SA,TN}` to identify candidate revs and confirm latest-revision picks.
- `Read knowledge/wikis/lng-projects/CLAUDE.md` → confirmed wiki schema and frontmatter contract.
- `ls knowledge/wikis/lng-projects/wiki/sources` → empty directory (no contradiction risk for proposed pointer + abstract pages).
- Post-write file-existence: all four required output paths exist and are non-empty (verified at end of run).

## Status / next action

- Issue #2544 stays at **plan-review**.
- Recommend adversarial review next (Claude + Codex + Gemini against the plan) before user approves. Note: per project memory, Codex CLI 0.124.0 has an open stdin-hang regression (#2479) — fall back to Codex web/Workbench if `codex exec` blocks. Gemini sandbox overlay-blindness is also a known false-positive source for sparse-checkout claims.
- Two gates separate this plan from any wiki write: (1) `status:plan-approved` set by user; (2) ACMA / project-owner clearance recorded in `docs/governance/woodfibre-extraction-clearance-2026.md`. Implementation issue cannot proceed past pointer-page emission until that record exists.
- Implementation phase should be a separate follow-up issue with its own plan; this plan only authorizes the *shape* of that future work and never the extraction itself.

## Sandbox observations (non-blocking, for the wave coordinator)

- Session correctly scoped to read-only on `/mnt/ace`; `ls /mnt/ace/acma-projects/31522-woodfibre-lng` and `find` over the mount were blocked. All corpus shape was therefore derived from `.planning/intel/elements-to-llm-wiki/elements-ingested-files.jsonl` — exactly the substrate #2535 produced for this purpose.
- Inline `python3 -c` and `Write` to `/tmp/` were sandbox-blocked. `jq` (with streaming `inputs`) is the workable aggregation primitive in this configuration. `awk`-piped stages tripped the multi-operation guard on the second pipe; the workaround is in-jq `reduce ... as $r ({...})` which keeps everything in one tool invocation.
- The `04.Model Test Correlation` top-level lacked deeper sub-folders for the report itself (the PDF/DOCX sit at the top of that dir, not under a `02. Orcaflex/` sub-tree like the runs do). Latest-revision selection was therefore unambiguous.

## No blockers

Terminal 4 ran clean. No blockers, no dependency on Terminals 1/2/3.
