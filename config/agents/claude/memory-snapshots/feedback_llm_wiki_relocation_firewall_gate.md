---
name: llm-wiki-relocation-firewall-gate
description: Relocating workspace-hub knowledge artifacts into llm-wiki requires a public-safe firewall screen first; most corpus-index data is non-relocatable pipeline state
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9d5c1253-dc2e-4029-884d-0f22ed116810
---

Before relocating any workspace-hub knowledge/data artifact into the **llm-wiki** repo, run a per-file public-safe screen against llm-wiki's agent-context firewall (its CLAUDE.md). Do NOT bulk `git mv`.

**Why:** Its CLAUDE.md firewall forbids workspace-hub private project state, internal mount/machine paths, and repo-portfolio inventories. `.gitignore` line 8 notes pipeline checkpoint state "should not migrate." (llm-wiki#118, PR #119, 2026-05-26)

**CORRECTION (2026-05-27):** llm-wiki is **PRIVATE since 2026-05-20** (flipped from public OSS per workspace-hub `.claude/rules/codes-standards-data-routing.md`), and vendor-licensed codes/standards **derived** data IS now allowed there (only raw vendor PDFs stay at `/mnt/ace/acma-codes/`). The repo CLAUDE.md still said "public OSS / vendor-derivative content NEVER lands" — stale; corrected via llm-wiki PR #130. So the firewall screen described here was MORE conservative than current policy requires: still screen for workspace-hub private *project state* (machine layout, repo-portfolio, recruiter notes), but vendor-licensed standards derivations are NOT a blocker. Always `gh repo view vamseeachanta/llm-wiki --json visibility` to confirm PRIVATE before treating content rules as public-bound.

**How to apply:**
- `data/document-index/` is workspace-hub **pipeline state**, not publishable content: ~666 inbound hub references (198 scripts, 60 .claude), and a Codex firewall screen of 78 candidate files returned only **3 PUBLIC_SAFE (2 empty), 68 INTERNAL_ONLY, 7 NEEDS_REDACTION**. It does NOT relocate.
- The correct operation is **publish redacted copies** of the cleared subset into llm-wiki; **originals stay in the hub** (so the ingest pipeline + its references are untouched). It is not a move.
- Delegate the screen + redaction to Codex (`codex exec -C <hub> -s workspace-write --add-dir <staging> </dev/null`, `env -u CLAUDECODE`), then **independently re-scan** the redacted output for internal markers (`/mnt/`, machine names, `workspace-hub`, `.claude`, `knowledge/wikis`, issue/plan provenance) before pushing — never trust the redactor's own "clean" claim for a public-leak decision.
- Push to llm-wiki via a **branch + PR**, not direct-to-main. Commit only your paths via explicit pathspec — the llm-wiki tree is often dirty with another session's staged work (e.g. acma concept files). See [[feedback_multi_agent_commit_serialization]], [[feedback_per_repo_metadata_is_firewall]].
- Routing for the workspace-hub "personal" knowledge wiki (decided 2026-05-26): route by **relevance + public-safety**, not wholesale to one repo. `assethold` AND `llm-wiki` are both **PUBLIC** repos → only public-safe content (generic software-eng knowledge → llm-wiki `wikis/engineering/wiki/entities/`; generic finance/real-estate methodology → assethold `docs/domain/realestate/`). **Health reports = private medical data → `achantas-data` (private), never a public repo.** Wiki scaffolding (index.md/CLAUDE.md) stays in the hub when entities are split across repos. PRs: llm-wiki#120, assethold#53, achantas-data#116.
