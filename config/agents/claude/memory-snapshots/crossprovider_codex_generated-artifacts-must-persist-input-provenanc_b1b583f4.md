---
name: crossprovider codex generated-artifacts-must-persist-input-provenanc
description: Generated artifacts must persist input provenance for reproducibility
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [reproducibility, artifact-generation, testing]
---

Generated outputs require embedded input provenance: source file paths, content hashes, git refs, CLI arguments. Synthetic tmpdir-only tests cannot guarantee real-world reproducibility; verification must include actual source regeneration that confirms committed outputs match current inputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
