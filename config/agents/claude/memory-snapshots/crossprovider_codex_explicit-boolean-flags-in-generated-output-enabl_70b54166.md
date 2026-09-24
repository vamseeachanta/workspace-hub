---
name: crossprovider codex explicit-boolean-flags-in-generated-output-enabl
description: Explicit boolean flags in generated output enable post-hoc audit of safety assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [auditing, safety, output-format]
---

Include fields like raw_file_ingestion_allowed, source_body_reads_allowed, source_mutation_allowed, broad_ingestion_dispatched as explicit true/false in JSONL/JSON outputs. Allows reviewers to verify the generator's safety model was enforced, not inferred from absence of violations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
