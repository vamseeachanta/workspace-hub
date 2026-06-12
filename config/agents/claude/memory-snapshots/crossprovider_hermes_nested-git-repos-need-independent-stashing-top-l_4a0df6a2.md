---
name: crossprovider hermes nested-git-repos-need-independent-stashing-top-l
description: Nested git repos need independent stashing; top-level stash doesn't preserve internal dirty state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, nested-repos, stash, safety]
---

When a repo contains nested git repos (e.g., submodules or gitlinks like `heavyequipment-rag`), running `git stash push -u` at the parent level does not preserve changes inside the nested repo's working tree. Nested repos must be stashed separately before parent reconciliation. This is a critical risk in multi-level git structures.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
