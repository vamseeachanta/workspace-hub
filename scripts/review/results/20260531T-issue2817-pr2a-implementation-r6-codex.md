### Verdict: MINOR

### Summary
The r4 blockers named in the prompt appear closed in the payload: binding `recorded_at` is included in freshness via `label_is_fresh(...)`, missing `pushedDate` returns `(None, False)`, CI captures the new gate result then still runs the legacy gate, and the SHA regex/test rejects hex after a closing backtick. I did not find a merge-blocking bypass in the provided diff.

### Issues Found
- MINOR: `scripts/workflow/plan_approval_gate_check.py:resolve_linked_issues` only derives authority from the branch name, while `_evaluate_issue` reports `no linked issue from branch or GitHub metadata`. There is no GitHub metadata fallback in this implementation. This is fail-closed, so not a security bypass, but it is a cutover hazard for legitimate PRs whose branches do not match `_BRANCH_ISSUE_RE`.
- MINOR: `tests/workflow/test_plan_approval_gate_check.py` does not exercise the workflow cutover behavior in `.github/workflows/enforcement-gate.yml`: specifically that the legacy marker gate still runs when `uv run python scripts/workflow/plan_approval_gate_check.py` fails. The YAML diff is logically ordered correctly, but there is no regression test/parse assertion covering this required behavior.

### Suggestions
- Either implement real GitHub-native linked issue resolution or change the denial text/tests to say branch-derived issue only, so operators do not expect metadata support that is not present.
- Add a small workflow-level test or script assertion that checks the plan approval step invokes `uv run python`, captures `PLAN_APPROVAL_LABEL_GATE_RC`, runs `scripts/enforcement/require-plan-approval.sh --strict` before exiting on the new gate result, and preserves legacy diagnostics.

### Questions for Author
- Is branch-name issue resolution intentionally the only supported authorization source for PR2a, despite the denial text mentioning GitHub metadata?
