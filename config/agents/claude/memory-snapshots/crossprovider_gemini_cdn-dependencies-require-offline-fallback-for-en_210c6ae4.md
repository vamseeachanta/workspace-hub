---
name: crossprovider gemini cdn-dependencies-require-offline-fallback-for-en
description: CDN dependencies require offline fallback for enterprise deployments
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cdn-dependencies, air-gapped-networks, enterprise-readiness]
---

External CDNs (KaTeX, Chart.js, MathJax) fail in air-gapped networks. Provide --offline flag or configuration to embed assets directly, or use local fallbacks (e.g., self-hosted CDN mirrors). Document offline limitation explicitly. Affects generated HTML reports, dashboards, and any stakeholder-facing artifacts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
