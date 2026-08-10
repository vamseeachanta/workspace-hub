---
name: crossprovider codex verify-ci-workflow-architecture-claims-empirical
description: Verify CI workflow architecture claims empirically against actual config
metadata:
  type: reference
  source: codex
  bridged: 2026-08-09
  tags: [ci-cd, architecture, verification, rigor]
---

Don't trust a plan's description of which gates/sweeps apply to PRs vs main/nightly/manual without checking the actual workflow YAML and gate routing. Empirical verification catches stale or incorrect architectural assumptions that contradict the real CI configuration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
