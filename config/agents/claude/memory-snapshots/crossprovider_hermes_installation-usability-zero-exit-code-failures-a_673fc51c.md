---
name: crossprovider hermes installation-usability-zero-exit-code-failures-a
description: Installation ≠ usability: zero-exit-code failures are silent for Windows tools
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [windows-tools, fixture-design, correctness]
---

AQWA/ANSYS/OrcaFlex can report exit 0 despite runtime/license failure or missing launcher dependencies. Usability classification requires dedicated zero-exit-code-failure fixtures, not just path-existence checks. This is distinct from and deeper than install-vs-usable classification.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
