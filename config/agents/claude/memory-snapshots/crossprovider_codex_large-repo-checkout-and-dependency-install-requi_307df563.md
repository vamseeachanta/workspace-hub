---
name: crossprovider codex large-repo-checkout-and-dependency-install-requi
description: Large repo checkout and dependency install require patience; monitor for hung bytecode compilation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [environment-setup, dependency-resolution, performance]
---

Large repositories (14k files) and heavy ML dependencies (PyTorch + CUDA ~4.6 GB) take time; let checkout/install finish. Pytest collection can hang on bytecode compilation; disable with `UV_COMPILE_BYTECODE=0` if needed. Monitor for non-responsive processes before interrupting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
