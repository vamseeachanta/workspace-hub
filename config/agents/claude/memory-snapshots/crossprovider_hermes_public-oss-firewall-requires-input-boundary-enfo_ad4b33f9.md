---
name: crossprovider hermes public-oss-firewall-requires-input-boundary-enfo
description: Public OSS firewall requires input-boundary enforcement for private archives
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [public-oss, data-firewall, compliance]
---

Private archives like `/mnt/ace` are input boundaries only; commits must not echo private memory, raw paths, vendor-derivative, or credentials. Output is MIT for code, CC-BY-4.0 for content. Service-provider data routing applies. Separate constraints on what data can cross the repo boundary vs. what can be observed during processing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
