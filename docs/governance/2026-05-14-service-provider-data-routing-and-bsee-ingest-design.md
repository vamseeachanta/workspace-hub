---
title: Service-provider data routing matrix + BSEE 2024 deepwater riser life-extension source ingest — design
date: 2026-05-14
status: executed-2026-05-14
authors: [vamsee, claude (opus 4.7)]
related:
  - llm-wiki/CLAUDE.md (target of matrix codification)
  - workspace-hub#2482 (vendor-derivative deny-list)
  - llm-wiki/wikis/drilling-engineering/CLAUDE.md (target wiki domain)
  - feedback_per_repo_metadata_is_firewall (precedent: boundary enforced by license + repo, not file-system distance)
  - feedback_llm_wiki_concept_pages_need_public_references (precedent: source grounding discipline)
---

# Design — service-provider data routing matrix + BSEE source ingest

## Context

User asked to add three external resources to llm-wiki in a single session:

1. BSEE 2024 *Deepwater Riser Life Extension Perspectives and Process* — US federal regulator PDF.
2. Helix ESG Q4000 LTR brochure (2024-09-12) — vendor product brochure PDF.
3. Helix ESG IRS 7-15K LTR brochure (2023-11-28) — vendor product brochure PDF.
4. Helix ESG "Riser-Based Well Intervention" landing page — vendor marketing HTML page.

Items 2–4 surfaced a governance question that wasn't yet codified: how should service-provider data routinely enter the workspace-hub / llm-wiki ecosystem? The repo CLAUDE.md has a one-line "Vendor PDFs live at <private-vendor-mount>, never in this repo" but no matrix covering related document classes (SEC filings, conference papers, landing pages, regulator records).

## Decisions

### D1 — Service-provider data routing matrix (codified in `llm-wiki/CLAUDE.md`)

| Document class | Examples | Route | Rationale |
|---|---|---|---|
| Vendor brochure / spec sheet / marketing PDF | Q4000 LTR, IRS 7-15K LTR | Private vendor mount (`/mnt/ace/vendor-pdfs/<vendor>/`); off-repo | Copyright owned by vendor; not redistributable under CC-BY-4.0; #2482 deny-list |
| SEC filings (10-K, 10-Q, 8-K, investor decks) | Helix 10-K fleet section | Public llm-wiki entity page (paraphrased, page-cited) | Public record; factual disclosures not copyrightable; prose paraphrase under fair-use |
| Conference papers (SPE / OTC / IADC) | "Helix Well Intervention — OTC 12345" | Public llm-wiki source page (DOI-grounded paraphrase) | Conference-publication norms; DOI stable reference; mirrors Papkov treatment |
| Press releases / news / vendor landing pages | helixesg.com/our-assets/... | URL-only bibliographic reference if discloses material facts; verbatim copy to private mount | PR/marketing copy is vendor-controlled; fact extraction allowed, prose copy not |
| Public classification-society / regulator records | DNV / ABS class records, USCG vessel registry, IMO MODU records, BSEE OCS reports | Public llm-wiki entity/standards page | Regulatory / class-society records are public-domain factual data |
| User's own annotated extracts | Engineering notes after reading a vendor brochure | Private vendor mount alongside source | User's notes are user's; preserves chain of custody so they don't accidentally land in public repo |

### D2 — BSEE PDF route

US federal-regulator publication → public-record route. Single source-page ingest in drilling-engineering wiki, mirroring the Papkov source-page precedent. URL-only reference, no `raw/` PDF deposit (matches established precedent). No GitHub issue filed first.

### D3 — Helix Q4000 + IRS 7-15K PDFs route

Vendor brochures → private-mount route. Deposit at `/mnt/ace/vendor-pdfs/helix-esg/`. Index in `workspace-hub/docs/governance/vendor-pdf-inventory.md` recording filename, origin URL, observed date, vendor identity, document character. No llm-wiki touch.

### D4 — Helix landing page route

Vendor marketing HTML → hybrid route per matrix row 4: URL bibliographic reference + verbatim copy saved to private mount (HTML snapshot). Fact extraction into a public Helix entity page deferred until accompanied by SEC 10-K grounding (matrix row 2 requirement). This avoids the `feedback_llm_wiki_concept_pages_need_public_references` failure mode of single-source vendor-marketing-only entity pages.

### D5 — Memory codification

Write `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_service_provider_data_routing.md` referencing this design doc. Index in MEMORY.md feedback section. Ensures future sessions auto-apply the matrix regardless of which repo cwd is in.

## Plan of execution (atomic commits)

