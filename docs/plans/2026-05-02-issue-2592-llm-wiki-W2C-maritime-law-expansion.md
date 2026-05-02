# Plan for W2-C: feat(llm-wiki) — maritime-law wiki topical expansion (IMO conventions + 10 core concepts)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2592
> **Review artifacts:** scripts/review/results/2026-05-02-plan-W2C-maritime-law-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

Wiki target tree: `knowledge/wikis/maritime-law/wiki/` — 22 markdown files on disk. Directory schema declared in `knowledge/wikis/maritime-law/CLAUDE.md` (frontmatter contract: `title`, `tags`, `added`, `last_updated` required; `sources`, `cross_links` recommended). The wiki migrated from two YAML seeds (`knowledge/seeds/maritime-law-cases.yaml`, `knowledge/seeds/maritime-liabilities.yaml`) on 2026-04-07; **no `wiki/standards/` directory exists yet** and no `entities/` page covers IMO regulatory bodies.

Inventory by subdirectory (verified `find … -name "*.md" | sort` 2026-05-02):

- `wiki/concepts/` — 7 pages: `athens-convention-2002.md`, `bunker-convention-2001.md`, `clc-1992.md`, `environmental-liability.md`, `hns-convention-2010.md`, `llmc-1996.md`, `opa-90.md`.
- `wiki/entities/` — 10 case-law pages: `amoco-cadiz-1978.md`, `deepwater-horizon-2010.md`, `eurasian-dream-2002.md`, `msc-flaminia-2012.md`, `mv-erika-1999.md`, `mv-ever-given-2021.md`, `mv-prestige-2002.md`, `mv-wakashio-2020.md`, `sea-empress-1996.md`, `torrey-canyon-1967.md`.
- `wiki/sources/` — 2 pages: `maritime-law-cases.md`, `maritime-liability-conventions.md`.
- `wiki/standards/` — **does not exist** (`ls` reports absent).
- Top-level: `index.md`, `log.md`, `overview.md`.

Key shape observations:

- The 6 existing convention pages currently sit under `concepts/` despite carrying `code_id`-able identity (CLC-1992, LLMC-1996, OPA-90, etc.). Per #2471 routing principle and the constraint stated by the task, **IMO/national-statute conventions are standards-pages, not concept pages** — they belong under `wiki/standards/<code-id>.md`. This plan does NOT relocate the 6 existing convention pages (out of scope; flagged as Open Question for a follow-up); new IMO conventions added by this plan WILL land in `wiki/standards/` with proper `code_id`/`publisher`/`revision` frontmatter.
- The frontmatter in 5 of the 6 existing convention pages uses singular `source:` (deprecated) where `CLAUDE.md` recommends plural `sources:`. Outside this plan's scope.
- The 6 existing convention pages are **descriptive shells** (Summary table + 1–3 sentence Details), not concept-abstraction pages. There are NO concept-abstraction pages for general average, salvage, limitation of liability (only the LLMC convention page), port-state control, flag-state jurisdiction, charterparties, bills of lading, or marine insurance.

### Standards

Maritime-law standards-page production is **bootstrapping from zero**. Per `.claude/rules/calc-citation-contract.md`, calc-module citations need wiki pages with `code_id`/`publisher`/`revision` frontmatter; maritime-law wiki has no such pages today. The plan introduces 4 new standards pages under `wiki/standards/` (the first ever in this wiki).

| Standard | Status | Source |
|---|---|---|
| MARPOL 73/78 (IMO consolidated, six annexes incl. 2020 sulphur cap) | gap (not codified — only mentioned in `mv-wakashio-2020.md` body) | https://www.imo.org/en/about/Conventions/Pages/International-Convention-for-the-Prevention-of-Pollution-from-Ships-(MARPOL).aspx |
| SOLAS 1974 as amended | gap | https://www.imo.org/en/About/Conventions/Pages/International-Convention-for-the-Safety-of-Life-at-Sea-(SOLAS),-1974.aspx |
| MLC 2006 (Maritime Labour Convention, ILO) | gap; corpus exists at `/mnt/ace/acma-codes/ABS Rules/ILO Maritime Labour Convention/` | https://www.ilo.org/global/standards/maritime-labour-convention/lang--en/index.htm |
| COLREGs 1972 | gap | https://www.imo.org/en/About/Conventions/Pages/COLREG.aspx |
| ISM Code (incorporated SOLAS Ch IX) | mentioned only in pre-existing case bodies | https://www.imo.org/en/OurWork/HumanElement/Pages/ISMCode.aspx |
| ISPS Code | gap | https://www.imo.org/en/OurWork/Security/Pages/SOLAS-XI-2%20ISPS%20Code.aspx |
| Nairobi Wreck Removal 2007 | gap | https://www.imo.org/en/About/Conventions/Pages/Nairobi-International-Convention-on-the-Removal-of-Wrecks.aspx |
| BWM 2004 (Ballast Water Management) | gap | https://www.imo.org/en/About/Conventions/Pages/International-Convention-for-the-Control-and-Management-of-Ships-Ballast-Water-and-Sediments-(BWM).aspx |

