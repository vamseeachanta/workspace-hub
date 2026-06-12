---
name: crossprovider hermes verify-gpu-vram-and-compute-capability-before-pr
description: Verify GPU VRAM and compute capability before proposing local LLM infrastructure
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hardware, infrastructure, llm]
---

GTX 750 Ti (2GB VRAM, Compute Capability 5.0) is insufficient for Ollama; even 1B-parameter models need 4-8GB VRAM or face CPU-only fallback (slow). Always check hardware before recommending tools requiring GPU.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
