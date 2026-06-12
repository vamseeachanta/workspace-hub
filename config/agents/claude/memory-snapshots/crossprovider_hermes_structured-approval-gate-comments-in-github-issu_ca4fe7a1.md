---
name: crossprovider hermes structured-approval-gate-comments-in-github-issu
description: Structured approval-gate comments in GitHub Issues
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gate, github-workflow, audit-trail, async-coordination]
---

When moving planned work to approval stage, post a GitHub comment with four sections: (1) Plan artifact link, (2) Review artifacts (provider verdicts), (3) Evidence (test results, legal scan, validation status), (4) Recommended Next Action. This creates an auditable record in GitHub Issues and allows async discussion without Slack context-switching. Enables the user to approve via status label change with full context visible inline.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
