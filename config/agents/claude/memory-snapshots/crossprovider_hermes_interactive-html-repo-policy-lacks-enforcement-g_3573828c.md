---
name: crossprovider hermes interactive-html-repo-policy-lacks-enforcement-g
description: Interactive HTML repo policy lacks enforcement gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [policy-compliance, visualization, review-gate]
---

Repo rule states 'all visualizations: interactive HTML' but static HTML infographics pass review and commit without validation. No lint/test gate checks for Plotly/script interactivity. Add htmlproof check or manual review gate to catch static artifacts against policy.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
