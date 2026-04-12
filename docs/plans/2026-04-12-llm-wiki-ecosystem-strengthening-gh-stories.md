# LLM-wiki ecosystem strengthening — GH stories for review/approval

Date: 2026-04-12
Repo: `vamseeachanta/workspace-hub`
Context basis:
- Parent operating model `#2205`
- Accessibility map `#2096`
- Entry-point implementation `#2104` (closed)
- Accessibility registry `#2136` (closed)
- Retrieval contract `#2208` (closed)
- ACMA umbrella `#2216` (open, plan-approved)
- ACMA source registration `#2225` (closed)
- ACMA ledger/provenance backfill `#2226` (closed)

## Current grounded review

Completed already:
1. `#2104` landed the intelligence entry-point surfaces.
2. `#2136` landed `data/document-index/intelligence-accessibility-registry.yaml`.
3. `#2208` landed the issue-workflow retrieval contract and tightened plan docs.
4. `#2225` registered `/mnt/ace/acma-codes` as `acma_codes_local`.
5. `#2226` backfilled ledger/provenance for OCIMF and CSA entries.

Still missing in repo state:
1. No promoted wiki pages yet for:
   - OCIMF Tandem Mooring
   - CSA Z276.1-20
   - CSA Z276.18
2. `knowledge/wikis/.../index.md` and `log.md` do not yet reflect those sources.
3. `docs/document-intelligence/intelligence-accessibility-map.md` contains stale pre-landing claims, including statements that are no longer true after `#2104` / `#2136` / README updates.
4. Parent `#2216` remains open because the durable-knowledge and accessibility layers are not fully updated yet.

Important scope note:
- `#2226` discovered additional standards beyond the original parent description:
  - `CSA-Z276.2-19`
  - `CSA-B625-13`
  - `CSA-C22.1-12`
  - additional API RP 2SK 3rd-ed / addendum coverage
- These should NOT be silently absorbed into the currently intended wiki/accessibility wave without explicit approval.

## Story A — approve existing #2227 for direct execution

Issue: `#2227`
Title: `feat(acma-codes): promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis`

Why approve now:
- It is the main missing L3 durable-knowledge step under approved umbrella `#2216`.
- The required L2 provenance surfaces already exist from `#2226`.
- The promotion targets are clearly bounded and high-value for future engineering retrieval.

Recommended approved scope:
- Create:
  - `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md`
  - `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1.md`
  - `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-18.md`
- Update:
  - `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md`
  - relevant `wiki/index.md` and `wiki/log.md` files
- Require provenance back-links grounded in ledger entries from `#2226`
- Explicitly defer:
  - `CSA-Z276.2-19`
  - `CSA-B625-13`
  - `CSA-C22.1-12`
  - broader API-family promotion

Approval checklist:
- [ ] approve current bounded scope only
- [ ] require no silent expansion to newly discovered CSA/API items
- [ ] require provenance-first wiki updates

## Story B — approve existing #2228 for direct execution

Issue: `#2228`
Title: `chore(acma-codes): update accessibility and entry-point surfaces after source integration`

Why approve now:
- The entry-point and registry layers already landed, but the accessibility map still reflects stale pre-landing assumptions.
- Without this update, issue workflows may still read obsolete guidance about discoverability.

Recommended approved scope:
- Refresh `docs/document-intelligence/intelligence-accessibility-map.md` to reflect current repo reality:
  - `docs/README.md` now includes knowledge/intelligence links
  - `docs/document-intelligence/README.md` exists
  - accessibility registry exists
  - ACMA source registration + ledger backfill have landed
  - new wiki pages should be referenced if Story A is also executed
- Keep changes minimal and inventory-focused
- Only touch `docs/document-intelligence/README.md` if a small ACMA-source mention is clearly warranted
- Do not redesign architecture, registry schema, or workflow policy

Approval checklist:
- [ ] approve minimal reality-sync only
- [ ] keep scope constrained to accessibility/navigation surfaces
- [ ] no architecture or schema redesign

## Story C — recommended NEW follow-on issue for explicit user decision

Suggested title:
`feat(acma-codes): triage newly discovered CSA/API breadth beyond approved wiki-promotion scope`

Why this should be separate:
- `#2226` uncovered materially more standards than the parent plan originally named.
- These include both marine-relevant and out-of-domain documents.
- Absorbing them now would violate scope discipline.

Suggested scope:
- classify newly discovered items into:
  - promote to LLM-wiki now
  - retain in ledger only
  - route to repo-specific downstream work
  - ignore/archive
- at minimum review:
  - `CSA-Z276.2-19`
  - `CSA-B625-13`
  - `CSA-C22.1-12`
  - API RP 2SK 3rd edition + addendum
  - remaining API-family documents found in acma-codes
- decide whether any belong in:
  - marine-engineering wiki
  - engineering wiki
  - digitalmodel follow-on issue
  - no wiki promotion

Why this matters to the repo ecosystem:
- It is the bridge between raw source acquisition and disciplined multi-repo knowledge curation.
- It prevents workspace-hub from becoming a dumping ground while still making net-new standards visible.

## Story D — optional NEW cross-repo ecosystem story

Suggested title:
`feat(knowledge): add explicit repo-target mapping from standards ledger entries to downstream ecosystem repos`

Why this may be worth approval later:
- The current intelligence stack is strong inside workspace-hub, but repo-target implications remain implicit.
- For example, future work may need clearer routing from standards/knowledge assets into:
  - `digitalmodel`
  - `worldenergydata`
  - `assetutilities`
  - selected client/project repos

Suggested scope:
- define a small, explicit routing convention from L2/L3 intelligence assets to downstream repo candidates
- do not implement solver code; only improve discoverability and routing metadata
- ensure this complements, not duplicates, the accessibility registry and retrieval contract

## Recommended user approval order

1. Approve `#2227`
2. Approve `#2228`
3. Decide whether to create/approve Story C as a new issue
4. Treat Story D as optional, only if you want explicit multi-repo routing metadata next

## Recommended Claude execution mode after approval

Use the saved prompt:
- `docs/plans/2026-04-12-claude-agent-team-prompt-2216-remaining-llm-wiki-ecosystem-wave.md`

That prompt is designed to:
- verify live approval state first
- consume the landed intelligence architecture and registry surfaces
- execute only approved work
- avoid scope creep into the newly discovered CSA/API breadth
