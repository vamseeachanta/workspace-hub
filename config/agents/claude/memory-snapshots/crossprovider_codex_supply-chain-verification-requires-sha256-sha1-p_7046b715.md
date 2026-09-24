---
name: crossprovider codex supply-chain-verification-requires-sha256-sha1-p
description: Supply-chain verification requires SHA256/SHA1 pinning, not just source citation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, codex-pattern, supply-chain, artifact-integrity]
---

Vendored assets (fonts, JS libraries, PDFs) must have digest verification (e.g., 'npm view plotly.js-dist-min@2.32.0 dist.shasum'). Citing the source without pinning the artifact hash leaves the asset vulnerable to supply-chain mutation. Package names matter (plotly.js vs plotly.js-dist vs plotly.js-dist-min are different assets).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
