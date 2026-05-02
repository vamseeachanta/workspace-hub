# Plan for #2482: llm-wiki → GTM content boundary — governance policy (v6)

> **Status:** draft (v6 — SCOPE SPLIT: mechanical enforcement rescoped to new issue #2485; this plan is policy-only)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2482
> **Sibling issue:** https://github.com/vamseeachanta/workspace-hub/issues/2485 (mechanical enforcement)
> **Review artifacts:**
> - v1 review: scripts/review/results/2026-04-24-plan-2482-claude.md (MAJOR 5/4 — structural defects)
> - v2 review: scripts/review/results/2026-04-24-plan-2482-claude-v2.md (MINOR; 2 MAJOR-severity scope residuals)
> - v3 review: scripts/review/results/2026-04-24-plan-2482-claude-v3.md (MINOR; 1 MAJOR + 4 MINOR rule-path gaps)
> - v4 review: scripts/review/results/2026-04-24-plan-2482-claude-v4.md (MINOR; 0 MAJOR + 4 MINOR spec gaps)
> - v5 review: scripts/review/results/2026-04-24-plan-2482-claude-v5.md (MAJOR 3/6 — spec drift from patching)
> - v6 review: (pending; scope narrowed substantially so prior linter-related findings are out-of-scope)

---

## Revision history

| Version | Date | Change |
|---|---|---|
| v1 | 2026-04-24 | Initial draft; user-approved; Claude self-review returned MAJOR → rolled back |
| v2 | 2026-04-24 | Expanded scope to adjacent knowledge surfaces; full 30-publisher deny-list; memory hard-rule encoded; prose sanitization → mechanical frontmatter linter; quarantine action for forbidden-pipeline wiki page |
| v3 | 2026-04-24 | Added `data/document-index/`, `cross-links.md`; scope-bounding carve-out; `_archive/` convention; sources/concepts precedence |
| v4 | 2026-04-24 | Added `auto_generated: true → deny` rule; corrected sources/ rule-path citation; ledger-backed exit-0; wiki-root defined; publisher-typo correction path |
| v5 | 2026-04-24 | Full ledger schema; yq+Python impl; terminal exit-2 for scope-bounding pages; Rule 1b top-level deny. Self-review returned MAJOR 3/6 for spec drift (signoff_sha ambiguity, dangling artifacts, prose-vs-code contradiction) |
| v6 | 2026-04-24 | **SCOPE SPLIT per user decision 2026-04-24.** Mechanical enforcement (linter + ledger + pre-commit hook + yq/Python impl) rescoped to new issue #2485. This plan is now policy-only, restoring original T2 complexity. All policy content (scope, allow/deny, sanitization, quarantine) is retained; all mechanical-enforcement components are removed |

---

## What v6 keeps (policy, from v2-v5 iteration)

- Full 6-wiki + 4-adjacent-surface + `data/document-index/` scope
- Full 30-publisher collection deny-list
- Memory's "Hard rule discovered" negative-constraint clause
- Quarantine action for `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md`
- Sources/concepts rule precedence (prose)
- Scope-bounding pages never publishable (prose convention)
- Classification exercises as **reviewer exercises** (not linter assertions)
- `#2022` close-as-superseded recommendation
- `knowledge/_archive/README.md` convention

## What v6 removes (rescoped to #2485)

- `scripts/enforcement/check-gtm-boundary.sh` linter
- Rule 1-6 pseudo-code + exit-code semantics block
- `docs/governance/gtm-publish-ledger.yaml` schema + contents
- `yq` / Python implementation decisions
- `tools/gtm-boundary-ledger.py` Python fallback
- `scripts/enforcement/require-gtm-ledger-signoff.sh` pre-commit hook
- Signoff-SHA binding semantics
- `.claude/rules/gtm-boundary-enforcement.md` (mechanical-enforcement agent rule)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `knowledge/wikis/` — 6 wiki surfaces: `engineering/` (83 pages), `marine-engineering/` (19,190 pages), `naval-architecture/` (45), `maritime-law/` (22), `personal/` (5), `health-reports/` (repo health reports)
- Found: `knowledge/wikis/cross-links.md` — top-level auto-generated navigation artifact
- Found: `knowledge/dark-intelligence/` — competitive intel
- Found: `knowledge/seeds/` — raw research YAML
- Found: `.planning/research/` — strategic/market research
- Found: `data/document-index/` — publisher manifests upstream of wiki sources
- Found: `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` — live wiki page (Apr 8 2026; tags: gtm, website, publishing, content-pipeline, aceengineer) advocating the forbidden pipeline
- Gap: no governance doc at `docs/governance/llm-wiki-to-gtm-boundary.md`

### Standards
Not applicable — governance decision.

### LLM Wiki pages consulted (real, verified to exist)
- `knowledge/wikis/engineering/wiki/overview.md` — scope-bounding doc ("how we engineer, not what we engineer"); authoritative llm-wiki scope statement
- `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` — contradicts the boundary; quarantine target
- `knowledge/wikis/marine-engineering/wiki/sources/001.md` + siblings — 30 publisher-collection pages used to derive deny-list
- `knowledge/wikis/health-reports/health-2026-04-07.md` — repo PII content; deny-list example
- `knowledge/wikis/cross-links.md` — auto-generated navigation; deny-list example

### Documents consulted
- `#2022` — proposes 5-phase wiki → aceengineer.com pipeline; 3 of 4 acceptance criteria fall on the deny-list (effective null after boundary) → close as superseded
- `#2398` CLOSED — llm-wiki stays embedded
- `#2463` — aceengineer-website routing cleanup (downstream consumer)
- `#2390` — epic roadmap
- `#2485` — mechanical enforcement (sibling issue); consumes the allow/deny policy defined here
- Memory: `project_aceengineer_copy_canonical_sources.md` — priority order + hard negative-constraint rule quoted below
- Memory: `project_llm_wiki_stays_embedded.md` — architectural constraint

### Gaps identified
- No written governance decision reconciling #2022 with the 2026-04-24 firm-copy memory decision
- Live `knowledge-to-website-pipeline.md` wiki page actively contradicts the intended policy — must quarantine
- Allow/deny classification has no authoritative prose reference agents can cite

### Evidence (embedded verification, from iterative rounds)

**Publisher collections** (grep `^| collection |` in `knowledge/wikis/marine-engineering/wiki/sources/*.md`, verified 2026-04-24):
```
Arctic Technology Conference, Coiled Tubing & Well Intervention Conference 2011,
DeepGulf, DOT, Dry Tree Forum, EUCI, Euroforum Offshore Risers, Flow Induced Vibration,
IADC International Deepwater Drilling, IMarEST Offshore Oil and Gas Conference, ISO 9001,
ISOPE, JPT, NACE, Offshore West Africa, OMAE, OTC, Pipeline Pigging & Integrity Management Feb 2009,
Rio Oil & Gas, Robert Restore, SNAME, SPE, Subsea Houston, Subsea Survey IMMR, Subsea Tieback,
SUT, TOD, TO SORT, UK Conference Folder, Unlocking Deepwarter Potential- Mumbai
```
30 unique collections; "Deepwarter" typo is in upstream frontmatter (preserved verbatim — see note below).

**Memory hard rule** (from `project_aceengineer_copy_canonical_sources.md`):
> "Hard rule discovered: the live `about.html` contains explicit negative constraints ('We deliver automated workflows, not consulting hours'; 'AceEngineer is the firm ... not a contractor with a laptop'). Treat live-site negatives as canonical rules — any proposed phrase landing on the forbidden side (e.g. 'consulting practice') is drift, not a rephrasing."

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-2482-llm-wiki-gtm-boundary.md |
| Governance doc | docs/governance/llm-wiki-to-gtm-boundary.md |
| Archive README | knowledge/_archive/README.md |
| Quarantined page | knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md → knowledge/_archive/wikis/engineering/concepts/knowledge-to-website-pipeline-2026-04-08-superseded-by-2482.md |
| Issue comments | #2022 (close rationale), #2463 (intake-policy pointer), #2390 (epic prerequisite), #2485 (policy-input handoff) |

---

## Deliverable

A governance decision document defining the llm-wiki → GTM content boundary (allow-list, deny-list, sanitization contract, classification exercises), a quarantine action for the live wiki page contradicting the boundary, and cross-issue comments. Mechanical enforcement of this boundary is tracked separately under #2485 and is NOT in scope for this plan.

---

## Proposed governance decision

### Governing principle
llm-wiki and adjacent knowledge surfaces (`knowledge/`, `.planning/research/`, `data/document-index/`) are the engineering knowledge substrate for internal and agent consumption. They are **not** sources of firm-facing GTM copy. Firm copy canonical sources are:
1. Live `aceengineer-website/*.html` (public, authoritative for already-shipped framing)
2. Private `aceengineer-strategy` repo (privacy-walled; canonical for positioning, GTM, pricing, competitive, ideal-customer content)

Cross-flow from wiki → GTM is permitted only for allow-list content, only after sanitization, and only via explicit manual review.

### Scope — governed surfaces
- `knowledge/wikis/engineering/`
- `knowledge/wikis/marine-engineering/`
- `knowledge/wikis/naval-architecture/`
- `knowledge/wikis/maritime-law/`
- `knowledge/wikis/personal/` (deny-list by nature)
- `knowledge/wikis/health-reports/` (deny-list — repo PII / operational health data)
- `knowledge/wikis/cross-links.md` (deny-list — auto-generated navigation artifact)
- `knowledge/dark-intelligence/` (deny-list — competitive intel)
- `knowledge/seeds/` (deny-list — raw research)
- `.planning/research/` (deny-list — strategic/market intelligence)
- `data/document-index/` (deny-list — upstream publisher manifests for the 30 collections above)

### Allow-list (may flow from wiki → GTM with sanitization + manual review)
- Anonymized technical case-study narratives derived from engineering workflows
- Methodology explainers for public-domain or fair-use standards (ASCE, public API RPs, ISO general-audience material)
- Curated "what is X" educational pages under `concepts/` directories, **only if**:
  - Not tagged with `gtm` / `website` / `publishing` / `content-pipeline` / `aceengineer`
  - No `collection` frontmatter field (would indicate vendor-derivative)
  - Not `auto_generated: true`
- Capability explainers that map 1:1 onto live `aceengineer-website/*.html` CAP-NN headings (verified against live site at publish time)

### Deny-list (MUST NOT flow to GTM)

**Firm-copy negatives** (from memory hard rule + live site):
- Any phrase positioning AceEngineer as "consulting practice", "consulting hours", "contractor with a laptop"
- Any staffing claim not verified against live `about.html`
- Any pricing, service description, or client-list material

**Vendor-derivative content** (licensed third-party material):
- All pages under `knowledge/wikis/*/wiki/sources/` — the 30 publisher collections enumerated above
- All Orcina / AQWA / BEMRosetta manual derivatives
- Any page whose frontmatter `collection` field names a publisher
- Upstream manifests: `data/document-index/conference-registry.yaml`, `conference-paper-catalog.yaml`, `conference-index*.{jsonl,yaml,json,md}`, `dde-literature-catalog.yaml`, `dde-oil-gas-codes-scan.yaml`, `dde-standards-inventory.yaml`, `engineering-refs-catalog.md` and sibling catalog/registry files

**Private / strategic content:**
- `aceengineer-strategy` derivatives (entire repo, never cross boundary)
- `.planning/research/*.md` strategic intelligence
- `knowledge/dark-intelligence/**` competitive intel
- `knowledge/wikis/personal/**`
- `knowledge/seeds/**` raw research YAML files
- `knowledge/wikis/health-reports/**` repo PII

**Pattern exclusions:**
- Pages tagged with `{gtm, website, publishing, content-pipeline, aceengineer}` — explicit quarantine, not publish
- Pages containing client names, project codes, or proprietary identifiers
- Auto-generated navigation artifacts (`auto_generated: true`)
- Immediate children of `knowledge/wikis/` other than `cross-links.md` (which is already deny-listed for a separate reason)

**Rule precedence** (prose):
- `sources/` directory match is **absolute deny**, even if a page is also at a `concepts/` path
- `concepts/` is allow-eligible **only** when no other deny-list rule matches
- Scope-bounding pages (`overview.md` / `index.md` / `log.md`) are conventionally **not publishable** regardless of their content — they are navigation-meta, not content
- When rules conflict, deny wins

### Sanitization contract (prose checklist for allow-list material)

A page that clears allow-list classification must additionally pass the sanitization checklist before any publish attempt:

1. **Client identifiers stripped** — no client names, project codes, vessel names, field names, operator names
2. **Numeric examples generalized** — specific project values replaced with public reference values
3. **Negative-constraint screen** — page must NOT contain any firm-copy negative (see memory hard rule above)
4. **Attribution footer** — external sources cited with license statement
5. **Manual review** — user (not automation) signs off per publish

**Enforcement note:** mechanical enforcement of this checklist (frontmatter-based linter + revision-binding ledger + pre-commit hook) is tracked under **#2485**. Until that lands, reviewers enforce this contract by hand using this governance doc plus the classification exercises below.

### Classification exercises (prose reviewer exercises — not linter assertions)

A reviewer walks these eight real classifications to sanity-check the policy:

| # | Page (verified exists) | Classification | Rationale |
|---|---|---|---|
| 1 | `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` | **deny + quarantine** | tags `gtm,website,publishing` advocate the forbidden pipeline |
| 2 | `knowledge/wikis/engineering/wiki/overview.md` | **non-publishable by convention** (scope-bounding) | navigation/meta, not content |
| 3 | `knowledge/wikis/marine-engineering/wiki/sources/001.md` | **deny** | under `/sources/` → absolute-deny precedence |
| 4 | `knowledge/wikis/health-reports/health-2026-04-07.md` | **deny** | repo PII |
| 5 | `.planning/research/2026-04-02-competitor-market.md` | **deny** | strategic intelligence |
| 6 | `knowledge/seeds/career-learnings.yaml` | **deny** | raw research |
| 7 | `data/document-index/conference-registry.yaml` | **deny** | upstream publisher manifest |
| 8 | `knowledge/wikis/cross-links.md` | **deny** | auto-generated navigation (`auto_generated: true`) |

A reviewer whose classification of any of these differs from the table is a signal the policy text is ambiguous — in which case the policy is not approval-ready.

**Publisher-name fidelity note:** the deny-list enumerates publisher collections verbatim from upstream frontmatter. "Unlocking Deepwarter Potential- Mumbai" is preserved as written in the source (typo is in upstream frontmatter). When upstream corrects the typo, the governance doc should be updated via PR adding the corrected name while keeping the old one (union) until wiki-ingest confirms propagation. This coordination concern is carried forward to #2485 where it matters for the linter's publisher list.

### Recommendation for #2022

**Close as superseded by #2482.** 3 of 4 acceptance criteria in #2022 ("10+ wiki domains published", "5+ skills as service pages", "daily cron auto-publish") fall on the deny-list; the residual scope is effectively null. Closing is more honest than pretending to re-scope.

### Quarantine action

`knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` (Apr 8 2026, tags: gtm, website, publishing, content-pipeline, aceengineer) is moved to:
```
knowledge/_archive/wikis/engineering/concepts/knowledge-to-website-pipeline-2026-04-08-superseded-by-2482.md
```
`knowledge/_archive/` is a new convention introduced by this plan; `knowledge/_archive/README.md` declares that the archive is not ingested by `search-wiki.py` (verified behavior via `resolve_wiki_path.py` during v3 review).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/governance/llm-wiki-to-gtm-boundary.md | governance decision doc |
| Create | knowledge/_archive/README.md | establish archive convention; declare out-of-ingest-scope |
| Move | knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md → knowledge/_archive/wikis/engineering/concepts/knowledge-to-website-pipeline-2026-04-08-superseded-by-2482.md | quarantine contradicting wiki page |
| Update | docs/plans/README.md | mark v6 row |
| Comment | GitHub #2022 | close as superseded with rationale |
| Comment | GitHub #2463 | link boundary doc as intake policy |
| Comment | GitHub #2390 | register prerequisite for GTM-adjacent batch packs |
| Comment | GitHub #2485 | link governance doc as policy input |

No code, no linter, no ledger. Those are owned by #2485.

---

## Acceptance Criteria

- [ ] `docs/governance/llm-wiki-to-gtm-boundary.md` committed with full scope (6 wikis + `cross-links.md` + 4 adjacent surfaces + `data/document-index/`)
- [ ] Deny-list enumerates all 30 publisher collections verbatim (with publisher-name-fidelity note)
- [ ] Sanitization contract encodes memory's "Hard rule discovered" negative-constraint clause
- [ ] Rule precedence clause ("sources/ absolute deny; concepts/ conditional") is present
- [ ] Classification exercises table present and reviewer-walkable
- [ ] `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` moved to `knowledge/_archive/...`
- [ ] `knowledge/_archive/README.md` committed with ingest-scope declaration
- [ ] #2022 closed as superseded with written rationale
- [ ] #2463 comment posted
- [ ] #2390 epic updated with prerequisite reference
- [ ] #2485 comment posted linking this governance doc as policy input
- [ ] Memory pointer aligns with final decision

---

## Adversarial Review Summary

| Round | Verdict | Key finding class |
|---|---|---|
| v1 | MAJOR 5/4 | structural (fabricated exemplars, missing publishers, memory mis-cited, live contradictor, missing surfaces) |
| v2 | MINOR (2 MAJOR-severity) | scope completion (data/document-index, overview.md linter contradiction) |
| v3 | MINOR (1 MAJOR + 4 MINOR) | rule-consistency (exercise 8 gap, exercise 3 wrong rule) |
| v4 | MINOR (0 MAJOR + 4 MINOR) | spec gaps (schema, impl, bootstrap hazard, top-level defaults) |
| v5 | MAJOR 3/6 | spec drift from patching (signoff_sha, dangling artifacts, prose-code contradiction) |
| v6 | PENDING | scope-narrowed: linter/ledger removed to #2485; policy-only |

**Interpretation:** v5 MAJOR was entirely within the linter/ledger sub-scope that v6 rescopes out. Policy content survives all 5 rounds of review unchanged — reviewers consistently approved the allow/deny content and classification exercises. The iteration's real value was scope discovery (v2-v3) and implementation rigor (v4-v5). Moving the implementation rigor to #2485 lets v6 stand as a clean T2 policy doc.

---

## Risks and Open Questions

- **Risk:** governance doc without mechanical enforcement leaves classification to human judgment. Mitigation: classification exercises table + #2485 dependency for audit-grade enforcement.
- **Risk:** deny-list may over-restrict educational content. Mitigation: allow-list explicitly carves public-domain standards and live-site-anchored capability explainers.
- **Risk:** quarantining `knowledge-to-website-pipeline.md` loses institutional context. Mitigation: governance doc itself records rationale; archive preserves git history.
- **Risk:** closing #2022 removes tracked user intent. Mitigation: close comment preserves rationale and references #2482 as the governing decision.
- **Open:** does the governance doc also govern `aceengineer-strategy` → GTM flow, or scope strictly to wiki? Current proposal: wiki/knowledge/.planning only; strategy repo is already privacy-walled by separate mechanism.
- **Open:** Future additions to top-level `knowledge/wikis/` (beyond `cross-links.md`) — process? Recommendation: any new top-level file requires a governance-doc update; default is deny until policy is explicit.

---

## Complexity: T2

Governance doc + one file move + README + 4 issue comments. No code. No linter. No ledger. Matches original T2 scope.
