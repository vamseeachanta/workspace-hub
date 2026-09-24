---
name: crossprovider codex enforcement-script-drift-via-silent-deletion
description: Enforcement script drift via silent deletion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, versioning, git-hooks, silent-failure]
---

When enforcement scripts (e.g., `scripts/hooks/pre-push.sh`) are deleted from version control but their copies persist in `.git/hooks/`, the working hook drifts from tracked source without detection. The live hook can gain 57+ lines (four months of development) while tests targeting the missing tracked path go red into a noisy suite. When the hook stops working, there is no git history to debug against.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
