---
name: crossprovider codex public-scan-constraints-need-enumerated-closed-g
description: Public-scan constraints need enumerated, closed grammar and tooling enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [public-safety, validation, build-enforcement]
---

Design acceptable patterns as closed enums (e.g., six fixed manifest sources, five closed drift verdicts, closed role maps) and encode denied patterns (private paths, raw hashes, unbounded operations) in build-time scanners. Aspirational rules ('do not commit X') fail; make them machine-enforced and fail the build on violation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
