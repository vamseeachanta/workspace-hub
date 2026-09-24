---
name: crossprovider codex revision-lineage-needs-explicit-supersession-sta
description: Revision lineage needs explicit supersession state, not just version tracking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [versioning, audit-trail, data-structure]
---

Tracking version numbers alone is insufficient for audit; explicit revision_lineage.supersedes, revision_lineage.superseded_by, and revision_lineage.revision_trigger fields are required to answer why a version was replaced without reading external history.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
