---
name: crossprovider codex tool-reports-of-no-new-artifacts-created-are-unv
description: Tool reports of "no new artifacts created" are unverified intent claims, not inventory facts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [reporting, governance, inventory, verification]
---

Scripts that report `new_dataset_files: 0` based on internal `write_set` tracking may be incorrect if the repo state already contains new files. Actual filesystem/git inventory needed for governance closure. Output reports should say "this tool did not intend dataset writes" not "no datasets exist."

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
