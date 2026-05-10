# Design: anthropics/financial-services → llm-wiki engineering/ ingest

- **Date:** 2026-05-09
- **Target repo:** `vamseeachanta/llm-wiki` (nested at `/mnt/local-analysis/workspace-hub/llm-wiki/`)
- **Source URL:** https://github.com/anthropics/financial-services
- **Source license:** Apache-2.0 (permissive — synthesis allowed; no verbatim README dumps)
- **Source pushed_at observed:** 2026-05-07T21:10:05Z
- **Workflow:** 8-step external-post ingest (`memory/project_llm_wiki_external_post_ingest_workflow.md`)
- **Deviation from default workflow:** source is a GitHub repo, not a LinkedIn/blog post. Steps 1 (WebFetch) and 5 (concept page) bend; everything else holds.

## Why this lands here

Anthropic's "Claude for Financial Services" is a marketplace of agent plugins and Managed Agent cookbooks (Pitch Agent, GL Reconciler, KYC Screener, etc.) for finance verticals (IB, equity research, PE, wealth management). The financial-domain content has no consumer in `llm-wiki` today — its 8 domain wikis are offshore/marine.

What is consumable: the **multi-agent architecture patterns** the repo demonstrates concretely — managed-agent cookbooks (`agent.yaml` + leaf-worker subagents + `steering-examples.json`), the `callable_agents` research-preview pattern, `handoff_request` events as the cross-agent control plane, and the dual-deployment principle (one source tree → Cowork plugin **and** Managed Agent template share the same skills). These map directly to existing `engineering/wiki/` meta-AI material:

- Existing peer sources: `agent-equivalence-architecture-doc.md`, `ai-agent-guidelines-doc.md`, `ai-development-ecosystem-doc.md`, `compound-engineering-methodology.md`, `methodology-docs.md`
- Existing peer concepts: `agent-delegation`, `orchestrator-worker-separation`, `multi-agent-parity`, `compound-engineering`

So this lands as a **source page** in `engineering/wiki/sources/`, ignoring the financial-services domain content and capturing only the agent-architecture lessons.

## Out of scope

- No new concept page (`managed-agent-orchestration.md`) — gap acknowledged but deferred per YAGNI; promote later if downstream code/chatbots surface the need.
- No touches to other domain wikis (`asset-management/`, etc.) — the org-name "asset management" overlap is coincidental; that wiki is physical-asset-focused.
- No vendor-PDF archival — none involved.
- No issue filed against `vamseeachanta/llm-wiki` — single-page additions don't require issue tracking under the current workflow.
- No workspace-hub state changes beyond this spec file.

## Files to write

### 1. New source page

Path: `llm-wiki/wikis/engineering/wiki/sources/anthropics-2026-financial-services-managed-agents.md`

Slug rationale: `<author>-<year>-<topic-slug>` workflow convention. Author = `anthropics` (org-as-author, since no individual maintainer is canonical for the repo); year = 2026 (repo activity confirms 2026 timeframe); topic-slug = `financial-services-managed-agents` (captures both the repo identity and the agent-architecture angle).

Frontmatter:

```yaml
---
title: "Claude for Financial Services — managed-agent reference patterns"
tags: [managed-agents, multi-agent-orchestration, plugin-architecture, anthropic, agent-handoff, leaf-worker-subagents]
added: 2026-05-09
last_updated: 2026-05-09
sources:
  - url: https://github.com/anthropics/financial-services
    license: Apache-2.0
    observed_pushed_at: 2026-05-07T21:10:05Z
---
```

Section outline (workflow step 4):

- **Relevance** — why an Anthropic finance-vertical reference repo is methodology-grade input for a marine/offshore wiki: the agent architecture is domain-agnostic; finance is incidental to what's being captured.
- **Key teachings** — bullet list:
  - Managed-agent cookbook structure: `agent.yaml` + `subagents/*.yaml` (leaf workers, depth-1) + `steering-examples.json`.
  - `callable_agents` research-preview pattern: orchestrator delegates to depth-1 leaf workers, not arbitrary depth recursion.
  - `handoff_request` steering events as the cross-agent control plane, with a reference event loop in `scripts/orchestrate.py`.
  - Dual-surface principle: one source tree compiles to both a Cowork plugin (`plugins/agent-plugins/<slug>/`) and a Managed Agent template (`managed-agent-cookbooks/<slug>/`), sharing identical system prompts and skills.
  - Self-contained agent plugins bundle synced copies of vertical-plugin skills — install one plugin, get everything that agent needs.
  - Vertical plugins decouple skills+commands+connectors from end-to-end agents, so a user can install `/comps` without installing Pitch Agent.
  - Partner-built plugins (`plugins/partner-built/lseg`, `plugins/partner-built/spglobal`) demonstrate the ecosystem extension pattern.
