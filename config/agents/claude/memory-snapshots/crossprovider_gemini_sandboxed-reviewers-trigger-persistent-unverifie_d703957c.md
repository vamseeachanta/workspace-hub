---
name: crossprovider gemini sandboxed-reviewers-trigger-persistent-unverifie
description: Sandboxed reviewers trigger persistent 'unverified claims' findings
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [sandboxed-review, attestation, verification-gap]
---

Codex and Gemini reviews cite 'unverified claims' as MAJOR even when plans embed evidence blocks with `gh`/`ls`/`grep` output. Root cause: reviewers run in sandboxes without repo access and cannot independently verify plan assertions. Embedded evidence is textual narrative, not verifiable by the sandbox. Solution: pre-verification attestation at dispatch time (local repo access) before sending to sandboxed reviewer, rather than expecting reviewers to verify from evidence prose.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
