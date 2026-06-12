---
name: crossprovider hermes symlink-boundary-bypass-in-path-filtering-genera
description: Symlink boundary bypass in path-filtering generators
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [generator-safety, symlink-bypass, data-boundary]
---

Prefiltering based on string paths (e.g., allowlist `wikis/*/wiki/**/*.md`) is bypassed by tracked symlinks; later `path.resolve()` follows the symlink into raw/private subdirs (e.g., `wikis/*/raw/secret.md`), emitting the resolved raw path into artifacts. Data-boundary safety requires symlink checks (`Path.is_symlink()`) at eligibility, not just allowlisting by string.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
