---
name: crossprovider codex generated-artifact-timestamps-from-date-today-br
description: Generated-artifact timestamps from date.today() break version stability
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [reproducibility, versioning, generated-artifacts]
---

Using `datetime.date.today()` in generated artifacts (#733) causes content to change daily while keeping date-stamped filenames. Reruns after today produce different JSON/HTML with stale filenames, breaking reproducibility. Avoid daily-resolution timestamps or accept that artifacts are not deterministic; use `--generated-date` args to lock the timestamp.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
