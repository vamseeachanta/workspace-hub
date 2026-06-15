---
name: crossprovider gemini ace-linux-1-as-cross-machine-state-coordinator
description: Ace-linux-1 as cross-machine state coordinator
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cross-machine, coordination-pattern, git-workflow]
---

The comprehensive-learning skill uses ace-linux-1 as a single coordinator that pulls git-synced state files from other machines (ace-linux-2, mkt-a-ansys05) before running a nightly pipeline. For multi-machine workflows, designate one coordinator to collect, process, and commit results rather than attempting distributed consensus.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
