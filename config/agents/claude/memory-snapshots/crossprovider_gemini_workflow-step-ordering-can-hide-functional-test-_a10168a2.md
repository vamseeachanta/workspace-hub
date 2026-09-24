---
name: crossprovider gemini workflow-step-ordering-can-hide-functional-test-
description: Workflow step ordering can hide functional test failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci-cd, workflow-design, test-visibility]
---

Placing linting and static checks before functional tests creates invisible gates. If lint fails before smoke tests run, the test result is never observed. Reorder steps to run smoke tests early (or in parallel) so functional failures surface independently of lint status.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
