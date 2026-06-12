---
name: crossprovider hermes client-data-redaction-in-public-artifacts-is-non
description: Client data redaction in public artifacts is non-negotiable
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-governance, security, client-data]
---

Public artifact inventories (path maps, taxonomy docs, machine-readable contracts) must redact actual client/project folder names from `/mnt/ace/` while describing the category allowed (e.g., allowed: `/mnt/ace/client_projects/<client>/`, forbidden: publishing actual client names without explicit approval).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
