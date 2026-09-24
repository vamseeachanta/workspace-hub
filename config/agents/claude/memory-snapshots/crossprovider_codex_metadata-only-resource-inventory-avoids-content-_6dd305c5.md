---
name: crossprovider codex metadata-only-resource-inventory-avoids-content-
description: Metadata-only resource inventory avoids content exposure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [resource-intel, cleanup-triage, data-safety, llm-wiki-pattern]
---

For cleanup triage, extension:size:count multiset signatures are sufficient without reading file contents or computing content hashes. Use mtimes, file counts, directory depth, size buckets, and extension histograms to classify resources as unique, migration-residue, or redundant candidates. This keeps output safely private and speeds triage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
