---
name: crossprovider codex provenance-validators-must-enforce-strict-whitel
description: Provenance validators must enforce strict whitelists
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provenance, validation, contracts]
---

Document-key validators should restrict algorithms to canonical only (e.g., sha256 for provenance), not broader sets like sha1/sha512/md5. Tests must verify rejection of non-canonical variants, not acceptance; accepting broader sets locks in the wrong contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
