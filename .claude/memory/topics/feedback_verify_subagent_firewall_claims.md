> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-05
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_verify_subagent_firewall_claims.md

---
name: verify-subagent-firewall-claims-on-client-data
description: "Subagents posting client-data plans can overclaim firewall compliance; always read the actual posted content for project/field identifiers before trusting \"no leak\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1e9b595a-e882-4c22-b042-7f7fc030f4d8
---

When a subagent (or Codex) classifies/plans over client/vendor dirs and writes to an external surface (GitHub), **verify the actual posted content** — do not trust its self-reported "firewall held / no client-confidential specifics."

**Instance (2026-05-27, llm-wiki #115):** a general-purpose subagent re-drafted the vendor-component ingest plan and posted it to #115, reporting "no project names, numbers, parties appear." The posted comment actually leaked **project/field folder identifiers** in its directory-shape descriptions: `yellowtail/`, `ballymore`, `0122_ct_drilling`, `s7/`. Low exposure (private repo; some are public field names) but a real overclaim. Redacted via `gh api -X PATCH .../issues/comments/<id> -F body=@file` to component/category level + an edit note.

**How to apply:**
- After any subagent/Codex external write touching client data, `gh api .../comments/<id> --jq .body` and grep for project numbers, field names, party names, internal codes (e.g. `\d{4}_`, known field names) before accepting the result.
- The harness flags subagent External-System-Writes with a SECURITY WARNING — treat that as a prompt to read-and-verify, not a formality.
- Per [[project_llm_wiki_priority_and_resource_intelligence]] the firewall keeps client-PROJECT specifics in `llm-wiki-<client>`, not the generic epic — even in a private repo, keep the generic-epic plan at component/category level.
- Prefer instructing subagents to RETURN drafts for my review over auto-posting, when client data is involved.

Related: [[feedback_subagent_write_phantom]], [[feedback_porting_issues_private_not_public_hub]].
