---
name: crossprovider hermes artifact-mtimes-detect-background-process-comple
description: Artifact mtimes detect background process completion when process API lacks records
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [background-process, artifact-validation, mtime-detection, process-monitoring]
---

When checking if a background process successfully updated canonical output files, the process API may show 'not found', but file mtimes on the canonical artifacts themselves reveal whether the process executed and regenerated outputs. Timestamps on the actual output files are more reliable than process state records for determining completion.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
