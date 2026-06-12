---
name: crossprovider hermes hermes-requires-hardcoded-venv-shebang-not-env-p
description: Hermes requires hardcoded venv shebang, not env python3
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, shebang, python, venv, dependencies]
---

Scripts invoked by Hermes MUST use `/home/vamsee/.hermes/hermes-agent/.venv/bin/python` shebang, not `#!/usr/bin/env python3`. The env shebang resolves to miniforge3, which lacks hermes's site-packages (python-dotenv, requests, etc.). Hardcoded venv shebang guarantees correct site-packages despite being less portable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
