---
name: crossprovider gemini wrk-queue-has-schema-compliance-gaps-and-status-
description: WRK queue has schema compliance gaps and status-directory drift
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, schema-compliance, work-queue]
---

Active work items lack consistent frontmatter: missing plan_reviewed, plan_approved, provider, complexity, created_at, or target_repos fields. Status-directory drift occurs (e.g., items marked status:working stored under pending/ directory). Enforcement gate gap historically allowed execution without plan_reviewed:true.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
