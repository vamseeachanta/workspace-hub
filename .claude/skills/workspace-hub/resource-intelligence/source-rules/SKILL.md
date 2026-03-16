---
name: resource-intelligence-source-rules
description: 'Sub-skill of resource-intelligence: Source Rules.'
version: 1.1.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Source Rules

## Source Rules


- Prefer repo-native and already-indexed sources first.
- Every downloaded source must record: `source_type`, `origin`, `license/access`, `retrieval_date`, `canonical_storage_path`, `duplicate/superseded`, `status` (`available` | `source_unavailable`), fallback evidence when unavailable.

Read `references/source-registry.md` before adding or changing source-root mappings.

---
