---
name: crossprovider hermes untracked-implementation-files-after-review-inva
description: Untracked implementation files after review invalidate verdicts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, review-integrity]
---

Implementation work completed but not staged/committed leaves review artifacts untracked. Adversarial reviewers cannot verify what's actually being shipped. Fixes must be committed (with explicit test validation) before re-review; untracked files are invisible to git diff and sha checks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
