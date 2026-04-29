# Plan for #2544: feat(llm-wiki) — scout Woodfibre LNG corpus for bounded extraction candidates

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-04-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2544
> **Review artifacts:** _pending — adversarial review not yet run for this overnight wave; provider verdicts to be filed under `scripts/review/results/2026-04-28-plan-2544-<claude|codex|gemini>.md` once a permitted reviewer session runs._

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.planning/intel/elements-to-llm-wiki/elements-ingested-files.jsonl` — 41,561 records; bucket-filter `acma-projects-31522-woodfibre` returns 5,364 records totaling 1,879,405,139,855 bytes (1.879 TB). Each record carries `absolute_path`, `relative_path`, `extension`, `content_kind`, `bytes`, `mtime_ns`, `parent_exists`, `same_size`, `hardlinked_to_staging`.
- Found: `.planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md` — bucket #8 entry: `acma-projects-31522-woodfibre` → wiki `lng-projects`, `extract_priority: metadata-only`, retention verification clean (`missing=0, size_mismatch=0, not_hardlinked=0`).
- Found: `.planning/intel/elements-to-llm-wiki/batches/lng-projects.jsonl` — 2 records (Woodfibre + SESA companion bucket).
- Found: `knowledge/wikis/lng-projects/` — wiki initialized 2026-04-28 19:23 UTC; `wiki/sources/`, `wiki/entities/`, `wiki/concepts/`, `wiki/standards/` directories present and **empty** (no #2535 source page emitted yet for either Woodfibre or SESA).
- Found: `.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv` — Woodfibre is **not** in the deep-extraction queue (zero matches), consistent with its `metadata-only` priority.
- Gap: no Woodfibre source-of-record pointer page in `lng-projects/wiki/sources/`. Gap: no shape/scope intelligence for the corpus exists in the workspace prior to this plan.

### Standards
| Standard | Status | Source |
|---|---|---|
| n/a (project corpus, not a standards bucket) | not applicable | This bucket holds project deliverables under ACMA EDMS prefix `350106-SC-EN-003-SD-XXXXXX`; standards consulted by the project are not the artefact being catalogued. |

### LLM Wiki pages consulted
- `knowledge/wikis/lng-projects/CLAUDE.md` — wiki conventions: frontmatter schema (`title`, `tags`, `added`, `last_updated`, `sources`, optional `domain`/`cross_links`); Standards-page extra fields (`code_id`, `publisher`, `revision`) — not exercised by this plan.
- `knowledge/wikis/lng-projects/wiki/index.md`, `wiki/log.md`, `wiki/overview.md` — present but unpopulated (auto-generated stubs from `llm-wiki init`).
- `knowledge/wikis/lng-projects/wiki/sources/` — empty directory; no contradiction risk for proposed `woodfibre-*` source pages.
- No companion-bucket pointer page exists for `doris-62092-sesa` either; coordination with Terminal-1 plan is captured under "Cross-corpus boundary".

### Documents consulted
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/master-plan.md` — overnight wave governance: planning-only, no `/mnt/ace` writes, no raw bulk extraction, no self-approval.
- `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md` — sibling overnight-wave plan; this plan adopts the same artifact-map and approval-boundary conventions.
- `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md` — companion scout produced by this terminal (depth-2 structure, extension histogram, content-kind histogram, document-control register decode, risk assessment, uncertainties).
- `.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv` — 15-row candidate matrix with `priority`, `family`, `content_kind`, `bytes`, `absolute_path`, `rationale`, `extraction_method`, `target_wiki_page`, `confidentiality_risk`.
- `.claude/rules/calc-citation-contract.md` — confirms `wiki/sources/*` are deny-list for calc citations; this plan does not route any calc citations into Woodfibre source pages.
- Issue body #2544 + parents #2540 (umbrella), #2526 (parent ingest), #2534 (retention), #2535 (metadata indexing), #2536 (first-pass extraction).

### Gaps identified
- No Woodfibre source-of-record pointer page in `lng-projects/wiki/sources/` (would be #2535's residue, never emitted for this bucket).
- No structured catalogue of the ACMA EDMS document register (`DB`, `RA`, `FD`, `SA`, `TN`, `WS`, `XA`, `XD`, `XE`, `XG`, `LA`, `DS`, `CA`, `DEMOLITION`) inside the wiki.
- No client-confidentiality boundary statement against the lng-projects wiki has been written; this is required before any extracted content can land publicly.
- No latest-revision policy is documented for ACMA EDMS revision-letter conventions in either `lng-projects/CLAUDE.md` or any project rule.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-28 via `gh issue view`):
- `#2544` — OPEN — feat(llm-wiki): scout Woodfibre LNG corpus for bounded extraction candidates
- `#2540` — OPEN — epic(llm-wiki): overnight Elements corpus planning wave after #2536
- `#2535` — referenced (closed) — completed metadata indexing parent
- `#2536` — referenced (closed) — completed first-pass extraction parent
- `#2534` — referenced — retention/cleanup boundary

