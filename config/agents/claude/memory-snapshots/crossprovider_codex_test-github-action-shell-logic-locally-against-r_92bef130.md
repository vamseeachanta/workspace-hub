---
name: crossprovider codex test-github-action-shell-logic-locally-against-r
description: Test GitHub Action shell logic locally against real API responses
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [github-actions, security-review, shell-logic, testing-strategy]
---

Don't trust Action logic inspection alone. Test the shell/jq/base64 logic locally against real gh api responses before trusting a flow. Example: PR body/comment extraction needs to run against actual PR objects to verify pagination, multiline safety, and grep correctness. A typo in jq filter (.[].body vs .[]..[].body) becomes obvious in a live test.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
