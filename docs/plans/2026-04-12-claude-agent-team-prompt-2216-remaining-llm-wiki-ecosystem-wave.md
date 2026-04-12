# Claude agent-team prompt: #2216 remaining LLM-wiki ecosystem strengthening wave

Use this prompt as a single self-contained handoff to Claude Code for the remaining ACMA/LLM-wiki ecosystem work.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Knowledge/Docs Implementer
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Primary objective:
Complete the remaining repo-ecosystem strengthening work under umbrella issue `#2216` by grounding all changes in the already-landed intelligence architecture, the available resource/document intelligence, and the current multi-repo ecosystem context.

Live issue state to honor:
- `#2216` https://github.com/vamseeachanta/workspace-hub/issues/2216
  - state: OPEN
  - label: `status:plan-approved`
  - role: approved umbrella issue for ACMA-codes integration
- `#2225` source registration + indexing: CLOSED
- `#2226` ledger/provenance backfill: CLOSED
- `#2227` wiki promotion: OPEN
- `#2228` accessibility / entry-point updates: OPEN

Execution gate discipline:
- `#2216` is approved.
- `#2227` and `#2228` may or may not have explicit plan-approved markers when you start.
- Before any write, verify live GitHub labels and any local approval markers for `#2227` / `#2228`.
- If both are explicitly approved, implement and close them.
- If either is not approved, do NOT implement that issue blindly. Instead:
  - create or refresh a concise execution dossier/comment for the blocked issue,
  - report exactly what approval is missing,
  - still complete any read-only verification and umbrella synthesis under `#2216`.
- Never violate the repo hard gate: issue -> plan -> user approves -> implement.

Authoritative architecture and workflow artifacts to consume, not redefine:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (`#2205`)
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` (`#2207`)
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` (`#2209`)
- `docs/document-intelligence/intelligence-accessibility-map.md` (`#2096`)
- `docs/document-intelligence/README.md` (`#2104` implementation surface)
- `data/document-index/intelligence-accessibility-registry.yaml` (`#2136` implementation surface)
- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md`
- `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md`
- `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md`
- `docs/plans/README.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md`

Current grounded state already landed in repo (verify before writing):
- `data/document-index/mounted-source-registry.yaml` contains `acma_codes_local`.
- `data/document-index/standards-transfer-ledger.yaml` already contains OCIMF + CSA entries from `#2226`, including:
  - `OCIMF-MEG-3RD-ED-2008`
  - `OCIMF-MEG4-2018`
  - `OCIMF-TANDEM-MOORING`
  - `CSA-Z276.1-20`
  - `CSA-Z276.2-19`
  - `CSA-Z276.18`
  - plus additional discovered CSA/API entries.
- `docs/README.md`, `docs/document-intelligence/README.md`, and `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` already expose the intelligence ecosystem at a high level.
- No wiki pages currently exist for OCIMF Tandem Mooring or CSA Z276 pages in `knowledge/wikis/`.
- `docs/document-intelligence/intelligence-accessibility-map.md` still contains stale statements written before #2104/#2136/#2225/#2226 landed, so it needs a careful reality refresh rather than a blind append.

Cross-repo / ecosystem context you must account for:
- Workspace-hub is the control plane for 25 managed repositories.
- Core engineering repos explicitly called out in `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` and `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` include:
  - `digitalmodel`
  - `worldenergydata`
  - `assetutilities`
  - `assethold`
- This wave remains workspace-hub-first. Do NOT edit those repos unless a path is explicitly owned below.
- You must still read the ecosystem docs so the final wiki and accessibility surfaces reflect the repo ecosystem honestly, not just a local folder drop.

Critical safety constraints:
- The repo has unrelated dirty/untracked files.
- Do NOT touch unrelated files.
- Stage and commit ONLY the files explicitly owned by this wave.
- Never use `git add .` or broad globs.
- If you detect unavoidable conflict with unrelated dirty files, stop and report clearly.

Owned implementation paths for the remaining wave:
- `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md`
- `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md`
- `knowledge/wikis/engineering/wiki/index.md`
- `knowledge/wikis/engineering/wiki/log.md`
- `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1.md`
- `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-18.md`
- `knowledge/wikis/marine-engineering/wiki/index.md`
- `knowledge/wikis/marine-engineering/wiki/log.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`

Conditionally owned path only if a minimal reality-sync is clearly required by your findings:
- `docs/document-intelligence/README.md`

Read-only context paths:
- `data/document-index/standards-transfer-ledger.yaml`
- `data/document-index/mounted-source-registry.yaml`
- `data/document-index/intelligence-accessibility-registry.yaml`
- `docs/README.md`
- `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- `knowledge/wikis/**/CLAUDE.md`
- all plan/review artifacts for `#2216`, `#2225`, `#2226`

Forbidden paths:
- `scripts/**`
- `tests/**`
- `config/**`
- `.claude/**`
- `.codex/**`
- `.gemini/**`
- `digitalmodel/**`
- `worldenergydata/**`
- `assetutilities/**`
- `assethold/**`
- any unrelated dirty/untracked file outside the owned paths above

Success condition:
Finish the remaining approved `#2216` deliverables without scope drift, using the already-landed intelligence architecture and registry evidence rather than reparsing blindly or inventing new contracts.