- **How this maps to existing wiki structure** — cross-link block:
  - `concepts/agent-delegation.md` — base pattern; this source adds `callable_agents` as the API-surface name and the depth-1 constraint.
  - `concepts/orchestrator-worker-separation.md` — repo's `agent.yaml` (orchestrator) + `subagents/*.yaml` (workers) is a concrete instantiation.
  - `concepts/multi-agent-parity.md` — the dual-surface principle is parity through shared source.
  - `sources/agent-equivalence-architecture-doc.md` — closest peer source; this entry extends it with managed-agent specifics.
- **Use as a wiki source** — citation pointer for future managed-agent or plugin-architecture wiki content. (The `concepts/managed-agent-orchestration.md` gap is tracked in this governance doc's "Deferred follow-ups" section, not in the published wiki page.)

Cross-link verification gate (workflow step 3): all four cross-link targets must resolve before write. Pre-checked during exploration:
- `concepts/agent-delegation.md` ✓ (visible in concept listing)
- `concepts/orchestrator-worker-separation.md` ✓
- `concepts/multi-agent-parity.md` ✓
- `sources/agent-equivalence-architecture-doc.md` ✓

### 2. Index update

Path: `llm-wiki/wikis/engineering/wiki/index.md`

Diffs:
- Frontmatter: `page_count: 107 → 108`, `source_count: 16 → 17`, `last_updated: 2026-05-06 → 2026-05-09`.
- Sources table: append a row for the new page (alphabetical or appended-at-end depending on existing ordering — verify at edit time).
- Section header: bump `## Sources (16 pages)` to `(17 pages)` if such a header exists; verify at edit time.

### 3. Log update

Path: `llm-wiki/wikis/engineering/wiki/log.md`

Append (firewall language verbatim per workflow memory):

```
## [2026-05-09] ingest | Anthropic — Claude for Financial Services

- Processed: https://github.com/anthropics/financial-services (Apache-2.0, observed pushed_at 2026-05-07T21:10:05Z)
- Pages created: 1 — sources/anthropics-2026-financial-services-managed-agents.md
- Pages updated: 2 — index.md (page_count, source_count, last_updated, sources table row), log.md (this entry)
- Notes: Source-only ingest. No raw PDFs, private paths, vendor standards text, project specifications, clauses, tables, formulas, or source archive content copied. Concept page on managed-agent orchestration deferred per YAGNI.
```

## Commit plan

Single commit inside `llm-wiki/.git`:

- Explicit-paths `git add` (no `-A` / `.`) — three paths only:
  - `wikis/engineering/wiki/sources/anthropics-2026-financial-services-managed-agents.md`
  - `wikis/engineering/wiki/index.md`
  - `wikis/engineering/wiki/log.md`
- HEREDOC commit message: `Add anthropics/financial-services as managed-agent reference source (engineering/)`
- No workspace-hub issue refs in the commit body (firewall).
- No `--amend`, no `--no-verify`. Iron Law.
- Pre-commit hooks run normally — must pass before commit lands.
- Push policy: write-only by default; do not push without explicit user authorization.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Cross-link target rename between exploration and write | Re-verify with `ls` at edit time; abort write if any of the four targets is missing |
| Index sources-table ordering convention misread | Read full table at edit time; preserve existing order discipline |
| `page_count` / `source_count` counter is phantom (per marine-engineering precedent in workflow memory) | Bump by literal +1 anyway per workflow convention |
| Pre-commit hook flags Apache-2.0 attribution as a license-discipline issue | Synthesize methodology only; cite repo URL + license in frontmatter; no verbatim README copy |
| Parallel session lands on `engineering/wiki/index.md` between read and write | Re-read the file inside the same edit transaction; preflight `pgrep` for hermes-active per memory feedback if any sync activity is detected |

## Deferred follow-ups

- `concepts/managed-agent-orchestration.md` — gap acknowledged; promote when a downstream consumer surfaces the need.
- Coverage-gap issue against `vamseeachanta/llm-wiki` for the absent `financial-services/` domain wiki — only file if/when the user accumulates finance-side material justifying a domain.
- Pre-promotion intel routing to `/mnt/ace/llm-wiki/docs/external-intel.md` — not needed; the source is being promoted directly into the wiki.

## References

- Workflow memory: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_llm_wiki_external_post_ingest_workflow.md`
- Strategic-role memory: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_llm_wiki_strategic_role.md`
- Spinout governance: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_llm_wiki_spunout.md`
- Spec-location feedback: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_superpowers_specs_gitignored.md`
- Workspace-hub citation contract: `.claude/rules/calc-citation-contract.md` (precedent for schema/citation discipline)
