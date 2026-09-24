---
name: crossprovider codex python-startup-latency-driven-by-eager-module-le
description: Python startup latency driven by eager module-level imports
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python, performance, debugging]
---

CLI help/no-op commands timeout when heavy dependencies (pandas, data science libs) are imported at module level before argparse runs. Lazy import refactoring or entrypoint restructuring required to meet <10s startup targets; measure import cost per module during optimization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
