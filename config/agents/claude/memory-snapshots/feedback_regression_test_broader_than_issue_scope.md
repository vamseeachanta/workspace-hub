---
name: feedback_regression_test_broader_than_issue_scope
description: "When writing a regression test for a specific issue, scope the test pattern (glob/regex) BROADER than the named target — sibling files with the same defect class get caught for free at no additional cost."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 214b6592-b65b-480f-accf-16e6a9761175
---

When writing a TDD regression test for a specific issue (e.g. "no conflict markers in file X"), make the test's collection scope BROADER than the named file — match the defect pattern across a sensible directory/glob neighborhood. The named file is the minimum scope; the directory/glob is the right scope.

**Why:** workspace-hub#2719 → aceengineer-website#14 (2026-05-16): the issue scoped resolution narrowly to `content/blog/AI_AGENT_ORCHESTRATION.md` (105 conflict markers). I wrote `tests/python/test_content_clean.py::test_no_conflict_markers_in_any_markdown` to glob `content/**/*.md` instead of only the named file. On step-1 fail-first verification, the broader test caught a **sibling regression** in `content/blog/HTML_REPORTING_STANDARDS.md` (15 markers, 5 blocks, identical structural-path pattern from the same conflict-introducing commit). Resolving both files cost zero additional effort (same `awk` one-liner); narrow-scoped test would have left HTML_REPORTING_STANDARDS.md broken indefinitely. The PR closed both files under #14's umbrella because the *defect class* was what mattered, not the specific named instance.

Sibling pattern to:
- [[feedback_adversarial_review_stance]] — tests should hunt for defects, not describe known ones
- [[feedback_naive_secret_scan_false_positive_cascade]] — opposite direction (overscoping CAN cause false positives); balance is "broader than named target, scoped to defect class"

**How to apply:**

1. **Identify the defect class, not just the named file.** "Unresolved merge markers in X.md" → defect class is "any unresolved merge markers in `content/`". "Broken JSON in X.json" → defect class is "any broken JSON in `.claude/`".
2. **Glob the right neighborhood.** Match the directory that semantically owns the file: `content/**/*.md`, `.claude/*.json`, `tests/**/*.py`, etc. Not the whole repo (overscope risks false positives in unrelated paths).
3. **Keep the narrow assertion too.** Pair the broader test with a specific-file assertion that fails with a clear message naming the original issue target. This way:
   - Broader test catches surprises (sibling regressions) → wider value
   - Narrow test confirms the named-target fix → matches the issue acceptance criteria literally
4. **In PR description, surface the broader scope explicitly.** If the test catches siblings, mention them in the PR body so reviewers don't think the fix is out of scope. The pattern *"Issue scope was X; test caught sibling regression in Y; resolved both since the defect class is identical"* is reviewer-friendly.

**Do NOT apply when:** the issue resolution has semantic-side-effect risk that varies by file. E.g. "fix the encoding in this Markdown file" with hand-crafted content choices doesn't translate to "fix encoding in all .md files" — each file may need separate review.

**Verification (2026-05-16):**
- aceengineer-website#14 [PR #15](https://github.com/vamseeachanta/aceengineer-website/pull/15): broader test caught `HTML_REPORTING_STANDARDS.md` regression that issue #14 didn't name; same `awk` resolution applied; both files now PASS the durable test.
- Worth tracking: did the narrow alternative ("test only AI_AGENT_ORCHESTRATION.md") have caught anything later, or would the sibling have stayed broken until a future audit? Future audit would have caught it. But "until a future audit" might be weeks or months.

**Cost of broader scope:** near-zero. Same regex, same glob, same `find`-style traversal. The only meaningful difference is the error message: narrow gives `"X.md has markers"`, broader gives `"3 files have markers: [a, b, c]"`. Broader message is more useful for debugging.
