---
name: crossprovider gemini unix-shebang-with-multiple-arguments-requires-en
description: Unix shebang with multiple arguments requires `env -S` flag
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [shebang, unix, compatibility]
---

`env` treats everything after first space as a single argument. Use `#!/usr/bin/env -S uv run --no-project python` or native `uv` shebang instead of `#!/usr/bin/env uv run --no-project python`.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
