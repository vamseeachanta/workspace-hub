---
name: crossprovider hermes pytest-targeting-on-large-repos-avoids-timeout
description: Pytest targeting on large repos avoids timeout
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, pytest, large-repo]
---

Full pytest suite on workspace-hub (~19K files) times out at 600s; use targeted runs instead: `uv run pytest -q -p no:cacheprovider -k <pattern> tests/<file>`. This pattern verified passing on llm-wiki validation suites (2026-05-11).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
