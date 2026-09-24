---
name: crossprovider gemini cross-machine-learning-aggregation-via-git-state
description: Cross-machine learning aggregation via git state files
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [learning-pipeline, distributed, coordination]
---

Learning pipeline runs on single machine (ace-linux-1) but aggregates state files (`candidates/`, `corrections/`, `patterns/`, `session-signals/`) committed by all machines. Enables distributed session learning without central infrastructure; other machines commit state files after sessions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