**File existence** (workspace reads, 2026-04-28):
- EXISTS: `.planning/intel/elements-to-llm-wiki/elements-ingested-files.jsonl`
- EXISTS: `.planning/intel/elements-to-llm-wiki/batches/lng-projects.jsonl`
- EXISTS: `.planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md`
- EXISTS: `knowledge/wikis/lng-projects/CLAUDE.md`
- EXISTS: `knowledge/wikis/lng-projects/wiki/{index.md,log.md,overview.md}`
- EXISTS (empty): `knowledge/wikis/lng-projects/wiki/sources/`
- EXISTS (this plan creates): `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md`
- EXISTS (this plan creates): `.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv`
- MISSING (deferred — implementation PR creates): `knowledge/wikis/lng-projects/wiki/sources/woodfibre-corpus-pointer.md`
- MISSING (deferred — implementation PR creates): `knowledge/wikis/lng-projects/wiki/sources/woodfibre-{15 named pages}.md`

**Corpus-shape evidence** (jq-aggregated from JSONL, 2026-04-28):

Top-level dirs (count, bytes):
```
2658 files / 1,800,448,567,394 bytes  02.Mooring Analysis
 549 files /    61,975,609,685 bytes  04.Model Test Correlation
 296 files /    11,852,953,908 bytes  03.Ansys FEA
 500 files /     3,394,217,689 bytes  05.Deliverables
1344 files /     1,732,554,612 bytes  orcaflex_no_sim
  17 files /         1,236,567 bytes  01.Stability
```

Extension histogram (top 6 by bytes):
```
.sim   1,383 / 1,854.72 GB   ← OrcaFlex time-history binaries (DO NOT extract)
.csv     144 /     4.10 GB
.dat     137 /     4.01 GB
.pdf     321 /     2.68 GB
.sldprt    9 /     2.43 GB   ← SolidWorks parts (skip)
.docx     65 /     0.41 GB
```

content_kind histogram:
```
engineering-data 4,269 / 1,858.74 GB   (overwhelmingly .sim binaries)
other              353 /    11.64 GB
tabular            173 /     4.11 GB
pdf                321 /     2.68 GB
cad                 85 /     0.91 GB
text                68 /     0.88 GB
document            77 /     0.41 GB
presentation        17 /     0.03 GB
image                1 /     0.00 GB
```

**ACMA EDMS register decode** (from path tokens — uncertainty: not opened, naming-pattern inferred):
```
DB Design Briefs                          14 files
RA Reports                                 6 files
FD Project design criteria/philosophies   31 files
SA Specifications & Standards              9 files
TN Technical Notes                        25 files
WS Workshop Sessions                       4 files
XA Flow Diagrams (P&IDs)                  21 files
XD General arrangements                   21 files
XE Layout drawings                         6 files
XG Structural information                115 files
LA Lists & Registers                       9 files
DS Data sheets                            25 files
CA Analysis                               49 files
DEMOLITION (CAPRICORN+TAURUS)            162 files  (record drawings; very large)
```

**Cross-corpus** (companion bucket also in `lng-projects`):
- `doris-62092-sesa` — 418 files / 1,465,267,463 bytes — scouted by Terminal 1 in this overnight wave.

<!-- Distinct source count: issue #2544 body (1) + #2540 (2) + #2535 (3) + intel JSONL (4) + intel domain summary (5) + lng-projects/CLAUDE.md (6) + master-plan.md (7) + sibling #2543 plan (8) + .claude/rules/calc-citation-contract.md (9). 9 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` |
| Corpus scout (intel) | `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md` |
| First-tranche TSV (intel) | `.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv` |
| Terminal-4 result | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-4-woodfibre.md` |
| Future implementation issue | (not created here) — would spawn `feat(llm-wiki): emit Woodfibre LNG corpus pointer + bounded 15-doc abstract pages (post-ACMA-clearance)` |
| Future wiki updates | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-corpus-pointer.md` + 15 abstract pages — emitted only after `status:plan-approved` AND ACMA / project-owner clearance |
| Plan review — Claude | `scripts/review/results/2026-04-28-plan-2544-claude.md` (pending) |
| Plan review — Codex | `scripts/review/results/2026-04-28-plan-2544-codex.md` (pending) |
| Plan review — Gemini | `scripts/review/results/2026-04-28-plan-2544-gemini.md` (pending) |

