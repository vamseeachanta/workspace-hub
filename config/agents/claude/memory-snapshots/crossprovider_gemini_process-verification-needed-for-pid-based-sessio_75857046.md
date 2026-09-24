---
name: crossprovider gemini process-verification-needed-for-pid-based-sessio
description: Process verification needed for PID-based session detection across machines
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [session-management, process-detection, cross-machine]
---

Using `kill -0 $pid` alone to verify live sessions is insufficient; PID can be reused after machine reboot or process termination. Cross-machine detection requires hostname enforcement before PID check AND process name/command verification via `/proc/$pid/cmdline` or `ps` to avoid false positives.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
