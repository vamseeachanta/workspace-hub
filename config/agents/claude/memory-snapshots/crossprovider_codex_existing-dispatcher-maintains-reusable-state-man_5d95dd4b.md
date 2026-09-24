---
name: crossprovider codex existing-dispatcher-maintains-reusable-state-man
description: Existing dispatcher maintains reusable state manifests for orchestration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [orchestration, dispatcher, state-management, reuse]
---

dispatch_corpus_ingest.py already persists .dispatch-state.json and .dispatch-state-mechanical.json tracking completed chunks, commits, and attempt history. New dispatch cockpit or orchestration logic can consume these manifests for queue health signals and priority ranking without re-implementing queue tracking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
