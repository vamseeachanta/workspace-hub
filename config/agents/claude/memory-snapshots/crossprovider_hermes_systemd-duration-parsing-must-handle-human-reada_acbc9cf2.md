---
name: crossprovider hermes systemd-duration-parsing-must-handle-human-reada
description: Systemd duration parsing must handle human-readable format strings
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [systemd, parsing, hermes, logging]
---

Systemd `TimeoutStopUSec` and similar fields accept human-readable strings like `1min`, `3min 30s`, `30s`, or `infinity`. Raw `journalctl` output doesn't parse these; verification scripts need regex-based conversion to numeric seconds. Scoping duplicate-check logs to recent journalctl output (e.g., `-S '30 minutes ago'`) instead of stale `-n 200` history avoids stale data triggering false positives.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
