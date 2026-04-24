# Plan for #2482: llm-wiki → GTM content boundary reconciliation (v3)

> **Status:** draft (v3 — v2 returned MINOR with 2 residual MAJOR-severity items; v3 closes both)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2482
> **Review artifacts:**
> - v1 review: scripts/review/results/2026-04-24-plan-2482-claude.md (MAJOR 5/4)
> - v2 review: scripts/review/results/2026-04-24-plan-2482-claude-v2.md (MINOR; 2 MAJOR-severity sub-findings)
> - v3 review: (pending)

---

## Revision history

| Version | Date | Change |
|---|---|---|
| v1 | 2026-04-24 | Initial draft; user-approved; Claude self-review returned MAJOR → rolled back |
| v2 | 2026-04-24 | Addresses 5 MAJOR + 4 MINOR findings; expands scope to adjacent knowledge surfaces; replaces prose sanitization with frontmatter-linter contract; quarantines the live `knowledge-to-website-pipeline.md` wiki page that contradicts the boundary |
| v3 | 2026-04-24 | Closes v2 residuals: (a) scopes in `data/document-index/` publisher manifests (the 30-collection upstream); (b) carves linter exception for scope-bounding docs so `overview.md` doesn't fail its own classification exercise; (c) adds `knowledge/wikis/cross-links.md` to surveyed surfaces; (d) adds `knowledge/_archive/` creation step; (e) clarifies `sources/` vs `concepts/` precedence; (f) annotates the "Unlocking Deepwarter" publisher name as a source typo preserved verbatim |

## How v2 resolves v1 findings

| # | v1 defect | v2 fix |
|---|---|---|
| MAJOR 1 | 3 of 5 classification exemplars don't exist | Classification exercises replaced with **real** existing pages (verified) |
| MAJOR 2 | Deny-list names only Orcina/AQWA/BEMRosetta | Full 30-publisher collection deny-list (extracted from sources tree) |
| MAJOR 3 | Memory's "Hard rule discovered" clause ignored | Sanitization contract now includes live-site **negative constraints** as first-class deny items |
| MAJOR 4 | Live wiki page `knowledge-to-website-pipeline.md` advocates forbidden pipeline | Quarantine action added to Files-to-Change |
| MAJOR 5 | dark-intelligence / seeds / health-reports / .planning/research excluded | Scope extended to all four adjacent surfaces |
| MINOR 1 | Prose sanitization ambiguous | Mechanical **frontmatter-based linter** added as primary enforcement |
| MINOR 2 | No mechanical alternative | Linter design spec included |
| MINOR 3 | "5 domain wikis" framing omits health-reports | Revised to "6 wiki surfaces + 4 adjacent knowledge surfaces" |
| MINOR 4 | #2022 "re-scope" is effectively closure | Honest recommendation: **close as superseded** with documented rationale |

---

## Resource Intelligence Summary

### Existing repo code
- Found: `knowledge/wikis/` — 6 wiki surfaces: `engineering/` (83 pages), `marine-engineering/` (19,190 pages), `naval-architecture/` (45), `maritime-law/` (22), `personal/` (5), `health-reports/` (repo health PII)
- Found: `knowledge/dark-intelligence/` — competitive intel (includes geotechnical, xlsx-poc subtrees)
- Found: `knowledge/seeds/` — raw research (career-learnings, maritime-law-cases, maritime-liabilities, mooring-failures-lng, naval-architecture-resources YAML files)
- Found: `.planning/research/` — strategic/market research (`2026-04-02-competitor-market.md` and others)
- Found: `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` — live wiki page (Apr 8 2026) advocating the forbidden pipeline; tags: gtm, website, publishing, content-pipeline, aceengineer
- Gap: no governance doc at `docs/governance/llm-wiki-to-gtm-boundary.md`
- Gap: no frontmatter-based linter enforcing allow/deny

### Standards
Not applicable — governance decision, not engineering calculation.

### LLM Wiki pages consulted (real, verified to exist)
- `knowledge/wikis/engineering/wiki/overview.md` — scope-bounding doc: "how we engineer, not what we engineer" (cited in memory as canonical llm-wiki framing)
- `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` — **contradicts** the boundary; must quarantine
- `knowledge/wikis/marine-engineering/wiki/sources/001.md` (and siblings) — publisher-collection-frontmatter pages used to derive the full deny-list
- `knowledge/wikis/health-reports/health-2026-04-07.md` — repo health report (candidate PII / internal-only; deny-list target)

