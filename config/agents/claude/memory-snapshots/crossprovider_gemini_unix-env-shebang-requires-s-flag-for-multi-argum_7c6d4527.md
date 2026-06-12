---
name: crossprovider gemini unix-env-shebang-requires-s-flag-for-multi-argum
description: Unix env shebang requires -S flag for multi-argument programs
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [shebangs, unix, cross-platform, env-syntax]
---

Shebangs like `#!/usr/bin/env uv run --no-project python` fail because env treats the entire post-space string as a single argument. Use `#!/usr/bin/env -S uv run --no-project python` (with -S flag) or native uv shebang support. Cross-platform issue affecting Linux, Mac, and older Unix systems.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
