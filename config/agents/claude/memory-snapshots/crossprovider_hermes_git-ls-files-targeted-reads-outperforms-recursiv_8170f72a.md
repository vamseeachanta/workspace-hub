---
name: crossprovider hermes git-ls-files-targeted-reads-outperforms-recursiv
description: git ls-files + targeted reads outperforms recursive search on large repos
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [performance, large-repo-optimization, search-patterns]
---

Full recursive `find`/`search_files` on workspace-hub (933 skills, ~329K files) times out after 22+ minutes. Using `git ls-files` for file inventory plus targeted reads is ~145 seconds and reliable. Apply to skill audits, capability scans, and other whole-repo inventories when performance matters.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
