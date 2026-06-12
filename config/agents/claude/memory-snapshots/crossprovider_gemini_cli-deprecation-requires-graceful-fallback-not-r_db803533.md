---
name: crossprovider gemini cli-deprecation-requires-graceful-fallback-not-r
description: CLI deprecation requires graceful fallback, not removal
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cli, deprecation, argparse]
---

Removing deprecated flags entirely causes argparse to crash with 'unrecognized arguments' before reaching deprecation-warning logic. Keep the flag in argparse (using help=argparse.SUPPRESS if appropriate) and handle the fallback in code. WRK-1031 --type flags removed; p2 finding was hard crash on legacy invocations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
