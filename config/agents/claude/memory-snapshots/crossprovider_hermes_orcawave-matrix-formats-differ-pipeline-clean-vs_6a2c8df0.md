---
name: crossprovider hermes orcawave-matrix-formats-differ-pipeline-clean-vs
description: OrcaWave matrix formats differ: pipeline (clean) vs native (nested blocks)
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [orcawave, data-format, technical-quirk]
---

Pipeline-format .xlsx (from process-queue.py) has flat columns [Frequency, Heading, Surge_Real, ...] and is consistent across runs. Native OrcaWave .xlsx has frequency-block structure ("Added mass for frequency X rad/s" row headers, 6x6 matrix blocks nested per frequency/heading). Pipeline format is cleaner and what the queue generates; prefer it for extraction.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
