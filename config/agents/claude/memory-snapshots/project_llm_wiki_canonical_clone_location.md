---
name: llm-wiki-canonical-clone-location-2026-05-26-correction
description: "Canonical local llm-wiki clone is /mnt/local-analysis/llm-wiki (NOT workspace-hub/llm-wiki, which does not exist) — corrects project_llm_wiki_spunout"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e9b595a-e882-4c22-b042-7f7fc030f4d8
---

As of 2026-05-26, the canonical local working clone of `vamseeachanta/llm-wiki` is **`/mnt/local-analysis/llm-wiki`** (git, 16 domains under `wikis/`). The nested path `/mnt/local-analysis/workspace-hub/llm-wiki` **DOES NOT EXIST**.

**Why this matters:** [[project_llm_wiki_spunout]]'s "Resolution executed 2026-05-18" section claims the nested `workspace-hub/llm-wiki/` became the sole canonical clone and the outside `/mnt/local-analysis/llm-wiki/` was removed. That is now **stale/reversed** — the standalone sibling clone is what exists. Three independent Codex dispatches (#105/#106/#109 plan-drafts) flagged the nested path as absent; verified directly 2026-05-26.

**How to apply:**
- Any agent/Codex brief or execution dispatch that writes wiki content must target `/mnt/local-analysis/llm-wiki`, not `workspace-hub/llm-wiki`.
- `/mnt/ace/llm-wiki` is a different thing — the off-repo holding pen (`docs/` only), per [[project_llm_wiki_strategic_role]]; not a clone.
- The Codex sandbox runs with `--cwd /mnt/local-analysis/workspace-hub`; the canonical clone is a SIBLING outside that cwd, so execution dispatch needs the clone added to the sandbox writable roots (see [[feedback_codex_worktree_sandbox_three_layer]]).

Related: [[project_llm_wiki_spunout]] (now partially stale on clone location), [[feedback_porting_issues_private_not_public_hub]].
