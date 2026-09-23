---
name: crossprovider codex pr-description-closes-vs-refs-controls-issue-aut
description: PR description 'Closes' vs 'Refs' controls issue auto-closure
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [github, workflow, issue-closure]
---

Using 'Closes #issue' in PR descriptions auto-closes issues on merge; 'Refs' leaves them open for manual closure. When fixing stale-open issues after merge, check whether child PRs used 'Refs' — they'll need explicit closure comments with evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
