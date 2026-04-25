# Adversarial Plan Review — aceengineer-strategy #4 (Standards LLM-Wiki Industrialization)

**Reviewer:** Claude (single-author r3, fallback per `feedback_permission_gate_blocks_cross_review.md`)
**Plan file:** `docs/plans/2026-04-25-aces-4-flywheel-standards-canonical-home.md`
**Date:** 2026-04-25
**Stance:** Adversarial — assume defects until proven otherwise. T2 plan with real implementation; defect bar is higher.

---

## What I checked

1. Resource Intelligence — source-count, factual accuracy of file-existence claims, upstream-decision chain coverage
2. Cross-repo workflow handling (`digitalmodel/` is a separate git repo per CLAUDE.md)
3. Frontmatter `license_class` field — concrete allowed values
4. Smoke test linkage to existing #2480 patterns (claimed but not concretely cited)
5. `tests/standards/` directory existence — plan claims new file goes there
6. Phase 1 audit completeness — is "audit dispersion" specific enough?
7. "Minimum clause set TBD by Phase 1" — fallback if scope creep happens?
8. Verbatim-text token threshold (`test_no_verbatim_clause_text_published`) — what's the threshold?

---

## Verdict: MAJOR

Multiple substantive findings that materially affect implementability. Plan needs a v2 patch before `status:plan-review`.

---

## Findings

### F1 — MAJOR: Cross-repo workflow not addressed for `digitalmodel/` modifications
**Plan §Files to Change:** "Modify `digitalmodel/src/digitalmodel/mooring/<2-3 modules>` — Add `code_id` citations on relevant functions." But CLAUDE.md states `digitalmodel/` is a separate git repo. Modifying files there from this plan's commit context will either fail (if path is gitignored from workspace-hub root) or land in the wrong repo. Plan does not address branch creation, PR flow, or commit attribution in the separate repo.

**Evidence:** `ls digitalmodel/.git/branches` (verified 2026-04-25) confirms separate `.git`. Workspace-hub `CLAUDE.md` quick-reference: "digitalmodel/ — separate git repo — cd in before committing."

**Recommendation:** add explicit cross-repo subsection to §Files to Change: which `digitalmodel/` branch to create, how to PR upstream, how to coordinate the workspace-hub plan-approval gate with the digitalmodel commit gate. Reference workspace-hub plan `2026-04-24-issue-2481-calc-output-citation-contract.md` (which dealt with the same cross-repo issue and resolved with cherry-pick to `digitalmodel/main` as `c3be1472`). Either follow that pattern or document why this plan deviates.

### F2 — MAJOR: `license_class` frontmatter field has no allowed-value enumeration
**Plan §Phase 1 / §Pseudocode / §TDD:** plan introduces `license_class` field but never specifies allowed values. Without enumeration, every page-author will pick something different and the field becomes useless.

**Recommendation:** plan must specify allowed values up-front (proposed): `summary-only-with-citation` (default for copyrighted standards like DNV/API), `cc-by-publishable` (for content we authored), `public-domain-quoted` (for ASTM/government docs without copyright restriction), `private-derived` (client-derived, default-private; rare). Acceptance criterion should require all pages have one of these values; smoke test should enforce.

### F3 — MAJOR: `test_no_verbatim_clause_text_published` lacks threshold specification
**Plan §TDD Test List:** "no verbatim block over N tokens from source standard." `N` is undefined.

**Recommendation:** specify threshold in plan body. Suggested: ≥30 consecutive tokens that match a passage in source PDF triggers FAIL. Plan must also specify how the comparison is implemented (pre-loaded source PDF text? simhash? n-gram set?). Without this, the test is unimplementable.

### F4 — MAJOR: `tests/standards/` directory already exists with conflicting tests
**Plan §Files to Change:** "Create `tests/standards/test_dnv_api_canonical_home_smoke.py`." But `ls tests/standards/` (verified 2026-04-25) shows the directory already exists with `test_ingest_standards.py`, `test_integration.py`, `conftest.py`, `__init__.py`. The plan does not address whether the new test file collides or coexists with existing tests, whether they share fixtures via `conftest.py`, or whether the existing tests' coverage overlaps with the new test's claims.

