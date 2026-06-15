---
name: crossprovider codex github-pull-request-event-doesn-t-trigger-on-iss
description: GitHub pull_request event doesn't trigger on issue label changes
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [github-api, workflow-automation, approval-gate]
---

Workflow checks triggered by pull_request event do not re-run when a label is applied to the linked issue. Approval gates that require label verification must include issue.labeled event bridge, offer workflow_dispatch for manual rerun, or document that users must manually retrigger the check after labeling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
