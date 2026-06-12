---
name: crossprovider hermes filename-path-contracts-must-span-producer-and-c
description: Filename/path contracts must span producer and consumer
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-discovery, producer-consumer-contract, filename-conventions]
---

If provider artifacts switch to timestamped filenames (YYYY-MM-DDTHHMMSSZ), the downstream consumer/parser (e.g., disagreement-diff script) must also be updated to discover those new filenames, or the contract breaks silently and the pipeline stops seeing artifacts. Path discovery is a shared contract between producer and consumer. Found in #2502 fanout/disagreement redesign.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
