---
name: crossprovider codex feature-support-varies-per-action-version-verify
description: Feature support varies per action version; verify before bulk adoption
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-actions, setup-uv, feature-flags]
---

setup-uv's `enable-cache` support is not uniform across v4/v5/v7. Confirm the pinned major version actually supports the feature before adding it to all steps using that version. Mismatched support causes silent no-ops.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
