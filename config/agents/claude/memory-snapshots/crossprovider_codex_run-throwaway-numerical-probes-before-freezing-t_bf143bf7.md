---
name: crossprovider codex run-throwaway-numerical-probes-before-freezing-t
description: Run throwaway numerical probes before freezing test thresholds
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-methodology, numerical-validation, test-design]
---

Before committing test cases with specific expected-value thresholds (like '49.1% parity' or '395.35 lb load'), run an independent numerical solver against the fixtures to empirically derive the correct values. This catches specification mismatches and fixture-dependent artifacts before tests are locked in.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
