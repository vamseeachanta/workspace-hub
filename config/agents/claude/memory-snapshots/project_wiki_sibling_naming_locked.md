---
name: project-wiki-sibling-naming-locked
description: "llm-wiki sibling repos use suffix form `llm-wiki-<client>`, one per client, projects nest as folders. Decided"
metadata: 
  node_type: memory
  type: project
  originSessionId: 721b0f0b-2e7f-4368-9d11-6836c232136c
---

llm-wiki sibling naming and structure — **already implemented** for instantiation; retrieval-time rule still pending.

## Naming convention (locked)

- Generic sibling: `vamseeachanta/llm-wiki` (PRIVATE since 2026-05-20).
- Client siblings: **`vamseeachanta/llm-wiki-<client>` (suffix form)** — decided in [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D4, implemented via [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746). Examples: `llm-wiki-acma`, `llm-wiki-rock-oil-field`, `llm-wiki-doris`.
- **One sibling per CLIENT, not per project.** Projects nest as folders, e.g., `llm-wiki-acma/projects/sirocco/`. User-confirmed 2026-05-22; SIROCCO does NOT get its own `llm-wiki-sirocco` repo.

## Already-existing artifacts (do not re-propose)

- Registry: [`config/client-wikis.yml`](file:///mnt/local-analysis/workspace-hub/config/client-wikis.yml) — 1 bootstrapped (`acma`), 5 planned (`rock-oil-field`, `client-projects`, `doris`, `frontierdeepwater`, `saipem`).
- Factory skill (instantiation-time): [`.claude/skills/coordination/client-llm-wiki-factory/SKILL.md`](file:///mnt/local-analysis/workspace-hub/.claude/skills/coordination/client-llm-wiki-factory/SKILL.md).
- Privacy firewall templates: [`templates/client-llm-wiki/`](file:///mnt/local-analysis/workspace-hub/templates/client-llm-wiki/).
- Registry enforcement test: `tests/enforcement/test_client_wiki_registry.sh` (8/0 pass).
- First instantiation: `vamseeachanta/llm-wiki-acma` (PRIVATE, bootstrapped 2026-05-18).

## Still pending (scope of [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778))

The **retrieval-time** routing rule and cross-layer plumbing are NOT yet codified:

- `.claude/rules/wiki-sibling-routing.md` does not exist (the factory skill is instantiation-time only).
- `docs/plans/_template-issue-plan.md` lacks `client:` field.
- `.claude/rules/calc-citation-contract.md` sidecar lacks `source_sibling:` field.
- `private-client-llm-wiki` frontmatter visibility tier not documented as a schema rule.
- Client ↔ generic cross-link discipline not codified (note: [#2776](https://github.com/vamseeachanta/workspace-hub/issues/2776) covers a different sibling pair — public worldenergydata-wiki ↔ private llm-wiki).
- Reference-not-duplicate posture (client wikis cite generic; never re-derive) lives only in 2026-05-20 OCIMF handoff prose.

## How to apply

- When planning any new client wiki repo: use the factory skill above. Naming is automatic from the registry.
- When choosing which sibling to retrieve from during agent work: until [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778) lands its rule, default to `generic` for sanitized public knowledge and the registered client sibling for client-private content. Per the OCIMF handoff: client work CITES generic, never duplicates.
- The 2026-05-20 OCIMF handoff (`docs/session-handoffs/2026-05-20-handoff-digitalmodel-616-ocimf-to-llm-wiki.md`) speculated `llm-wiki-sirocco` as a per-project repo — that speculation is **superseded** by the one-wiki-per-client decision.
- [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744) parent epic body still recommends prefix-form `acma-llm-wiki` in its "Current naming / residency decision" section — out of sync with the executed reality but not time-critical (one-line doc hygiene, separate from #2778).

## Lessons (this session)

Filed #2778 with over-claimed gaps because I read the GH-issue layer but didn't grep workspace-hub for the skills/configs/tests #2746's closeout referenced. Rescoped post-filing. Next session: when [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746)-style closeout comments enumerate deliverables ("workspace-hub implementation commits through SHA X, including template tree, config/client-wikis.yml, registry checker, factory skill, ..."), grep workspace-hub for each named artifact BEFORE drafting any successor issue.

Related: [[project-llm-wiki-privacy-flip]], [[feedback-codes-standards-data-in-private-wiki]], [[feedback-discovery-first-on-stale-plan-approved]].