1. **Create private mount directory + deposit Q4000 PDF + deposit IRS 7-15K PDF.**
   - `mkdir -p /mnt/ace/vendor-pdfs/helix-esg`
   - `curl -L <Q4000-url> -o /mnt/ace/vendor-pdfs/helix-esg/Helix_Well_Ops_Q4000_LTR_2024-09-12.pdf`
   - `curl -L <IRS-url>   -o /mnt/ace/vendor-pdfs/helix-esg/Helix_Well_Ops_IRS-7-15k_LTR_2023-11-28.pdf`
   - `wget --no-check-certificate -O /mnt/ace/vendor-pdfs/helix-esg/Helix_riser-based-well-intervention_2026-05-14_snapshot.html https://helixesg.com/our-assets/riser-based-well-intervention/`
   - No commit (off-repo).

2. **Write `workspace-hub/docs/governance/vendor-pdf-inventory.md`** with the four Helix entries.
   - Atomic commit: `docs(governance): add vendor-pdf inventory for private-mount routing per service-provider data matrix`.

3. **Expand `llm-wiki/CLAUDE.md` "Vendor PDFs" section into the full matrix.**
   - Atomic commit in `llm-wiki/` repo: `docs(governance): expand vendor-PDF rule to full service-provider data routing matrix`.

4. **Write BSEE source page + update index.md + update log.md in `llm-wiki/wikis/drilling-engineering/`.**
   - Atomic commit in `llm-wiki/` repo: `docs(drilling-engineering): ingest BSEE 2024 deepwater riser life extension perspectives source`.

5. **Write workspace-hub feedback memory + index in MEMORY.md.**
   - No commit (memory files are tracked separately, not part of workspace-hub commit cadence by default).

## Out-of-scope (deferred to future issues)

