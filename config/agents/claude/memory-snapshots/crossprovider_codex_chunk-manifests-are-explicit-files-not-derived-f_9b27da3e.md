---
name: crossprovider codex chunk-manifests-are-explicit-files-not-derived-f
description: Chunk manifests are explicit files, not derived from directory order
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, manifest, chunking, workflow]
---

Ingest chunks are defined by explicit manifest files (e.g., `/tmp/ingest-prompt-iso-0008.txt`) rather than assumed from directory listing or file count. Always check for a manifest artifact before processing a batch; it contains the authoritative PDF list and chunk boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
