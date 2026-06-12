---
name: crossprovider codex result-file-path-fallback-for-sandboxed-executio
description: Result file path fallback for sandboxed execution
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [scout-pattern, sandbox-operations, evidence-capture]
---

When scout cannot write to exact result path (outside sandbox write roots), provide result content directly as markdown in final output. Mark clearly as 'directly usable as result content' so user can preserve the artifact; avoids silent loss of evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
