---
name: crossprovider gemini stale-reference-confinement-via-allowlist-is-saf
description: Stale reference confinement via allowlist is safer than binary bans
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tech-debt, testing, refactoring, governance]
---

When cleaning up references to deleted code/scripts, allow mentions only in intentional legacy docs/historical reports via targeted allowlist tests; fail if current instructional docs mention them. This makes tech-debt cleanup measurable and prevents reoccurrence without blocking historical audit trails.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
