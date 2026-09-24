---
name: crossprovider codex detectors-must-cover-assignment-and-parameter-fo
description: Detectors must cover assignment and parameter forms
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [detection, coverage, security]
---

Static detectors for forbidden mechanisms (SSH, Tailscale, etc.) must recognize assignment forms (`$status = & ssh`), typed parameter defaults (`[string]$Host = "literal"`), and indirect invocation, not just line-start direct calls. False negatives hide the exact violations they exist to catch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
