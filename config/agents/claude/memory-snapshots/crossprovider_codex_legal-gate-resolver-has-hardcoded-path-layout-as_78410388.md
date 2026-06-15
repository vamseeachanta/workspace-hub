---
name: crossprovider codex legal-gate-resolver-has-hardcoded-path-layout-as
description: Legal gate resolver has hardcoded path layout assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [legal-gate, path-resolution, plan-verification, sibling-repos]
---

Plans referencing `scripts/legal/legal-sanity-scan.sh --repo=digitalmodel` resolve the path to `workspace-hub/digitalmodel`, but actual repo sibling layout is `/mnt/local-analysis/digitalmodel`. Legal gates become non-executable as written when checklist assumes workspace-hub contains the target repo.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
