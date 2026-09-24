---
name: crossprovider gemini file-pattern-discovery-must-match-all-patterns-i
description: File pattern discovery must match all patterns in pseudocode
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [patterns, discovery, coverage]
---

File loops that target only dominant patterns (e.g., `*.yaml`) while pseudocode mentions others (e.g., `*.json`) create incomplete scans. Verify loop coverage matches documented scope; update pseudocode or loop to match.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
