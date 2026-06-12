---
name: crossprovider hermes scripts-in-monorepo-src-layouts-need-self-contai
description: Scripts in monorepo src/ layouts need self-contained sys.path injection
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [python, monorepo, environment]
---

Audit wrapper failed in new environments relying on PYTHONPATH; fragile across machines. Inject sys.path in script startup: `sys.path.insert(0, os.path.join(repo_root, 'src'))` before imports; don't depend on wrapper setup.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
