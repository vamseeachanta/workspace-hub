# Disagreement report — plan #2216 (2026-04-23)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MAJOR |
| codex | UNAVAILABLE (codex CLI failed, rc=2: error: unexpected argument '--no-interactive' found    tip: to pass '--no-interactive' as a value, use '-- --no-interactive'  Usage: codex exec [OPTIONS] [PROMPT]        codex exec [OPTIONS] <COMMAND>) |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **Plan §"Existing repo code / artifacts" row 1 (line 18) and §Gaps #1 (line 61) both state `/mnt/ace/acma-codes` is "NOT registered" in `mounted-source-registry.yaml`.** This is false at HEAD. Lines 181–189 of the registry already contain `source_id: acma_codes_local`, `mount_root: /mnt/ace/acma-codes`, `document_intelligence_bucket: acma_codes`, and a `dedup_rule: prefer /mnt/ace/0000 O&G for overlapping content (API duplicates); acma-codes`. The gap the plan is built to close does not exist.
- **Plan §"Standards / registries consulted" rows 3–6 (lines 32–35) and §Gaps #2–#3 (lines 62–63) state OCIMF Mooring Equipment Guidelines, OCIMF Tandem Mooring, CSA Z276.1-20, and CSA Z276.18 are "NOT in transfer ledger".** All four are present: `OCIMF-MEG-3RD-ED-2008` at ledger line 7525, `OCIMF-TANDEM-MOORING` at line 7580, `CSA-Z276.1-20` at line 7600, `CSA-Z276.18` at line 7635. Ledger entry at line 7538–7540 reads "Backfilled from acma_codes" — self-documenting evidence the ledger backfill this plan proposes has already executed.
- **Plan §"Gaps identified" #6 (line 66) claims "No doc_key hashing — acma-codes files have never been hashed".** `data/document-index/index.jsonl` contains 2521 records matching `acma_codes` (grep count). Indexing already occurred. Plan §Pseudocode step 2 (lines 137–142) and §Files-to-change "Run `phase-a-index.py`" (line 196) are re-executing completed work.
- **Plan §"Files to Change" lines 202–203 propose creating `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1.md` and `csa-z276-18.md`, and §TDD row `verify_wiki_csa` (line 223) tests files at this path.** The path `knowledge/wikis/marine-engineering/wiki/standards/` does not exist in the tree. The parent wiki has `comparisons/`, `concepts/`, `entities/`, `sources/` but no `standards/` subdir. Acceptance criteria will fail by path-not-found.
- **Plan §"Wiki promotion" pseudocode (lines 177–182) and §"Files to Change" lines 202–203 pre-commit CSA Z276 wiki files to `knowledge/wikis/marine-engineering/wiki/standards/` before #2471 resolves.** Issue #2471 is currently OPEN: "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract". The plan is dictating an outcome to a decision that hasn't happened, violating the sanction-pending gate. Per memory record `project_issue_2460_approval_binding` and the broader "sanctioned routing" pattern, this is a binding collision, not a minor naming choice.
- **Plan §"Recommended Follow-On Issue Split" (lines 289–300) proposes 4 new follow-ons whose scopes match issues already CLOSED.** Follow-on #1 ≡ #2225 "register /mnt/ace/acma-codes as mounted source and run initial indexing/dedup" (CLOSED). Follow-on #2 ≡ #2226 "backfill OCIMF/CSA ledger entries and provenance aliases" (CLOSED). Follow-on #4 ≡ #2228 "update accessibility and entry-point surfaces" (CLOSED). Only Follow-on #3 has a still-open analogue (#2227, `status:plan-review`). Approving this plan would authorize creating duplicates of three closed issues.
- **Plan §"Adversarial Review Summary" (lines 242–260) acknowledges MAJOR verdicts from Codex and Gemini on 2026-04-14 citing "stale/false state assumptions" and lists 5 required revisions (lines 254–259), but none of those revisions have been applied to the plan body.** The Resource Intelligence table, Gaps list, Pseudocode, Files-to-change, TDD table, Acceptance Criteria, and Follow-on Split all still reflect the pre-rewrite state. The plan is internally contradictory: the summary says the scope must be recomputed from live state, then the body assumes a world where nothing has been done.
- **Plan §"Acceptance Criteria" line 229 (`/mnt/ace/acma-codes` is registered) and line 232 (OCIMF+CSA added to ledger) are already satisfied.** This makes approval circular — the plan claims work remaining that live registries show as complete. Criteria line 237 ("No regression in existing registries") is the only criterion that disciplines the plan, and it is untestable without a diff baseline the plan does not specify.
- **Plan §Real Inventory table (line 81) lists CSA contents as only `276.1-20` and `Z276.18`.** Ledger shows additional CSA entries sourced from the same path: `CSA-Z276.2-19 Near-Shoreline FLNG Facilities` (line 7618), `CSA-B625-13 Portable Tanks` (line 7652), `CSA-22.1-12 Canadian Electrical Code` (line 7671). The plan's inventory disclaimer (line 75) calls this out as a "known limitation" but the breadth triage issue `#2244` is CLOSED, meaning the real inventory is already resolved — yet the plan's inventory and T2 sizing are built on the pre-triage guess.
- **Plan §Artifact Map (line 110) and header §Review artifacts (line 7) cite `scripts/review/results/2026-04-11-plan-2216-final.md` as a "Plan review — Final synthesis" artifact.** A 2026-04-14 MAJOR review and a 2026-04-23 Claude run with a `.err` sidecar exist downstream of that "final" synthesis. Calling the 2026-04-11 artifact "final" while a 2026-04-23 review run has errored is misleading; the plan header's review-artifact list is stale.
- **Plan §"Pseudocode / Integration Logic Sketch" step 4 (line 164) proposes adding `OCIMF-MEG-2008` to the ledger, but ledger line 7525 uses id `OCIMF-MEG-3RD-ED-2008`.** If approved and executed naively, this creates a duplicate ledger entry under a different id. Plan does not reconcile the existing id.
- **Plan §T2 complexity rationale (line 306) reads "involves multiple registries and a dedup pass".** Both registry updates and the dedup pass are complete at HEAD (findings 1, 2, 3). The bounded remaining scope is wiki promotion for OCIMF Tandem + CSA Z276 (gated by #2471) plus any residual accessibility map work. T2 is not justified against the true remainder.

### codex

- (none)

### gemini

- Plan section "Existing repo code / artifacts relevant to this source collection" references `data/document-index/mounted-source-registry.yaml` — no such file or `data` directory exists at HEAD.
- Plan section "Existing repo code / artifacts relevant to this source collection" references `data/document-index/standards-transfer-ledger.yaml` — no such file exists at HEAD.
- Plan section "Existing repo code / artifacts relevant to this source collection" references `data/design-codes/code-registry.yaml` — no such file exists at HEAD.
- Plan section "Existing repo code / artifacts relevant to this source collection" references `scripts/data/document-index/phase-a-index.py` — no such file or `scripts` directory exists at HEAD.
- Plan section "LLM Wiki pages consulted" references `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — no such file or `knowledge` directory exists at HEAD.
- Plan section "Documents consulted" references `docs/document-intelligence/intelligence-accessibility-map.md` — no such file or `docs` directory exists at HEAD.
- Plan section "Pseudocode / Integration Logic Sketch" instructs to "Add source_id 'acma_codes_local' to mounted-source-registry.yaml", and "Acceptance Criteria" requires "`/mnt/ace/acma-codes` is registered as a mounted source". This directly contradicts the plan's own "Adversarial Review Summary" section, which states that source registration is already complete and requires the author to "Remove already-completed registration / ledger-population work from the umbrella scope." The plan has not been updated to reflect its own review mandate.
- Plan section "Recommended Follow-On Issue Split" proposes creating an issue to "Register `/mnt/ace/acma-codes` as mounted source", violating the explicit requirement in "Adversarial Review Summary" to remove this already-completed work from the scope.

