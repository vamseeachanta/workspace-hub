---
name: crossprovider codex portable-scripts-must-be-tested-on-all-target-pl
description: Portable scripts must be tested on all target platforms; not all standard tools are portable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [portability, platform-testing, gnu-vs-bsd]
---

GNU `date -d` is not available on BSD/macOS; scripts claiming portability must not use it. Tests that only validate GNU behavior will miss the failure mode on other hosts. Run portable tools through all target platforms—or accept platform-specific variants and gate them explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
