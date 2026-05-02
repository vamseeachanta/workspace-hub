### Verdict: APPROVE

### Summary
v4 surgically addresses every v3 P1/P2 (Attested Evidence populated payload R29, --now idempotency seam R30, secondary_domains list with schema v1.2 R31, scoped safe_open helper R32) plus the secondary review items (R33-R42). The attested evidence block (sha256 4d720fcade...) confirms issue states and file existence at HEAD 3e0e7c2b, removing the v2/v3 "scaffold not payload" concern. Remaining issues are minor hardening/clarity items, not correctness blockers; the plan is implementable as written with the suggested follow-ups.

### Issues Found
- [P3] Test count claim wrong: 'Total: 28 tests; v3 had 26' but the table actually contains 31 entries when 5b, 5c, 6.5, 7b are counted. Reviewer fact-check failure.
- [P2] Runtime stopwords SHA verification gap: the only runtime guard is `STOPWORDS_SHA == '<unpinned>'`. If the stopwords file is edited after pin without re-running `make pin-stopwords-sha`, the runner silently uses a stale constant against a different file. Test 12 catches it at test time but not at production runtime.
- [P2] CI grep whitelist (Test 5b) is line-based and substring-matched: `grep -vE '(def safe_open|return open\(|from pathlib import Path)'` would whitelist a comment line like `# def safe_open wraps open()`, defeating the guard. Should use anchored patterns.
- [P3] `isope_proposed_body()` function referenced in pseudocode but never defined; only AC13/Test 27 imply the shape (a markdown blob with a non-empty body under `## ISOPE re-index follow-on (proposed body)` header).
- [P3] AC10 wording awkward: 'misc not allowed in either engineering_domain secondary slots'. `engineering_domain` (singular, primary) DOES allow misc per Appendix A; only `secondary_domains` excludes it. Should be rephrased to reference R16 explicitly.
- [P3] Makefile target location uncertain: 'Makefile (or scripts/knowledge/Makefile)' — pick one before review begins, since AC2 sequencing depends on it being invokable.
- [P3] `target_wiki_path_hint` is a required field in Appendix A but pseudocode does not show how it is computed from a topic cluster (e.g., slugify(topic_label) under `concepts/`).

### Suggestions
- Add a runtime SHA check: at runner startup, compute `sha256(open(stopwords_path).read())` and compare to `STOPWORDS_SHA` constant; raise a typed error on mismatch. This closes the silent-drift window between Test 12 invocations.
- Tighten the Test 5b grep whitelist with anchored patterns: `^def safe_open\(`, `^    return open\(`, `^from pathlib import Path$`. Add a Test 5d with an intentionally-disguised `open()` call (e.g., in a docstring or trailing comment) to confirm the guard rejects it.
- Define `isope_proposed_body()` inline as a constant string at top of runner, or extract to a sibling YAML file referenced by both the runner and Test 27 fixture. Either way, name the source-of-truth so future edits land in one place.
- Rewrite AC10 as: 'Cross-link JSONL conforms to Appendix A schema v1.2; secondary_domains is list[str] (may be empty []); misc is rejected from secondary_domains entries at parse time per R16. engineering_domain (primary) may be misc.'
- Resolve the Makefile question (root vs scripts/knowledge) and update both the Files-to-Change row and Runbook step 1 to point to the chosen path. Either is fine but consistency matters.
- Add a one-line procedural note acknowledging that the attestation block was generated against v3-staged content; v4-introduced paths (pin_stopwords_sha.py, eval_cluster_quality.py) happen to be MISSING in either case, so the block remains valid for v4. This pre-empts a reviewer flagging the staging path as stale.
- Specify `target_wiki_path_hint` derivation rule in pseudocode (e.g., `f"concepts/{slugify(topic_label.split(' | ')[0])}.md"`). Otherwise this field becomes implementer-discretion and #2068 cannot rely on its shape.

### Questions for Author
- Should the runner re-verify `sha256(stopwords_file) == STOPWORDS_SHA` at startup (production-time guard), or is the test-time check via Test 12 sufficient given the runner is invoked from CI / a controlled environment?
- What is the expected behavior when `--now` is provided but is malformed (e.g., not ISO-8601)? Reject with typed error, fall back to runtime-now, or silently coerce?
- For the ISOPE proposed-issue body (AC13/R35): is the body content static (a constant) or does it reflect the actual deferred-set details (e.g., paper count, why-deferred reason) computed at run time?
- Does `target_wiki_path_hint` need to be unique within a target wiki, or is collision acceptable (downstream #2068 deduplicates)?
- On schema arbitration (Risks): when this plan lands first, does that mean #2068 inherits v1.2 verbatim, or does #2068 plan-author have license to propose a v1.3 that this plan would then need to adopt retroactively? The 'whichever issue is open at the time files a PR' rule is mutual but ambiguous about who blocks whom.
