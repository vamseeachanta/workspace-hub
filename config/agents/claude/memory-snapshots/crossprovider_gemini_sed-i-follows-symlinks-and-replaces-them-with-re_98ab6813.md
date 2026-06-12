---
name: crossprovider gemini sed-i-follows-symlinks-and-replaces-them-with-re
description: sed -i follows symlinks and replaces them with regular files
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git, shell-scripting, gotcha]
---

Bulk `sed -i` operations will replace symlink targets with regular files, breaking symlink chains. After sed bulk edits, check `git diff --diff-filter=T` (type changes) to catch unwanted symlink→file conversions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
