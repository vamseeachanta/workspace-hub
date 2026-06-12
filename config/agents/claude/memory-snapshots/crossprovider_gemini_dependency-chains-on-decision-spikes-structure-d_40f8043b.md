---
name: crossprovider gemini dependency-chains-on-decision-spikes-structure-d
description: Dependency chains on decision spikes structure deferred choices
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [spikes, dependencies, decisions]
---

Binary decisions (which embedding model?) can be deferred via spike issues that measure options, define cost caps, and curate eval sets. The spike (#2403) produces data that unblocks downstream implementation (#2402). Pattern: when decision data is missing, propose a spike with measurement framework rather than guessing in the implementation design.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
