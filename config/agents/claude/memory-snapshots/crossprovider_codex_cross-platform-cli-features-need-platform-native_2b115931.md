---
name: crossprovider codex cross-platform-cli-features-need-platform-native
description: Cross-platform CLI features need platform-native testing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, cross-platform, windows, verification]
---

Static shell analysis of cmd.exe quoting (`%*`), Windows path forms (UNC, 8.3, junctions), or metacharacter handling cannot prove argv preservation. Test with actual cmd.exe on Windows, actual bash on macOS/Linux, including spaces, quotes, repeated flags, trailing backslashes, and empty arguments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
