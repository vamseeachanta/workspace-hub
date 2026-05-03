# Disagreement report — plan #2588 (2026-05-02)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNKNOWN |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### gemini

- **Unaccounted corpus files invalidate the misclassification thesis.** The plan asserts that "The 4–5x raw-vs-wiki mismatch is therefore largely a misclassification artifact" based on bucketing out-of-scope files. However, the plan's listed buckets (56 + 88 + 34 + 25 + 9 + 9 + 16 = 237) plus the 14 "domain-engineering candidates" only account for 251 out of the 520 files in `raw/papers/`. This leaves 269 files (over 50% of the corpus) completely unaccounted for. (Cited: § "Gaps identified" and § "Evidence -> Raw filename-prefix bucketing")
- **Flawed `grep` evidence suppresses missing-directory errors.** Under § "Gap proofs", the command `grep -rl "knowledge/wikis/engineering" digitalmodel/ 2>/dev/null` is used to prove no internal citations exist. By omitting the valid `src/digitalmodel/` paths used in the earlier scan and explicitly silencing stderr, this command will silently hide a "No such file or directory" error if the `digitalmodel/` directory does not exist at the root, rendering the proof invalid. (Cited: § "Evidence -> Gap proofs")
- **Unit test time-bomb will break CI upon backfill.** The TDD pseudocode defines an assertion where "each cited subdir has a verifiable file_count that matches a live `find` result within ±5% tolerance". By embedding an assertion that checks static markdown counts against the live filesystem, this test will permanently fail as soon as the first proposed backfill issue adds files to the wiki. (Cited: § "Pseudocode" -> `test_audit_artifact`)
- **Integration test masquerading as a unit test.** The § "TDD Test List" mandates `test_audit_no_wiki_writes` which expects to execute `git diff --name-only HEAD~1 -- knowledge/wikis/engineering/wiki/`. Checking git history in a pytest suite evaluates the environment's current local commit state, not the correctness of the code or artifact, guaranteeing random test failures depending on when or how commits are grouped. (Cited: § "TDD Test List" -> `test_audit_no_wiki_writes`)
- **Contradictory Acceptance Criteria for the Gap table.** The § "Acceptance Criteria" states the audit table must cover "every top-level subdir of wiki/... AND every prefix bucket of raw/papers/". However, § "Pseudocode" defines the "Gap audit table" as only having "rows >= 8, covering every wiki/* subdir + key missing-domain rows", completely omitting the prefix buckets (which are isolated to `table_A_raw_inventory`). (Cited: § "Acceptance Criteria" vs § "Pseudocode")

