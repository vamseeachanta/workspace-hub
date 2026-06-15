---
name: crossprovider hermes ocimf-workbook-external-dependency-creates-silen
description: OCIMF workbook external dependency creates silent test brittleness
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [external-dependency, test-brittleness, licensing]
---

Licensed workbook at `/mnt/ace/mkt-a-codes/OCIMF/OCIMF Coef.xlsx` is a hard gate for test passage; missing file causes test failure without clear error message. Off-repo path creates cross-machine deployment risk and makes tests environment-dependent. Consider mock or error-handling for missing licensed resources.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