---

## Deliverable

A reviewable, metadata-first scout for the Woodfibre LNG (ACMA project 31522) corpus that, when approved, authorizes a bounded ≤15-document abstract extraction into the `lng-projects` wiki — strictly metadata + 1-page summary per document, no raw bytes copied to git, and conditional on explicit ACMA / project-owner confidentiality clearance.

---

## Pseudocode

```
PLAN-AUTHORIZED IMPLEMENTATION (deferred — runs only after status:plan-approved AND
                                ACMA / project-owner sign-off recorded in implementation issue):

1. Confidentiality clearance gate (HARD BLOCK):
     human reviewer (project lead) confirms each row of woodfibre-first-tranche.tsv
     is approved for abstract publication; sign-off filed under:
       docs/governance/woodfibre-extraction-clearance-2026.md
     If any row is rejected, drop it from the implementation set.

2. Create wiki/sources/woodfibre-corpus-pointer.md:
     frontmatter (title, tags=[woodfibre, lng, fst, mooring, acma-31522],
                  added, last_updated, sources, domain=lng-projects, cross_links)
     body: corpus pointer to /mnt/ace/acma-projects/31522-woodfibre-lng (no embed)
     body: top-level structure table (from scout)
     body: ACMA EDMS register decode
     body: explicit no-extraction banner for .sim/.r00X/.sldprt/.wbpz
     body: cross-link to companion bucket sources/sesa-corpus-pointer.md (if Terminal-1
           plan also approved) and to umbrella #2540

3. For each approved row in woodfibre-first-tranche.tsv:
     extract via row.extraction_method:
       - docx: python-docx → text → 1-page abstract template
       - pdf:  pdfplumber  → text → 1-page abstract template
       - txt:  inline quote (≤2 KB cap)
     emit knowledge/wikis/lng-projects/wiki/sources/<row.target_wiki_page>:
       frontmatter:
         title: <human-readable from filename, ACMA doc-number suffix preserved>
         tags: [woodfibre, lng, fst, <family-tag>]
         added: 2026-XX-XX
         last_updated: 2026-XX-XX
         sources: [<absolute_path>]
         domain: lng-projects
       body sections:
         - Document identity: ACMA EDMS doc-number, revision letter, file size
         - Provenance pointer: absolute_path (no byte copy)
         - Abstract: 1-page summary, methodology-only; no specific numerical values
         - Confidentiality: row.confidentiality_risk + ACMA clearance reference
         - Latest-revision marker: explicit note that older revs exist and were skipped

4. Update wiki/index.md to list 1 pointer + 15 abstract pages (16 row appends).

5. Append wiki/log.md entry:
     ## [2026-XX-XX] ingest | Woodfibre LNG (ACMA 31522) — bounded 15-doc tranche
     - Corpus pointer: woodfibre-corpus-pointer.md
     - Abstract pages: 15
     - Clearance ref: docs/governance/woodfibre-extraction-clearance-2026.md

6. Update wiki/overview.md to anchor Woodfibre as one of two seeded LNG-project
   case studies (the other being SESA, Terminal-1).

7. Open follow-up issue: "verify Woodfibre tranche abstracts via project-lead
   1-pass review" — closes only after ACMA confirms each abstract is publishable.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` | this plan |