### Documents consulted
- `#2022` — GitHub issue; verified body proposes SEO/leadgen pipeline with 5 phases. 3 of 4 acceptance criteria are forbidden by this boundary. Re-scope would null the issue → recommend close.
- `#2398` CLOSED — llm-wiki stays embedded (architectural constraint this decision inherits)
- `#2463` — aceengineer-website routing cleanup (downstream consumer that needs this boundary)
- `#2390` — epic roadmap (Batch Packs need this boundary before GTM-adjacent promotion)
- Memory: `project_aceengineer_copy_canonical_sources.md` (verified content; priority order + hard negative-constraint rule quoted in this plan)
- Memory: `project_llm_wiki_stays_embedded.md` — architectural constraint
- Live site `aceengineer.com/about.html` — canonical source of negative constraints
- Private `aceengineer-strategy` repo — true canonical firm-copy source (privacy-walled)

### Gaps identified
- No written decision reconciling #2022 intent with 2026-04-24 firm-copy memory decision
- No deny-list covering the full 30 publisher collections ingested into the wiki
- No mechanical frontmatter-based linter to enforce allow/deny classification
- No quarantine action for the live `knowledge-to-website-pipeline.md` wiki page
- No scoping of dark-intelligence / seeds / health-reports / .planning/research surfaces
- Live site negative constraints ("not a contractor with a laptop"; "not consulting hours") not encoded as deny-list inputs

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#2022` — OPEN — proposes 5-phase wiki → aceengineer.com pipeline (unrevised)
- `#2398` — CLOSED — llm-wiki stays embedded
- `#2463` — OPEN — aceengineer-website routing cleanup
- `#2390` — OPEN — epic roadmap

**Directory existence** (`ls` 2026-04-24):
- EXISTS: `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` (1649 bytes, Apr 8)
- EXISTS: `knowledge/wikis/health-reports/`
- EXISTS: `knowledge/dark-intelligence/`
- EXISTS: `knowledge/seeds/`
- EXISTS: `.planning/research/2026-04-02-competitor-market.md`
- MISSING (this plan creates): `docs/governance/llm-wiki-to-gtm-boundary.md`
- MISSING (this plan creates): `scripts/enforcement/check-gtm-boundary.sh` or equivalent linter

**Publisher collections extracted** (via `grep "^| collection |" knowledge/wikis/marine-engineering/wiki/sources/` 2026-04-24):
```
Arctic Technology Conference, Coiled Tubing & Well Intervention Conference 2011,
DeepGulf, DOT, Dry Tree Forum, EUCI, Euroforum Offshore Risers, Flow Induced Vibration,
IADC International Deepwater Drilling, IMarEST Offshore Oil and Gas Conference, ISO 9001,
ISOPE, JPT, NACE, Offshore West Africa, OMAE, OTC, Pipeline Pigging & Integrity Management Feb 2009,
Rio Oil & Gas, Robert Restore, SNAME, SPE, Subsea Houston, Subsea Survey IMMR, Subsea Tieback,
SUT, TOD, TO SORT, UK Conference Folder, Unlocking Deepwater Potential – Mumbai
```
30 unique publisher collections. Each is licensed third-party material — deny-list by default.

**Memory content excerpt** (from `project_aceengineer_copy_canonical_sources.md`):
> "**Hard rule discovered:** the live `about.html` contains explicit negative constraints ('We deliver automated workflows, not consulting hours'; 'AceEngineer is the firm ... not a contractor with a laptop'). Treat live-site negatives as canonical rules — any proposed phrase landing on the forbidden side (e.g. 'consulting practice') is drift, not a rephrasing."

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v2) | docs/plans/2026-04-24-issue-2482-llm-wiki-gtm-boundary.md |
| Governance doc | docs/governance/llm-wiki-to-gtm-boundary.md |
| Frontmatter linter | scripts/enforcement/check-gtm-boundary.sh |
| Linter rule file | .claude/rules/gtm-boundary.md |
| Quarantine action | delete or move `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` → `.archive/` |
| Issue comments | #2022 (close rationale), #2463 (intake policy pointer), #2390 (epic prerequisite) |
| v1 review artifact | scripts/review/results/2026-04-24-plan-2482-claude.md |
| v2 review artifacts | scripts/review/results/2026-04-24-plan-2482-claude-v2.md |

