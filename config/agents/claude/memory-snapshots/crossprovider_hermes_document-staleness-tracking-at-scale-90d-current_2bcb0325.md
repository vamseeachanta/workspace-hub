---
name: crossprovider hermes document-staleness-tracking-at-scale-90d-current
description: Document staleness tracking at scale: <90d current, 90-180d stale, >180d critical
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [documentation-quality, staleness-monitoring, document-intelligence]
---

Issue #1568 adds doc-staleness-scanner.py scanning 1000s of .md files in docs/, docs/assessments/, docs/modules/, docs/research/, docs/standards/, docs/vision/ using git log -1 --format=%aI to extract last-modified date (secondary: frontmatter date field). Output: JSON report to .claude/state/doc-staleness/YYYY-MM-DD.json + ASCII dashboard sorted by staleness + summary stats. Thresholds: current (<90d), stale (90-180d), critical (>180d). This pattern applies broadly to maintaining documentation freshness.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
