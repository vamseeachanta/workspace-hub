---
name: crossprovider codex opt-in-defaults-for-gated-features-silently-viol
description: Opt-in defaults for gated features silently violate issue requirements
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [defaults, backward-compat, requirement-mismatch]
---

#608 adds mesh QA gates that default to `off` for backward compatibility, but the issue requires "blocking errors prevent solve/package generation." With defaults off, ordinary `run-orcawave` output can bypass QA entirely, leaving issue acceptance unmet. Opt-in + requirement = contradiction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
