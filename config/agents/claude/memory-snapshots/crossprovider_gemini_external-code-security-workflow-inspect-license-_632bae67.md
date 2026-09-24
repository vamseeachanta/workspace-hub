---
name: crossprovider gemini external-code-security-workflow-inspect-license-
description: External code security workflow: inspect → license-gate → isolate
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [security, external-code, adoption-workflow, supply-chain-risk]
---

Before executing external code via npx or scripts, establish: (1) read raw GitHub source first for manual inspection, (2) apply license gate (permissive allowed, restrictive/none summarize-only) as early adoption step, (3) execute only in disposable/sandboxed environment. Mitigates supply chain attacks in skill/tool adoption (WRK-1084 cross-review: npx skillsadd supply chain risk; Codex fix: passive-first pattern + license gate).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
