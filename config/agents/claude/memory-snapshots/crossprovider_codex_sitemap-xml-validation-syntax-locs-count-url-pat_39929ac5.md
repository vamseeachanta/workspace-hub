---
name: crossprovider codex sitemap-xml-validation-syntax-locs-count-url-pat
description: Sitemap XML validation: syntax, locs count, URL patterns, duplicates, metadata order
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [xml, validation, testing, sitemap]
---

Validate generated sitemaps with `xmllint --noout`, count loc entries against expected, verify URL patterns (no apex-host entries if www expected), scan for duplicates, and confirm metadata order matches source. These checks catch silent generation failures before deployment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