| Create | `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md` | corpus structure intel |
| Create | `.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv` | candidate tranche matrix |
| Create | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-4-woodfibre.md` | overnight-wave result summary |
| (DEFERRED — only if approved + ACMA-cleared) Create | `docs/governance/woodfibre-extraction-clearance-2026.md` | sign-off record |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-corpus-pointer.md` | corpus pointer page |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-fst-naval-architecture-design-brief.md` | abstract for DB rev C1 |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-fst-structural-design-brief.md` | abstract for DB rev C |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-fst-structural-design-basis.md` | abstract for DB basis rev B |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-model-test-correlation-report.md` | abstract for SD-000114 rev B |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-fst1-ise-capricorn-report.md` | abstract for SD-000010 rev B |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-fst2-ise-taurus-report.md` | abstract for SD-000024 rev B |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-fst-report-sd-000171.md` | abstract for RA SD-000171 rev B1 |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-permanent-mooring-interface-loads.md` | abstract for SD-000163 rev C1 |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-stability-and-ballast-requirements.md` | abstract for SD-000158 rev C |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-loading-arm-motions.md` | abstract for SD-000157 rev E |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-operational-maintenance-failure-loadcases.md` | abstract for SD-000172 rev B |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-fst-cp-system-design-philosophy.md` | abstract for FST CP rev B |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-fst-load-monitoring-system-philosophy.md` | abstract for SD-000168 rev B1 |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-design-criteria-sd-000141.md` | abstract for FD SD-000141 rev C |
| (DEFERRED — only if approved + ACMA-cleared) Create | `knowledge/wikis/lng-projects/wiki/sources/woodfibre-orcaflex-no-sim-readme.md` | inline-quote of corpus readme |
| (DEFERRED — only if approved + ACMA-cleared) Modify | `knowledge/wikis/lng-projects/wiki/index.md` | append 16 new sources/* rows |
| (DEFERRED — only if approved + ACMA-cleared) Modify | `knowledge/wikis/lng-projects/wiki/log.md` | append ingest entry |
| (DEFERRED — only if approved + ACMA-cleared) Modify | `knowledge/wikis/lng-projects/wiki/overview.md` | seed lng-projects domain narrative |

This plan does **not** authorize emission of the deferred files. Those land in a separate implementation PR after `status:plan-approved` is set by the user **and** ACMA / project-owner clearance is recorded.

---

## TDD Test List

The deliverables in this plan are documentation/metadata pages; the relevant verification is structural rather than numerical. Tests are written against the page set as a whole, plus binary boundary checks on the corpus.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_no_raw_bytes_under_git | no PDF/DOCX/SIM/SLDPRT/WBPZ copied from `/mnt/ace/acma-projects/31522-woodfibre-lng` is tracked in git | `git ls-files knowledge/wikis/lng-projects/` filtered by binary extensions | empty result |
| test_no_sim_or_cad_paths_in_pages | no abstract page references a `.sim`, `.r001-3`, `.sldprt`, `.wbpz`, `.scdoc`, `.osav`, `.esav`, `.rst`, `.db`, `.mechdb`, `.dspsymb` file | grep over `wiki/sources/woodfibre-*.md` | zero matches |
| test_frontmatter_required_fields | every new wiki page has required frontmatter (`title`, `tags`, `added`, `last_updated`, `domain`, `sources`) | each new `.md` page | YAML parse passes; required keys present |
| test_acma_doc_number_present | every abstract page references its ACMA EDMS doc-number in frontmatter sources | each abstract page | substring matching `350106-SC-EN-003` (or equivalent corpus-prefixed identifier) |
| test_latest_revision_only | only the latest-revision file in any rev family is referenced; older revs are not linked | grep abstract pages for rev letters | each doc-number appears with at most one rev letter |
| test_index_links_resolve | every link added to `wiki/index.md` resolves to an existing file | parsed index links | each target file exists |
| test_no_extraction_banner_present | the corpus pointer page contains an explicit no-extraction banner for sim/CAD binaries | `wiki/sources/woodfibre-corpus-pointer.md` body | substring `no-extraction` or `metadata-only` |
| test_acma_clearance_reference_present | the corpus pointer page references the clearance record | `wiki/sources/woodfibre-corpus-pointer.md` body | substring `docs/governance/woodfibre-extraction-clearance-2026.md` |
| test_provenance_backlinks_present | each abstract page links to its absolute source path | each new abstract page | substring `/mnt/ace/acma-projects/31522-woodfibre-lng/` present in sources frontmatter |
| test_corpus_size_assertion | the pointer page records the 1.879 TB / 5,364-file corpus shape | pointer page body | substrings `1.879` and `5,364` |
| test_demolition_excluded | DEMOLITION/CAPRICORN/TAURUS PDFs are not in any abstract page | grep wiki for `100[012]\d\d_A` (DEMOLITION doc-number prefix) | zero matches |

For the planning artifacts in this PR, the analogous gate is `test -s` on each output file (run during overnight verification step).

---

## Acceptance Criteria

- [ ] Plan file exists at `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` and is non-empty.
- [ ] Corpus scout exists at `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md` and is non-empty.
- [ ] First-tranche TSV exists at `.planning/intel/elements-overnight-wave/woodfibre-first-tranche.tsv` with 15 candidate rows + header.
- [ ] Plan is metadata-first: zero proposed copy of raw bytes (PDF/DOCX/SIM/CAD) into git/wiki.
- [ ] Tranche is bounded to ≤15 artifacts; total proposed bytes ≤ ~80 MB; no `.sim` / `.r00X` / `.sldprt` / `.wbpz` / `.scdoc` / `.osav` / `.esav` / `.rst` / `.mechdb` rows.
- [ ] Plan states `/mnt/ace`-write boundary (none) and #2534 retention boundary.
- [ ] Plan documents confidentiality posture: every candidate marked `confidentiality_risk: high` or `medium` and gated on ACMA / project-owner clearance.
- [ ] Plan identifies that additional ACMA / client confidentiality review **is required** before extraction.
- [ ] DEMOLITION/CAPRICORN/TAURUS subdir explicitly excluded from first tranche.
- [ ] Issue is left at `status:plan-review`; plan is **not** self-approved.
- [ ] Result summary file exists under `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/`.
- [ ] (Deferred to implementation PR) All TDD-test rows above pass on the eventual wiki page set.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | _pending_ | overnight wave dispatched; review not yet run for #2544 |
| Codex | _pending_ | codex-cli 0.124.0 stdin-hang regression open (#2479) — fall back to Codex web/Workbench if `codex exec` blocks |
| Gemini | _pending_ | known sandbox overlay-blindness risk for sparse-checkout paths; verify any "file missing" claims with `git ls-files` before accepting |

**Overall result:** _pending — plan-review pending adversarial round; no self-approval._

Revisions made based on review:
- (to be appended after reviewers run)

---

## Risks and Open Questions

- **Risk:** Project-owner identity and IP terms are inferred from filename tokens (`WoodfibreLNG`, `WSP Interface loads`, `FST-1/FST-2`, `Capricorn/Taurus`). Mitigation: every abstract page is gated on `docs/governance/woodfibre-extraction-clearance-2026.md` sign-off. The implementation PR may proceed only after ACMA confirms client-IP posture in writing.
- **Risk:** ACMA EDMS revision-letter convention is assumed (B = IFR, C = IFA, sub-numbers = sub-revisions). If the convention differs, the "latest-revision" rule may pick a wrong file. Mitigation: implementation step calls a 2-row sanity check ("does the chosen rev's mtime exceed all sibling revs?") — if not, escalate.
- **Risk:** OrcaFlex `.sim` files (1.8 TB) are catastrophic if any extraction script lacks an extension allowlist. Mitigation: implementation enforces `--allow-ext .pdf,.docx,.txt,.md,.rtf` and `--max-bytes 25_000_000`. Test `test_no_sim_or_cad_paths_in_pages` is the trip-wire.
- **Risk:** Demolition record drawings (162 files, 14 MB avg) under `05.Deliverables/DEMOLITION/{CAPRICORN,TAURUS}` may carry separate third-party (prior-vessel-owner) IP. Mitigation: explicit exclusion at TSV level + `test_demolition_excluded`.
- **Risk:** Document-number `350106-SC-EN-003-SD-000XXX` may be referenced from DORIS or other internal systems; abstracting them in a public wiki could be cross-referenced back to the project. Mitigation: clearance gate; `confidentiality_risk` flag on every row.
- **Risk:** Past-tense drift (per memory: `feedback_plan_past_tense_artifact_claims.md`) — this plan describes proposed wiki pages as deferred, not committed. The artifact map labels them DEFERRED.
- **Risk:** Cross-corpus collision in `lng-projects` wiki — Terminal-1 (SESA) is producing companion pointer pages in the same domain. Mitigation: all Woodfibre source pages are `woodfibre-` prefixed; SESA's must be `sesa-` prefixed (coordinate at implementation time).
- **Open:** Should the corpus pointer page be committed independently (lower-risk: structure metadata only, no document abstracts) before the 15-doc abstract tranche, to de-risk the clearance step? (Defer to project-owner reviewer.)
- **Open:** Should the model test correlation report (#4 in tranche, 13 MB PDF) be split into a numerical-results-omitted abstract vs a methodology-only abstract? (Defer to ACMA reviewer's confidentiality call.)
- **Open:** Is there an external Woodfibre LNG public regulator filing (BC OGC / EAO) that has already published comparable summaries? If so, the abstracts can cite the public filing instead of paraphrasing internal docs — eliminates clearance friction for any shared content. (Researcher follow-up.)

---

## Approval Boundary

This plan is left at `status:plan-review`. It does **not** carry `status:plan-approved`. The overnight terminal that produced it does not, and must not, set the approval label. Per `feedback_never_offer_to_self_label_plan_approved.md`, that gate is user-in-loop and load-bearing across session boundaries.

A second gate sits between `status:plan-approved` and any wiki write: ACMA / project-owner confidentiality clearance, recorded in `docs/governance/woodfibre-extraction-clearance-2026.md`. The implementation issue cannot proceed past pointer-page emission until that record exists.

---

## Complexity: T2

**T2** — multiple new planning artifacts plus a deferred multi-file wiki ingestion (1 corpus pointer + 15 abstract pages + index/log/overview updates = 19 wiki edits). No code changes in this plan. The bounded-extraction script that consumes the TSV is a follow-up implementation issue, not part of this plan.
