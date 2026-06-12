---
name: crossprovider hermes engineering-reference-cataloging-discovery-patte
description: Engineering reference cataloging discovery pattern identifies integration candidates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cataloging-pattern, anomaly-discovery, integration-decision]
---

Cataloging should identify anomalies (out-of-domain files, duplicates, unorganized root files, type distributions) before deciding integration. Example: /mnt/ace/docs/engineering-refs/ has 53 files (124MB); discovery found 1 out-of-domain biomedical PDF, 31 unorganized root files (need subdir organization), dev-tools cheat sheets (need re-tagging). Integration decision: include majority, exclude/re-tag anomalies. Drives cleanup-before-indexing pattern.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
