---
name: llm-wiki-public-private-routing
description: >-
  Firewall between the public llm-wiki repo (vamseeachanta/llm-wiki, MIT + CC-BY-4.0)
  and per-client private wikis (vamseeachanta/llm-wiki-<client>, e.g.
  llm-wiki-acma per #2746). Use when (1) deciding whether a converted wiki
  page lands in public or private surface, (2) applying the project-name
  abstraction rule to public-bound content, (3) evaluating the public-
  availability exception that lets actual project names pass through unmodified,
  (4) promoting content from private to public after sanitization. Encodes the
  2026-05-20 user routing directive verbatim: exact client results → private;
  abstracted (project-name only) → public; project name + all key data publicly
  available → exception applies. Companion to research/llm-wiki-page-shape-contract
  (which calls this skill at Rule 8) and research/llm-wiki-source-extraction-coverage
  (which produces the source pages this skill decides where to send).
metadata:
  category: research
  related_skills:
    - research/llm-wiki
    - research/llm-wiki-page-shape-contract
    - research/llm-wiki-source-extraction-coverage
    - coordination/client-llm-wiki-factory
  related_issues:
    - vamseeachanta/workspace-hub#2727
    - vamseeachanta/workspace-hub#2746
    - vamseeachanta/workspace-hub#2374
  related_rules:
    - .claude/rules/legal-compliance.md
    - .legal-deny-list.yaml
  references:
    - references/abstraction-decision-tree.md
---

# llm-wiki public/private routing

The firewall between client-attributed and abstracted content. Routes
converted wiki pages to the correct repository surface and enforces the
project-name abstraction rule with its public-availability exception.

This skill is invoked by `llm-wiki-page-shape-contract` Rule 8 before any
public-wiki commit. It is NOT optional — every page bound for public
`llm-wiki` clears this gate first.

---

## The two surfaces

| Surface | Purpose | License | Content posture |
|---|---|---|---|
| `vamseeachanta/llm-wiki` (public) | Trunk for code, client work, chatbots; improvable via public + legally-sanitized private sources | MIT (code) + CC-BY-4.0 (content) | Sanitized, abstracted, defensible-public |
| `vamseeachanta/llm-wiki-<client>` (private, per [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)) | Exact client + project + raw numbers retained for project work | proprietary | Full fidelity, no abstraction needed |

Both surfaces follow the same page-shape contract (Skill A). They differ
only in routing rules.

---

## The routing rule (verbatim from 2026-05-20 user directive)

> "Exact client results will go into llm-wiki-`<client>` private repo;
> project name, client name abstracted results will go into llm-wiki
> public repo."
>
> "Only client project names are to be abstracted. If project name is
> available public, can be used in the llm-wiki public repo provided all
> key data is publicly available."

### Decoded routing matrix

| Content type | Public llm-wiki | Private llm-wiki-`<client>` |
|---|---|---|
| Industry-standard reference (OCIMF MEG, DNV, API, ISO) | YES — cite section + edition | YES — same |
| Public methodology, generic algorithm | YES | YES — usually duplicative; prefer linking from private to public |
| Anonymized worked example | YES | YES |
| Client-attributed calc results (specific project, specific operator) | NO | YES |
| Project name (default) | abstracted (e.g., "Project Alpha") | actual name |
| Project name (public-availability exception applies) | actual name OK | actual name |
| Client name | governed by `.legal-deny-list.yaml` — typically abstracted to "the operator" / "the contractor" / unspecified | actual name |
| Raw numerical results (specific tensions, specific frequencies, specific dimensions) | sanitized to ranges or removed | actual values |
| Methodology + abstracted illustrative numbers (e.g., "typical deepwater mooring tensions cluster around 60–80% MBL") | YES | YES — link to private exact-value page |

---

## The abstraction surface (public-bound content)

**By default, abstract client project names** in public-wiki content.

Examples:
- `B1528 SIROCCO` → `Project Alpha` (or `a deepwater FSO project`)
- `acma-projects/<specific project>` → `a marine engineering project`
- specific platform name → generic platform-class descriptor

### What is NOT in the abstraction surface

- **Industry-standard names** (DNV-OS-E301, API RP 2SK, OCIMF MEG, ISO 19901): never abstracted
- **Standard editions / revisions**: never abstracted (defensibility requires explicit edition)
- **Public operators in public roles** (e.g., regulatory filing data — operator named in the filing): not abstracted per the exception below
- **Generic methodology**: no abstraction needed (no client tie)
- **Open-source code / library references**: not abstracted

### What IS in the abstraction surface

- **Client project names** (engineering project identifiers, internal codenames)
- **Project-specific numerical results** (only the specific values, not the methodology)
- **Project-specific dimensions / configurations** when they would identify the asset

Client *identity* (the operator company) is governed by
`.legal-deny-list.yaml` and `.claude/rules/legal-compliance.md` — this
skill does not relax those rules.

---

## The public-availability exception

A project name can be used **as-is** in public llm-wiki when **both** of
the following hold:

1. **Project name is in the public domain**, evidenced by at least one of:
   - SEC filing (10-K, 10-Q, 8-K, S-1) naming the project
   - Operator press release naming the project
   - Conference paper (OTC, SPE, OMAE, ISOPE) naming the project
   - Regulator record (BSEE, BOEM, NOPSEMA, PSA, NSTA) naming the project
   - Public reservoir / pipeline database entry (e.g., BSEE production records)
   - Project's own public-facing website

2. **All key data being cited is also publicly available**, evidenced by:
   - The data appears in the same public source as the project name, OR
   - The data appears in a separate public source (conference paper, regulator filing) that can be cited alongside
   - "Key data" means: any numerical result, dimensional spec, or
     operational parameter the wiki page presents as derived from the
     project

**Both conditions, or the project name gets abstracted.** Name-only
public availability without data backing fails the exception. Data-only
without project-name backing has nothing to exception away — abstract the
name as usual.

### Worked examples of the exception

| Scenario | Verdict |
|---|---|
| Project "Vito" named in Shell 2023 press release + OTC 2023 conference paper with field data → reference these to discuss tieback methodology | EXCEPTION APPLIES — use "Vito" as-is, cite both sources |
| Project named in Shell press release; numerical results from internal calc → derive methodology page | EXCEPTION DOES NOT APPLY — name in public, data is not → abstract the name |
| Internal client codename + conference paper with sanitized data from the same project | EXCEPTION DOES NOT APPLY — codename not in conference paper, abstract |
| OCIMF MEG3 sign-convention discussion, no project tie | NO ABSTRACTION NEEDED — pure methodology, no client surface |

---

## Pre-promotion decision tree

For each page bound for public llm-wiki:

```
page bound for public llm-wiki
  │
  ├── Page references a client project name?
  │     │
  │     ├── NO ──────────────────────────────► commit to public (no abstraction needed)
  │     │
  │     └── YES
  │           │
  │           ├── Is the project name publicly available?
  │           │     (SEC / press release / conference paper / regulator filing / public DB)
  │           │     │
  │           │     ├── NO ──────────────────► ABSTRACT project name → commit
  │           │     │
  │           │     └── YES
  │           │           │
  │           │           ├── Is ALL key data also publicly available?
  │           │           │     │
  │           │           │     ├── NO ──────► ABSTRACT project name → commit
  │           │           │     │
  │           │           │     └── YES ─────► EXCEPTION APPLIES → use actual name, cite public source(s)
  │
  └── Page also references client identity (operator, contractor)?
        │
        ├── Refer to `.legal-deny-list.yaml` and `.claude/rules/legal-compliance.md`
        └── Not governed by this skill
```

When in doubt: **abstract**. The exception is opt-in with evidence, not
opt-out.

---

## Pre-promotion checklist (public-bound page)

- [ ] Page references a client project name? (yes / no)
- [ ] If yes: is project name in public domain? (cite sources, otherwise abstract)
- [ ] If public domain: is all key data publicly available? (cite sources, otherwise abstract)
- [ ] If exception applies: public sources cited explicitly in the page's `## Sources` section
- [ ] No raw numerical results that would identify a specific asset (sanitize to ranges or remove)
- [ ] No filenames / paths referencing client-private directories (`acma-projects/`, `<client>-projects/`)
- [ ] Client identity (operator company) check passes `.legal-deny-list.yaml`
- [ ] `bash scripts/legal/legal-sanity-scan.sh --diff-only` returns PASS
- [ ] Page's commit message records abstraction verdict: `abstraction: applied | not-needed-exception-met | not-applicable-public-standard-only`

---

## Promotion from private to public

If a private-wiki page should also exist in public form:

1. **Copy, don't move** — the private page stays as the canonical
   client-attributed record
2. Create a new public page (different slug, abstracted content)
3. Run the full pre-promotion checklist
4. Cross-link: private page can wikilink to its public counterpart for
   "see also the abstracted version"; public page MUST NOT link back to
   the private page (the private repo is invisible to public readers)
5. Commit message on the public-wiki side: `abstraction: applied; source private llm-wiki-<client> page-id <id>` — the source reference stays in the commit message only, never in page body

### Anti-pattern: replace-with-abstraction

Do NOT delete the private page after promoting an abstracted copy. The
private page is the audit-trail; the public copy is the share-out.

---

## Anti-patterns

- **Name-substitution without data-substitution** — replacing "B1528 SIROCCO" with "Project Alpha" while keeping a specific tension envelope from B1528. The number identifies the asset.
- **"Public domain" by hand-wave** — "I think it's been mentioned somewhere" doesn't qualify. Cite the source.
- **Per-page abstraction without checklist** — judgment calls drift across pages. Use the decision tree.
- **Abstracted page in private wiki** — abstraction has no purpose in the private surface; just write the actual name. (Private→public copies are the exception.)
- **Exact-name page in public wiki without exception verification** — the abstraction gate must clear; either abstract or document the exception.
- **Promotion via `git mv`** — never. Copy the file with a new slug to public; private original stays.
- **Self-approving the exception** — when the exception is borderline, route through audit per Skill B and defer to user.

---

## Hand-off back to `research/llm-wiki-page-shape-contract`

Once routing is decided and the abstraction gate cleared:

```bash
# Public commit:
git -C /mnt/local-analysis/llm-wiki commit -m "wiki(<domain>): <slug> — <one-line>

abstraction: applied | not-needed-exception-met | not-applicable-public-standard-only

Refs: <upstream issue>
" -- wikis/<domain>/<page>.md wikis/<domain>/index.md wikis/<domain>/log/YYYYMMDD.md

# Private commit (per-client repo):
git -C /mnt/local-analysis/llm-wiki-<client> commit -m "wiki: <slug> — <one-line>

source: <upstream issue> | <upstream artifact path>
" -- wikis/<domain>/<page>.md wikis/<domain>/index.md wikis/<domain>/log/YYYYMMDD.md
```

Pathspec form per `feedback_multi_agent_commit_serialization`.

---

## What this skill is NOT

- Not a replacement for `.legal-deny-list.yaml` — that enforces client
  identity rules; this skill adds the project-name layer above
- Not a replacement for `coordination/client-llm-wiki-factory` — that
  skill creates the private-wiki repo infrastructure; this skill governs
  routing decisions within the infrastructure
- Not a replacement for the data-layer boundary ([#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727)) — that defines what content is wiki-eligible at all; this skill decides which wiki
- Not for `.gitignore` / `.git` firewall mechanics — those are repo
  configuration, governed by `feedback_per_repo_metadata_is_firewall`

## Related must-fire rules

- `feedback_service_provider_data_routing` — 6-row matrix; vendor brochures → off-repo; SEC / conference / regulator → public
- `feedback_per_repo_metadata_is_firewall` — license + .gitignore + per-repo .claude + .git are the file-system firewall
- `feedback_credential_issuer_copy_paste_leak` — never commit raw "save this token" output; same hygiene applies to client identifiers
- `feedback_external_permission_email_hygiene` — when a rights-holder approval email is supplied, record the minimum permission/citation conclusion needed for traceability; do not persist personal contact details, and do not inflate “citation looks appropriate” into unlimited bulk-copy permission
- `feedback_never_offer_to_self_label_plan_approved` — borderline exception cases route through user, not self-approval
- `feedback_offrepo_intel_routing` — for published repos, side-channel notes go to `/mnt/ace/<repo-name>/docs/`, not in-repo
