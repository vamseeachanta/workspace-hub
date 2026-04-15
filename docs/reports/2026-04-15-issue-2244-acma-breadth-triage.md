# ACMA Breadth Triage — Issue #2244

> **Issue:** [#2244](https://github.com/vamseeachanta/workspace-hub/issues/2244)
> **Parent umbrella:** [#2216](https://github.com/vamseeachanta/workspace-hub/issues/2216)
> **Generated:** 2026-04-15
> **Source quality:** metadata-only — no clause-level claims
> **Evidence base:** Wave 1 family map (#2261), Wave 2 family map (#2262), Wave 1/2 metadata stubs, exit handoff (2026-04-12)

---

## 1. Purpose and Scope

Issue #2226 (ledger/provenance backfill) discovered materially broader content in `/mnt/ace/acma-codes/` than what #2227 was scoped to promote. The current wiki-promotion target (#2227) is intentionally bounded to three documents:

- **OCIMF-TANDEM-MOORING** — Tandem Mooring and Offloading Guidelines
- **CSA-Z276.1-20** — Marine Structures Associated with LNG Facilities
- **CSA-Z276.18** — LNG Production, Storage, and Handling

This triage report classifies **all newly discovered breadth** outside that bounded set, assigns a recommended layer and target repo per item or group, and proposes concrete follow-on issues where implementation is warranted.

### What this report does NOT do

- It does not expand #2227 scope.
- It does not make clause-level claims about any document content (all PDFs are DRM-protected or metadata-only).
- It does not create wiki pages — it only recommends whether wiki promotion is warranted.

---

## 2. Triage Table — Explicitly Named Candidates

These are the items specifically called out in the #2244 issue body for individual triage.

| # | Item | Org | Domain | Source Evidence | Artifact Quality | Recommended Layer | Target Repo/Domain | Rationale | Follow-on? |
|---|------|-----|--------|----------------|-----------------|-------------------|-------------------|-----------|------------|
| 1 | **CSA-Z276.2-19** — Near-Shoreline FLNG Facilities | CSA | marine/LNG | Wave 1 family map (CSA row 2); metadata stub exists | blocked-metadata-only; 102pp; AES/Vitrium DRM | L3 wiki — deferred pending DRM resolution | workspace-hub / LNG wiki domain | Thematically adjacent to Z276.1-20 and Z276.18 (same CSA Z276 family). Strong candidate for LNG wiki domain promotion once DRM-blocked metadata is resolved. Should NOT be absorbed into #2227 — requires its own bounded promotion issue. | Yes |
| 2 | **CSA-B625-13** — Portable Tanks for Transport of Dangerous Goods | CSA | transport/hazmat | Wave 1 family map (CSA row 3); metadata stub exists | blocked-metadata-only; 176pp; AES/Vitrium DRM | Ledger-only (L2) — defer | N/A (out of domain) | Not marine/mooring/LNG domain. Portable tank transport is a distinct regulatory domain. No clear workspace-hub wiki domain exists for this. Keep in ledger for provenance but do not promote. | No |
| 3 | **CSA 22.1-12** — Canadian Electrical Code (Part I) | CSA | electrical | Wave 1 family map (CSA row 4); metadata stub exists as `CSA-22.1-12` | blocked-metadata-only; FileOpen (FOPN) DRM — even pdfinfo failed | Ledger-only (L2) — defer | N/A (out of domain) | The Canadian Electrical Code is a general electrical standard with no specific marine/offshore/LNG focus. Not relevant to any current workspace-hub wiki domain. Metadata extraction itself failed due to proprietary DRM, making even stub quality extremely low. | No |
| 4 | **API RP 2SK — 3rd ed. (2005 base + 2008 addendum)** | API | offshore/mooring | Wave 2 family map (API row 11); metadata stub `API-RP-2SK-3E`; 2 merged fragments (alternate copy + addendum) | blocked-metadata-only; base + addendum consolidated | L3 wiki — group with API mooring family | workspace-hub / mooring wiki domain | Core stationkeeping/mooring standard. Directly relevant to mooring engineering domain. Should be promoted as part of an API mooring/stationkeeping group, not individually. The 2nd edition (1996, superseded) should be a cross-reference within the same wiki page. | Yes |
| 5 | **API RP 2SK — 2nd ed. (1996)** | API | offshore/mooring | Wave 2 family map (API row 1); metadata stub `API-RP-2SK-2E` | blocked-metadata-only; superseded by 3rd ed. | Ledger-only (L2) — superseded | N/A | Superseded by 3rd edition. Keep in ledger for historical provenance. If API RP 2SK 3rd ed. gets promoted, note supersession in that wiki page. | No |

### Naming note: CSA 22.1-12 vs CSA C22.1-12

The issue body references `CSA-C22.1-12`. The repo artifacts (Wave 1 family map, metadata stubs) consistently use `CSA-22.1-12` without the `C` prefix. The `C` prefix is sometimes used in formal CSA references to denote "Canadian" but our file-derived normalized ID is `CSA-22.1-12`. This report uses `CSA 22.1-12` to match the repo convention. Both refer to the same standard: the Canadian Electrical Code, Part I, 2012 edition.

---

## 3. Triage Table — API Family (Grouped)

The Wave 2 inventory contains 22 API standards spanning offshore engineering disciplines. Rather than triaging each individually, they are grouped by domain relevance.

### 3a. Mooring/Stationkeeping (promote as group)

| standard_id | Title | Year | Recommendation |
|-------------|-------|------|----------------|
| API-RP-2SK-3E | Stationkeeping Systems (3rd ed. + 2008 addendum) | 2005 | L3 wiki — mooring domain |
| API-RP-2SK-2E | Stationkeeping Systems (2nd ed.) | 1996 | L2 ledger — superseded; cross-ref in 3E page |

**Rationale:** API RP 2SK is the primary API standard for floating structure stationkeeping. Directly relevant to the mooring engineering domain alongside OCIMF MEG and tandem mooring guidelines.

### 3b. Offshore Structural/Platforms (defer as group)

| standard_id | Title | Year | Recommendation |
|-------------|-------|------|----------------|
| API-RP-2A-WSD | Fixed Offshore Platforms (WSD) | 2007 | L2 ledger — defer |
| API-BULL-2U-3E | Stability Design of Cylindrical Shells | 2004 | L2 ledger — defer |
| API-RP-2H-9E | Carbon Manganese Steel Plate | 2006 | L2 ledger — defer |

**Rationale:** Relevant to offshore structural engineering but not to the current mooring/LNG/marine focus of workspace-hub wiki domains. These belong in a future structural engineering domain if one is created, or in a downstream engineering repo.

### 3c. Offshore Cranes/Lifting (defer as group)

| standard_id | Title | Year | Recommendation |
|-------------|-------|------|----------------|
| API-RP-2D-6E | Offshore Cranes (6th ed.) | 2007 | L2 ledger — defer |
| API-RP-2D-5E | Offshore Cranes (5th ed.) | 2003 | L2 ledger — superseded |
| API-RP-2C | Offshore Pedestal-Mounted Cranes | 2004 | L2 ledger — defer |

**Rationale:** Offshore crane standards are a distinct engineering domain. No current wiki domain exists for them. Keep in ledger.

### 3d. Offshore Safety/Fire/Hazards (defer as group)

| standard_id | Title | Year | Recommendation |
|-------------|-------|------|----------------|
| API-RP-14C-7E | Surface Safety Systems (7th ed.) | 2001 | L2 ledger — defer |
| API-RP-14G | Fire Prevention and Control | 2007 | L2 ledger — defer |
| API-RP-14J-2013 | Design and Hazards Analysis (2013) | 2013 | L2 ledger — defer |
| API-RP-14J-2002 | Design and Hazards Analysis (2002) | 2002 | L2 ledger — superseded |
| API-RP-54 | Occupational Safety | 2013 | L2 ledger — defer |
| API-RP-75 | Safety and Environmental Management | 2013 | L2 ledger — defer |

**Rationale:** Offshore safety/fire/hazards analysis is operationally important but represents a distinct domain. No current wiki domain; could become a downstream repo focus.

### 3e. Offshore Electrical (defer as group)

| standard_id | Title | Year | Recommendation |
|-------------|-------|------|----------------|
| API-RP-14F | Electrical Systems, Offshore Petroleum | 2008 | L2 ledger — defer |
| API-RP-505 | Electrical Installations, Classification | 1997 | L2 ledger — defer |
| API-RP-500 | Electrical Classifications | 1997 | L2 ledger — defer |

**Rationale:** Electrical classification standards for hazardous areas. Distinct domain, no current wiki target.

### 3f. Other API (defer individually)

| standard_id | Title | Year | Recommendation |
|-------------|-------|------|----------------|
| API-RP-1111-3E | Offshore Hydrocarbon Pipelines | 1999 | L2 ledger — defer |
| API-SPEC-7K | Drilling and Well Servicing Equipment | 2001 | L2 ledger — defer |
| API-SPEC-4F | Drilling and Well Servicing Structures | 2013 | L2 ledger — defer |
| API-2INT-MET | GOM Metocean Interim Guidance | 2007 | L2 ledger — defer |
| API-RP-95J | GOM Jackup Operations, Hurricane Season | 2013 | L2 ledger — defer |

**Rationale:** Miscellaneous API standards covering pipelines, drilling, metocean. No current wiki domain alignment.

---

## 4. Triage Table — Other Org Families (Grouped)

### 4a. OCIMF Family (Wave 1) — beyond #2227 scope

| standard_id | Title | Recommendation | Notes |
|-------------|-------|----------------|-------|
| OCIMF-MEG4-4E | MEG4 (4th ed.) | L3 wiki — mooring domain | Core mooring standard; 297pp; strong promotion candidate |
| OCIMF-MEG-3E | MEG3 (3rd ed., 2008) | L3 wiki — mooring domain | Predecessor to MEG4; relevant for edition comparison |
| OCIMF-MEG4-JUSTIFICATION | MEG4 Justification | L2 ledger — supporting | 9pp justification doc; not independently wiki-worthy |
| OCIMF-OVID-OVPQ | OVID Vessel Questionnaire | L2 ledger — defer | Vessel inspection domain, not mooring |
| OCIMF-OVID-APP | OVID Operator Application | L2 ledger — defer | Application form; RC4 encrypted |

**Rationale:** OCIMF MEG3 and MEG4 are the definitive mooring equipment guidelines and are strong L3 wiki promotion candidates for the mooring domain. The OVID items are vessel inspection tools — a different domain.

### 4b. Lloyd's Register Family (Wave 2 — 24 stubs)

| Group | Count | Recommendation | Notes |
|-------|-------|----------------|-------|
| LR Ship Rules (various years) | 8 | Downstream repo — defer | Ship classification rules are a large, versioned corpus. Better suited to a dedicated classification-rules domain or downstream repo. |
| LR Offshore Units / FOIFL | 7 | Downstream repo — defer | Floating installation classification rules. Large corpus with notice fragments. |
| LR Specialty (cranes, stability, lifting, load line, quality, CAPbook) | 6 | L2 ledger — defer | Miscellaneous LR publications. No current wiki domain. |
| LR Classification News | 1 (consolidated from 7 PDFs) | L2 ledger — defer | Newsletter compilation, not a standard. |
| LR Ships Liquefied Gases 2022 | 1 | L2 ledger — potential LNG future | Tangentially LNG-relevant but part of the broader LR rules corpus. |
| **Total** | **24** (unique) | | |

**Rationale:** Lloyd's Register rules are a massive classification corpus that spans decades and multiple editions. Promoting individual editions to workspace-hub wiki would create maintenance burden without clear value. Better suited to a downstream repo with its own edition-tracking strategy.

### 4c. SIGTTO Family (Wave 2 — 13 stubs)

| Group | Count | Recommendation | Notes |
|-------|-------|----------------|-------|
| LNG-focused publications (rollover, risk, fire, hard arms, shipping) | 6 | L3 wiki — LNG domain (deferred, grouped) | SIGTTO is the primary LNG tanker/terminal industry body. These publications are relevant to the LNG wiki domain. |
| Mooring-related (quick release hooks, HMPE mooring lines) | 2 | L3 wiki — mooring domain (deferred, grouped) | Mooring equipment publications complementary to OCIMF MEG. |
| Training/safety/equipment (lifeboat, LSA, valves, insulation, training, HCB) | 5 | L2 ledger — defer | Operational/training materials, not engineering standards. |
| **Total** | **13** | | |

**Rationale:** SIGTTO has strong LNG and mooring domain relevance. The LNG-focused and mooring-related publications are good future wiki candidates but should be promoted as a grouped batch, not absorbed into #2227.

### 4d. Noble Denton / DNV GL Family (Wave 2 — 8 stubs)

| Group | Count | Recommendation | Notes |
|-------|-------|----------------|-------|
| Marine transportation guidelines (ND 0030 variants, GL ND transport) | 3 | L2 ledger — defer | Marine transportation is a distinct domain. Multiple editions with supersession. |
| Marine projects general guidelines (ND 0001, GL ND projects) | 2 | L2 ledger — defer | General marine project management guidelines. |
| Towage (ND 0014, ND 0021) | 2 | L2 ledger — defer | Towage/towing operations. Distinct from mooring. |
| Marine lifting (GL ND lifting/lowering) | 1 | L2 ledger — defer | Lifting operations. Distinct domain. |
| **Total** | **8** | | |

**Rationale:** Noble Denton guidelines are well-established marine engineering references but cover transportation, towage, and lifting — domains not currently served by workspace-hub wikis. Keep in ledger for provenance.

---

## 5. What Remains Out of Scope for #2227

**#2227 is and must remain bounded to exactly three documents:**

1. OCIMF-TANDEM-MOORING
2. CSA-Z276.1-20
3. CSA-Z276.18

The following must NOT be absorbed into #2227, even though they are thematically adjacent:

| Category | Items | Why excluded |
|----------|-------|-------------|
| CSA Z276 family expansion | CSA-Z276.2-19 | Same Z276 family but different standard; requires its own promotion issue |
| CSA non-marine | CSA-B625-13, CSA 22.1-12 | Different regulatory domains entirely |
| OCIMF MEG | OCIMF-MEG4-4E, OCIMF-MEG-3E | Different OCIMF publications; major standards deserving dedicated promotion |
| API RP 2SK | API-RP-2SK-3E + addendum | Different org, different standard; requires its own promotion issue |
| All Wave 2 orgs | LR (24), SIGTTO (13), ND (8), API non-2SK (20) | Entirely different organizations and scope areas |

**Boundary enforcement principle:** #2227 was scoped before the Wave 1/2 inventories existed. Expanding it retroactively would defeat the purpose of bounded planning. Each group above that warrants promotion should get its own issue with its own plan.

---

## 6. Follow-on Issue Map

Based on the triage above, the following bounded follow-on issues are proposed:

### Issue A: CSA Z276 Family Completion — Wiki Promotion

- **Proposed title:** `feat(wiki): promote CSA Z276.2-19 to LNG wiki domain`
- **Why split:** Z276.2-19 is the natural companion to Z276.1-20 and Z276.18 (already in #2227), but adding it to #2227 would break the approved plan boundary. It shares the same DRM blocker, so it can follow #2227's resolution pattern.
- **Suggested labels:** `enhancement`, `cat:documentation`, `priority:medium`
- **Owned-path expectation:** Wiki page creation in LNG domain; depends on DRM resolution from #2245/#2227 chain
- **Blocked by:** #2227 completion (to reuse the DRM resolution pattern)

### Issue B: OCIMF MEG3/MEG4 — Wiki Promotion (Mooring Domain)

- **Proposed title:** `feat(wiki): promote OCIMF MEG3 and MEG4 to mooring wiki domain`
- **Why split:** MEG4 (297pp) and MEG3 (293pp) are the definitive OCIMF mooring guidelines. They are substantial standards that deserve dedicated wiki pages with edition cross-referencing. Far too large and distinct to bundle into the tandem-mooring-focused #2227.
- **Suggested labels:** `enhancement`, `cat:documentation`, `priority:medium`
- **Owned-path expectation:** Two wiki pages (MEG3, MEG4) in mooring domain with edition lineage and fragment inventory

### Issue C: API RP 2SK — Wiki Promotion (Mooring/Stationkeeping)

- **Proposed title:** `feat(wiki): promote API RP 2SK 3rd ed. to mooring wiki domain`
- **Why split:** API RP 2SK is the primary API stationkeeping standard for floating structures. It has a natural home in the mooring wiki domain alongside OCIMF content. The 2nd edition should be cross-referenced as superseded. Separate from #2227 because it is a different org and standard.
- **Suggested labels:** `enhancement`, `cat:documentation`, `priority:medium`
- **Owned-path expectation:** One wiki page covering 3rd ed. + 2008 addendum; cross-reference to superseded 2nd ed.

### Issue D: SIGTTO Batch — Wiki Promotion (LNG + Mooring Domains)

- **Proposed title:** `feat(wiki): promote SIGTTO LNG and mooring publications as batch`
- **Why split:** SIGTTO has 8 publications (6 LNG, 2 mooring) that are relevant to existing wiki domains. Promoting them as a single batch avoids per-item issue overhead. The remaining 5 (training/safety materials) stay in ledger.
- **Suggested labels:** `enhancement`, `cat:documentation`, `priority:low`
- **Owned-path expectation:** 8 wiki pages across LNG and mooring domains; batch creation to avoid issue proliferation

### Issue E: Lloyd's Register / Noble Denton — Downstream Domain Assessment

- **Proposed title:** `feat(architecture): assess LR and Noble Denton corpus for downstream repo routing`
- **Why split:** LR (24 stubs) and Noble Denton (8 stubs) represent large classification/marine-transport corpora with complex edition histories. They don't fit naturally into existing workspace-hub wiki domains. This issue should assess whether a downstream engineering repo is the right home, or whether a new wiki domain should be created.
- **Suggested labels:** `enhancement`, `cat:architecture`, `priority:low`
- **Owned-path expectation:** Architecture decision record; no wiki pages created — only routing recommendation

---

## 7. Linkage to #2216 and #2227

### Relationship to #2216 (ACMA Umbrella)

Issue #2216 is the umbrella tracking all ACMA-related work. This triage report (#2244) is a direct child of #2216 and fulfills the umbrella's requirement that all newly discovered breadth be explicitly classified rather than left implicit. The follow-on issues proposed above (A through E) would each become new children of #2216.

**Chain:** #2216 (umbrella) → #2226 (discovery) → #2244 (triage) → Issues A-E (implementation)

### Relationship to #2227 (Bounded Wiki Promotion)

Issue #2227 remains bounded to its three approved targets (OCIMF-TANDEM-MOORING, CSA-Z276.1-20, CSA-Z276.18). This triage report explicitly prevents scope creep into #2227 by:

1. Classifying all out-of-scope items discovered in #2226
2. Routing each to its own follow-on issue where promotion is warranted
3. Documenting the boundary enforcement principle (Section 5)

**#2227 should not reference this triage report as a source of additional scope.** It should reference it only as evidence that out-of-scope items were handled elsewhere.

### Relationship to #2245 (Unblock Prerequisites)

Issue #2245 (prepare summary/classification artifacts) is the prerequisite for #2227 execution. The DRM resolution pattern established by #2245/#2227 may be reused by follow-on Issues A and B, which face the same blockers.

---

## 8. Summary Statistics

| Category | Count | L3 Wiki (future) | L2 Ledger | Downstream Assessment |
|----------|-------|-------------------|-----------|----------------------|
| CSA (triage candidates) | 3 | 1 (Z276.2-19) | 2 (B625-13, 22.1-12) | 0 |
| API RP 2SK family | 2 | 1 (3rd ed.) | 1 (2nd ed., superseded) | 0 |
| API other | 20 | 0 | 20 | 0 |
| OCIMF (beyond #2227) | 4 | 2 (MEG3, MEG4) | 2 (OVID items) | 0 |
| SIGTTO | 13 | 8 (LNG + mooring) | 5 (training/safety) | 0 |
| Lloyd's Register | 24 | 0 | 0 | 24 |
| Noble Denton | 8 | 0 | 0 | 8 |
| **Total** | **74** | **12** | **30** | **32** |

> Note: The 3 documents already in #2227 scope (OCIMF-TANDEM-MOORING, CSA-Z276.1-20, CSA-Z276.18) are NOT counted here — they are handled by #2227.
