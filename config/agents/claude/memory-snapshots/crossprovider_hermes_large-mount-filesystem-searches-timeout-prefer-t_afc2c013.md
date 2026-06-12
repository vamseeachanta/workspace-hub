---
name: crossprovider hermes large-mount-filesystem-searches-timeout-prefer-t
description: Large-mount filesystem searches timeout; prefer targeted paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [filesystem-search, performance, large-repos]
---

Broad search_files/find operations over /mnt/ace or /mnt/local-analysis timeout after 60–180s; narrower path searches or Python os.walk with depth limits are more reliable for locating files in large repos.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
