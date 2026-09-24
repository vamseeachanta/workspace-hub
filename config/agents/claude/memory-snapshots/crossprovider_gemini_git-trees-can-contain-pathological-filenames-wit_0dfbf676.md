---
name: crossprovider gemini git-trees-can-contain-pathological-filenames-wit
description: Git trees can contain pathological filenames with literal backslashes
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git-hygiene, windows-portability, cross-platform, data-integrity]
---

File entries in git trees can have literal backslash characters in their filenames (e.g., tests\modules\file.csv as a single filename, not a path). These cause Windows checkout failures with 'invalid path' errors and represent a data-integrity hazard. Backslash-named entries are distinct blobs from their forward-slash equivalents.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
