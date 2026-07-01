---
name: ecosystem-data-sources
description: "Proactively surface what DATA the ecosystem already has for an engineering domain — before starting analysis, points to the consolidated data-source catalog, any latent ACE_SHARE project precedent, and the domain-database issue that curates it. Use when work touches an engineering domain (riser, mooring, pipeline, structural/FFS, naval-arch/hydro, metocean, materials, production, geotech, drilling, CAD/sim, or financial/asset), when someone asks 'do we have data for X', 'where do we get X data', 'build the X database', or before implementing a calculation that needs reference data."
version: 1.0.0
category: data
related_skills:
- research-literature
- worldenergydata-source-readiness
triggers:
- do we have data for
- where do we get data
- what data do we have
- build the database
- establish the database
- data sources for
- riser data
- mooring data
- metocean data
- reference data for
type: reference
freedom: high
---

# Ecosystem Data Sources — proactive surfacing

## Why this exists

Data discovery used to be tribal: each repo knew its own sources, and the **7.3 TB of latent
past-project data** in `ACE_SHARE_ROOT` was invisible unless the owner pointed at it. This skill
makes a session **proactively answer** — *before* re-deriving anything — "we already have data X
for this domain; here's the catalog, the latent precedent, and the issue that curates it."

**Fire this skill early** when work enters an engineering domain, or when anyone asks where data
comes from / to build a domain database. Don't wait to be asked twice.

## What to do

1. **Identify the domain** of the current work (riser, mooring, pipeline-subsea, structural-ffs,
   naval-arch-hydro, metocean, materials-standards, production-reservoir, geotech, asset-financial,
   drilling-well, cad-simulation).
2. **Consult the canonical catalog** (source of truth — read these if available):
   - `llm-wiki/data/data-source-catalog.yml` — 25 sources, tagged route/relevance/lane/fed-calcs
   - `llm-wiki/data/domain-database-index.yml` — domain → tables → seed sources → the `digitalmodel` calcs each feeds
   - `llm-wiki/site_assets/data-sources.html` — human quick-reference (flywheel, coverage matrix, gaps)
   - `llm-wiki/docs/data-sources/README.md` + `provider-routing-guide.md`
3. **Surface, proactively**: (a) the online/public sources for the domain, (b) whether **latent
   `ACE_SHARE` precedent** exists (register as metadata only — see governance), (c) the standards
   that feed it, and (d) the **"Establish the `<domain>` database" issue** so the work connects to
   the flywheel instead of a one-off.
4. **Route the work** using the provider-routing guide (`lane:claude` reasoning/de-id, `lane:codex`
   bulk/review, `lane:frontier-pending` = T3, reserved for frontier models).

## Quick lookup — read from the source of truth (do NOT hardcode issue numbers here)

Epic: **llm-wiki #799**. The authoritative per-domain map lives in
`llm-wiki/data/domain-database-index.yml` — each domain entry carries its
`issue`, `tables`, `seed_sources`, and `feeds_calcs`. **Read that file** to get the
current "Establish the `<domain>` database" issue and its sources; do not rely on a
stale copy pasted here.

Domains covered: riser, mooring, pipeline-subsea, structural-ffs, naval-arch-hydro,
metocean, materials-standards, production-reservoir, geotech, asset-financial,
drilling-well, cad-simulation. Latent `ACE_SHARE` precedent is strongest for riser,
naval-arch-hydro, and cad-simulation (registered metadata-only). Completeness
follow-ups are the `C*` issues under the epic.

> Implementation note (#801): this section and the hook's keyword→pointer map are
> **generated from `domain-database-index.yml`** by `scripts/data-sources/gen_domain_pointers.py`
> so they never drift. No hand-maintained issue numbers.

## Governance (never violate)

- `ACE_SHARE_ROOT` holds **client data** — never reproduce raw content or client names in any repo;
  surface it as **metadata only** ("we have ~N past-project X analyses"). Bounded reads only
  (`ls`/`find -maxdepth N` + `timeout`); never an unbounded share crawl.
- De-identification and public/private routing **stay on `lane:claude`** — never delegate them.
- `llm-wiki` is private/re-publishable; the public tier is `worldenergydata-wiki` + tier-1 repos.

## Related

- `research-literature` — deeper standards/literature briefs for a calculation.
- `worldenergydata-source-readiness` — freshness/completeness of the live energy feeds.
- Full flywheel context: `llm-wiki/docs/data-sources/README.md`.
