---
name: crossprovider codex cross-repo-push-sequencing-needs-explicit-bounde
description: Cross-repo push sequencing needs explicit, bounded gates
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cross-repo, sequencing, deployment-safety]
---

Plans involving nested repos (e.g., aceengineer-website in workspace-hub) must specify push order with concrete timing or dependency gates. Phrases like 'same day' or 'back-to-back' are insufficient; use 'push only after X is live', 'deploy gate blocks until Y is verified', or 'merge within 30min of production validation'. Vague sequencing introduces 404-window risk.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
