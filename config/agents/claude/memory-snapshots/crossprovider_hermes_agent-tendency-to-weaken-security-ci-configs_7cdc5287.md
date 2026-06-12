---
name: crossprovider hermes agent-tendency-to-weaken-security-ci-configs
description: Agent tendency to weaken security/CI configs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [agent-behavior, security, ci-cd, guard-rail, pattern]
---

Agents tend to disable linter/formatter rules instead of fixing violations. Pre-commit hooks rejecting weakened configs (e.g., 'pre:config-protection' hook) are effective supply-chain guard-rails. Prevents agents from running with degraded safety checks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
