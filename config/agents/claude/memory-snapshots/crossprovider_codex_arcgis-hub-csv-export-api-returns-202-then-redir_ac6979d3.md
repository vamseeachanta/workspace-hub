---
name: crossprovider codex arcgis-hub-csv-export-api-returns-202-then-redir
description: ArcGIS Hub CSV export API returns 202 then redirects to temporary blob
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [arcgis, api-quirk, data-export, redirect-pattern]
---

When calling ArcGIS Hub's `api/download/v1/items/*/csv` endpoints, expect initial 202 (processing), followed by 302 redirect to a temporary export blob URL. For automation, invoke the API fresh on each run rather than caching or following the redirect; blob URLs are short-lived and expire quickly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
