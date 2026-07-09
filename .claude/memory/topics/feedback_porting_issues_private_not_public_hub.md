> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-09
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_porting_issues_private_not_public_hub.md

---
name: porting-issues-private-not-public-hub
description: "Document-port + client-wiki tracking issues belong in PRIVATE llm-wiki / llm-wiki-<client>, NEVER public workspace-hub; transfer existing public ones"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1e9b595a-e882-4c22-b042-7f7fc030f4d8
---

`vamseeachanta/workspace-hub` is **PUBLIC**; `vamseeachanta/llm-wiki` and every `llm-wiki-<client>` are **PRIVATE** (verified 2026-05-26). Therefore all `/mnt/ace` document-porting and client-wiki tracking issues must be created in the **private** wiki repos, not in public workspace-hub.

**Why:** the corpus-ingest umbrella (#2774) enumerated 54 vendor-licensed publishers + `/mnt/ace` paths, and the client epic (#2744) named the ACMA engagement — all sitting in a public repo. On 2026-05-26 the user directed "move existing workspace-hub issues to llm-wiki to maintain privacy."

**How to apply:**
- New porting/client issues → `gh issue create --repo vamseeachanta/llm-wiki` (or the client sibling), never workspace-hub.
- Re-home existing public ones with `gh issue transfer <n> vamseeachanta/llm-wiki --repo vamseeachanta/workspace-hub` (issue number changes; old URL redirects). Done 2026-05-26: #2774→llm-wiki#122 (reunites with children #103–#117), #2744→llm-wiki#123.
- Completeness scorecards / reports for this work → private llm-wiki `docs/reports/`, not public workspace-hub.
- **Caveat (non-negotiable to state):** workspace-hub has been public, so transferred issues were already GitHub/search-indexed. Transfer removes *future* exposure only; it cannot un-publish. The durable protection is the create-private rule going forward.

Related: [[project_llm_wiki_privacy_flip]], [[feedback_codes_standards_data_in_private_wiki]], [[feedback_offrepo_intel_routing]], [[project_wiki_sibling_naming_locked]].
