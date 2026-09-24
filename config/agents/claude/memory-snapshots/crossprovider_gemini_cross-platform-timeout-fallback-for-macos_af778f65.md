---
name: crossprovider gemini cross-platform-timeout-fallback-for-macos
description: Cross-platform timeout fallback for macOS
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [shell, cross-platform, macos, orchestration]
---

GNU `timeout` not available on macOS; use Perl-based alarm as fallback: `perl -e 'alarm shift; exec @ARGV' <seconds>`. Fall back to running unguarded if both timeout and perl unavailable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
