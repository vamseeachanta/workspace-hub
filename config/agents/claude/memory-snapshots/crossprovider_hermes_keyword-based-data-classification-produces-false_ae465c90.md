---
name: crossprovider hermes keyword-based-data-classification-produces-false
description: Keyword-based data classification produces false positives without explicit rules
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-quality, marine-safety, classification, testing]
---

Marine incident data keyword matching on 'foundered', 'hatch', 'watertight' sweeps in benign/control records (severity=None, 'procedure verified secure') as risk incidents. Separate each classification type into distinct metrics, define severity/status exclusion rules explicitly, and require test coverage for false-positive thresholds.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