### LLM Wiki pages consulted

- `knowledge/wikis/maritime-law/wiki/index.md` — confirms `page_count: 20` in frontmatter (auto-generated from seed YAMLs) while on-disk count is 22 (index regenerator discrepancy similar to #2589 — index.md and overview.md not catalogued). This plan will refresh `page_count` accordingly.
- `knowledge/wikis/maritime-law/CLAUDE.md` — frontmatter schema (title, tags, added, last_updated mandatory; sources/cross_links recommended). Architecture parent: `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (#2205).
- `knowledge/wikis/maritime-law/wiki/concepts/llmc-1996.md` (lines 1–33) — confirms current convention-page style: `Summary` table + `Details` (1 sentence) + `Cases Testing This Convention` + `Cross-References`. ~150 words. Strong candidate for routing forward into a concept page on **limitation-of-liability doctrine** (separate from the convention surface).
- `knowledge/wikis/maritime-law/wiki/concepts/clc-1992.md`, `opa-90.md`, `bunker-convention-2001.md`, `hns-convention-2010.md`, `athens-convention-2002.md` (lines 1–33 each) — same template; all will benefit from concept-abstraction layer above them (e.g., `concepts/marine-pollution-liability-regimes.md`).
- `knowledge/wikis/maritime-law/wiki/concepts/environmental-liability.md` — already serves as a concept-abstraction page over the conventions; demonstrates the pattern. NEW concept pages will follow this shape.
- `knowledge/wikis/maritime-law/wiki/sources/maritime-liability-conventions.md` — 6-row summary table; the 4 new standards pages will be linked from a refreshed sources index in a future pass (not in this plan; flagged Open Question).
- Sibling: `knowledge/wikis/naval-architecture/wiki/` — precedent for batch-of-10 expansion shape (#2589, plan dated 2026-05-02). Sibling: `knowledge/wikis/marine-engineering/wiki/` — referenced via cross-links from existing maritime-law pages; not in scope.

### Documents consulted

- `docs/plans/_template-issue-plan.md` — followed structure verbatim; retrieval contract requires ≥3 distinct sources with embedded evidence.
- `docs/plans/2026-05-02-issue-2589-llm-wiki-W1D-naval-architecture-expansion.md` — W1-D precedent; this plan mirrors its shape (10 new pages, frontmatter contract, see-also test, word-count cap, single index/log update). Differences: maritime-law gets MIXED concepts + standards (per #2471 routing for IMO conventions); naval-arch was concepts-only.
- `.claude/rules/calc-citation-contract.md` — concept pages do not emit `Citation` instances (citations are calc-module artifacts); the 4 new standards pages WILL carry `code_id`/`publisher`/`revision` frontmatter so future calc-module citations (e.g., a marine-insurance calc) can resolve them via the resolver in #2481/#2482.
- `.claude/rules/coding-style.md` — single-site edits; verify each new file added to `index.md` does not delete adjacent rows.
- Memory `feedback_plan_past_tense_artifact_claims.md` — this plan uses **future tense throughout** for all proposed pages.
- Memory `project_wiki_standards_path_decision.md` — `wiki/standards/<code-id>.md` is the sanctioned routing for codified standards. Note: that memory states **#2471 is CSA-Z276-only** — the routing principle generalizes, the codification plan does not. This plan extends the principle to IMO conventions (a forward extension; flagged as Open Question for sanction).
- #2540 — OPEN, "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — wave epic; this plan is W2-C under that wave (maritime-law domain).
- #2589 — OPEN, "feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)" — sibling W1 plan, same shape.
- #2471 — CLOSED, "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — sanctioned `wiki/standards/<code-id>.md` routing principle.
- GH issue search `maritime-law in:title --state open` returns only `#51 — WRK-1126: Add maritime law domain: skill, data, public cases, liabilities` (the original migration ticket; CLOSED-class work). **No parallel maritime-law content issue is open** — confirms no overlap risk.
- `find /mnt/ace -maxdepth 3 -type d -iname "*maritime*" -o -iname "*law*"` returns:
  - `/mnt/ace/acma-codes/IMO/` (full IMO PDF corpus — SOLAS, MARPOL, ISM, ISPS, Polar Code, BWM, COLREGs subdirs visible)
  - `/mnt/ace/acma-codes/Bahamas Maritime Auth/`
  - `/mnt/ace/acma-codes/ABS Rules/ILO Maritime Labour Convention/` (MLC 2006 ABS guidance notes — single PDF)
  - Plan does NOT extract from these PDFs (per #2482 deny-list); standards pages will cite them by reference and link to the IMO/ILO canonical URLs.
- WebSearch — IMO conventions list active 2026: SOLAS-1974, MARPOL-73-78, STCW, COLREGs-1972, ISM-Code, ISPS-Code, MLC-2006 confirmed active; recent amendments entered force 1 January 2026 (https://www.imo.org/en/about/conventions/pages/listofconventions.aspx, https://wwwcdn.imo.org/localresources/en/About/Conventions/StatusOfConventions/List%20of%20the%20Conventions%20and%20their%20amendments%20May%202024.pdf, https://safety4sea.com/imo-key-regulatory-updates-coming-into-force-in-january-2026/).
- WebSearch — Aleka Mandaraka-Sheppard *Modern Maritime Law* 3e Vol 2 chapter list: ISM/ISPS Codes, Ship Ownership, Mortgage, Shipbuilding Contracts, Sale & Purchase, Collisions, Salvage, Towage, General Average, Harbour Authorities, Limitation of Liability, Passenger Compensation, Marine Pollution & Nuclear Damage (https://www.routledge.com/Modern-Maritime-Law-Volume-2-Managing-Risks-and-Liabilities/Mandaraka-Sheppard/p/book/9781032931357). This is the canonical UK/EU academic curriculum — anchors concept-page topic selection.
- WebSearch — Schoenbaum *Admiralty and Maritime Law* 6e (Hornbook) chapter list: Admiralty Jurisdiction, Federalism, General Maritime Law, Seamen, Longshore Workers, Wrongful Death, Maritime Liens & Ship Mortgages, Carriage of Goods, Charter Parties, Towage, Pilotage, Collision, Limitation of Liability, Salvage, General Average, Marine Pollution, Sovereign Immunity (https://faculty.westacademic.com/Book/Detail?id=47985). This is the canonical US admiralty curriculum — anchors charterparty / bill-of-lading / general-average / salvage selection.

### Gaps identified

Coverage matrix vs. canonical Mandaraka-Sheppard + Schoenbaum + IMO-active-conventions curriculum:

| Canonical topic | Existing wiki status | Page tier (per #2471) | Action |
|---|---|---|---|
| **IMO regulatory framework** (IMO + MSC + MEPC + LEG committees) | gap (no entity page) | concept | **NEW** `concepts/imo-regulatory-framework.md` |
| **Port-state control / Paris MoU** | gap | concept | **NEW** `concepts/port-state-control.md` |
| **Flag-state jurisdiction** | gap (referenced in `mv-prestige-2002.md` body) | concept | **NEW** `concepts/flag-state-jurisdiction.md` |
| **General average** (York-Antwerp Rules) | gap (referenced in `mv-ever-given-2021.md` body) | concept | **NEW** `concepts/general-average.md` |
| **Salvage** (LOF, SCOPIC, 1989 Salvage Convention) | gap | concept | **NEW** `concepts/salvage.md` |
| **Limitation of liability doctrine** (above LLMC) | partial — only LLMC convention page | concept | **NEW** `concepts/limitation-of-liability.md` |
| **Charterparties** (voyage / time / bareboat / NYPE / GENCON) | gap | concept | **NEW** `concepts/charterparties.md` |
| **Bills of lading / Hague-Visby / Hamburg / Rotterdam Rules** | partial — referenced in `eurasian-dream-2002.md` body | concept | **NEW** `concepts/bills-of-lading.md` |
| **Marine insurance** (P&I clubs, IG, hull, MIA 1906) | gap | concept | **NEW** `concepts/marine-insurance.md` |
| **Collisions (COLREGs application + civil liability)** | gap | concept | **NEW** `concepts/collisions-and-colregs.md` |
| **MARPOL 73/78** | partial — body reference only in `mv-wakashio-2020.md` | standards | **NEW** `standards/marpol-73-78.md` |
| **SOLAS 1974** | gap | standards | **NEW** `standards/solas-1974.md` |
| **MLC 2006** | partial — body reference only in `mv-wakashio-2020.md` | standards | **NEW** `standards/mlc-2006.md` |
| **ISM Code** | partial — referenced in pre-existing case bodies | standards | **NEW** `standards/ism-code.md` |
| **ISPS Code** | gap | standards | not in this batch — defer to W3 |
| **COLREGs 1972** | gap | standards | not in this batch — defer (concept page covers application surface) |
| **CLC / Bunker / HNS / Athens / LLMC / OPA-90** | covered (existing pages) | concept→standards (relocation) | **OUT OF SCOPE** — relocation flagged Open Question |
| **Nairobi Wreck Removal 2007 / BWM 2004** | gap | standards | not in this batch — defer to W3 |
| **Arbitration (LMAA, ICC, SMA)** | gap | concept | not in this batch — defer to W3 |
| **Classification societies' role in regulatory regime** | gap | entity | reserved for naval-architecture batch (#2589) |

**Top-10 selected** for this expansion (foundational + cross-linkable, citable canonical reference, 6 concept pages + 4 standards pages):

Concepts (legal doctrine, 6 pages):
1. `concepts/general-average.md`
2. `concepts/salvage.md`
3. `concepts/limitation-of-liability.md`
4. `concepts/port-state-control.md`
5. `concepts/flag-state-jurisdiction.md`
6. `concepts/marine-insurance.md`

Concepts (regulatory + commercial-shipping doctrine, 2 more pages — selecting bills-of-lading and charterparties as the most cross-linkable to existing case-law entities `eurasian-dream-2002.md` and `mv-ever-given-2021.md`; deferring `imo-regulatory-framework.md`, `collisions-and-colregs.md`, `charterparties.md` selection rationale below):

Wait — to stay strictly at 10 with the 4 standards pages in, I need exactly 6 concept pages. Adjusting selection:

Final top-10:

**Concepts (6):**
1. `concepts/general-average.md`
2. `concepts/salvage.md`
3. `concepts/limitation-of-liability.md`
4. `concepts/port-state-control.md`
5. `concepts/flag-state-jurisdiction.md`
6. `concepts/charterparties.md` (selected over marine-insurance and bills-of-lading because charterparty doctrine subsumes both via incorporation clauses; bills-of-lading + marine-insurance deferred to W3)

**Standards (4):**
7. `standards/marpol-73-78.md`
8. `standards/solas-1974.md`
9. `standards/mlc-2006.md`
10. `standards/ism-code.md`

Selection rationale: each concept page is foundational (named in BOTH Mandaraka-Sheppard and Schoenbaum chapter lists) and has ≥1 existing case entity to cross-link from (general-average → ever-given; salvage → ever-given; limitation → prestige + llmc-1996; port-state-control → wakashio + erika; flag-state-jurisdiction → prestige; charterparties → eurasian-dream + msc-flaminia). Each standards page has either an active IMO/ILO website citation OR a /mnt/ace acma-codes corpus reference for the publisher/revision metadata.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):

- `#2540` — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — parent wave epic.
- `#2589` — OPEN — "feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)" — sibling W1 precedent.
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — sanctions `wiki/standards/<code-id>.md` routing principle.

**Parallel-work check** (`gh issue list --search "maritime-law in:title" --state open`):

- Only `#51 — WRK-1126` open; ancient migration ticket; no content-overlap risk.

**File existence** (`find … | sort` 2026-05-02):

- EXISTS: `knowledge/wikis/maritime-law/wiki/index.md`, `log.md`, `overview.md`
- EXISTS: `knowledge/wikis/maritime-law/wiki/concepts/{athens-convention-2002,bunker-convention-2001,clc-1992,environmental-liability,hns-convention-2010,llmc-1996,opa-90}.md` (7 concept pages)
- EXISTS: `knowledge/wikis/maritime-law/wiki/entities/{amoco-cadiz-1978,deepwater-horizon-2010,eurasian-dream-2002,msc-flaminia-2012,mv-erika-1999,mv-ever-given-2021,mv-prestige-2002,mv-wakashio-2020,sea-empress-1996,torrey-canyon-1967}.md` (10 entity case-law pages)
- EXISTS: `knowledge/wikis/maritime-law/wiki/sources/{maritime-law-cases,maritime-liability-conventions}.md`
- EXISTS: `knowledge/wikis/maritime-law/CLAUDE.md` (schema declared)
- MISSING (this plan creates): `wiki/concepts/{general-average,salvage,limitation-of-liability,port-state-control,flag-state-jurisdiction,charterparties}.md`
- MISSING (this plan creates): `wiki/standards/{marpol-73-78,solas-1974,mlc-2006,ism-code}.md`
- MISSING (this plan creates): `wiki/standards/` directory itself (does not exist today)
- MISSING (this plan creates): `tests/knowledge/test_maritime_law_expansion.py`

**Line excerpts** (from `concepts/llmc-1996.md` lines 1–10 — frontmatter pattern this plan must reproduce; note this is the legacy 5-field `source:` shape; new concept pages will use the 6-field `sources:` shape per `CLAUDE.md`):

```
---
title: "LLMC 1976/1996 Protocol — General Limitation of Maritime Claims"
tags: [maritime-law, convention, liability, compensation]
source: maritime-liabilities.yaml
added: 2026-04-07
last_updated: 2026-04-07
---
```

**Standards-frontmatter target shape** (per `.claude/rules/calc-citation-contract.md` + #2471 routing — this is the contract the 4 new standards pages will carry):

```
---
title: "MARPOL 73/78 — International Convention for the Prevention of Pollution from Ships"
code_id: MARPOL-73-78
publisher: IMO
revision: "Consolidated Edition 2022 (incl. 2020 sulphur cap MARPOL Annex VI)"
tags: [maritime-law, standards, imo, marpol, pollution]
added: 2026-05-02
last_updated: 2026-05-02
sources:
  - maritime-liability-conventions
see_also:
  - ../concepts/environmental-liability.md
  - ../concepts/port-state-control.md
---
```

**Gap proofs**:

- `ls knowledge/wikis/maritime-law/wiki/standards/ 2>&1` → "No such file or directory" — confirms the directory does not yet exist; this plan creates it.
- `grep -l 'general average' knowledge/wikis/maritime-law/wiki/concepts/*.md` → no match — confirms no concept page on general average.
- `grep -l 'port state control\|port-state control' knowledge/wikis/maritime-law/wiki/concepts/*.md` → no match — confirms gap.
- `grep -l 'flag state\|flag-state' knowledge/wikis/maritime-law/wiki/concepts/*.md` → no match — confirms gap.

<!-- Source count: 11 distinct sources cited above —
  (1) wiki index/CLAUDE.md schema/existing pages,
  (2) #2540, (3) #2589, (4) #2471,
  (5) GH parallel-work search,
  (6) /mnt/ace acma-codes/IMO inventory,
  (7) /mnt/ace ABS-Rules/ILO MLC corpus,
  (8) WebSearch IMO active conventions list,
  (9) WebSearch Mandaraka-Sheppard chapter list,
  (10) WebSearch Schoenbaum chapter list,
  (11) `.claude/rules/calc-citation-contract.md` + project memory `project_wiki_standards_path_decision.md`.
  Minimum 3 met (4× over). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2592-llm-wiki-W2C-maritime-law-expansion.md` |
| Tests | `tests/knowledge/test_maritime_law_expansion.py` |
| Implementation (10 wiki pages) | `knowledge/wikis/maritime-law/wiki/concepts/*.md` (6) + `knowledge/wikis/maritime-law/wiki/standards/*.md` (4) |
| Index update | `knowledge/wikis/maritime-law/wiki/index.md` |
| Log update | `knowledge/wikis/maritime-law/wiki/log.md` |
| New directory | `knowledge/wikis/maritime-law/wiki/standards/` (created by this plan; first standards page in this wiki) |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-W2C-maritime-law-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-02-plan-W2C-maritime-law-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-W2C-maritime-law-gemini.md` |

---

## Deliverable

Ten new pages will exist under `knowledge/wikis/maritime-law/wiki/` — 6 concept pages (legal doctrine: general average, salvage, limitation of liability, port-state control, flag-state jurisdiction, charterparties) and 4 standards pages under a newly-created `wiki/standards/` directory (MARPOL-73-78, SOLAS-1974, MLC-2006, ISM-Code) — each carrying `CLAUDE.md`-compliant frontmatter, with the 4 standards pages additionally carrying `code_id`/`publisher`/`revision` per #2471 routing, ≥1 case-law citation OR convention reference per concept page, and ≥2 `see_also` cross-links per page. `index.md` will list every new page; `log.md` will carry the audit entry.

---

## Pseudocode

```
# Per-CONCEPT-page authoring contract (applies to 6 concept pages):
function author_concept_page(slug, scope_summary):
    write frontmatter:
        title: human-readable
        tags: [maritime-law, concept-tag, sub-topic-tag]
        added: 2026-05-02
        last_updated: 2026-05-02
        sources: [maritime-law-cases, maritime-liability-conventions]
        see_also: [≥2 sibling-page paths — at least 1 entity case + 1 standard or convention]
    section "Scope" — 1 paragraph stating what the page IS and what it is NOT (boundary against existing pages)
    section "Doctrine" — 5–10 bulleted definitions naming the legal concept, jurisdictional split (US vs UK vs EU vs civil-law), and the convention that codifies it
    section "Cases" — ≥1 cross-link to an existing entity page (case law) IF such a case exists; if none, MUST cite a named landmark case with citation (court, year)
    section "Cross-References" — markdown links to ≥2 see_also targets
    forbid: extracted text from textbooks/case reports (#2482 deny-list)
    forbid: copying convention article text verbatim (cite by reference only)
    enforce: word count ≤ 400 per page (concept summary, not chapter copy)

# Per-STANDARDS-page authoring contract (applies to 4 standards pages):
function author_standards_page(slug, code_id, publisher, revision):
    write frontmatter:
        title: human-readable
        code_id: <CANONICAL-ID>      # e.g., MARPOL-73-78, SOLAS-1974, MLC-2006, ISM-Code
        publisher: IMO | ILO
        revision: <consolidated edition / amendment year>
        tags: [maritime-law, standards, <publisher-tag>, <topic-tag>]
        added: 2026-05-02
        last_updated: 2026-05-02
        sources: [maritime-liability-conventions]
        see_also: [≥2 sibling-page paths — concepts/ pages preferred]
    section "Scope" — 1 paragraph: what the convention regulates, geographic/sector scope, entry-into-force date
    section "Structure" — bulleted list of annexes/chapters BY NAME ONLY (no clause text)
    section "Key Mechanisms" — 3–5 bullets naming the mechanisms (e.g., MARPOL Annex VI sulphur cap; ISM Designated Person Ashore; MLC seafarers' employment agreement) WITHOUT restating thresholds, formulas, or article text
    section "Cross-References" — to concept pages and case-law entities
    section "Citation Source" — IMO/ILO canonical URL + /mnt/ace corpus path (reference only, no extraction)
    forbid: any verbatim convention article text (#2482)
    forbid: enumerating specific numerical thresholds (e.g., "0.5% sulphur" is fine as a named cap; reproducing the regulation's prose is not)
    enforce: word count ≤ 400 per page

function update_index(index_path, new_pages):
    add a new "Standards" section to the index AFTER the "Conventions (Concepts)" section
    insert each new concept page into "Concepts (Cross-cutting)" table (alphabetical by title)
    insert each new standards page into a NEW "Standards" table
    bump page_count from 20 → 30 in frontmatter
    update last_updated to 2026-05-02

function append_log(log_path):
    append "[2026-05-02] expand | maritime-law W2-C — 10 core pages (6 concepts + 4 standards)"
        - Pages added: <list>
        - Notes: covers Mandaraka-Sheppard + Schoenbaum + IMO-active-conventions core curriculum gaps; first standards-page tier in this wiki.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/maritime-law/wiki/concepts/general-average.md` | York-Antwerp Rules + general-average doctrine; cross-link `mv-ever-given-2021.md` |
| Create | `knowledge/wikis/maritime-law/wiki/concepts/salvage.md` | LOF, SCOPIC, 1989 Salvage Convention; cross-link `mv-ever-given-2021.md` |
| Create | `knowledge/wikis/maritime-law/wiki/concepts/limitation-of-liability.md` | Doctrine layer above the LLMC convention page; cross-link `mv-prestige-2002.md` and existing `concepts/llmc-1996.md` |
| Create | `knowledge/wikis/maritime-law/wiki/concepts/port-state-control.md` | Paris MoU, Tokyo MoU, USCG inspection regime; cross-link `mv-wakashio-2020.md`, `mv-erika-1999.md` |
| Create | `knowledge/wikis/maritime-law/wiki/concepts/flag-state-jurisdiction.md` | UNCLOS Art 91/94 nationality + jurisdiction; cross-link `mv-prestige-2002.md` |
| Create | `knowledge/wikis/maritime-law/wiki/concepts/charterparties.md` | Voyage / time / bareboat; NYPE, GENCON, Shellvoy; cross-link `eurasian-dream-2002.md`, `msc-flaminia-2012.md` |
| Create | `knowledge/wikis/maritime-law/wiki/standards/marpol-73-78.md` | Six annexes incl. 2020 sulphur cap; first standards page in this wiki |
| Create | `knowledge/wikis/maritime-law/wiki/standards/solas-1974.md` | SOLAS chapter overview; ISM is Ch IX |
| Create | `knowledge/wikis/maritime-law/wiki/standards/mlc-2006.md` | ILO seafarers' bill of rights |
| Create | `knowledge/wikis/maritime-law/wiki/standards/ism-code.md` | Safety Management System; Designated Person Ashore |
| Modify | `knowledge/wikis/maritime-law/wiki/index.md` | Add 6 concept rows + new "Standards" table with 4 rows; bump `page_count` 20 → 30; update `last_updated` |
| Modify | `knowledge/wikis/maritime-law/wiki/log.md` | Append expansion log entry |
| Create | `tests/knowledge/test_maritime_law_expansion.py` | TDD: frontmatter, see-also resolves, IMO-conv pages have `code_id`/`publisher`/`revision`, concept pages have ≥1 case-law citation OR convention reference, no PDF extraction, word count ≤400 |
| Update | `docs/plans/README.md` | Add this plan to plan index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_all_ten_pages_exist` | Each of the 10 new files is on disk | path list | all 10 `Path.exists()` is True |
| `test_standards_directory_created` | `wiki/standards/` directory exists | `Path.is_dir()` | True |
| `test_concept_frontmatter_required_fields` | Every new concept page has `title`, `tags`, `added`, `last_updated` per `CLAUDE.md` schema | parse YAML frontmatter | all 4 keys present, non-empty |
| `test_standards_frontmatter_code_id` | Every new standards page has `code_id`, `publisher`, `revision` per #2471 + calc-citation contract | parse YAML | all 3 keys present, non-empty |
| `test_standards_code_id_canonical` | `code_id` matches `^[A-Z][A-Z0-9-]+$` and is one of the canonical IMO/ILO short codes | regex per page | match per page |
| `test_frontmatter_see_also_min_two` | Each page lists ≥2 entries in `see_also` | parse YAML | `len(see_also) >= 2` |
| `test_see_also_paths_resolve` | Every `see_also` entry points to a real file on disk | parse YAML, `Path.exists()` per entry | 100% resolve |
| `test_concept_has_case_or_convention_ref` | Each concept page body contains ≥1 link to either an entity case page (`../entities/*.md`) OR a convention page (`./*-convention-*.md`, `./clc-1992.md`, `./opa-90.md`, `./llmc-1996.md`) OR an inline case citation matching `r'\b\(\d{4}\)\b'` (court-year pattern) | regex search of body | ≥1 match per concept page |
| `test_word_count_under_400` | Concept summary discipline (no chapter copy per #2482) | count words | each page < 400 words |
| `test_no_verbatim_convention_text` | No new standards page contains a paragraph >80 words AND >5 commas (heuristic for copy-pasted regulatory prose) | heuristic scan | no flagged paragraph |
| `test_index_links_resolve` | Every relative link in `index.md` Concepts + Standards tables resolves | walk markdown links | 100% resolve |
| `test_index_page_count_bumped` | `index.md` frontmatter `page_count` updated to ≥30 | parse YAML | `page_count >= 30` |
| `test_index_has_standards_section` | `index.md` body contains a `## Standards` heading after the existing Conventions section | grep | match present |
| `test_log_entry_appended` | `log.md` contains a 2026-05-02 expand entry | grep | match present |
| `test_no_pdf_extraction_markers` | New pages contain no copy-paste markers (e.g., very long single paragraphs > 80 words, or "Page N of M" stamps) | heuristic | no flagged paragraphs |

---

## Acceptance Criteria

- [ ] All 10 new wiki pages will exist with valid frontmatter (`title`, `tags`, `added=2026-05-02`, `last_updated=2026-05-02`).
- [ ] The 4 new standards pages will additionally carry `code_id`, `publisher`, `revision` frontmatter per #2471 routing and `.claude/rules/calc-citation-contract.md`.
- [ ] `wiki/standards/` directory will be created (does not exist today).
- [ ] Each new concept page will cite ≥1 case (cross-link to existing `entities/*.md` OR inline `(YYYY)` citation) OR a named convention.
- [ ] Each new standards page will cite the IMO/ILO canonical URL AND a /mnt/ace corpus path reference (no extraction).
- [ ] Each new page will list ≥2 `see_also` cross-links that resolve to real files.
- [ ] No new page will restate convention article text verbatim (#2482 deny-list).
- [ ] Each new page will be ≤400 words (concept-summary discipline).
- [ ] `index.md` will contain a new `## Standards` section listing all 4 standards pages and the existing Concepts table will list 6 new rows.
- [ ] `index.md` frontmatter `page_count` will read ≥30; `last_updated` will read `2026-05-02`.
- [ ] `log.md` will carry a `[2026-05-02] expand | maritime-law W2-C` entry.
- [ ] `tests/knowledge/test_maritime_law_expansion.py` will pass: `uv run pytest tests/knowledge/test_maritime_law_expansion.py -v`.
- [ ] No regression in existing knowledge tests: `uv run pytest tests/knowledge/ -v`.
- [ ] Review artifacts will be posted under `scripts/review/results/2026-05-02-plan-W2C-maritime-law-{claude,codex,gemini}.md`.

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | TBD |
| Codex | TBD | TBD |
| Gemini | TBD | TBD |

**Overall result:** TBD

---

## Risks and Open Questions

- **Risk: jurisdictional bias.** Maritime-law doctrine is not uniform across US admiralty (Schoenbaum), UK admiralty (Mandaraka-Sheppard, Aleka), and continental-Europe codified systems (e.g., French Code des transports, German HGB). The 6 concept pages WILL flag the jurisdictional split explicitly in the "Doctrine" section and avoid privileging US or UK doctrine as default. Plan adopts UK/Commonwealth-leaning vocabulary as primary (Mandaraka-Sheppard) with US parenthetical on first occurrence — same convention as #2589.
- **Risk: convention-lifecycle drift.** IMO conventions are amended frequently — MARPOL Annex VI (sulphur cap), SOLAS (cyber-resilience amendments coming Jan 2026), MLC (recent amendments via STC). Standards pages will cite the consolidated-edition revision year in `revision:` frontmatter and link to the IMO `listofconventions.aspx` page rather than embedding numerical thresholds — so a page does not silently go stale when the next amendment lands. Tests will not lock numerical values; they will lock structural shape.
- **Risk: IP boundary on case-law summaries.** Quoting judgment text triggers copyright concerns even for old cases. Concept pages will refer to cases by court+year+name only, with cross-link to the existing entity page (which already summarizes the case in our voice) — no judgment-text reproduction. The `test_no_verbatim_convention_text` heuristic catches the analogous risk for convention text.
- **Risk: standards routing not yet sanctioned for IMO conventions.** Memory `project_wiki_standards_path_decision.md` notes #2471 is **CSA-Z276-only**; the routing principle generalizes but the codification plan does not. This plan EXTENDS the principle to IMO conventions as a forward-adoption call. If Open Question #1 below resolves "no", the 4 standards pages will be re-homed to `concepts/`.
- **Risk: relocation churn.** The 6 existing convention pages (CLC, Bunker, HNS, Athens, LLMC, OPA-90) sit in `concepts/` despite carrying `code_id`-able identity. They are NOT relocated by this plan; this preserves URL stability for the case-law entity pages that link to them. A follow-up issue should cover the relocation as a separate atomic change (Open Question #2).
- **Risk: page-count regenerator drift.** `index.md` frontmatter says `page_count: 20` but on-disk count is 22 (index.md + overview.md not catalogued). After this plan: on-disk = 32, catalogued count = 30 (10 new pages added). Same shape as #2589 finding m2.

- **Open #1: standards routing sanction.** Should `wiki/standards/<code-id>.md` be sanctioned for IMO/ILO conventions in the maritime-law wiki, or should this plan be re-homed to `concepts/standards-<code-id>.md`? Current plan assumes YES based on #2471 routing principle generalization; flagged for explicit user sanction.
- **Open #2: existing convention page relocation.** Should the 6 pre-existing convention pages (CLC, Bunker, HNS, Athens, LLMC, OPA-90) be relocated from `concepts/` to `standards/` in a follow-up issue, given they carry standards-page identity? Not in scope of this plan.
- **Open #3: foreign-language conventions.** Should multilingual convention text (e.g., Rotterdam Rules French/Spanish authoritative versions) be cross-linked from the standards page or limited to the English IMO consolidation? Current plan: **English IMO consolidation only**, with a "Authoritative texts" line naming the official languages without linking. Flagged for user feedback.
- **Open #4: 11th candidate.** `concepts/imo-regulatory-framework.md` was deferred to keep batch size at 10. Should it ship in this batch (making it 11) or in W3?

---

## Complexity: T2

**T2** — 10 new wiki pages (6 concepts + 4 standards) + new directory creation + 2 modified registry files + 1 new test module. Multi-file, TDD required, but no new code logic / no calc-citation emission / no calc-module touch. Risk is concentrated in (a) jurisdictional vocabulary discipline, (b) standards-page frontmatter contract per #2471, (c) word-count + verbatim-text heuristics — all addressable with regex tests. Not T3 because there is no new module / no calc / no migration / no schema change beyond the additive `code_id` frontmatter on 4 pages.
