---
name: crossprovider hermes bulk-output-placement-respects-data-code-separat
description: Bulk output placement respects data/code separation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-placement, repo-structure, scalability]
---

Generated or bulk outputs exceeding ~10MB or ~1000 files belong under /mnt/ace/data/, not in git-tracked repo paths. This convention prevents repo bloat and enforces the data/code separation boundary. Failure to respect this causes repository scalability issues.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
