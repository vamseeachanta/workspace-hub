---
name: crossprovider codex vague-allowlisting-in-code-modifying-tools-creat
description: Vague allowlisting in code-modifying tools creates uncontrolled scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [targeting, autorewrite, scope-control]
---

Autorewrite, templating, and config-management tools need concrete allowlists with enumerated paths/globs and explicit denylist/exclusions. Saying 'whitelisted config surfaces' without enumerating paths creates scope creep and uncontrolled failure modes. Observed in #2408 workflow-config targeting debate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
