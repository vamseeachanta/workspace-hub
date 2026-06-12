---
name: crossprovider hermes relative-links-in-hierarchical-manifests-resolve
description: Relative links in hierarchical manifests resolve from file's directory, not repo root
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [manifest-validation, relative-paths, github-rendering]
---

Domain manifests in subdirectories (e.g., `wikis/engineering/llms.txt`) fail link resolution when they use root-relative paths like `wikis/engineering/wiki/index.md`. GitHub resolves relative links from the file's own directory, causing `wikis/engineering/` + `wikis/engineering/wiki/index.md` = `wikis/engineering/wikis/engineering/wiki/index.md` (broken). Fix: either rewrite links as `../../../wiki/index.md` (relative to manifest location) or validate all Markdown links from the manifest's perspective, not the repo root.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
