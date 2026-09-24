---
name: crossprovider codex enforcement-script-evaluators-need-adversarial-t
description: Enforcement script evaluators need adversarial tests for bypass and namespace closure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, adversarial-test, evaluator, bypass-coverage, completeness]
---

Substring-based checks in destructive-operation enforcement scripts are insufficient; tests must cover executable sentinel literal bypasses, dead-code scopes (unreachable aborts), and complete evaluator namespace across all platforms (Windows, systemd, etc.). Evaluator completeness is not automatically enforced.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
