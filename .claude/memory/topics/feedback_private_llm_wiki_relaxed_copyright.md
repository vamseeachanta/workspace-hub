> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_private_llm_wiki_relaxed_copyright.md

---
name: feedback_private_llm_wiki_relaxed_copyright
description: "llm-wiki is private → don't be copyright-conservative in page content as long as the source is referenced"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5092af59-7aa5-4d95-ad31-2130d85ad6f3
---

For the PRIVATE `llm-wiki` repo, do NOT apply public-OSS copyright conservatism to page CONTENT. Capturing fuller article substance — including tables, figures, longer passages, and direct technical detail — is fine **as long as the source is clearly referenced/cited**. The defensive "Public-Wiki Boundary — does not reproduce..." framing and the reflexive "verify against primary before reuse" hedging are unnecessary here; reserve those for genuinely public sibling wikis (worldenergydata-wiki etc.).

**Why:** The repo went private specifically to host vendor-licensed/derived data (see llm-wiki CLAUDE.md). The user's knowledge base is the consumer; over-hedging strips out the substance that makes a page useful. Many ingested sources are also first-party (e.g. World Oil articles the user co-authored via Frontier Deepwater).

**How to apply:** Include the real numbers/tables/figures with attribution; keep a `sources:` field + URL/citation. Still NEVER commit the raw vendor PDF itself (that constraint stands — [[feedback_llm_wiki_relocation_firewall_gate]]). Data-fidelity "provisional" tagging from [[project_llm_wiki_table_fidelity_provisional]] is a separate concern (correctness, not copyright) — keep it only where values were auto-parsed/uncertain, not as blanket copyright caution. My own chat responses still avoid large verbatim dumps; this relaxation is about file content, not chat output. Distinct from the agent-context firewall ([[feedback_verify_subagent_firewall_claims]]) which still applies.
