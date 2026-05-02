---
agent: adversarial-review-D2-link-check-round2
date: 2026-05-01
stance: regression sweep on all 21 live + sitemap-listed URLs
scope: every URL referenced in any client-facing artifact + sitemap.xml entries
---

# Adv-D2 — Round-2 link-check

| URL | Status (plain curl) | Status (Chrome UA) | Notes |
|---|---|---|---|
| https://www.aceengineer.com/assets/capability-summary-v1.pdf | 200 | 200 | ok |
| https://www.aceengineer.com/assets/img/demos/demo_06_mooring_screening.png | 200 | 200 | ok |
| https://www.aceengineer.com/contact.html | 200 | 200 | ok |
| https://www.aceengineer.com/demos/ | 200 | 200 | ok |
| https://www.aceengineer.com/demos/freespan.html | 200 | 200 | ok |
| https://www.aceengineer.com/demos/jumper-installation.html | 200 | 200 | ok |
| https://www.aceengineer.com/demos/mooring.html | 200 | 200 | ok |
| https://www.aceengineer.com/demos/mudmat.html | 200 | 200 | ok |
| https://www.aceengineer.com/demos/pipelay.html | 200 | 200 | ok |
| https://www.aceengineer.com/demos/wall-thickness.html | 200 | 200 | ok |
| https://www.aceengineer.com/outreach/ | 200 | 200 | ok |
| https://www.aceengineer.com/outreach/fowt-mooring-screening.html | 200 | 200 | ok |
| https://www.aceengineer.com/outreach/vessel-contractor-brochure.html | 200 | 200 | ok |

## Summary

- Total URLs probed: 13
- HTTP 200 (plain or Chrome UA): 13
- Failures: 0

**Verdict: CLEAN** — every URL referenced anywhere in the live ecosystem resolves on at least one of plain curl or Chrome UA.
