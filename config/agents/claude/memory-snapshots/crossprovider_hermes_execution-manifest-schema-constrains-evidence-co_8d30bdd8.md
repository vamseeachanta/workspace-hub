---
name: crossprovider hermes execution-manifest-schema-constrains-evidence-co
description: Execution manifest schema constrains evidence containers and payload keys
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema, contract, test-evidence]
---

Schema must validate test_evidence shape, legal_scan vocabulary closure, non-empty review artifact paths, and raw/private payload key name patterns. Negative test coverage proves invalid combinations (missing exception_reason for limited_pdf, failed legal scan, pending checksum) are rejected.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
