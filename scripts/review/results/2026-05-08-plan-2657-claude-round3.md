## Verdict
MAJOR

## Retrieval

- Read `docs/plans/2026-05-08-issue-2657-hermes-llm-wiki-spinout-path-drift.md` (full file, 349 lines).
- `ls`/stat checked all 23 file paths cited by the plan: 20 EXISTS as claimed; 3 focal `knowledge/wikis/*` paths MISSING as claimed.
- `wc -l` on review artifacts: `2026-05-08-plan-2657-claude.md` = **0 lines**, `claude.md.err` = **0 lines**, `codex.md` = 11 lines (UNAVAILABLE stub), `gemini.md` = 11 lines (UNAVAILABLE stub), `disagreement.md` = 35 lines.
- Read `scripts/review/results/2026-05-08-plan-2657-codex.md`, `gemini.md`, `disagreement.md` end-to-end.
- Read `scripts/analysis/provider_session_ecosystem_audit.py:140-160` to verify the rule definition at line 144.
- Read `tests/analysis/test_provider_session_ecosystem_audit.py:455-470` (event-time/corpus-growth test) and `:1510-1545` (sampled-path assertion).
- `pytest --collect-only` on the audit test file: confirmed **49 tests collected**, matching the plan's stated baseline.
- Read `knowledge/wikis/README.md` to verify the moved-domain list (`acma-projects`, `asset-management`, `engineering`, `engineering-standards`, `lng-projects`, `marine-engineering`, `maritime-law`, `naval-architecture`, plus `cross-links.md`, `knowledge/seeds/`, `tests/fixtures/llm-wiki/`).
- `grep "asset_key:"` in `data/document-index/intelligence-accessibility-registry.yaml`: registry contains only `wiki-engineering`, `wiki-marine-engineering`, `wiki-maritime-law`, `wiki-naval-architecture`, `wiki-personal`, `wiki-cross-links`, `knowledge-seeds` — confirming the four absent moved-domain rows the plan now correctly forbids fabricating.
- `grep current_authority_path|legacy_workspace_hub_path_disposition` in registry: zero matches (confirms proposed marker fields are not yet present and would be net-new).
- Pulled `total_count` for `llm_wiki_spinout_path_drift` from `analysis/provider-session-ecosystem-audit.json`: matched value `225`, consistent with plan line 45.
- Verified `docs/document-intelligence/README.md` contains 2 occurrences of focal paths (in-scope active surface), `llm-wiki-resource-doc-intelligence-operating-model.md` 1, `durable-vs-transient-knowledge-boundary.md` 1.
- Confirmed `scripts/install/pin-codex.sh` and `docs/plans/_template-issue-plan.md` exist.

## Findings

1. **MAJOR — Plan cites a 0-byte Claude review artifact as the source of the MAJOR verdict's substantive findings, and §Adversarial Review Summary line 322 contains a factually false claim about that artifact.**
   - Plan §header line 7 lists `scripts/review/results/2026-05-08-plan-2657-claude.md` under "Review artifacts" with the framing "per-provider artifacts carry substantive provider findings when available".
   - File on disk: 0 bytes. Sidecar `claude.md.err`: 0 bytes. There is no Claude provider signal recorded under `scripts/review/results/`.
   - Plan §Adversarial Review Summary line 316 attributes a MAJOR verdict and six specific findings to "Latest re-review" (Claude). Those findings text actually live in `disagreement.md` lines 18–26, not in the per-provider artifact.
   - Plan line 322 reads: "This revision keeps the non-empty Claude artifact as the per-provider review evidence." This statement is **literally false** — the artifact is 0 bytes. A plan reader following the citation chain reaches no Claude review.
   - Plan AC line 308 demands "the plan summary cites non-empty per-provider artifacts where available and uses `disagreement.md` only as fanout/synthesis evidence, not as a substitute for a missing provider artifact." The plan body violates its own AC.
   - This is the identical defect `disagreement.md:18` raised against this revision (item #1: "Cited Claude review artifact is 0 bytes; verdict and findings text is unbacked"); the revision left the citation chain unchanged.

2. **MINOR — Codex `UNAVAILABLE` accepted without gating on the documented downgrade workaround.**
   - Plan §Adversarial Review Summary line 318 and `disagreement.md:8` record Codex CLI 0.129.0 in known-bad range with the explicit recovery path `scripts/install/pin-codex.sh` (verified to exist).
   - Memory `feedback_cross_provider_review_payoff.md` records Codex as the only provider that finds non-overlapping defects vs. Claude; with Claude artifact empty and Gemini at 429, Codex is the only available cross-provider signal.
   - Plan does not gate posting on running `pin-codex.sh` and re-fanning out, and does not record a workaround attempt-and-failure in the disagreement artifact. The "fresh re-review" requirement at line 320 inherits this gap.

3. **MINOR — Pseudocode line 252 specifies regeneration via "`scripts/cron/provider-session-ecosystem-audit.sh` or equivalent documented command".**
   - The cron wrapper exists. "Or equivalent documented command" leaves regeneration command-of-record unspecified, so the JSON/markdown diff committed under AC 306 is not reproducible across implementers. Pin one command path.

4. **MINOR — Plan status field (line 4) reads `draft` while §Adversarial Review Summary line 320 calls for "fresh re-review before posting".**
   - There is no recorded review-checkpoint between revisions tying line-316 attributions to a specific revision SHA. A plan reviewer cannot tell whether the line-316 findings list was generated against the prior revision or this one. `disagreement.md:26` flagged the same gap and it survives this pass.

5. **MINOR — AC line 305 retains a "per-surface inclusion test" gray zone for active surfaces.**
   - AC 305: "No broad ... behavior changes are made under #2657 beyond the known active focal references unless a specific line passes the per-surface inclusion test and has matching verification." The per-surface test at line 65 is workable for `<domain>/wiki/`, `cross-links.md`, `knowledge/seeds/`, `tests/fixtures/llm-wiki/` — but the AC's escape hatch ("unless a specific line passes...") is judgment-call gray space without an enumerated allowlist or a test fixture. An implementer can route any single targeted edit through this clause; recommend either an explicit allowlist enumerated at planning time or a closeout-evidence requirement that lists every line accepted under the clause.

## Blockers

1. Finding #1 (empty Claude review artifact cited as substantive evidence; line 322 is factually false). The plan cannot be implemented until either (a) a non-empty Claude review artifact is produced and committed at the cited path, or (b) the plan rewrites §header line 7, §Artifact Map line 184, and §Adversarial Review Summary lines 316–322 to acknowledge that **no Claude provider signal exists**, the MAJOR findings live in `disagreement.md`, and the artifact-binding AC at line 308 is satisfied by removing the empty-artifact citation rather than carrying it.

`★ Insight ─────────────────────────────────────`
- The core failure mode here is *citation-chain rot*: a plan revision can list the work it *did* (rebalanced scope, marker structure, RED-first gate) without re-validating that its evidence pointers still resolve to non-empty artifacts. The 0-byte file plus the 0-byte `.err` sidecar is the on-disk fingerprint of a fanout that never produced output, and the plan's own AC line 308 was specifically written to catch this — but only enforces against future implementers, not against the plan's own body, so the contradiction sits inside one document.
- The disagreement.md report is doing real work here: it has caught and re-stated the empty-artifact defect, but the plan revision treated that disagreement report as a discussion partner instead of a binding gate. When `disagreement.md` raises a MAJOR against the plan it is reviewing, the plan revision must close the finding *in the plan*, not reply to it elsewhere.
`─────────────────────────────────────────────────`
