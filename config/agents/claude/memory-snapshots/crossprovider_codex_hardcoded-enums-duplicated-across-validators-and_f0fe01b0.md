---
name: crossprovider codex hardcoded-enums-duplicated-across-validators-and
description: Hardcoded enums duplicated across validators and contracts create drift risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [single-source-of-truth, maintenance, coordination]
---

When an enum (e.g., six manifest sources) is hardcoded in validator logic, contract files, and tests, consistency becomes a manual maintenance burden. Load the contract file as the single authoritative source instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
