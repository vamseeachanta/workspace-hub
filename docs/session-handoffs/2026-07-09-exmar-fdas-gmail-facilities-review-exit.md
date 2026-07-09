# 2026-07-09 Exmar FDAS Gmail and Facilities Review Exit Handoff

## Active Task

User asked to review whether Gmail can be accessed via CLI, inspect the Exmar/FDAS email context, and determine whether topsides/process-module/process-facility information can be collected online or from existing local data.

This was a research/review/documentation session. File-writing side effects are limited to OAuth token refresh from Gmail API access, this control-plane handoff, and the private FDAS wiki page named below.

## Suggested Skills

- `email/gmail-operations`
- `email/gmail-data-extraction`
- `email/gmail-headless-oauth`
- `field-dev-code-recon`
- `research/llm-wiki-public-private-routing`
- `research/llm-wiki-page-shape-contract`
- `coordination/pre-completion-cleanup-audit`

## Completed Actions

- Verified Gmail CLI/API access through existing OAuth credentials.
- Confirmed live Gmail API access works for the `ace` account.
- Confirmed `personal` and `skestates` token refresh currently fail with HTTP 400; do not claim those inboxes were checked.
- Searched the live `ace` mailbox for Exmar/FDAS terms.
- Reviewed the Exmar-related FDAS threads:
  - Gmail thread `19f2564bcf43c357`, subject: `EXMAR OFFSHORE meeting July 1st`.
  - Gmail thread `19f4418d021916cb`, subject: `RE: Issues & Opportunities for the Paleogene and global deepwater productivity`.
  - Gmail thread `19a1c19b9175f507`, subject: `FDAS | Riser System Analysis`.
  - Gmail thread `19cb13ae2febcf37`, subject: `2026 whitepaper draft`.
- Parsed the Dec. 2025 attached DOCX from Gmail in memory only; no attachment was written to the repo.
- Cross-checked local structured offshore-facility data under `gdrive-extraction/staging/worldenergydata-seed/og-website-db/`.
- Searched public web sources for Exmar OPTI, Who Dat, Delta House, and Horn Mountain process/payload benchmarks.
- Routed the detailed FDAS/Exmar technical basis to the private `llm-wiki-fdas` repo after the user's routing correction.
- Created private wiki page: `llm-wiki-fdas/pages/exmar-fdas-topsides-process-basis-2026.md`.

## Canonical Technical Artifact

The detailed Exmar/FDAS topsides, process-facility, and freestanding-riser basis belongs canonically in the private `llm-wiki-fdas` repo, not in `workspace-hub`.

Canonical page:

- `/mnt/local-analysis/llm-wiki-fdas/pages/exmar-fdas-topsides-process-basis-2026.md`

This `workspace-hub` document is the operational exit handoff. Future technical edits should update the private wiki page and its FDAS knowledge-map/index entries.

## Current Findings

### Email Context

The Exmar ask is specific. Exmar asked FDAS for a topsides payload capacity for the proposed configuration, including:

- TTR/riser loads.
- Drilling module.
- Process systems.
- Target water depth.
- Comparison against OPTI-X hull designs.
- Exmar noted existing hull designs around a 25K-ton topsides basis.

Internal FDAS response stance was cautious: do not send a single number until Paul/Howard/Roy validate drilling-module, wellbay, and riser-load assumptions.

### Important Internal Technical Context

The Dec. 2025 `FDAS | Riser System Analysis` thread and attached `Dual Barrier Freestanding Risers for the FrPS.docx` are important because they shift the riser-load framing:

- 10 freestanding production risers in a 2x5 movable wellbay.
- Water-depth cases: 6,000 / 8,000 / 10,000 ft.
- Fixed drilling rig; well access by movable/indexing wellbay rather than skidding the rig.
- Riser tension is intended to be provided by buoyancy/seabed anchorage, not permanent topside tensioners.
- The movable wellbay becomes primarily a guide/stop/indexing structure, not the primary vertical riser-load reaction system.

Useful internal riser stackup figures from the DOCX:

| Case | 6,000 ft | 8,000 ft | 10,000 ft |
|---|---:|---:|---:|
| Config A air-can joints | 4 | 5 | 7 |
| Config A foam buoyancy joints | 17 | 23 | 30 |
| Config B air-can joints | 10 | 12 | 14 |
| Config B foam buoyancy joints | 22 | 29 | 36 |
| Config B fully aired buoyant capacity | ~2,310 kips | ~2,870 kips | ~3,430 kips |
| Config B flooded unlatch margin | ~112 kips negative | ~121 kips negative | ~131 kips negative |

Treat those as internal working-basis figures, not public-facing values.

### Public / Local Benchmark Data

Public sources:

- Exmar OPTI family payload range: OPTI-micro 4,500-5,000 mt to OPTI-28,500 at 28,500 mt payload.
  Source: https://exmaroffshore.com/services/floating-production-systems/
- Exmar/Who Dat OPTI-EX context:
  - Who Dat / OPTI-EX project page: https://exmar.com/en/projects/who-dat-opti-ex/
  - Exmar first OPTI-EX sale/deployment: https://exmar.com/en/milestones/exmar-signs-contract-for-the-sale-of-the-first-opti-ex-floating-production-system-to-llog-exploration/
  - Exmar delivery/installation page: https://exmar.com/en/milestones/delivery-and-installation-of-opti-ex/
  - Offshore Magazine reports processing capacity 60,000 b/d oil and 150 MMcf/d gas: https://www.offshore-mag.com/production/article/16776704/exmar-delivers-floating-production-system-to-llog
