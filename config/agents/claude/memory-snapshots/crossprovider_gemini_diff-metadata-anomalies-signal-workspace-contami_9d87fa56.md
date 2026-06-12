---
name: crossprovider gemini diff-metadata-anomalies-signal-workspace-contami
description: Diff metadata anomalies signal workspace contamination
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git, debugging, multi-repo, workspace-state]
---

Anomalous file paths in diff headers (e.g., assethold/docs/ appearing in worldenergydata commit metadata) indicate dirty working directory or stale stash entries from parallel work. Before merging multi-submodule commits, inspect diff headers for cross-project leakage — this is a diagnostic signal for state management issues that precedes silent data corruption.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
