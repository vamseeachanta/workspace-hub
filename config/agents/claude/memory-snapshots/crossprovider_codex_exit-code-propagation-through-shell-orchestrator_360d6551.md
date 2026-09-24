---
name: crossprovider codex exit-code-propagation-through-shell-orchestrator
description: Exit code propagation through shell orchestrators: `|| true` swallows gate enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-patterns, error-handling, gates]
---

When subprocess scripts (Python, bash) return non-zero to signal failures (e.g., FAIL findings from a drift check), `script.py || true` in the orchestrator silently swallows that exit code and reports success upstream. Gates defined by exit codes must explicitly propagate: capture exit code, accumulate into FAIL_COUNT or OVERALL_EXIT, and respect the accumulated status at script exit. Discovered in WRK-1094: config-drift check returning non-zero was masked by `|| true` in both check-all.sh and pre-push.sh, making the gate ineffective.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
