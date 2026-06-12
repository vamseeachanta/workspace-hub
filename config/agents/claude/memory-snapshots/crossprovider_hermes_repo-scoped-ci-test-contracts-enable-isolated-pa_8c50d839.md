---
name: crossprovider hermes repo-scoped-ci-test-contracts-enable-isolated-pa
description: Repo-scoped CI test contracts enable isolated parallel repair
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ci-readiness, repo-structure, test-contracts, subagent-dispatch]
---

Tier-1 repos each have distinct pytest invocations (PYTHONPATH, noconftest flags, uv setup). Centralizing contracts in AGENTS.md enables isolated subagent dispatch without cross-contamination; avoid deploying root-level test patterns blindly to nested repos.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
