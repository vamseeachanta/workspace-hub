# Codes and standards data routing — agent rule

**When ingesting any code, standard, or vendor-licensed specification (OCIMF, API, DNV, ABS, IACS UR, ASCE, ASME, ISO, BS EN, SOLAS, MARPOL, MODU, USCG NVIC, IMO MSC, etc.) and its derived data (coefficient tables, figures, clauses, formulas, worked examples), route to the private `vamseeachanta/llm-wiki` repo.**

**Why:** OCIMF/API/DNV/ABS/IACS/ASCE/ASME etc. are sold by their publishers (or their distributors — Witherby, Techstreet, IHS Markit). They are widely treated as "public knowledge" in engineering practice but are not freely redistributable. The 2026-05-20 policy decision flipped `llm-wiki` from public to private specifically to close the licensing window so codes-and-standards data can live in the wiki ecosystem without per-page metadata-only friction.

**How to apply:**

1. **Repo target = private `vamseeachanta/llm-wiki`** for any code/standard data ingest. Confirm visibility with `gh repo view vamseeachanta/llm-wiki --json visibility` returns `PRIVATE` before committing standards-derived content.

2. **Frontmatter does NOT carry the legacy public-era boundary fields**:
   - Drop `extraction_policy: metadata-only` — no longer applicable.
   - Drop `raw_copy_allowed: false` — no longer applicable.
   - DO add `visibility: private-llm-wiki` so the page declares its hosting tier explicitly. Forward-compatible if some pages later move back to public.
   - DO add a `sources:` field pointing to the off-repo PDF at `/mnt/ace/acma-codes/<code>/` for provenance traceability.

3. **Body content is unrestricted within copyright fair use**:
   - Verbatim convention/clause text quoted with attribution — fine.
   - Digitized coefficient tables (re-emitted as CSV under `wikis/<domain>/wiki/datasets/<standard>/`) — fine.
   - Figure captions and per-figure descriptions — fine.
   - **Do NOT** commit the raw vendor PDF itself to the repo, even though the repo is private. Keep the canonical PDF at `/mnt/ace/acma-codes/<code>/` so the off-repo path remains the single source of truth for the published artifact. The wiki holds the digitized derivation; `/mnt/ace/` holds the source.

4. **Calc-citation contract** ([`.claude/rules/calc-citation-contract.md`](calc-citation-contract.md)) is unchanged. Citation modules in public repos (e.g., MIT-licensed `digitalmodel`) still bind to wiki slugs; the resolver fails closed for unauthenticated external users since the wiki is now private. This is by design — `pip install digitalmodel` users see `CitationResolutionError` and must configure `LLM_WIKI_PATH` to a local clone they have authorized access to.

5. **Cross-repo references**: public `workspace-hub` and `digitalmodel` may reference llm-wiki paths in plans, handoffs, issue comments, and citation modules. Those URLs will 404 for external readers. Use the literal path form (`wikis/<domain>/...`) rather than https://github.com/vamseeachanta/llm-wiki/blob/... URLs to keep the prose useful to authorized readers without misleading external ones.

6. **For codes/standards that ARE genuinely public-domain or open-license** (e.g., US federal regulations 33 CFR / 46 CFR, NOAA datasets, USCG NVIC pre-2010 issues, IMO MSC circulars after public release, IEC publications past expiry, NIST publications, ASTM withdrawn-and-republished): route to a **public sibling wiki**. As of 2026-05-20 the public sibling for US federal public-domain energy data (BSEE / NOAA / USGS / MMS) is [`vamseeachanta/worldenergydata-wiki`](https://github.com/vamseeachanta/worldenergydata-wiki) (CC-BY-4.0 + MIT). Per-page frontmatter: `visibility: public-federal-data`, `license: public-domain`, `source_authority: <agency>`, `contribution_status: us_federal_only | mixed_private_contributors`, `last_license_check: YYYY-MM-DD`. Cross-wiki linking discipline: public→private uses prose-only references (no Markdown links — they'd 404 for external readers); private→public uses full URLs. Decision rationale: [`docs/governance/2026-05-20-public-data-corpus-routing-decision.md`](../../docs/governance/2026-05-20-public-data-corpus-routing-decision.md). Confirm public-domain status before routing — when in doubt, route private.

**Do NOT apply when:**
- The data is methodology / convention / interpretive content not directly reproducing standard text. Default landing is the private llm-wiki under `methodology/`; if a public sibling wiki exists for that domain (e.g., `worldenergydata-wiki` per §6), interpretive content derived ONLY from public-domain substrate may route there instead.
- The data is generated synthetically (test fixtures, sample VLCCs, generated CSVs from `create_sample_database()`). Synthetic data is not derivative; can sit in public repos.
- The data is the user's own original work (in-house digitization methodology, validation analysis, comparison studies). Original analysis carries the user's own copyright; routing is a strategy choice not a licensing constraint.

**Pilot reference:** OCIMF MEG3/MEG4 Annex A landed 2026-05-20 under `wikis/marine-engineering/wiki/datasets/ocimf-meg4-annex-a/` with the verbatim §A1/§A2 convention text in [[marine-engineering/standards/ocimf-meg3]] and [[marine-engineering/standards/ocimf-meg4]]. Commit reference: llm-wiki main HEAD after 2026-05-20 21:30 CT.

**Related:**
- `feedback_offrepo_intel_routing` — superseded for codes-and-standards specifically (off-repo `/mnt/ace/` still holds the PDFs; derived data now in private wiki instead of off-repo only)
- `service_provider_data_routing` — superseded for codes-and-standards row; vendor brochures still off-repo
- `project_llm_wiki_spunout` — superseded as of 2026-05-20; llm-wiki is private again
- [`.claude/rules/calc-citation-contract.md`](calc-citation-contract.md) — unchanged; resolver behavior implications noted in §4 above
