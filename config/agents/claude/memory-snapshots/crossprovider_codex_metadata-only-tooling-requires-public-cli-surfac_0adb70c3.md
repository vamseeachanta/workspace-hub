---
name: crossprovider codex metadata-only-tooling-requires-public-cli-surfac
description: Metadata-only tooling requires public CLI surface
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cli-design, public-api, testing]
---

Phase A metadata discovery should expose an executable CLI with explicit output-path arguments, not just importable library functions. Tests must verify the full public contract so repo-tracked artifacts are produced and validated, not just internal library behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
