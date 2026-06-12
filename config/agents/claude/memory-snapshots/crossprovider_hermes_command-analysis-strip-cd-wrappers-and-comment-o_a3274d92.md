---
name: crossprovider hermes command-analysis-strip-cd-wrappers-and-comment-o
description: Command analysis: strip cd-wrappers and comment-only lines before tokenizing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-cleaning, command-analysis, signal-extraction]
---

Leading 'cd ... && ' wrappers and comment-only prefixes (e.g., '#') obscure real signal in Bash distribution. Without cleanup, cd dominates (46.5% Hermes); cleanup reveals actual behavior (gh 15.4%, uv run 8.6%). Lightweight fix: drop blank/comment-only leading lines, skip 'cd ... && ' prefix before normalize_command_to_prefix().

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
