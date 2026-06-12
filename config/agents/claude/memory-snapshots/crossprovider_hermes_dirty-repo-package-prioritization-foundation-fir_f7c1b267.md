---
name: crossprovider hermes dirty-repo-package-prioritization-foundation-fir
description: Dirty-repo package prioritization: foundation-first for minimal conflict risk
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, package-management, dirty-repo, merge-risk]
---

When multiple implementation packages are candidates in a dirty repo, prioritize packages with smallest diff surface (unmodified templates) that serve as dependency foundation. Expand config baselines before changing active runtime hooks—foundation layer provides payoff for later work while minimizing merge conflicts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
