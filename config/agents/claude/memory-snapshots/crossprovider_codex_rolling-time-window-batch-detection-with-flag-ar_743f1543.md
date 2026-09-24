---
name: crossprovider codex rolling-time-window-batch-detection-with-flag-ar
description: Rolling time-window batch detection with flag arrays
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [batch-detection, algorithms, time-windows, data-pipeline]
---

To detect campaigns from grouped historical data: iterate each (rig, field) group with a boolean flag array to mark assigned rows. Assign wells to rolling time windows sequentially; when the window closes, start a new batch. Avoids complex state machines for overlapping campaign detection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
