---
name: crossprovider codex ci-cd-enforcement-tests-must-cover-all-equivalen
description: CI/CD enforcement tests must cover all equivalent bypass vocabulary
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [testing, ci-cd, security, enforcement]
---

Banning one bypass spelling (e.g., `paths`) while missing equivalents (e.g., `paths-ignore`) leaves enforcement gaps. Tests should either reject all equivalent spellings or assert an exact allowed schema shape. Promote as a generalizable defect class: enforcement must be exhaustive, not selective.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
