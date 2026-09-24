---
name: crossprovider codex verify-encryption-status-claims-against-actual-p
description: Verify encryption status claims against actual PDF properties
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pdf-ingestion, metadata-validation, contract-enforcement]
---

When marking a PDF metadata-only due to encryption/copy-disabled status, verify the PDF encryption flags actually match the claim. False claims (e.g., marking as encrypted-metadata-only when unencrypted) introduce ambiguity and break downstream contract enforcement that depends on encryption status accuracy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