- Concept page `riser-life-extension.md` in drilling-engineering wiki (needs multi-source grounding).
- `marine-drilling-riser-overview.md` foundational concept page (would need its own issue under llm-wiki epic #55).
- Helix entity page `entities/helix-energy-solutions-fleet.md` in drilling-engineering wiki (needs SEC 10-K + class-society grounding; landing-page alone insufficient).
- Public entity-page sweep for other service providers (Halliburton, SLB, Baker Hughes, etc.) — open work.
- Cross-wiki edits to asset-management or engineering wikis.

## Self-review (placeholder / contradiction / ambiguity / scope)

- **Placeholder scan**: No TBDs. All paths, URLs, commit messages, and routing rules explicit.
- **Internal consistency**: D1 matrix and D2–D4 individual routes agree. D4 landing-page route correctly applies matrix row 4 (URL ref + private snapshot).
- **Scope check**: Five-step execution plan with three atomic commits — focused, single-session.
- **Ambiguity check**: "Vendor identity" in row 6 (user's own notes) clarified as "user's notes about vendor content" — distinct from "vendor's content".
- **Past-tense drift check** (`feedback_plan_past_tense_artifact_claims`): All plan items in future tense — "Write", "Deposit", "Expand". No claims that artifacts already exist.

## Execution-time deviations from this spec

### D2-DEV-01: BSEE source page rerouted from drilling-engineering to asset-management

- **What the spec said**: D2 specified `llm-wiki/wikis/drilling-engineering/wiki/sources/bsee-2024-deepwater-riser-life-extension.md` as the target file.
- **What happened**: Content-grade `pdftotext` extraction of the BSEE PDF (after WebFetch reported it as image-only — that report turned out wrong; the PDF has embedded selectable text) revealed the document covers **production dynamic pipeline risers** (SCR / SLWR / unbonded flexible / FSHR) under the BSEE Pipeline Section's 30 CFR 250.910 / 250.916 regulatory framework — **not** drilling marine risers.
- **Where it actually landed**: `llm-wiki/wikis/asset-management/wiki/sources/bsee-2024-deepwater-dynamic-pipeline-riser-life-extension.md`. The asset-management wiki already has the closest existing scaffolding (life-extension, integrity-management-cycle, FFS, RBI concepts; api-579-1 / dnv-rp-g101 / api-rp-580 / 581 standards).
- **Why this is OK**: the original spec target was an unverified inference from the URL keyword "riser life extension". The user's framing "appropriately" implies correctness-by-content, not correctness-by-spec-letter. The deviation was surfaced in chat to the user before execution, not silently absorbed.
- **Process lesson** (candidate workspace-hub feedback memory): for any wiki-ingest spec where the target sub-wiki depends on the document's actual subject matter, the spec phase must include a content-grade read (`pdftotext` / WebFetch / PyMuPDF) of the source before locking the target. URL-keyword inference is unsound. Filed for capture as the matrix-codification memory's process-lesson section.
- **Slug change**: corrected from `bsee-2024-deepwater-riser-life-extension` (spec) to `bsee-2024-deepwater-dynamic-pipeline-riser-life-extension` (executed) — adds "dynamic-pipeline-" to disambiguate from drilling-riser life extension, which is a different regulatory regime.

## Session execution outcome (2026-05-14)

### Commits landed

| Repo | SHA | Purpose | Pushed |
|---|---|---|---|
| workspace-hub | `a2103c707` | Matrix design doc + vendor-PDF inventory file | Yes (auto-sync) |
| workspace-hub | `fbd38f8b5` | D2-DEV-01 deviation log (BSEE rerouted to asset-management) | Yes (auto-sync) |
| workspace-hub | _this commit_ | Session execution outcome appended to this doc | Pending |
| llm-wiki | `86b601c7` | `CLAUDE.md` Vendor-PDFs rule → 6-row matrix; new `docs/governance/service-provider-data-routing.md` | Yes (auto-sync) |
| llm-wiki | `a6b50d23` | BSEE 2024 source page + `wikis/asset-management/wiki/{sources,index.md,log.md}` | **No** — local-only at session exit; auto-sync window did not fire before close. Will sync on next poll OR user can `cd llm-wiki && git push` to force. |

### Private mount deposits (off-repo, no commit)

`/mnt/ace/vendor-pdfs/helix-esg/`:
- `Helix_Well_Ops_Q4000_LTR_2024-09-12.pdf` (3.2 MB, 4 pages)
- `Helix_Well_Ops_IRS-7-15k_LTR_2023-11-28.pdf` (4.0 MB, 4 pages)
- `Helix_riser-based-well-intervention_2026-05-14_snapshot.html` (70 KB)

Inventory entry in `workspace-hub/docs/governance/vendor-pdf-inventory.md`.

### Memory artifact

- New: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_service_provider_data_routing.md` (6.3 KB, 52 lines)
- Indexed: `MEMORY.md` line 95 (217 chars).
- **Caveat**: MEMORY.md is now 30.3 KB, exceeding the documented 24.4 KB load-limit (session-start warned at 28.7 KB). Future sessions will load truncated. Recommend a separate triage pass to retire stale feedback entries before adding more.

### Deferred follow-ups (open work for future sessions)

- **llm-wiki/wikis/asset-management/wiki/concepts/deepwater-dynamic-riser-life-extension-process.md** — concept page synthesizing the 8-step BSEE process with API RP 17G + DNV-OS-F201 + API RP 1160 + API RP 2RIM grounding. Blocked on multi-source grounding per `feedback_llm_wiki_concept_pages_need_public_references`.
- **llm-wiki standards pages**: `api-rp-1160.md`, `api-rp-2rim.md`, `30-cfr-250-subpart-i.md`. CFR routing convention may need a governance issue (similar to #2615 / #2596 for the API/DNV routing). Surface in next planning pass.
- **llm-wiki/wikis/asset-management/wiki/concepts/cva-platform-verification-program.md** — CVA workflow concept page; needs BSEE 30 CFR 250 Subpart B citations + at least one CVA-vendor public technical paper as grounding.
- **llm-wiki/wikis/drilling-engineering/wiki/entities/helix-energy-solutions-fleet.md** — Helix entity page sourced from SEC 10-K + class-society records + at least one OTC/SPE paper. Currently blocked: only vendor-derivative brochures available off-repo. Promote when public-record grounding accumulates.
- **MEMORY.md triage** — retire or consolidate stale feedback entries to get back under 24.4 KB load limit.
- **Promotion-path watch**: track recurrence of vendor-brochure-URL-in-public-wiki anti-patterns. If observed even once, promote the matrix from Level-0 prose to Level-2 pre-commit hook per `.claude/rules/patterns.md` enforcement gradient.

### Cross-session recovery

Future sessions can recover full context from:
1. This design doc (full design + deviation log + outcome).
2. `llm-wiki/docs/governance/service-provider-data-routing.md` (matrix authority).
3. `llm-wiki/CLAUDE.md` (pointer + summary).
4. `workspace-hub/docs/governance/vendor-pdf-inventory.md` (private-mount index).
5. `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_service_provider_data_routing.md` (auto-loaded on session start when index entry survives MEMORY.md truncation).
6. Commit messages on the 5 SHAs above carry redundant trace.

### Notable session observations (not durable but worth recording for the audit trail)

- **Plan-gate hook (from 51887c839) fired correctly** on both workspace-hub commits with `[plan-gate] PASS: No implementation changes or low-risk files only.` — first real-world validation of the marker-label parity gate enforcement.
- **Parallel-session interactions observed**: (a) Codex companion pushing `feat/marker-label-parity-gate` for ~1h10m — ultimately merged as PR #2706 during this session, mid-commit; (b) Hermes orchestrator polling `git status` every ~30s causing 5 retry-loop attempts for the first workspace-hub commit (index.lock contention); (c) production-engineering parallel session landing 4 ingest commits (#63 / #64 / #65 / #66) in llm-wiki, completing PE Phase 1. None of these collided with our subtree-disjoint writes — validates `feedback_parallel_agent_write_only_pattern`.
- **WebFetch report on the BSEE PDF was wrong** — it claimed "binary-heavy / no readable text" when the PDF has selectable embedded text fully extractable via `pdftotext`. Lesson: don't trust WebFetch's PDF-content read; always cross-check with `pdftotext` before declaring a PDF unreadable.

## Post-execution memory hygiene (2026-05-15)

After the session's primary work landed, MEMORY.md was triaged in response to the session-start size-warning (30.3 KB vs. the 24.4 KB load limit; entries after ~line 200 were being truncated for future sessions).

**Cleanup buckets applied** (user-approved as a set):
1. **Trim oversized index entries** to ≤200 chars — ~20 entries shortened by moving detail into their underlying topic .md files. Pure tightening; nothing deleted.
2. **Retire 5 superseded version-specific entries** from index: `codex_cli_0_124_0_upstream_regression`, `gemini_trust_env_blocks_reviews`, `x11vnc_vs_tigervnc_headless`, `wikimedia_thumb_width_quirk`, `python_m_build_no_isolation_flag`. **All 5 topic .md files preserved on disk** — recoverable via direct `Read` if needed.
3. **Consolidate near-duplicate clusters**: 5 Codex-sandbox entries → 1 umbrella entry (`[Codex sandbox model]`); 4 git-multi-agent sub-patterns folded into the existing `[Multi-agent commit serialization]` umbrella. Topic files preserved.
4. **Trim Project DONE entries** in-place — kept all 42 since they were already terse or carried follow-up trackers worth indexing.

**Outcome**: 30,346 bytes → 22,095 bytes (−27%); 2.3 KB under the 24.4 KB load limit with margin. 78 Feedback + 42 Project + 11 Reference entries. Phantom-reference scan: 0 dangling links.

**Reversibility**: pre-cleanup backup preserved at `/tmp/MEMORY.md.20260515-pre-cleanup-backup` (30,346 bytes, original). To restore: `cp /tmp/MEMORY.md.20260515-pre-cleanup-backup ~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md`. All retired/consolidated topic .md files remain on disk in the memory directory.

This cleanup is per-machine state (`~/.claude/projects/...` is not git-tracked) and therefore not part of any commit on this branch — recorded here purely for the audit trail.

## Follow-on research filed as #2714

At exit-time, user asked for research into Gulf of Mexico production progress + Lower Tertiary play + US energy-security framing, with anti-confirmation-bias guardrails against the FDAS (Frontier Deepwater's Field Development Solution) thesis. AceEngineer holds a 5% equity stake in Frontier Deepwater per BUSINESS_BRAIN, so the bias-source is real and the data-must-lead instruction is load-bearing.

Filed as **vamseeachanta/workspace-hub#2714** (labels: `cat:research`, `cat:knowledge-domain`) for execution in a future session. The issue body enumerates:

- Pre-existing wiki coverage to BUILD ON (no re-research): `engineering/concepts/field-development-economics.md` (already references FDAS + 8-field Lower Tertiary dataset), `drilling-engineering` deepwater concepts and entities, the `lng-projects/sources/doe-eia-lng-outlook.md` EIA source-page pattern to mirror.
- Net-new artifacts to create: 5-6 source pages (EIA AEO, BSEE OCS production stats, BOEM lease sales/reserves, USGS 2016 GoM resource assessment, IEA WEO), 3 concept pages (GoM production progress, Lower Tertiary play, US deepwater energy security), 5+ visualizations with CSV inputs.
- Four falsifiable hypotheses with explicit "supports / falsifies" evidence patterns, including H4 which tests the FDAS thesis directly.
- Anti-confirmation-bias guardrails: mandatory bias disclosure, "what would change my mind" sections, counter-position steelman, no vendor-derivative content per the 2026-05-14 matrix.
- Acceptance criteria requiring evidence-led conclusion (allowed: "thesis supported", "partially supported with qualifications", OR "thesis not supported").
- One ambiguity flagged for user clarification before execution: FDAS naming collision (worldenergydata module name vs. Frontier Deepwater branded service line — same thing under two names, or coincidence?).

The matrix from this session governs how the future research handles vendor-derivative materials encountered along the way (Frontier Deepwater own materials → off-repo per row 1; EIA/BSEE/BOEM/USGS → public wiki per row 5).
