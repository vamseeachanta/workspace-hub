---
name: crossprovider hermes deterministic-synthetic-fixtures-live-operationa
description: Deterministic synthetic fixtures ≠ live operational acceptance proof
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [operational-verification, acceptance-testing, live-environment, synthetic-vs-live]
---

Issue #2766 passed deterministic tests validating HTML report generation against synthetic fixtures, but had no evidence the report came from a live ace-linux-1 probe at closeout time. For operational changes (machine verification, repo placement), synthesized test coverage must be supplemented with live-run acceptance artifacts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
