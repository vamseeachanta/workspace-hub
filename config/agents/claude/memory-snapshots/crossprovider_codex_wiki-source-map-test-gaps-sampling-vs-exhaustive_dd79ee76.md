---
name: crossprovider codex wiki-source-map-test-gaps-sampling-vs-exhaustive
description: Wiki source-map test gaps: sampling vs exhaustive enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, source-maps, llm-wiki, test-rigor]
---

Tests for source-map content (like llm-wiki #626) often check representative rows and assert boundary text (e.g., 'no phone numbers') rather than row-level enforcement of volatility/scope and actual PII/contact literal scans. Tests also regex-match only https:// URLs, missing http://, ftp://, or www.-prefixed patterns. Fix: enumerate all required rows + volatility levels in test constants; validate all URL pattern classes; scan for actual contact literals (email regex, phone digits) not just forbidden substrings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
