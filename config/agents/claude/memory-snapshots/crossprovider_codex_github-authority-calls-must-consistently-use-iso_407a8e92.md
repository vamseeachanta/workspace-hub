---
name: crossprovider codex github-authority-calls-must-consistently-use-iso
description: GitHub authority calls must consistently use isolated environment and literal hostname
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [github, security, environment-isolation]
---

`gh repo view`, `gh repo create`, and all direct GitHub calls must use `env=isolated_env()` and explicit `--hostname github.com` consistently across all callers (factory, checker, verifier). Leaving any call to ambient `gh` config defeats the fixed-contract guarantee.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
