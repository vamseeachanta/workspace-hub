---
name: crossprovider hermes nested-git-detection-via-path-is-dir-masks-permi
description: Nested git detection via Path.is_dir() masks permission errors; explicit lstat() safer
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [error-handling, filesystem-ops, nested-git]
---

Path.is_dir()/is_file() swallow OSError internally, so inaccessible nested repos return False silently rather than raising. This causes missed nested-git warnings in audit output. Use explicit `lstat()` or handle OSError to distinguish 'no directory' from 'permission denied'.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
