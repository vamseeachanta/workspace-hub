---
name: crossprovider hermes hermes-orchestration-ace-linux-1-control-plane-a
description: Hermes orchestration: ace-linux-1 control plane, ace-linux-2 overflow worker
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, workstation-orchestration, hermes]
---

Architectural decision: ace-linux-1 owns all GitHub mutations, queue selection, labels/comments/closures, and final reconciliation. ace-linux-2 is execution-only overflow worker and should avoid GitHub API calls unless auth is freshly verified. Provider default: openai-codex with gpt-5.5 model; Gemini/Copilot explicit-use only.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