Required work sequence:
1. Preflight / authorization check
   - verify live state of `#2216`, `#2227`, `#2228`
   - verify whether plan approval exists for `#2227` / `#2228`
   - verify current file existence for the owned wiki/docs paths
2. Read and synthesize current evidence
   - confirm what `#2225` and `#2226` already completed
   - read ledger entries for OCIMF / CSA promotion targets
   - read current `ocimf-meg4.md`
   - inspect current engineering and marine-engineering wiki indexes/logs
   - inspect current accessibility map sections that are now stale because #2104/#2136/README updates have already landed
3. If `#2227` is approved, implement wiki promotion
   - create `ocimf-tandem-mooring.md`
   - create `csa-z276-1.md`
   - create `csa-z276-18.md`
   - update `ocimf-meg4.md` with tightly scoped historical/provenance context grounded by ledger evidence only
   - include provenance back-links in frontmatter/body consistent with `#2207`
   - update affected wiki indexes and logs
   - do NOT silently expand scope to CSA Z276.2-19, CSA B625-13, CSA C22.1, or the wider API set; capture those as follow-up recommendations unless approval explicitly includes them
4. If `#2228` is approved, implement accessibility/entry-point refresh
   - update `intelligence-accessibility-map.md` so it reflects current reality after #2104, #2136, #2225, and #2226
   - remove or revise stale claims such as "docs/README has no intelligence links" and "docs/document-intelligence/README does not exist"
   - add only the minimal ACMA-specific accessibility consequences needed after source registration and wiki promotion
   - keep the document as an inventory/gap-analysis artifact; do not redesign parent architecture or registry schema
   - touch `docs/document-intelligence/README.md` only if a small, concrete ACMA-source mention is needed and clearly justified
5. Adversarial review inside the same run
   - verify scope discipline against `#2205`, `#2207`, `#2208`, `#2209`, `#2096`, `#2104`, `#2136`
   - verify no unapproved expansion beyond the approved promotion targets
   - verify provenance claims do not outrank ledger evidence
6. Git / GitHub closeout
   - stage only owned files
   - commit only if actual approved implementation work was performed
   - post comments to the relevant issues (`#2227`, `#2228`, `#2216`)
   - close `#2227` / `#2228` only if their scoped work is complete and verified
   - update `#2216` with umbrella completion status and remaining follow-ons

Detailed implementation expectations for wiki pages:
- Each new page must clearly state what the standard/guideline covers.
- Use ledger-grounded provenance, including the standard ID and source path(s).
- Cross-link to existing mooring / marine wiki pages where relevant.
- Distinguish editions carefully:
  - MEG 3rd Ed (2008)
  - MEG4 (2018)
  - Tandem Mooring guideline
- Avoid claiming implementation in `digitalmodel` or other repos unless explicitly evidenced.

Detailed implementation expectations for accessibility-map refresh:
- Update only the sections made stale by already-landed work.
- Preserve the document's role as a map/gap analysis.
- Add ACMA-specific discoverability notes only where they materially improve future retrieval.
- Reflect that the intelligence ecosystem now has:
  - docs landing page
  - document-intelligence landing page
  - accessibility registry
  - registered mounted source
  - ledger-backed OCIMF/CSA source coverage
  - promoted wiki pages if this run completes #2227

Explicit follow-up capture expectations:
If you confirm additional valuable but out-of-scope material, call it out in GitHub comments rather than absorbing it silently. Examples:
- `CSA-Z276.2-19` promotion decision
- `CSA-B625-13` / `CSA-C22.1-12` treatment
- broader API-family backfill from acma-codes
- reverse backlink automation from ledger to wiki pages

Required verification before commit:
- confirm live approval status for each implemented issue
- confirm no forbidden paths were modified
- confirm new wiki pages exist and are linked from relevant indexes
- confirm all new/updated wiki pages include provenance back-links consistent with `#2207`
- confirm accessibility-map statements match current repo reality
- confirm the resulting docs are consistent with `docs/README.md`, `docs/document-intelligence/README.md`, and `data/document-index/intelligence-accessibility-registry.yaml`
- confirm no unsupported claims were added about other repos or standards coverage

Git discipline:
- Stage only explicit owned files by path.
- Use narrow commits.
- Suggested commit split if both issues are implemented:
  - `docs(knowledge): promote OCIMF tandem mooring and CSA Z276 wiki coverage (#2227)`
  - `docs(intelligence): refresh accessibility map after ACMA source integration (#2228)`
- Push to `origin main` only after verification.

GitHub closeout expectations:
- For `#2227`, comment with:
  - files changed
  - exact wiki pages created/updated
  - provenance sources consumed
  - any intentionally deferred promotion candidates
- For `#2228`, comment with:
  - stale assertions corrected
  - entry-point/accessibility surfaces touched
  - how the update stays consistent with `#2104` and `#2136`
- For `#2216`, comment with:
  - what from the umbrella plan is now complete
  - which child issues were closed in this run
  - any remaining future issues recommended

Final return format in the Claude session:
1. Approval state detected for `#2227` and `#2228`
2. What changed
3. Verification performed
4. Exact files committed
5. GitHub comment URLs
6. Which issues were closed
7. Remaining follow-ups / residual risks
