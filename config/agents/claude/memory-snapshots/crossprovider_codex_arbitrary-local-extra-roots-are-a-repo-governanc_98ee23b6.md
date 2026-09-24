---
name: crossprovider codex arbitrary-local-extra-roots-are-a-repo-governanc
description: Arbitrary local extra roots are a repo-governance gap unless explicitly allowed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [repo-governance, registry-schema, path-authority]
---

Plans that satisfy 'required' repos can be defeated by arbitrary local extra roots (e.g., `/mnt/dde/tmp/`, user-provided paths) unless the registry explicitly declares allowed paths per repo. Acceptance criteria must include tests that fail when required repos are found only in undeclared/arbitrary local roots.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
