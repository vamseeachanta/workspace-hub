---
name: crossprovider codex cron-audit-scripts-should-be-deterministic-and-l
description: Cron audit scripts should be deterministic and local-only by default
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron-safety, determinism, audit-scope]
---

Periodic audit scripts should not make network calls or GitHub mutations in default mode; keep output under a bounded output root. Use optional flags (e.g., `--render-github-payload`) for manual operator flows that need external posting. Mark optional payloads as local previews, never automatic posts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
