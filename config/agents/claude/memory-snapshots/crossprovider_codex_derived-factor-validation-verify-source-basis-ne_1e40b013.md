---
name: crossprovider codex derived-factor-validation-verify-source-basis-ne
description: Derived factor validation: verify source basis (net/gross, daily/annual) and temporal consistency
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [data-validation, derived-factors, multi-source]
---

When combining two data sources into a derived factor (e.g., bbl/t from operator barrels + official tonnes), verify both numerator and denominator basis independently. Operator reports default to 'net to company' (not gross field), and daily rates must be annualized; mixing bases produces wrong factors. Verify temporal consistency across years: one source year may have annual-only data while another has monthly detail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
