---
name: crossprovider codex provider-cli-transport-issues-differ-by-vendor
description: Provider CLI transport issues differ by vendor
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-transport, provider-semantics, cli-hardening]
---

Claude review wrapper uses a single large `-p` argument (brittle for escaping/size); Gemini wrapper mixes `-p` with piped stdin and `-y`, causing it to drift into planning/tool mode instead of returning review schema. Both need provider-specific transport handling—structured outputs for Claude, clear stdin-only boundaries for Gemini—rather than generic wrapper logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
