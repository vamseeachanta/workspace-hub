---
name: crossprovider codex pickle-deserialization-has-no-trust-boundary-can
description: Pickle deserialization has no trust boundary — can execute arbitrary code
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security-deserialization, trust-boundary, file-inputs]
---

pd.read_pickle() and pickle.load() execute arbitrary Python bytecode embedded in the file. There is no sanitization step; catching exceptions does not prevent code execution. Validate pickle source or switch to safer formats (JSON, parquet).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
