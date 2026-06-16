---
name: crossprovider codex legal-scan-diff-only-vs-full-scan-in-temp-prs
description: Legal-scan --diff-only vs full-scan in temp PRs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [legal-scan, pr-review, temp-clone]
---

Running a full `legal-sanity-scan.sh` without `--diff-only` in a temp PR-head clone scans the entire repository, not just the PR changes. Pre-existing deny-list hits dominate output and mask the PR-scoped violations. Use `--diff-only` where available, or use `git diff --check` + focused grep on changed blobs only to isolate PR scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