**Recommendation:** Phase 1 audit must inventory `tests/standards/` and explicitly document overlap/coexistence. The new smoke test name should be more specific (e.g., `test_dnv_api_e301_2sk_canonical_home_smoke.py` to avoid name collision with `test_ingest_standards.py`).

### F5 — MAJOR: "Minimum clause set TBD by Phase 1" with no fallback
**Plan §Risks:** plan says "Phase 1 specifies 'minimum viable seed content for the mooring wedge'" but provides no fallback for what to do if Phase 1 *doesn't* converge on a minimum. T2 plans with TBD scope risk indefinite expansion.

**Recommendation:** add a hard fallback: if Phase 1 cannot agree, the minimum is "all DNV-OS-E301 clauses cited by `digitalmodel.mooring.factor_of_safety` and `digitalmodel.mooring.fatigue_assessment`, plus the equivalent clauses in API RP 2SK." This is bounded by current code citations.

### F6 — MINOR: Smoke test "extending #2480 patterns" not concretely linked
**Plan §Phase 2 / §Artifact Map:** mentions extending workspace-hub #2480 patterns. But plan does not cite which patterns specifically — fixture tree? distractor-topic avoidance? MCP-capability gating? Without concrete pattern names, "extends #2480" is decoration.

**Recommendation:** name the 2–3 specific patterns to extend. (Likely candidates from #2480 plan summary: fixture tree at `tests/fixtures/llm-wiki/`, network-coupled-ingest CLI bypass, single-doc IDF-zero distractor avoidance.)

### F7 — MINOR: Workspace-hub #2481 verification claim is indirect
**Plan §Resource Intelligence — Documents consulted:** "Workspace-hub plan `docs/plans/2026-04-24-issue-2481-calc-output-citation-contract.md` (status: completed)." This was verified by reading the README index row in this session, not via direct `gh issue view 2481` or direct file read. The status claim chain is: Claude session → README row → plan claim. Real adversarial review per the issue-planning skill prefers direct evidence.

**Recommendation:** add direct evidence — `gh issue view 2481` output excerpt OR `grep status .../2481-...md` excerpt. Per the plan-template "Evidence (embedded verification)" section, this kind of verification is required for cited issue numbers.

### F8 — MINOR: Cross-references in #5, #6, #7, #9 are listed as files-to-update without specifying which lines/sections
**Plan §Files to Change:** "Update aceengineer-strategy `#5`, `#6`, `#7`, `#9` bodies — Add cross-reference to decision artifact path once locked." Vague. Each issue body has a specific section (Cross-links / Dependencies) where the reference belongs.

**Recommendation:** specify "add to §Cross-links section in each issue body."

---

## Empty-review check

8 findings (5 MAJOR, 3 MINOR). Not empty.

---

## Cross-provider context

- **Codex:** UNAVAILABLE — same upstream regression.
- **Gemini:** RECOMMENDED but deferred. This is a T2 plan with real implementation; Gemini cross-review would add genuine value, especially on F2 (license-class values) and F3 (verbatim threshold). Recommend running once codex-cli regression is fixed (#2479) or via Gemini-only fallback per `feedback_gemini_trust_env_blocks_reviews.md` durable fix in `submit-to-gemini.sh`.

---

## Recommended action

1. **REQUIRED before status:plan-review:** patch plan to address F1, F2, F3, F4, F5 (the five MAJOR findings).
2. **Recommended in the patch:** F6 and F8 (concrete linkages).
3. F7 should be addressed but is non-blocking.
4. After patch, re-review (this same single-author r3 fallback). If still MAJOR, return for v3.
5. Once MINOR-or-better, apply `status:plan-review` label.

The pattern this plan should follow for the digitalmodel cross-repo handling: workspace-hub plan `2026-04-24-issue-2481-calc-output-citation-contract.md` solved exactly this problem and landed via cherry-pick to `digitalmodel/main`. Adopt or document deviation.
