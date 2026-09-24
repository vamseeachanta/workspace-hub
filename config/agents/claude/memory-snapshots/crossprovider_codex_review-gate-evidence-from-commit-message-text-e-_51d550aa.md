---
name: crossprovider codex review-gate-evidence-from-commit-message-text-e-
description: Review gate evidence from commit-message text (e.g. 'reviewed with Codex') is spoofable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, audit, process]
---

Natural-language evidence in commit messages satisfying review gates can be fabricated without actual adversarial review. Gates should require cryptographic/structural evidence (commit hash of review artifact in git, signed review tag, dedicated audit file) rather than grepping keywords.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
