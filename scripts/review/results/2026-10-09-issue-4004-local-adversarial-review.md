# Issue 4004 Local Adversarial Review

Scope reviewed: staged implementation for the public-surface guard, including `scripts/enforcement/check-public-surface.py`, `.github/workflows/public-surface-guard.yml`, focused tests, allowlist and denylist config, the adoption snippet, and the O13 rule sentence.

External review status: the repo `cross-review.sh` plan run stalled in the first provider lane and produced no usable verdict. The zero-byte result artifact was replaced with an `UNAVAILABLE` record.

Findings:

- RESOLVED: the first staged self-scan failed because the scanner's own network constants and synthetic test secrets were not allowlisted. The allowlist now includes exact forensic/test values, and the staged diff self-scan passes.
- RESOLVED: short IP values were masked by the generic short-string branch before the IP branch. IP masking now runs first.
- RESOLVED: Anthropic keys could be double-reported as generic OpenAI keys. The OpenAI pattern now excludes `sk-ant-`, and a regression test covers this.
- RESOLVED: the reusable workflow runs the script from a separate guard checkout against a target checkout. `git diff` now runs in the current working directory, and a temp-repo test covers that behavior.
- RESOLVED: `sys` was imported but unused. The unused import was removed.
- RESOLVED: the workflow was not explicitly scoped to public repositories. Both jobs now skip private repositories.

Residual risk:

- The public `config/client-wikis.yml` is a relocated empty stub. The warn-only identifier job will produce findings only when a caller provides a provisioned registry path through `client_registry_path`.
- `actionlint` is not installed in this environment, so workflow validation was limited to YAML parsing and review of the GitHub Actions expressions.

Verdict: PASS after resolved findings, with the residual registry-provisioning and workflow-lint limits above.
