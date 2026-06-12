---
name: crossprovider hermes benchmark-domain-limitations-must-be-explicit-an
description: Benchmark domain limitations must be explicit and conservative
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [naval-architecture, validation, benchmark-domain, overclaiming-prevention]
---

When validating engineering calculations against workbook data, explicitly document the workbook's operational domain limits (e.g., ±1° rudder angle, specific speed ranges). Source formulae like Whicker & Fehlner may support wider domains (e.g., 35° rudder) but comparison data does not. Do not claim validation outside the measured domain, and explicitly exclude phenomena like breakaway/separation that workbook notes exclude.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
