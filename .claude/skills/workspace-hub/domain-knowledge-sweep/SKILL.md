---
name: domain-knowledge-sweep
description: Systematic multi-source research of an engineering domain. Spawns parent issue → 6 research subissues (Standards, Academic, Industry, LinkedIn-marketing, Code-audit, Synthesis) → gap implementation subissues. Replaces LinkedIn-only extraction with defensible comprehensive sourcing.
version: 1.0.0
category: workspace-hub
---

# Domain Knowledge Sweep

Use when the user wants to audit an engineering domain comprehensively (e.g., "strengthen llm-wiki with X" / "research domain Y" / "find gaps in our hydrodynamics coverage") so that:
- Standards, academic sources, industry practice, and codebase coverage are all surveyed
- A defensible coverage map is produced with proper citations
- Implementation gaps are spawned as actionable subissues
- LinkedIn is captured as marketing-surface only (not primary technical source)

## When this skill is the right fit

- User asks to research, strengthen, or audit a technical domain end-to-end
- User mentions parallel-account dispatch (multiple AI accounts available)
- Coverage gaps in llm-wiki, digitalmodel, or related repos need systematic discovery
- A LinkedIn post or single source kicked off the request but completeness matters

## When NOT to use

- User wants a one-off single-source extraction → use `field-dev-code-recon` instead
- User wants to ingest a specific document already in hand → use `gsd:ingest-docs`
- User wants implementation of a known gap → use normal feature-dev pipeline

## Parent feature

[#2667](https://github.com/vamseeachanta/workspace-hub/issues/2667) — Domain Knowledge Sweep meta-feature. Every domain sweep spawned via this skill must reference this parent.

## Workflow

### Phase 1: Domain Charter

Confirm with user:
1. **Domain name** (e.g., "Offshore Hydrodynamics", "Mooring Design")
2. **Scope IN** (what topics are inside the domain)
3. **Scope OUT** (what's a separate domain to avoid overlap)
4. **Existing codebase anchor** (which modules to audit)

### Phase 2: Spawn Parent Issue

Use template at `templates/domain-parent-issue.md`. Title format:
```
Domain Sweep: <Domain Name> (<key concepts>)
```
Labels: `enhancement, priority:medium, cat:knowledge-domain, cat:engineering`

### Phase 3: Spawn 6 Research Subissues (sequential)

To avoid the `feedback_parallel_gh_issue_create_reverses_numbers` pitfall, create subissues sequentially. Templates in `templates/`:

| ID | Title pattern | Account | Template |
|----|---------------|---------|----------|
| R1 | Standards & Codes inventory | 2 (rigor) | `r1-standards.md` |
| R2 | Academic sources sweep | 2 (rigor) | `r2-academic.md` |
| R3 | Industry practice | 3 (broad) | `r3-industry.md` |
| R4 | LinkedIn expert mapping | 3 (broad) | `r4-marketing.md` |
| R5 | Code coverage audit | 1 (main) | `r5-code-audit.md` |
| R6 | Synthesis + gap spawning | 1 (main) | `r6-synthesis.md` |

### Phase 4: Update Parents with Cross-refs

After all 6 are created:
1. Comment on Domain Parent with subissue tree + account assignments
2. Comment on Feature Parent (#2667) with Domain entry added to queue

### Phase 5: Dispatch (User-Driven)

The user dispatches R1-R4 in parallel across accounts. Account 1 handles R5 (after R1+R2) and R6 (after all R1-R5).

## Account Distribution Playbook

| Account | Streams | Rationale |
|---------|---------|-----------|
| 1 (Claude / main) | R5 (code audit), R6 (synthesis) | Needs holistic codebase context + synthesis judgment |
| 2 (high-rigor: Codex or Gemini) | R1 (standards), R2 (academic) | Requires careful sourcing, citation discipline |
| 3 (broader sweep) | R3 (industry), R4 (LinkedIn) | Lower-rigor but wider net for current practice |

## Rules to honor

1. **Citations:** All gap subissues must conform to `.claude/rules/calc-citation-contract.md`
2. **LinkedIn = marketing surface only:** Per `feedback_llm_wiki_concept_pages_need_public_references`, never import LinkedIn content as primary technical source. R4 is for outreach tracking, NOT technical extraction.
3. **Sequential issue creation:** Per `feedback_parallel_gh_issue_create_reverses_numbers`, don't bake cross-refs at create-time when parallelizing.
4. **Inline issue refs:** Per `feedback_inline_gh_issue_url`, render `#NNNN` as Markdown hyperlink in chat output.
5. **No self-approval:** Per `feedback_never_offer_to_self_label_plan_approved`, never self-approve. Implementation gaps spawned by R6 still need user approval before code work begins.

## Domain queue

Priority order (update as domains complete):

1. **Offshore Hydrodynamics** — [#2668](https://github.com/vamseeachanta/workspace-hub/issues/2668) launched 2026-05-12
2. **Mooring Design** — queued (40 knowledge seeds anchor)
3. **Subsea Pipelines** — queued
4. **VIV / Riser Dynamics** — queued
5. **CCS / CO2 Transport** — queued

## Output artifacts

Each domain sweep produces:
- `docs/field-development/<domain>-coverage-map.md` (R6 deliverable)
- `docs/standards/<domain>-inventory.yaml` (R1 deliverable)
- `docs/research/<domain>-academic-references.md` (R2 deliverable)
- `docs/research/<domain>-industry-practice.md` (R3 deliverable)
- `docs/marketing/<domain>-linkedin-experts.yaml` (R4 deliverable)
- Gap implementation subissues in `digitalmodel` (or relevant repo)
- llm-wiki ingestion checklist for synthesized concepts

## Related skills

- `field-dev-code-recon` — single-source predecessor pattern (still useful for quick LinkedIn extraction)
- `gsd:ingest-docs` — for ingesting docs already in hand
- `gsd:new-milestone` — when a domain sweep reveals enough work to constitute a milestone

## Related memory

- `project_domain_knowledge_sweep` — durable workflow record
- `project_llm_wiki_strategic_role` — why coverage gaps are first-class defects
- `feedback_llm_wiki_concept_pages_need_public_references` — root cause for shift from LinkedIn-only sourcing