---

## Deliverable

A governance decision document plus a mechanical frontmatter-based linter that deterministically classifies any wiki page as allow / deny / needs-sanitization, a quarantine action for the live page advocating the forbidden pipeline, and cross-issue comments closing the loop. #2022 is closed as superseded.

---

## Proposed decision outline (v2 — user-review target)

**Governing principle:** llm-wiki and adjacent knowledge surfaces (`knowledge/`, `.planning/research/`) are the engineering knowledge substrate for internal and agent consumption. They are not sources of firm-facing GTM copy. Firm copy canonical sources are (1) live `aceengineer-website/*.html` and (2) private `aceengineer-strategy` repo. Cross-flow from wiki → GTM is permitted only for allow-list content, only after sanitization, and only via explicit manual review.

### Scope (v3 — expanded from v2)

**Governed surfaces:**
- `knowledge/wikis/engineering/`
- `knowledge/wikis/marine-engineering/`
- `knowledge/wikis/naval-architecture/`
- `knowledge/wikis/maritime-law/`
- `knowledge/wikis/personal/` (deny-list by nature)
- `knowledge/wikis/health-reports/` (deny-list — repo PII)
- `knowledge/wikis/cross-links.md` (top-level navigation index — v3 addition)
- `knowledge/dark-intelligence/` (deny-list — competitive intel)
- `knowledge/seeds/` (deny-list by default — raw research)
- `.planning/research/` (deny-list — strategic/market intelligence)
- `data/document-index/` (deny-list — publisher manifests; v3 addition closing v2 MAJOR-in-MINOR #1)

### Allow-list (may flow from wiki → GTM with sanitization + manual review)

- Anonymized technical case-study narratives derived from engineering workflows
- Methodology explainers for public-domain or fair-use standards (ASCE, API public RPs, ISO general-audience material)
- Curated "what is X" educational pages at or above `knowledge/wikis/engineering/wiki/concepts/` scope, **only if** not tagged with gtm / website / publishing / content-pipeline / aceengineer tags
- Capability explainers that map 1:1 onto live `aceengineer-website/*.html` CAP-NN headings (verified against live site at publish time)

### Deny-list (MUST NOT flow to GTM under any circumstances)

**Firm-copy negatives** (from memory hard rule + live-site):
- Any phrase positioning AceEngineer as "consulting practice", "consulting hours", "contractor with a laptop"
- Any staffing claim not verified against live-site about.html
- Any pricing, service description, or client-list material

**Vendor-derivative content** (licensed third-party material):
- All pages under `knowledge/wikis/*/wiki/sources/` — the 30 publisher collections enumerated above (SPE, OMAE, OTC, ISOPE, NACE, SNAME, API, IADC, SUT, JPT, DOT, IMarEST, and 18 others)
- All Orcina / AQWA / BEMRosetta manual derivatives
- Any page whose frontmatter `collection` field names a publisher
- **Upstream manifests** (v3 addition): `data/document-index/conference-registry.yaml`, `conference-paper-catalog.yaml`, `conference-index*.{jsonl,yaml,json,md}`, `dde-literature-catalog.yaml`, `dde-oil-gas-codes-scan.yaml`, `dde-standards-inventory.yaml`, `engineering-refs-catalog.md`, and any sibling catalog/registry file. These are the allow-list promotion source for the 30 publisher collections — scoping the wiki tree but not the manifest tree would leave the allow-list promotion path unguarded.

**Rule precedence** (v3 clarification — addresses v2 MINOR "sources/ vs concepts/ ambiguity"):
- `sources/` directory match is **absolute deny**, even if a page additionally lives at a `concepts/` path
- `concepts/` directory is allow-eligible **only if** no other deny-list rule matches (no `collection` frontmatter, no forbidden tag, not under a deny-listed root)
- When rules conflict, deny wins

**Private / strategic content:**
- `aceengineer-strategy` derivatives (entire repo, never cross boundary)
- `.planning/research/*.md` strategic intelligence
- `knowledge/dark-intelligence/**` (competitive intel)
- `knowledge/wikis/personal/**`
- `knowledge/seeds/**` raw research YAML files
- `knowledge/wikis/health-reports/**` (repo PII)

**Pattern exclusions** (cross-cutting):
- Any page with frontmatter tags matching `{gtm, website, publishing, content-pipeline, aceengineer}` → explicit quarantine, not publish
- Any page containing client names, project codes, or proprietary identifiers
- Any page where `collection` frontmatter field is set (indicates third-party licensed material)

### Sanitization contract (for allow-list material only)

A page that clears the allow-list classification must additionally pass the sanitization checklist before any publish attempt:

1. **Client identifiers stripped** — no client names, project codes, vessel names, field names, operator names
2. **Numeric examples generalized** — specific project values replaced with public reference values
3. **Negative-constraint screen** — page must NOT contain any firm-copy negative from the deny-list above (automated grep at publish time)
4. **Attribution footer** — standards / external sources cited with license statement
5. **Manual review** — user (not automation) signs off per publish; signoff recorded in a ledger file at `docs/governance/gtm-publish-ledger.yaml`

### Frontmatter linter (mechanical enforcement — MINOR 1/2 fix)

`scripts/enforcement/check-gtm-boundary.sh` reads a wiki page path and returns exit 0 (allow-eligible), 1 (deny), or 2 (needs-sanitization). Logic:

```
# v3: scope-bounding carve-out resolves v2 MAJOR-in-MINOR #2
# (overview.md has no frontmatter; without the carve-out the linter would
#  contradict its own classification exercise #2)
SCOPE_BOUNDING_BASENAMES = { overview.md, index.md, log.md }

read frontmatter
if path.basename in SCOPE_BOUNDING_BASENAMES and path is at a wiki root: exit 0 (scope-bounding carve-out; no sanitization required since these are navigation/meta, not content)
if page under any deny-listed directory (including data/document-index/): exit 1 (deny, cite rule)
if frontmatter is absent (and not in scope-bounding carve-out): exit 1 (conservative deny; missing frontmatter)
if frontmatter.collection is non-empty: exit 1 (vendor-derivative, cite rule)
if any frontmatter.tag in {gtm, website, publishing, content-pipeline, aceengineer}: exit 1 (forbidden-pipeline advocacy)
if body contains any firm-copy negative phrase (configurable list): exit 1
if page passes above: exit 2 (allow-eligible, sanitization required)
allow-eligible paths with all sanitization boxes ticked: exit 0
```

This replaces v1's prose-only sanitization with a deterministic mechanical check. Prose sanitization remains as a human-facing explanation, but classification correctness is machine-verified.

### Recommendation for #2022

**Close as superseded by #2482.**

v1 proposed re-scoping, but review showed 3 of 4 acceptance criteria ("10+ wiki domains published", "5+ skills as service pages", "daily cron auto-publish") fall on the deny-list. The residual scope after applying this boundary is effectively null. Closing is more honest than pretending to re-scope.

### Quarantine action

`knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` is removed from the wiki. Options:
1. **Delete** with a promotion-provenance comment on #2022 explaining why
2. **Move to** `knowledge/_archive/wikis/engineering/concepts/knowledge-to-website-pipeline-2026-04-08-superseded-by-2482.md`

Recommendation: move, so git history is preserved and the archive shows the retired pipeline design. Archive is not ingested by `search-wiki.py`.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/governance/llm-wiki-to-gtm-boundary.md | decision doc (expanded allow/deny + sanitization contract) |
| Create | scripts/enforcement/check-gtm-boundary.sh | mechanical frontmatter-based linter |
| Create | .claude/rules/gtm-boundary.md | agent-consumable rule pointing at boundary doc + linter |
| Create | docs/governance/gtm-publish-ledger.yaml | manual-review signoff ledger (empty initially) |
| Move | knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md → knowledge/_archive/... | quarantine forbidden-pipeline wiki page |
| Update | docs/plans/README.md | keep row as `draft` until v2 re-review + re-approval |
| Comment | GitHub #2022 | close as superseded with rationale |
| Comment | GitHub #2463 | link boundary doc + linter as intake policy |
| Comment | GitHub #2390 | register prerequisite for GTM-adjacent batch packs |

No code changes to digitalmodel or other engineering repos.

---

## Classification exercises (v2 — real pages only, verified to exist)

A reviewer walks these six real classifications; all must match doc + linter:

| # | Page (verified exists) | Expected | Rule path |
|---|---|---|---|
| 1 | `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` | **deny + quarantine** | tags: gtm,website,publishing → forbidden-pipeline advocacy |
| 2 | `knowledge/wikis/engineering/wiki/overview.md` | allow-eligible | educational scope-bounding doc, no deny-list tags / collection |
| 3 | `knowledge/wikis/marine-engineering/wiki/sources/001.md` (and any sibling) | deny | `collection` frontmatter → vendor-derivative |
| 4 | `knowledge/wikis/health-reports/health-2026-04-07.md` | deny | under health-reports/ → repo PII |
| 5 | `.planning/research/2026-04-02-competitor-market.md` | deny | under .planning/research/ → strategic intel |
| 6 | `knowledge/seeds/career-learnings.yaml` | deny | under knowledge/seeds/ → raw research |

Reviewer approval requires: linter exit codes match expected column; governance doc's prose classification matches; any divergence is a not-approval-ready finding.

---

## Acceptance Criteria

- [ ] `docs/governance/llm-wiki-to-gtm-boundary.md` committed with v2 scope (6 wikis + 4 adjacent surfaces)
- [ ] Deny-list enumerates all 30 publisher collections verified from sources tree
- [ ] Sanitization contract encodes memory's "Hard rule discovered" negative-constraint clause
- [ ] `scripts/enforcement/check-gtm-boundary.sh` exists and correctly classifies all 6 exercise pages (verified by `bash -x` invocation)
- [ ] `knowledge-to-website-pipeline.md` moved to `_archive/` with superseded-by-2482 marker
- [ ] #2022 closed as superseded with written rationale
- [ ] #2463 comment updated with boundary pointer
- [ ] #2390 epic updated with prerequisite reference
- [ ] `.claude/rules/gtm-boundary.md` committed
- [ ] `docs/governance/gtm-publish-ledger.yaml` committed (empty)
- [ ] Memory pointer aligns with final decision (no contradiction between memory and doc)
- [ ] Fresh Claude adversarial self-review of v2 returns APPROVE or MINOR (not MAJOR)

---

## Adversarial Review Summary

| Provider | Verdict (v1) | Verdict (v2) | Key findings |
|---|---|---|---|
| Claude | **MAJOR (5+4)** | PENDING | v1: fabricated exemplars, deny-list misses 30 publishers, memory mischaracterized, live page contradicts, adjacent surfaces excluded. v2 addresses all. |
| Codex | n/a | n/a | codex-cli 0.124.0 regression (#2479) blocks `codex exec` |
| Gemini | n/a | PENDING | sandbox overlay blindness noted in memory; re-evaluate per run |

**Overall v1 result:** FAIL (MAJOR → rolled back, approval removed)
**Overall v2 result:** PENDING self-review; user approval deferred until Claude returns APPROVE or MINOR

---

## Risks and Open Questions

- **Risk:** Deny-list may over-restrict educational content. Mitigation: allow-list explicitly carves public-domain standards and live-site-anchored capability explainers.
- **Risk:** Frontmatter linter false-negatives on pages with missing frontmatter. Mitigation: linter treats missing frontmatter as **deny** (conservative default).
- **Risk:** Quarantining `knowledge-to-website-pipeline.md` loses institutional context on why that design was rejected. Mitigation: the governance doc itself records the rationale; archive preserves git history.
- **Risk:** `.planning/research/` is already gitignored in some checkouts — linter must handle path-not-present gracefully.
- **Risk:** Closing #2022 removes a tracked thread of user intent. Mitigation: close comment preserves the rationale and references #2482 as the governing decision.
- **Open:** who maintains `gtm-publish-ledger.yaml` — user only, or designated operator? Recommendation: user only, per memory's user-in-loop principle.
- **Open:** should the linter run on every `wiki-ingest` commit (pre-commit hook) or nightly? Recommendation: pre-commit on the boundary-scoped paths; nightly full scan as audit.

---

## Complexity: T2

Governance doc + small shell linter + rule file + one file move + cross-issue comments. No code touching engineering modules. Blast radius is policy surface plus one wiki-page archive action.
