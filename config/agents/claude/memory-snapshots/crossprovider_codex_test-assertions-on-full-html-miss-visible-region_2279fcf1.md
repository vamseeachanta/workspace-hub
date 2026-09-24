---
name: crossprovider codex test-assertions-on-full-html-miss-visible-region
description: Test assertions on full HTML miss visible-region regressions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-quality, html-assertions, regression-risk]
---

When full HTML includes embedded JSON payloads, assertions against the full document will pass even if visible rendering (e.g., Caveats list, markers) breaks. Assert against `visible_html` separately; reserve full-document checks for payload structure only. This prevents silent visibility regressions in rendered reports.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
