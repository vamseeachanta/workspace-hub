---
name: crossprovider hermes playwright-pdf-generation-avoids-chrome-render-a
description: Playwright PDF generation avoids Chrome render artifacts in HTML reports
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pdf-generation, html-report, playwright, report-tools, engineering-artifacts]
---

For engineering HTML reports to PDF, Playwright with CSS @page rules provides cleaner pagination than Chrome direct-print, which renders URL/date/page headers and breaks layout control. Used in digitalmodel B1528 proj-a rudder-current force report (7 pages A4 landscape) to eliminate unwanted browser chrome while maintaining CSS-driven page breaks and content flow.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
