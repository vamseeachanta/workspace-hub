# Abstraction decision tree — worked examples

Walks the public/private routing decision tree on real-world scenarios.
Read alongside SKILL.md decision tree.

---

## Example 1: OCIMF MEG sign-convention page

**Source**: digitalmodel#616 OCIMF coefficient explorer methodology

**Page**: `wikis/naval-architecture/standards/ocimf-meg.md`

**Walkthrough**:

```
Page references a client project name?
  → NO (only OCIMF as publisher, MEG as standard)

→ Commit to public — no abstraction needed
```

**Commit message**: `abstraction: not-applicable-public-standard-only`

---

## Example 2: B1528 SIROCCO mooring-tension analysis (hypothetical)

**Source**: workspace-hub#2760 SIROCCO force calculation review

**Proposed page**: `wikis/naval-architecture/methodology/sirocco-rudder-angle-envelope.md`

**Walkthrough**:

```
Page references a client project name?
  → YES (SIROCCO is the project; B1528 is the project code)

Is project name in public domain?
  → Investigate:
    - Operator press release? Check operator's public newsroom
    - SEC filing? Check operator's 10-K under "key projects"
    - Conference paper? Search OTC/SPE/OMAE/ISOPE proceedings
    - Regulator? BOEM/BSEE production database
  → Suppose: YES, named in OTC 2023 paper

Is all key data also publicly available?
  → Is the rudder-angle ±5° X/Y/Z/K/M/N envelope from the same OTC paper?
    Or from a separate public source?
  → Suppose: NO, the envelope values are from project-internal calcs

→ ABSTRACT project name → "a deepwater FSO mooring envelope"
```

**Commit message** (PRIVATE wiki, actual names retained):
`source: workspace-hub#2760`

**For a public page** (different slug, abstracted):
`abstraction: applied; source private llm-wiki-<client> page-id sirocco-rudder-envelope`

---

## Example 3: Public field development case study

**Source**: BSEE production records + Shell 2023 OTC paper on Vito field

**Proposed page**: `wikis/lng-projects/case-studies/vito-tieback-methodology.md`
(hypothetical example for documentation; verify before using)

**Walkthrough**:

```
Page references a client project name?
  → YES (Vito)

Is project name in public domain?
  → Shell press release 2018 announcing Vito sanction: YES
  → OTC 2023 paper "Vito tieback design and execution": YES
  → BSEE production records list Vito: YES
  → VERDICT: public

Is all key data also publicly available?
  → Cited well count, water depth, tieback distance: from OTC 2023 paper ✓
  → Production-rate range: from BSEE database ✓
  → Equipment supplier names: from press releases ✓
  → All cited data backs to public source
  → VERDICT: public

→ EXCEPTION APPLIES — use "Vito" as-is, cite all public sources in `## Sources`
```

**Commit message**: `abstraction: not-needed-exception-met; sources [OTC2023-vito, shell-press-2018, bsee-production-2024]`

---

## Example 4: Mixed-tier OCIMF methodology page

**Source**: OCIMF MEG4 Annex A convention + abstracted illustration from acma project

**Proposed page**: `wikis/naval-architecture/methodology/ocimf-coefficient-interpretation.md`

**Walkthrough**:

```
Page section A: OCIMF MEG Annex A convention
  Page references a client project name?
    → NO (only OCIMF / MEG)
  → No abstraction

Page section B: Worked example using a deepwater FSO
  Page references a client project name?
    → Original draft had "ACMA-2023-Q4 mooring study"
    → Public domain? NO
    → ABSTRACT to "a deepwater FSO mooring study (operator anonymized)"

Page section C: Coefficient envelope ranges
  References specific numeric envelopes from acma client work?
    → If exact: do NOT include in public; either remove section or
      sanitize to range like "typical Cyc range in deepwater
      single-screw FSOs is 0.4 to 0.8"
```

**Verdict**: page lands in public with section A unchanged, section B
abstracted, section C sanitized to range.

**Commit message**: `abstraction: applied; sections B+C sanitized`

---

## Example 5: Industry-survey aggregation

**Source**: SINTEF 2019 mooring-failure survey + API RP 2SK + own analysis

**Proposed page**: `wikis/engineering/concepts/mooring-failure-empirical-rates.md`

**Walkthrough**:

```
Page references a client project name?
  → NO (SINTEF survey is anonymized at source; API is a standard)
→ Commit to public — no abstraction needed
```

**Commit message**: `abstraction: not-applicable-public-aggregation-only`

---

## Cheat sheet

| Symptom | Routing |
|---|---|
| Cites industry standards only | Public, no abstraction |
| Cites a client project by internal codename | Public requires abstraction (or exception with evidence) |
| Cites a client project by name + has matching public data | Exception applies; use name + cite public sources |
| Cites raw numerical results from client work | Either: sanitize to ranges; or move to private wiki |
| References client identity (operator company) | Check `.legal-deny-list.yaml` separately |
| Methodology with abstracted illustration | Public with abstracted illustration |
| Conference paper that names the project | Public with paper citation, name preserved |
| BSEE / BOEM / regulator records | Public, names preserved (regulator records are public-by-definition) |

---

## When the tree returns ambiguous

If the public-availability exception is on the edge:

1. **Abstract** by default (fail-safe).
2. File an audit per `research/llm-wiki-audit-feedback-loop` with the
   ambiguity recorded.
3. Defer to user.
4. If user approves the exception: update the page, log the decision,
   and add the project to a private `public-name-exception-approved.yaml`
   ledger for future passes.

The exception ledger lives in the private surface, not public. Pattern:

```yaml
# llm-wiki-<client>/data/public-name-exception-approved.yaml
exceptions:
  - project_name: <name>
    approved_at: YYYY-MM-DD
    approved_by: vamsee
    public_sources:
      - <source-1-citation>
      - <source-2-citation>
    rationale: |
      <why the exception applies>
```

Future passes check this ledger before re-asking the user.
