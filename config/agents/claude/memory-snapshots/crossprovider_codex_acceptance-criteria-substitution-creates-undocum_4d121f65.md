---
name: crossprovider codex acceptance-criteria-substitution-creates-undocum
description: Acceptance criteria substitution creates undocumented debt
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [acceptance-criteria, governance, closeout]
---

When operational constraints force equivalent-but-different AC satisfaction (e.g., scoped `rg` scan instead of full `legal-sanity-scan.sh`, hook direct execution instead of git hook integration), this must be explicitly documented and user-approved in advance. Silent substitution masks incomplete verification and complicates future reversal. #2745 execution found 4 ACs satisfied by workarounds without waiver.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