- Delta House:
  - Audubon says water depth approximately 5,000 ft and design capabilities 80,000 BOPD / 200 MMSCFD / 40,000 BWPD: https://auduboncompanies.com/project/delta-house-fps/
  - AOGR says nameplate 80,000 bbl/d oil / 200 MMcf/d gas / 40,000 bbl/d water, with peak 100,000 bbl/d oil and 240 MMcf/d gas: https://www.aogr.com/magazine/sneak-peek-preview/standardized-fps-design-key-to-fast-track-success-at-delta-house
  - Offshore Technology repeats 80,000 bopd / 200 MMcfd: https://www.offshore-technology.com/projects/delta-house-field-gulf-mexico/
- Horn Mountain:
  - SPE Gulf Coast event page says platform nameplate 65,000 BOPD / 70 MMscfd / 40,000 BPD water injection: https://www.spegcs.org/events/254/
  - Offshore Technology says Horn Mountain peaked above 65,000 bpd and 68 MMcf/d: https://www.offshore-technology.com/projects/horn/

Local source rows:

- `gdrive-extraction/staging/worldenergydata-seed/og-website-db/og_host.csv`
  - OPTI-EX row: line 192.
  - Horn Mountain row: line 210.
  - Na Kika row: line 154.
  - Atlantis row: line 171.
  - Thunder Horse row: line 183.
  - Independence Hub row: line 201.
- `gdrive-extraction/staging/worldenergydata-seed/og-website-db/og_pfdata.csv`
  - Horn Mountain SPAR Platform row has water depth 1,653 m / 5,455 ft.
- `gdrive-extraction/staging/worldenergydata-seed/og-website-db/og_ongfields.csv`
  - Horn Mountain field row has production start and water depth.

FDAS local knowledge-base sources:

- `llm-wiki-fdas/pages/total-engagement-emails-2017.md`
  - Lines 79-99 summarize prior FDAS/TOTAL capacity discussion.
  - Lines 84-86: Horn Mountain topsides basis, 65,000 bbl oil + 80 MMcf gas/day with water injection. Reconcile the 80 MMcf/d internal note against public 68-70 MMcf/d sources before external use.
- `llm-wiki-fdas/pages/total-fdas-technical-decks.md`
  - Lines 67-83: VAM TTR / Q-125 riser and stress-joint context.
  - Lines 112+ mention 6,000 ft OrcaFlex FDAS vessel analysis.
- `llm-wiki-fdas/pages/frontier-20k-ttr-tubulars-reference.md`
  - Lines 33-38: VAM TTR connector claims.

## Recommended Next Checkpoint

Do not send Exmar a single topsides payload number yet.

Prepare a one-page "basis matrix" for internal review first:

1. Water-depth columns: 6,000 / 8,000 / 10,000 ft.
2. Process cases:
   - Horn Mountain-class dry-tree process basis.
   - Delta House-class hub process basis.
3. Riser architecture:
   - Freestanding riser case with no permanent topside tensioner payload.
   - Explicitly list local wellbay guide/stop/indexing loads as TBD.
4. Drilling-module basis:
   - Ask Exmar whether they already have OPTI-X central fixed-drilling-rig layouts.
   - Ask what drilling-package/deck/CG assumptions were used for the 25K-ton BP hull-design basis.
5. Internal approval:
   - Paul/Howard/Roy should validate drilling module, wellbay, and riser/well-access assumptions before any FDAS external number is issued.

Suggested external framing if replying before a full matrix is ready:

> We are collecting the basis as a range rather than a single number. The current FDAS concept treats the production risers as freestanding/self-tensioned, so the host payload question should separate process + drilling + wellbay structural/interface loads from conventional top-tensioner payload. We can compare Horn Mountain-class and Delta House-class process cases against OPTI-X/OPTI payload envelopes, then review drilling-module and CG assumptions with your team.

## Repo / Issue State

- No GitHub issue was opened or closed in this session.
- No implementation work was performed.
- No code tests were required or run.
- `uv run scripts/gen_index.py` in `llm-wiki-fdas` currently fails on unrelated pre-existing report metadata: `reports/figures/README.md` is missing `name`, `description`, and `issue` frontmatter. The new `pages/README.md` row was therefore updated manually.
- No raw email content or attachments were committed.
- Gmail token files may have been refreshed locally by the API calls.

## Cleanup Notes

Known unrelated workspace state before this handoff:

- `workspace-hub` was on `main`, behind `origin/main` by 3 at the time of closeout.
- The `workspace-hub` worktree already had substantial unrelated dirty/generated state, including `.claude/state`, `config/agents/.../memory-snapshots`, provider report outputs, and untracked coverage reports.
- Existing unrelated untracked file observed: `scripts/testing/coverage-reports/WRK-1067-coverage-20260708.txt`.
- Existing unrelated `/tmp` files and `/mnt/local-analysis/.cleanup-trash/20260616-095709` were present.

Do not clean or revert any of that as part of the Exmar/FDAS review. Treat it as pre-existing control-plane residue unless the user explicitly authorizes cleanup.
