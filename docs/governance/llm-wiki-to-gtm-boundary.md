# llm-wiki → GTM Content Boundary

> **Governance decision.** Authoritative policy for what may and may not flow from llm-wiki and adjacent knowledge surfaces to GTM destinations.
> **Status:** in-force
> **Adopted:** 2026-04-24
> **Governing issue:** [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482)
> **Mechanical enforcement:** [#2485](https://github.com/vamseeachanta/workspace-hub/issues/2485) (separate tracker; until it lands, enforcement is by reviewer using this doc)
> **Supersedes:** [#2022](https://github.com/vamseeachanta/workspace-hub/issues/2022) (the proposed wiki → aceengineer.com publishing pipeline was incompatible with this boundary)

## 1. Governing principle

llm-wiki and adjacent knowledge surfaces (`knowledge/`, `.planning/research/`, `data/document-index/`) are the engineering knowledge substrate for internal and agent consumption. They are **not** sources of firm-facing GTM copy.

Firm copy canonical sources are:

1. **Live `aceengineer-website/*.html`** (public, authoritative for already-shipped framing, schema.org, capability headings)
2. **Private `aceengineer-strategy` repo** (privacy-walled; canonical for positioning, go-to-market, ideal-customer, competitors, pricing-model content)

Cross-flow from wiki → GTM is permitted **only** for allow-list content, **only** after sanitization, and **only** via explicit manual review.

## 2. Governed surfaces

This policy governs the following surfaces:

- `knowledge/wikis/engineering/`
- `knowledge/wikis/marine-engineering/`
- `knowledge/wikis/naval-architecture/`
- `knowledge/wikis/maritime-law/`
- `knowledge/wikis/personal/` (deny-list by nature)
- `knowledge/wikis/health-reports/` (deny-list — repo PII / operational health data)
- `knowledge/wikis/cross-links.md` (deny-list — auto-generated navigation artifact)
- `knowledge/dark-intelligence/` (deny-list — competitive intelligence)
- `knowledge/seeds/` (deny-list — raw research)
- `.planning/research/` (deny-list — strategic/market intelligence)
- `data/document-index/` (deny-list — upstream publisher manifests that feed the 30 collections below)

Out of scope for this policy:

- `aceengineer-website/` (target; public firm copy is a separate concern)
- `aceengineer-strategy/` (privacy-walled by separate mechanism; never crosses to GTM regardless)
- All non-knowledge repos (digitalmodel, assetutilities, etc.)

## 3. Allow-list

Content that MAY flow from wiki → GTM, subject to the sanitization contract in §5:

- Anonymized technical case-study narratives derived from engineering workflows
- Methodology explainers for public-domain or fair-use standards (ASCE, public API RPs, ISO general-audience material)
- Curated "what is X" educational pages under `concepts/` directories, **only if** all of the following hold:
  - Not tagged with any of `{gtm, website, publishing, content-pipeline, aceengineer}`
  - No `collection` frontmatter field (would indicate vendor-derivative)
  - Not `auto_generated: true`
- Capability explainers that map 1:1 onto live `aceengineer-website/*.html` CAP-NN headings (verified against live site at publish time)

## 4. Deny-list

Content that MUST NOT flow to GTM under any circumstances.

### 4.1 Firm-copy negatives (from memory hard rule + live site)

The live `aceengineer-website/about.html` contains explicit negative constraints that are canonical for firm positioning. Any proposed content landing on the forbidden side is drift, not phrasing:

- Any phrase positioning AceEngineer as "consulting practice", "consulting hours", or "contractor with a laptop"
- Any staffing claim not verified against live `about.html`
- Any pricing, service description, or client-list material

### 4.2 Vendor-derivative content (licensed third-party material)

- All pages under `knowledge/wikis/*/wiki/sources/` (30 publisher collections — see §4.5)
- All Orcina / AQWA / BEMRosetta manual derivatives
- Any page whose frontmatter `collection` field names a publisher
- Upstream publisher manifests:
  - `data/document-index/conference-registry.yaml`
  - `data/document-index/conference-paper-catalog.yaml`
  - `data/document-index/conference-index*.{jsonl,yaml,json,md}`
  - `data/document-index/dde-literature-catalog.yaml`
  - `data/document-index/dde-oil-gas-codes-scan.yaml`
  - `data/document-index/dde-standards-inventory.yaml`
  - `data/document-index/engineering-refs-catalog.md`
  - Sibling catalog/registry files under `data/document-index/`

### 4.3 Private / strategic content

- `aceengineer-strategy` derivatives (entire repo; privacy wall is authoritative)
- `.planning/research/*.md` — strategic / market intelligence
- `knowledge/dark-intelligence/**` — competitive intel
- `knowledge/wikis/personal/**`
- `knowledge/seeds/**` — raw research YAML files
- `knowledge/wikis/health-reports/**` — repo PII

### 4.4 Pattern exclusions

- Pages tagged with any of `{gtm, website, publishing, content-pipeline, aceengineer}` → explicit quarantine, not publish
- Pages containing client names, project codes, or proprietary identifiers
- Auto-generated navigation artifacts (`auto_generated: true`)
- Immediate children of `knowledge/wikis/` (e.g., `cross-links.md` and any future top-level artifacts) — the top level of `knowledge/wikis/` is reserved for navigation/meta, not publishable content

### 4.5 Enumerated publisher collections (30 total)

The following publisher collections are represented in `knowledge/wikis/*/wiki/sources/` frontmatter as of 2026-04-24. Each is licensed third-party material and is deny-list by default (see §4.2):

Arctic Technology Conference; Coiled Tubing & Well Intervention Conference 2011; DeepGulf; DOT; Dry Tree Forum; EUCI; Euroforum Offshore Risers; Flow Induced Vibration; IADC International Deepwater Drilling; IMarEST Offshore Oil and Gas Conference; ISO 9001; ISOPE; JPT; NACE; Offshore West Africa; OMAE; OTC; Pipeline Pigging & Integrity Management Feb 2009; Rio Oil & Gas; Robert Restore; SNAME; SPE; Subsea Houston; Subsea Survey IMMR; Subsea Tieback; SUT; TOD; TO SORT; UK Conference Folder; Unlocking Deepwarter Potential- Mumbai.

**Publisher-name fidelity note:** names are preserved verbatim from upstream frontmatter. "Unlocking Deepwarter Potential- Mumbai" is a typo in the source and is preserved as-is. When upstream corrects a typo, this document should be updated via PR that adds the corrected name while retaining the old one (union, not replacement) until wiki-ingest propagates the change; a follow-up PR then retires the old name. This coordination is relevant to the mechanical enforcement in [#2485](https://github.com/vamseeachanta/workspace-hub/issues/2485).

## 5. Rule precedence

When a page could match multiple rules, the following precedence applies (most-specific deny wins):

1. **`sources/` directory match is absolute deny**, even if the page is also at a `concepts/` path or has no `collection` frontmatter.
2. **`concepts/` is allow-eligible only** when no other deny-list rule matches (no `collection` frontmatter, no forbidden tag, not under a deny-listed root, not `auto_generated`).
3. **Scope-bounding pages (`overview.md`, `index.md`, `log.md`) are conventionally non-publishable** regardless of content — they are navigation/meta, not content — and are not a publish target even if they would otherwise clear allow-list checks.
4. **When rules conflict, deny wins.**

## 6. Sanitization contract

A page that clears allow-list classification (§3) must additionally pass this sanitization checklist before any publish attempt:

1. **Client identifiers stripped** — no client names, project codes, vessel names, field names, operator names
2. **Numeric examples generalized** — specific project values replaced with public reference values
3. **Negative-constraint screen** — page must NOT contain any firm-copy negative from §4.1 (automated grep at publish time)
4. **Attribution footer** — external sources cited with license statement
5. **Manual review** — the user (not automation) signs off per publish

Mechanical enforcement of this checklist (frontmatter-based linter, revision-binding ledger, pre-commit hook) is tracked under [#2485](https://github.com/vamseeachanta/workspace-hub/issues/2485). Until that lands, reviewers enforce this contract by hand using this doc plus the classification exercises in §7.

## 7. Classification exercises (reviewer self-check)

A reviewer walks these eight real classifications against this policy; each must reach the same classification the table states. A divergence is a signal the policy text is ambiguous — in which case this doc needs a revision, not a publish workaround.

| # | Page (verified exists 2026-04-24) | Classification | Rationale |
|---|---|---|---|
| 1 | `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` | deny + quarantine | tags `gtm,website,publishing` advocate the forbidden pipeline |
| 2 | `knowledge/wikis/engineering/wiki/overview.md` | non-publishable by convention | scope-bounding navigation page |
| 3 | `knowledge/wikis/marine-engineering/wiki/sources/001.md` | deny | under `/sources/` → §5 rule 1 absolute deny |
| 4 | `knowledge/wikis/health-reports/health-2026-04-07.md` | deny | §4.3 repo PII |
| 5 | `.planning/research/2026-04-02-competitor-market.md` | deny | §4.3 strategic intelligence |
| 6 | `knowledge/seeds/career-learnings.yaml` | deny | §4.3 raw research |
| 7 | `data/document-index/conference-registry.yaml` | deny | §4.2 upstream publisher manifest |
| 8 | `knowledge/wikis/cross-links.md` | deny | §4.4 auto-generated navigation (`auto_generated: true`) |

## 8. Quarantine action (this policy adoption)

On adoption of this policy, the live wiki page `knowledge/wikis/engineering/wiki/concepts/knowledge-to-website-pipeline.md` (Apr 8 2026; tags: `gtm, website, publishing, content-pipeline, aceengineer`) is moved to:

```
knowledge/_archive/wikis/engineering/concepts/knowledge-to-website-pipeline-2026-04-08-superseded-by-2482.md
```

`knowledge/_archive/` is a new convention introduced alongside this policy; see `knowledge/_archive/README.md` for scope and ingest-exclusion declaration.

## 9. Scope changes

This policy may be amended only via a PR that:

1. Updates this document
2. Updates the classification-exercise table if §3, §4, or §5 shifted
3. Updates any downstream consumers ([#2485](https://github.com/vamseeachanta/workspace-hub/issues/2485) linter, [#2463](https://github.com/vamseeachanta/workspace-hub/issues/2463) website intake) to stay in sync
4. Is reviewed by a project owner

A new top-level file in `knowledge/wikis/` (beyond `cross-links.md`) requires a §2 and §4.4 amendment before it becomes part of this policy's governed scope; default is deny until explicit.

## 10. References

- Memory: `project_aceengineer_copy_canonical_sources` (priority order + hard negative-constraint rule)
- Memory: `project_llm_wiki_stays_embedded` (architectural constraint — llm-wiki is not spinning out)
- [#2398](https://github.com/vamseeachanta/workspace-hub/issues/2398) (CLOSED — llm-wiki embedded decision)
- [#2463](https://github.com/vamseeachanta/workspace-hub/issues/2463) — aceengineer-website routing cleanup (downstream consumer)
- [#2390](https://github.com/vamseeachanta/workspace-hub/issues/2390) — epic roadmap (GTM-adjacent batch packs depend on this policy)
- [#2022](https://github.com/vamseeachanta/workspace-hub/issues/2022) — superseded
- [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) — standards `code_id`/`publisher`/`revision` frontmatter (related, adjacent scope)
