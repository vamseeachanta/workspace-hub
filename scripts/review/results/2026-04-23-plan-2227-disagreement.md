# Disagreement report — plan #2227 (2026-04-23)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNKNOWN |
| codex | UNAVAILABLE (codex CLI failed, rc=2: error: unexpected argument '--no-interactive' found    tip: to pass '--no-interactive' as a value, use '-- --no-interactive'  Usage: codex exec [OPTIONS] [PROMPT]        codex exec [OPTIONS] <COMMAND>) |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

- (none)

### gemini

- **Missing source files at HEAD:** The plan's "Resource Intelligence Summary" asserts multiple files are "Found" and git-tracked (e.g., `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md`, `scripts/knowledge/llm_wiki.py`, and `data/document-index/summaries/...`). Verification confirms none of these files or directory structures exist in the repository at HEAD. The plan is hallucinating its foundational inputs.
- **Broken runner logic in T10:** Plan §TDD Test List for T10 specifies using `git diff --name-only` to verify "No new files...". This git command returns all changed files (including modified ones). Consequently, legitimate Branch A modifications to `ocimf-meg4.md`, `index.md`, and `log.md` will cause this test to falsely fail. It lacks a `--diff-filter=A` flag to isolate genuinely new files.
- **Underspecified boundary in T7:** Plan §TDD Test List for T7 asserts the diff of `ocimf-meg4.md` "has ≤ N lines added". `N` is an undefined placeholder. A concrete TDD test cannot be implemented against an abstract variable.
- **Vocabulary constraint contradicts grounding rule in T12:** Plan §TDD Test List for T12 demands the page body contain "at least 3 domain-specific terms from a curated list". Meanwhile, Plan §Pseudocode strictly bounds content to the "OCIMF-TANDEM-MOORING ledger entry + summary artifact". If the source artifact does not organically contain these specific words, the implementation will fail T12 despite perfectly adhering to the strict grounding rule. T12 incorrectly tests the source document's vocabulary rather than the implementation's correctness.
- **Branch B guarantees a broken test suite:** Plan §Acceptance Criteria (Cross-branch) dictates committing `tests/knowledge/test_ocimf_tandem_promotion.py` with all 12 tests implemented. If Branch B execution occurs ("No wiki files written"), tests T3–T12 will permanently fail on that branch because the artifacts they assert (file existence, index updates) were deliberately deferred. The plan provides no conditional test-skipping logic (e.g., `pytest.mark.skipif`) to accommodate Branch B execution without breaking CI.
- **Missing execution commands for follow-up issues:** Plan §Acceptance Criteria (Branch B) requires "Marine-wiki taxonomy decision follow-up issue opened". The Plan §Pseudocode lists no CLI commands (e.g., `gh issue create`) to fulfill this, leaving the execution phase without a mechanism to autonomously satisfy its own acceptance criteria.

