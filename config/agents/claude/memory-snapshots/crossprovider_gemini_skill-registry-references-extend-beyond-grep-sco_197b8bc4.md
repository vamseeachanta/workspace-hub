---
name: crossprovider gemini skill-registry-references-extend-beyond-grep-sco
description: Skill registry references extend beyond grep scope
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [skills, audit, registry, workspace-hub]
---

Skill deduplication/deletion cleanup must check not just `.md` files but also `.yaml` config (e.g., `.claude/agent-skills-map.yaml`). Grep-only link audits miss config-file references and leave dangling pointers.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
