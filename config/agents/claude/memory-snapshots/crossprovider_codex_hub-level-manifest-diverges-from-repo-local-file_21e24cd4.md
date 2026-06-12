---
name: crossprovider codex hub-level-manifest-diverges-from-repo-local-file
description: Hub-level manifest diverges from repo-local filesystem truth
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [multi-repo, coordination, architecture]
---

A hub-level manifest in workspace-hub describing enabled/disabled state diverges from actual repo state if repos' local filesystem is source of truth. Either derive manifest from repo inspection, validate against state during builds, or make manifest authoritative with repos reading from it; implicit sync fails silently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
