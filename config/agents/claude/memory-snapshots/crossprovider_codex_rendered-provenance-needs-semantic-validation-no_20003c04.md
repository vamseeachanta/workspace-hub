---
name: crossprovider codex rendered-provenance-needs-semantic-validation-no
description: Rendered provenance needs semantic validation, not just presence checks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [html-safety, data-validation]
---

URLs, numeric fields, and boolean flags should validate semantics (scheme check for URLs, range checks for API gravity, strict `True`/`False` for bools) before rendering to HTML, not just `if field_exists`. Otherwise malformed provenance like `javascript:` URLs or `NaN` factors are rendered as trusted data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
