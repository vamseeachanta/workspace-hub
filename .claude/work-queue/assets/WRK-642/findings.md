# WRK-642 Findings

## Executive Summary

Claude non-interactive review is not universally broken. It works on a minimal schema control case, but it fails reliably on WRK-624-sized review inputs. The dominant failure mode is `NO_OUTPUT` on compact and full plan-review payloads. A second issue exists in the Claude wrapper path: one scenario leaked the process chain well past the configured timeout and required manual termination.

## Ranked Root-Cause Hypotheses

### 1. Payload-size and payload-shape sensitivity is the primary trigger
Evidence:
- C1 passed on a minimal target.
- C2 failed on a compact WRK-624 review bundle with the same direct CLI pattern.
- C5 failed on the full plan via wrapper.

Conclusion:
- Claude CLI can return valid structured review output, but not reliably for the current WRK-624 review payload shape.

### 2. Wrapper cleanup is incomplete under timeout pressure
Evidence:
- C6 kept the wrapper process chain alive after the configured 60-second budget.
- Manual termination was required.

Conclusion:
- Even when the provider fails cleanly, the transport wrapper can still leak a long-lived process tree.

### 3. One direct full-payload test path had a harness bug
Evidence:
- C4 failed with `unknown option` because markdown content was passed positionally.

Conclusion:
- Any future direct full-payload tests must pass content through stdin or a temp file, never as positional CLI arguments.

## What This Means for Review Automation

### Reliable today
- minimal smoke-test review with strict schema
- deterministic classification of `NO_OUTPUT`
- wrapper fallback stubs for evidence preservation

### Not reliable today
- compact or full plan review payloads through Claude non-interactive mode
- timeout cleanup in all wrapper scenarios

## Recommended Next Actions

1. Add a hard outer watchdog around `submit-to-claude.sh` that kills the full process group, not just the immediate child.
2. Keep a minimal Claude smoke test in CI to verify the transport is alive independently of plan-review complexity.
3. Introduce a smaller provider-specific compact review bundle for Claude, with tighter content limits than the current WRK-624 compact bundle.
4. Never pass reviewed markdown as positional CLI arguments in direct mode.
5. Treat Claude as `NO_OUTPUT` for plan-review workloads when the compact bundle exceeds the proven boundary until a narrower input format is validated.

## Confidence

Medium-high.

The evidence clearly separates three behaviors:
- Claude works on a trivial schema-only control.
- Claude fails silently on WRK-624-scale review input.
- The wrapper has at least one reproducible timeout-cleanup defect.
