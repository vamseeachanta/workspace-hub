# Plan for W2-C: feat(llm-wiki) — maritime-law wiki topical expansion (IMO conventions + 10 core concepts)

> **Status:** plan-review (revised after r1 review)
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2592
> **Review artifacts:** scripts/review/results/2026-05-02-plan-2592-claude-internal.md (Codex/Gemini UNAVAILABLE — see Adversarial Review Summary)
>
> _This plan was amended on 2026-05-02 (W3-C erratum, #2596). Three residual lines (L66/L81/L128) used #2471 as a generalized routing-principle citation; #2471 is CSA-Z276-specific per memory `project_wiki_standards_path_decision.md`. Maritime-law concept-page placement under `wiki/concepts/` is unchanged._

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

- The 6 existing convention pages currently sit under `concepts/` despite carrying `code_id`-able identity (CLC-1992, LLMC-1996, OPA-90, etc.). Per the constraint stated by the task, IMO/national-statute conventions ARE standards-tier identity. **However, project memory `project_wiki_standards_path_decision.md` explicitly excludes maritime-law from the `wiki/standards/` routing principle** ("The principle applies to: marine-engineering, engineering, naval-architecture. **Maritime-law, personal, health-reports are out of scope.**"). This plan therefore **defaults to routing the 4 new IMO/ILO pages under `wiki/concepts/` with additive `code_id`/`publisher`/`consolidated_edition` frontmatter** (a schema-additive change, not a path extension). The original `wiki/standards/<code-id>.md` routing is preserved as Open Question #1 option (a) for explicit user override during plan-review. This plan does NOT relocate the 6 existing convention pages (out of scope; flagged as Open Question for a follow-up).
- The frontmatter in 5 of the 6 existing convention pages uses singular `source:` (deprecated) where `CLAUDE.md` recommends plural `sources:`. Outside this plan's scope.
- The 6 existing convention pages are **descriptive shells** (Summary table + 1–3 sentence Details), not concept-abstraction pages. There are NO concept-abstraction pages for general average, salvage, limitation of liability (only the LLMC convention page), port-state control, flag-state jurisdiction, charterparties, bills of lading, or marine insurance.

### Standards

Maritime-law standards-tier page production is **bootstrapping from zero**. Per `.claude/rules/calc-citation-contract.md`, calc-module citations need wiki pages with `code_id`/`publisher`/`revision` frontmatter; maritime-law wiki has no such pages today. **Default routing per Open Question #1**: the plan introduces 4 new IMO/ILO pages under `wiki/concepts/` (since memory excludes maritime-law from the `wiki/standards/` routing principle), each carrying additive `code_id`/`publisher`/`consolidated_edition` frontmatter. **Note on `consolidated_edition` vs `revision`**: IMO conventions are amended via amendments adopted at MSC/MEPC sessions, not by publisher revisions; the field is therefore named `consolidated_edition` (or `revision: <consolidated-edition-year>` if the user picks the standards/ option). This is a maritime-law-specific frontmatter convention NOT covered by #2471's calc-citation contract — calc-module resolvability is deferred until amendment-set matching semantics are decided (separate issue).

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
- `docs/plans/2026-05-02-issue-2589-llm-wiki-W1D-naval-architecture-expansion.md` — W1-D precedent; this plan mirrors its shape (10 new pages, frontmatter contract, see-also test, word-count cap, single index/log update). Differences: maritime-law remains all-`concepts/` per memory exclusion (default), with 4 IMO/ILO pages carrying additive standards-tier frontmatter (`code_id`/`publisher`/`consolidated_edition`); naval-arch was concepts-only.
- `.claude/rules/calc-citation-contract.md` — concept pages do not emit `Citation` instances (citations are calc-module artifacts); the 4 new IMO/ILO pages WILL carry forward-adoptable `code_id`/`publisher`/`consolidated_edition` frontmatter, but are **explicitly NOT calc-resolvable in v1** (amendment-set matching semantics deferred to a separate issue — see Risks).
- `.claude/rules/coding-style.md` — single-site edits; verify each new file added to `index.md` does not delete adjacent rows.
- Memory `feedback_plan_past_tense_artifact_claims.md` — this plan uses **future tense throughout** for all proposed pages.
- Memory `project_wiki_standards_path_decision.md` — `wiki/standards/<code-id>.md` is the sanctioned routing for codified standards in marine-engineering, engineering, naval-architecture. **Memory verbatim: "The principle applies to: marine-engineering, engineering, naval-architecture. Maritime-law, personal, health-reports are out of scope."** This plan therefore defaults to `concepts/` with additive frontmatter; `standards/` routing is only available as Open Question #1 option (a) pending explicit user override and a separate maritime-law sanction issue.
- #2540 — OPEN, "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — wave epic; this plan is W2-C under that wave (maritime-law domain).
- #2589 — OPEN, "feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)" — sibling W1 plan, same shape.
- #2471 — CLOSED, "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — sanctioned `wiki/standards/<code-id>.md` routing **for CSA-Z276 specifically** per memory `project_wiki_standards_path_decision.md`; **does NOT generalize** to maritime-law publishers (IMO/ILO). Cited here only as historical origin of the `code_id`/`publisher`/`revision` frontmatter triple via the calc-citation-contract. (Amended 2026-05-02 per W3-C erratum.)
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

| Canonical topic | Existing wiki status | Page tier (per local wiki schema; #2471 NOT applicable — CSA-Z276-specific) | Action |
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
| **MARPOL 73/78** | partial — body reference only in `mv-wakashio-2020.md` | standards-tier (default-routed to `concepts/`) | **NEW** `concepts/marpol-73-78.md` (default) — `standards/marpol-73-78.md` if Open Q#1 option (a) |
| **SOLAS 1974** | gap | standards-tier (default-routed to `concepts/`) | **NEW** `concepts/solas-1974.md` (default) — `standards/solas-1974.md` if Open Q#1 option (a) |
| **MLC 2006** | partial — body reference only in `mv-wakashio-2020.md` | standards-tier (default-routed to `concepts/`) | **NEW** `concepts/mlc-2006.md` (default) — `standards/mlc-2006.md` if Open Q#1 option (a) |
| **ISM Code** | partial — referenced in pre-existing case bodies | standards-tier embedded-in-SOLAS (default-routed to `concepts/`) | **NEW** `concepts/ism-code.md` (default) — see ISM-as-embedded-in-SOLAS note in Risks |
| **ISPS Code** | gap | standards | not in this batch — defer to W3 |
| **COLREGs 1972** | gap | standards | not in this batch — defer (concept page covers application surface) |
| **CLC / Bunker / HNS / Athens / LLMC / OPA-90** | covered (existing pages) | concept→standards (relocation) | **OUT OF SCOPE** — relocation flagged Open Question |
| **Nairobi Wreck Removal 2007 / BWM 2004** | gap | standards | not in this batch — defer to W3 |
| **Arbitration (LMAA, ICC, SMA)** | gap | concept | not in this batch — defer to W3 |
| **Classification societies' role in regulatory regime** | gap | entity | reserved for naval-architecture batch (#2589) |

**Top-10 selected** for this expansion (foundational + cross-linkable, citable canonical reference, 6 doctrine-concept pages + 4 IMO/ILO standards-tier pages):

**Doctrine-concept pages (6):**
1. `concepts/general-average.md`
2. `concepts/salvage.md`
3. `concepts/limitation-of-liability.md`
4. `concepts/port-state-control.md`
5. `concepts/flag-state-jurisdiction.md`
6. `concepts/charterparties.md` (selected over marine-insurance and bills-of-lading because charterparty doctrine subsumes both via incorporation clauses; bills-of-lading + marine-insurance deferred to W3)

**IMO/ILO standards-tier pages (4)** — default-routed to `concepts/` per Open Question #1 default; rename to `standards/` only if user picks option (a):
7. `concepts/marpol-73-78.md`
8. `concepts/solas-1974.md`
9. `concepts/mlc-2006.md`
10. `concepts/ism-code.md`

Selection rationale: each doctrine-concept page is foundational (named in BOTH Mandaraka-Sheppard and Schoenbaum chapter lists) and has ≥1 existing case entity to cross-link from (general-average → ever-given; salvage → ever-given; limitation → prestige + llmc-1996; port-state-control → wakashio + erika; flag-state-jurisdiction → prestige; charterparties → eurasian-dream + msc-flaminia). Each standards-tier page has either an active IMO/ILO website citation OR a /mnt/ace acma-codes corpus reference for the publisher/edition metadata.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):

- `#2540` — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536" — parent wave epic.
- `#2589` — OPEN — "feat(llm-wiki): naval-architecture wiki topical expansion — 10 core concept pages (W1-D)" — sibling W1 precedent.
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — sanctions the path-routing decision **for CSA-Z276 specifically**; the principle does NOT generalize across publishers. (Amended 2026-05-02 per W3-C erratum.)

**Parallel-work check** (`gh issue list --search "maritime-law in:title" --state open`):

- Only `#51 — WRK-1126` open; ancient migration ticket; no content-overlap risk.

**File existence** (`find … | sort` 2026-05-02):

- EXISTS: `knowledge/wikis/maritime-law/wiki/index.md`, `log.md`, `overview.md`
- EXISTS: `knowledge/wikis/maritime-law/wiki/concepts/{athens-convention-2002,bunker-convention-2001,clc-1992,environmental-liability,hns-convention-2010,llmc-1996,opa-90}.md` (7 concept pages)
- EXISTS: `knowledge/wikis/maritime-law/wiki/entities/{amoco-cadiz-1978,deepwater-horizon-2010,eurasian-dream-2002,msc-flaminia-2012,mv-erika-1999,mv-ever-given-2021,mv-prestige-2002,mv-wakashio-2020,sea-empress-1996,torrey-canyon-1967}.md` (10 entity case-law pages)
- EXISTS: `knowledge/wikis/maritime-law/wiki/sources/{maritime-law-cases,maritime-liability-conventions}.md`
- EXISTS: `knowledge/wikis/maritime-law/CLAUDE.md` (schema declared)
- MISSING (this plan creates): `wiki/concepts/{general-average,salvage,limitation-of-liability,port-state-control,flag-state-jurisdiction,charterparties}.md` (6 doctrine-concept pages)
- MISSING (this plan creates, default routing): `wiki/concepts/{marpol-73-78,solas-1974,mlc-2006,ism-code}.md` (4 IMO/ILO standards-tier pages with additive frontmatter)
- MISSING (this plan creates IF Open Q#1 option (a) chosen): `wiki/standards/{marpol-73-78,solas-1974,mlc-2006,ism-code}.md` AND `wiki/standards/` directory itself (does not exist today)
- MISSING (this plan creates): `tests/knowledge/test_maritime_law_expansion.py`
- MISSING (precondition IF Open Q#1 option (a) chosen): `knowledge/wikis/maritime-law/CLAUDE.md` schema update declaring `wiki/standards/` directory + `code_id`/`publisher`/`consolidated_edition` extra-fields contract; mirrors naval-architecture's CLAUDE.md schema

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

**Standards-tier frontmatter target shape** (default routing = `concepts/`; the 4 new IMO/ILO pages will carry additive `code_id`/`publisher`/`consolidated_edition` frontmatter):

```
---
title: "MARPOL 73/78 — International Convention for the Prevention of Pollution from Ships"
code_id: marpol-73-78
publisher: IMO
consolidated_edition: "2022 (consolidated through MEPC amendments adopted by 2026-05-02)"
tags: [maritime-law, standards-tier, imo, marpol, pollution]
added: 2026-05-02
last_updated: 2026-05-02
sources:
  - maritime-liability-conventions
see_also:
  - ./environmental-liability.md
  - ./port-state-control.md
---
```

**Note on `consolidated_edition` field semantics**: this is a maritime-law-specific frontmatter convention NOT covered by #2471's calc-citation contract. IMO conventions are amended via amendments adopted at MSC/MEPC sessions, not by publisher revisions, so the field describes the consolidated-edition cutoff rather than a single revision number. **Calc-resolvability is explicitly deferred** — these 4 pages carry forward-adoptable identity but a calc emitting `Citation(code_id="marpol-73-78", revision="...")` will NOT resolve until amendment-set matching semantics are decided in a separate issue. For ISM Code: it is embedded in SOLAS Ch IX, so its `consolidated_edition` rides on the SOLAS amendment chain — flagged in Risks. For MLC 2006: ILO publisher (not IMO), amended via Special Tripartite Committee — `publisher: ILO` and `consolidated_edition` describes STC amendment cutoff.

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
| Implementation (10 wiki pages) | `knowledge/wikis/maritime-law/wiki/concepts/*.md` (10 — default routing) OR 6 in `concepts/` + 4 in `standards/` (Open Q#1 option (a)) |
| Index update | `knowledge/wikis/maritime-law/wiki/index.md` |
| Log update | `knowledge/wikis/maritime-law/wiki/log.md` |
| Schema precondition (Open Q#1 option (a) ONLY) | `knowledge/wikis/maritime-law/CLAUDE.md` (declare `wiki/standards/` + extra-fields) AND new directory `knowledge/wikis/maritime-law/wiki/standards/` |
| Plan review — Claude (internal, single-author) | `scripts/review/results/2026-05-02-plan-2592-claude-internal.md` |
| Plan review — Codex | UNAVAILABLE — codex-cli 0.124.0 stdin-hang regression (#2479) |
| Plan review — Gemini | UNAVAILABLE — gemini sandbox path resolution failure |

---

## Deliverable

Ten new pages will exist under `knowledge/wikis/maritime-law/wiki/` — 6 doctrine-concept pages (general average, salvage, limitation of liability, port-state control, flag-state jurisdiction, charterparties) and 4 IMO/ILO standards-tier pages (MARPOL-73-78, SOLAS-1974, MLC-2006, ISM-Code). **Default routing per Open Question #1**: all 10 pages land under `wiki/concepts/`, with the 4 IMO/ILO pages carrying additive `code_id`/`publisher`/`consolidated_edition` frontmatter. (If Open Q#1 option (a) is chosen by user during plan-review, the 4 IMO/ILO pages relocate to a newly-created `wiki/standards/` directory and `knowledge/wikis/maritime-law/CLAUDE.md` is updated as a precondition.) Each page carries `CLAUDE.md`-compliant frontmatter, ≥1 case-law citation OR convention reference per doctrine-concept page, and ≥2 `see_also` cross-links per page. `index.md` will list every new page; `log.md` will carry the audit entry.

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

# Per-STANDARDS-TIER-page authoring contract (applies to 4 IMO/ILO pages — default routed under concepts/):
function author_standards_tier_page(slug, code_id, publisher, consolidated_edition):
    write frontmatter:
        title: human-readable
        code_id: <canonical-lowercase-id>      # e.g., marpol-73-78, solas-1974, mlc-2006, ism-code
        publisher: IMO | ILO
        consolidated_edition: <consolidated edition / amendment cutoff>
        tags: [maritime-law, standards-tier, <publisher-tag>, <topic-tag>]
        added: 2026-05-02
        last_updated: 2026-05-02
        sources: [maritime-liability-conventions]
        see_also: [≥2 sibling-page paths — doctrine concepts/ pages preferred]
    section "Scope" — 1 paragraph: what the convention regulates, geographic/sector scope, entry-into-force date
    section "Structure" — bulleted list of annexes/chapters BY NAME ONLY (no clause text)
    section "Key Mechanisms" — 3–5 bullets naming the mechanisms (e.g., MARPOL Annex VI sulphur cap; ISM Designated Person Ashore; MLC seafarers' employment agreement) WITHOUT restating thresholds, formulas, or article text
    section "Cross-References" — to doctrine-concept pages and case-law entities
    section "Citation Source" — IMO/ILO canonical URL + /mnt/ace corpus path (reference only, no extraction)
    forbid: any verbatim convention article text (#2482)
    forbid: enumerating specific numerical thresholds (e.g., "0.5% sulphur" is fine as a named cap; reproducing the regulation's prose is not)
    enforce: word count ≤ 400 per page

function update_index(index_path, new_pages):
    add a new "Standards-tier (IMO/ILO)" sub-section to the index after the existing "Conventions (Concepts)" section
    insert each new doctrine-concept page into "Concepts (Cross-cutting)" table (alphabetical by title)
    insert each new IMO/ILO standards-tier page into the new sub-section
    bump page_count from 20 → 30 in frontmatter
    update last_updated to 2026-05-02

function append_log(log_path):
    append "[2026-05-02] expand | maritime-law W2-C — 10 core pages (6 doctrine-concepts + 4 IMO/ILO standards-tier)"
        - Pages added: <list>
        - Notes: covers Mandaraka-Sheppard + Schoenbaum + IMO-active-conventions core curriculum gaps; first standards-tier identity in this wiki (default routed under concepts/ per memory exclusion).
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
| Create (default) | `knowledge/wikis/maritime-law/wiki/concepts/marpol-73-78.md` | Six annexes incl. 2020 sulphur cap; additive `code_id`/`publisher`/`consolidated_edition` frontmatter |
| Create (default) | `knowledge/wikis/maritime-law/wiki/concepts/solas-1974.md` | SOLAS chapter overview; ISM is Ch IX |
| Create (default) | `knowledge/wikis/maritime-law/wiki/concepts/mlc-2006.md` | ILO seafarers' bill of rights; `publisher: ILO` |
| Create (default) | `knowledge/wikis/maritime-law/wiki/concepts/ism-code.md` | Safety Management System; Designated Person Ashore; embedded-in-SOLAS Ch IX (see Risks) |
| Precondition (Open Q#1 option (a) ONLY) | `knowledge/wikis/maritime-law/CLAUDE.md` | Update schema to declare `wiki/standards/` directory + `code_id`/`publisher`/`consolidated_edition` extra-fields contract; mirrors naval-architecture's CLAUDE.md schema |
| Create (Open Q#1 option (a) ONLY) | `knowledge/wikis/maritime-law/wiki/standards/{marpol-73-78,solas-1974,mlc-2006,ism-code}.md` | Relocate the 4 IMO/ILO pages from `concepts/` to a newly-created `wiki/standards/` directory |
| Modify | `knowledge/wikis/maritime-law/wiki/index.md` | Add 6 doctrine-concept rows + 4 IMO/ILO standards-tier rows; bump `page_count` 20 → 32 (on-disk count post-plan); update `last_updated` |
| Modify | `knowledge/wikis/maritime-law/wiki/log.md` | Append expansion log entry |
| Create | `tests/knowledge/test_maritime_law_expansion.py` | TDD: frontmatter, see-also resolves, IMO/ILO pages have `code_id`/`publisher`/`consolidated_edition`, doctrine-concept pages have ≥1 case-law citation OR convention reference, no PDF extraction, word count ≤400 |
| Update | `docs/plans/README.md` | Add this plan to plan index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_all_ten_pages_exist` | Each of the 10 new files is on disk | path list | all 10 `Path.exists()` is True |
| `test_standards_directory_created` | `wiki/standards/` directory exists (Open Q#1 option (a) ONLY; skipped under default routing) | `Path.is_dir()` | True if option (a), test skipped under default |
| `test_concept_frontmatter_required_fields` | Every new doctrine-concept page has `title`, `tags`, `added`, `last_updated` per `CLAUDE.md` schema | parse YAML frontmatter | all 4 keys present, non-empty |
| `test_standards_tier_frontmatter_fields` | Every new IMO/ILO page has `code_id`, `publisher`, `consolidated_edition` (additive frontmatter; not calc-citation-contract-bound) | parse YAML | all 3 keys present, non-empty |
| `test_code_id_canonical_lowercase` | `code_id` matches `^[a-z][a-z0-9-]+$` (lowercase per `project_wiki_standards_path_decision.md`: "lowercase, hyphen-separated") and ∈ {marpol-73-78, solas-1974, mlc-2006, ism-code} | regex + set membership | match per page |
| `test_frontmatter_see_also_min_two` | Each page lists ≥2 entries in `see_also` | parse YAML | `len(see_also) >= 2` |
| `test_see_also_paths_resolve` | Every `see_also` entry points to a real file on disk | parse YAML, `Path.exists()` per entry | 100% resolve |
| `test_concept_has_case_or_convention_ref` | Each doctrine-concept page body contains ≥1 link to either an entity case page (`../entities/*.md`) OR a convention page (`./*-convention-*.md`, `./clc-1992.md`, `./opa-90.md`, `./llmc-1996.md`) OR an inline case citation matching `r'\b\(\d{4}\)\b'` (court-year pattern) | regex search of body | ≥1 match per page |
| `test_word_count_under_400` | Concept summary discipline (no chapter copy per #2482) | count words | each page < 400 words |
| `test_no_quoted_convention_prose_without_citation` | No new IMO/ILO page contains a quoted-prose block (text inside `>` blockquote OR text inside straight-double-quotes spanning >10 words) without a citation marker on the same or adjacent line (citation-form lint, replacing the rejected length+comma heuristic) | regex scan: blockquote / quoted span ≥10 words; require citation token within ±2 lines | no unmatched quoted prose |
| `test_index_links_resolve` | Every relative link in `index.md` Concepts + Standards-tier tables resolves | walk markdown links | 100% resolve |
| `test_index_page_count_matches_on_disk` | `index.md` frontmatter `page_count` equals on-disk markdown count under `wiki/` (32 post-plan: 22 existing + 10 new); replaces the `≥30` non-discriminating bound | parse YAML; `len(glob('wiki/**/*.md'))` | exact equality |
| `test_index_has_standards_tier_section` | `index.md` body contains a `## Standards-tier` (or `## Standards` if option (a)) heading after existing Conventions section | grep | match present |
| `test_log_entry_appended` | `log.md` contains a 2026-05-02 expand entry | grep | match present |
| `test_no_pdf_extraction_markers` | New pages contain no copy-paste markers (e.g., literal "Page N of M" stamps, OCR artifacts like multiple consecutive isolated digits, or character-encoding garbage) | heuristic | no flagged paragraphs |

---

## Acceptance Criteria

- [ ] All 10 new wiki pages will exist with valid frontmatter (`title`, `tags`, `added=2026-05-02`, `last_updated=2026-05-02`).
- [ ] The 4 new IMO/ILO standards-tier pages will additionally carry `code_id` (lowercase-hyphenated), `publisher`, `consolidated_edition` frontmatter (additive maritime-law-specific convention; not calc-citation-contract-bound in v1).
- [ ] Default routing: all 10 pages live under `wiki/concepts/`. (Open Q#1 option (a) ONLY: `wiki/standards/` directory created and CLAUDE.md schema updated.)
- [ ] Each new doctrine-concept page will cite ≥1 case (cross-link to existing `entities/*.md` OR inline `(YYYY)` citation) OR a named convention.
- [ ] Each new IMO/ILO standards-tier page will cite the IMO/ILO canonical URL AND a /mnt/ace corpus path reference (no extraction).
- [ ] Each new page will list ≥2 `see_also` cross-links that resolve to real files.
- [ ] No new page will contain quoted convention prose ≥10 words without a citation marker (#2482 deny-list).
- [ ] Each new page will be ≤400 words (concept-summary discipline).
- [ ] `index.md` will contain a new `## Standards-tier` (or `## Standards` if option (a)) section listing all 4 IMO/ILO pages and the existing Concepts table will list 6 new rows.
- [ ] `index.md` frontmatter `page_count` will equal exactly 32 (on-disk count post-plan: 22 existing + 10 new); `last_updated` will read `2026-05-02`.
- [ ] `log.md` will carry a `[2026-05-02] expand | maritime-law W2-C` entry.
- [ ] `tests/knowledge/test_maritime_law_expansion.py` will pass: `uv run pytest tests/knowledge/test_maritime_law_expansion.py -v`.
- [ ] No regression in existing knowledge tests: `uv run pytest tests/knowledge/ -v`.
- [ ] Review artifact for Claude (single-author internal): `scripts/review/results/2026-05-02-plan-2592-claude-internal.md` (Codex/Gemini UNAVAILABLE — see Adversarial Review Summary).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | MAJOR → revised | 2 MAJOR (wiki/standards/ routing contradicts memory for maritime-law; IMO revision-field semantics) + 5 MINOR — all addressed inline; default routing changed to concepts/ |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang (#2479) |
| Gemini | UNAVAILABLE | gemini sandbox path resolution failure |

**Overall result:** PASS-after-revision (2 MAJOR + 5 MINOR applied 2026-05-02)

**Revisions made based on review:**
- MAJOR-1: Re-framed Open Question #1 with verbatim memory quote excluding maritime-law from `wiki/standards/` routing; added third option (default = `concepts/` with additive frontmatter) and made it the plan default; added precondition step to update maritime-law CLAUDE.md schema if user picks `standards/` routing; added Risks entry that `standards/` choice pre-empts aces-#4 Phase 1.
- MAJOR-2: Renamed `revision` field to `consolidated_edition` and documented as a maritime-law-specific frontmatter convention NOT covered by #2471's calc-citation contract; explicitly deferred calc-resolvability; addressed ISM-as-embedded-in-SOLAS and MLC-as-ILO-publisher in Risks.
- MINOR-1: Replaced placeholder review-artifact paths in header and Artifact Map with `scripts/review/results/2026-05-02-plan-2592-claude-internal.md`; marked Codex/Gemini UNAVAILABLE inline.
- MINOR-2: Removed mid-draft self-correction text from top-10 selection; presented 6 doctrine-concepts + 4 IMO/ILO standards-tier cleanly with rationale.
- MINOR-3: Switched `code_id` regex to lowercase `^[a-z][a-z0-9-]+$` and renamed canonical IDs to lowercase (`marpol-73-78`, `solas-1974`, `mlc-2006`, `ism-code`) per `project_wiki_standards_path_decision.md`.
- MINOR-4: Replaced length+comma heuristic with citation-form lint that flags quoted prose ≥10 words missing a citation marker.
- MINOR-5: Changed `page_count` AC + test from `≥30` non-discriminating bound to exact `== 32` (on-disk count post-plan).

**Provenance:** Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`. Round 1.

---

## Risks and Open Questions

- **Risk: jurisdictional bias.** Maritime-law doctrine is not uniform across US admiralty (Schoenbaum), UK admiralty (Mandaraka-Sheppard, Aleka), and continental-Europe codified systems (e.g., French Code des transports, German HGB). The 6 doctrine-concept pages WILL flag the jurisdictional split explicitly in the "Doctrine" section and avoid privileging US or UK doctrine as default. Plan adopts UK/Commonwealth-leaning vocabulary as primary (Mandaraka-Sheppard) with US parenthetical on first occurrence — same convention as #2589.
- **Risk: convention-lifecycle drift.** IMO conventions are amended frequently — MARPOL Annex VI (sulphur cap), SOLAS (cyber-resilience amendments coming Jan 2026), MLC (recent amendments via STC). IMO/ILO pages will cite the consolidated-edition cutoff in `consolidated_edition:` frontmatter and link to the IMO `listofconventions.aspx` page rather than embedding numerical thresholds. Tests will not lock numerical values; they will lock structural shape.
- **Risk: IP boundary on case-law summaries.** Quoting judgment text triggers copyright concerns even for old cases. Doctrine-concept pages will refer to cases by court+year+name only, with cross-link to the existing entity page (which already summarizes the case in our voice). The `test_no_quoted_convention_prose_without_citation` lint catches the analogous risk for convention text.
- **Risk: routing memory exclusion.** Memory `project_wiki_standards_path_decision.md` verbatim: "The principle applies to: marine-engineering, engineering, naval-architecture. **Maritime-law, personal, health-reports are out of scope.**" Plan therefore defaults the 4 IMO/ILO pages to `wiki/concepts/` with additive frontmatter. If user picks Open Question #1 option (a) (`wiki/standards/`), this **pre-empts aces-#4 Phase 1 audit** (cradle-to-grave standards canonical home decision) — flag for user before approval; the maritime-law decision should not bind aces-#4's larger scope.
- **Risk: calc-citation contract gap for IMO/ILO.** IMO conventions are amended via MSC/MEPC amendments, MLC via ILO STC, ISM via SOLAS amendment chain — none publish a single "revision" matching the calc-citation contract semantic. The `consolidated_edition` field is a maritime-law-specific frontmatter convention; calc resolvers will NOT match against it in v1. Calc-resolvability for maritime-law standards-tier pages is deferred to a separate issue with amendment-set matching semantics.
- **Risk: ISM-as-embedded-in-SOLAS coupling.** ISM Code is embedded in SOLAS Ch IX, not a standalone publication. Treating it as a standalone page decouples it from the SOLAS amendment chain it actually rides on. This plan creates `ism-code.md` as a pointer page that explicitly states `embedded_in: solas-1974` in frontmatter and refers to SOLAS for `consolidated_edition` semantics; if user prefers to fold ISM content into a sub-section of `solas-1974.md`, flag during plan-review.
- **Risk: MLC-as-ILO-publisher distinct cadence.** MLC 2006 is ILO (not IMO), amended via Special Tripartite Committee on its own cadence (most recent amendments adopted 2022, in force 2024). Plan sets `publisher: ILO` and `consolidated_edition: "as amended through STC 2022 amendments (in force 2024)"` for `mlc-2006.md`; tests do not assume `publisher: IMO` uniformly across the 4 pages.
- **Risk: relocation churn.** The 6 existing convention pages (CLC, Bunker, HNS, Athens, LLMC, OPA-90) sit in `concepts/` despite carrying `code_id`-able identity. They are NOT relocated by this plan; this preserves URL stability for the case-law entity pages that link to them. A follow-up issue should cover the relocation as a separate atomic change (Open Question #2).
- **Risk: page-count regenerator drift.** `index.md` frontmatter says `page_count: 20` but on-disk count is 22 (index.md + overview.md not catalogued). After this plan: on-disk = 32. Test now requires exact match (`page_count == 32`) per MINOR-5 fix.

- **Open #1: routing for the 4 IMO/ILO pages — three options.**
  - **(a)** Override the memory exclusion and route to `wiki/standards/<code-id>.md`. Requires precondition: update `knowledge/wikis/maritime-law/CLAUDE.md` schema to declare the directory + extra-fields (mirrors naval-architecture). **NOTE: pre-empts aces-#4 Phase 1 cradle-to-grave standards-canonical-home audit.**
  - **(b)** Route to `wiki/concepts/standards-<code-id>.md` (slug-prefix convention).
  - **(c) [DEFAULT]** Route to `wiki/concepts/<code-id>.md` with additive `code_id`/`publisher`/`consolidated_edition` frontmatter (schema-additive, not path-extension). No CLAUDE.md change needed; aces-#4 audit not pre-empted; calc-resolvability deferred to a separate issue.
- **Open #2: existing convention page relocation.** Should the 6 pre-existing convention pages (CLC, Bunker, HNS, Athens, LLMC, OPA-90) be migrated to a different routing in a follow-up issue, given they carry standards-tier identity? Not in scope of this plan.
- **Open #3: foreign-language conventions.** Should multilingual convention text (e.g., Rotterdam Rules French/Spanish authoritative versions) be cross-linked from the IMO/ILO page or limited to the English IMO consolidation? Current plan: **English IMO consolidation only**, with a "Authoritative texts" line naming the official languages without linking. Flagged for user feedback.
- **Open #4: 11th candidate.** `concepts/imo-regulatory-framework.md` was deferred to keep batch size at 10. Should it ship in this batch (making it 11) or in W3?

---

## Complexity: T2

**T2** — 10 new wiki pages (6 doctrine-concepts + 4 IMO/ILO standards-tier) + 2 modified registry files + 1 new test module under default routing (Open Q#1 option (c)). Multi-file, TDD required, but no new code logic / no calc-citation emission / no calc-module touch. Risk is concentrated in (a) jurisdictional vocabulary discipline, (b) additive `code_id`/`publisher`/`consolidated_edition` frontmatter for 4 IMO/ILO pages, (c) citation-form lint for quoted prose — all addressable with regex tests. Not T3 because there is no new module / no calc / no migration / no schema change to CLAUDE.md (under default routing). If user picks Open Q#1 option (a), complexity bumps to T2+ due to CLAUDE.md schema precondition + new directory creation.
