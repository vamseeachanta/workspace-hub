---
name: crossprovider codex public-bsee-data-vs-private-synthesis-wiki-routi
description: Public BSEE data vs private synthesis wiki routing
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [routing, data-governance, wiki-architecture]
---

Route public-domain federal BSEE/NOAA/USGS data to `worldenergydata-wiki` with visibility/license frontmatter; private engineering synthesis and client work use private `llm-wiki` (domains) or `llm-wiki-<client>` (projects). Never route federal data through private wikis; always separate by visibility tier from outset.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
