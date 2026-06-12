---
name: crossprovider hermes stale-tracking-issue-detection-verify-all-sub-is
description: Stale tracking issue detection: verify all sub-issues are still open
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github, workflow, issue-management]
---

Tracking issues that cite sub-issues can become stale if those sub-issues close upstream (e.g., during nightly batch runs). Always query and verify all referenced sub-issues are actually still open before processing a tracking issue. Found pattern during Gemini issue triage: #1976 cited 4 already-closed sub-issues.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
