---
name: crossprovider codex fixture-based-tests-miss-real-mixed-signal-bound
description: Fixture-based tests miss real mixed-signal boundary cases
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, test-design, governance-validation]
---

Testing policy classification with curated example fixtures passes while missing real-world cases where multiple criteria conflict (e.g., high severity but low confidence, OR classification boundary ambiguity). Add explicit tests for precedence, mutual exclusivity/completeness, and stability across runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
