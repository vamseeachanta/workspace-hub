---
name: crossprovider codex regex-web-scraping-needs-fallback-patterns-for-f
description: Regex web scraping needs fallback patterns for format variants
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [web-scraping, regex, robustness]
---

Session 10 found Noble scrape parser regex too strict: case-sensitive (only `ft` not `feet`), limited availability tokens, exact link text matching. Web scraping regex should have multiple alternatives or be permissive; HTML/PDF formats vary widely across vendors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
