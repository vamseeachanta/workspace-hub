# Entry handoff — Issue #81 perforating sub-issue authoring

Date: 2026-05-15
Repository: `vamseeachanta/llm-wiki` (sub-repo at `workspace-hub/llm-wiki`)
Predecessor session: see [`2026-05-15-issues-41-42-standards-routing-exit.md`](2026-05-15-issues-41-42-standards-routing-exit.md) (closeout) + this session's slate handoff in MEMORY.

## What this session must do

Author the perforating sub-issue ([llm-wiki #81](https://github.com/vamseeachanta/llm-wiki/issues/81)) under PE Phase 2 epic ([#73](https://github.com/vamseeachanta/llm-wiki/issues/73)). Scope:

- 1 standards page: `wikis/production-engineering/wiki/standards/api-rp-19b.md`
- 4 concept pages: `wikis/production-engineering/wiki/concepts/{perforating,perforating-shaped-charges,perforation-strategy,perforating-gun-systems}.md`
- 3 reverse cross-links into Phase 1 + drilling-engineering pages (see #81 body)
- 1 index.md update + 1 log.md entry
- Commit + push direct to main

Estimated wall-clock: 2-3 hours for a focused session with perforating references at hand. T2 scope.

## Approval status (do NOT re-plan)

- Epic [#73](https://github.com/vamseeachanta/llm-wiki/issues/73): `status:plan-approved` (set 2026-05-15)
- Marker: `llm-wiki/.planning/plan-approved/73.md` (committed at [`60b272a7`](https://github.com/vamseeachanta/llm-wiki/commit/60b272a7))
- Sub-issue #81: plan-approved by inheritance per issue-planning-mode skill
- **Do NOT** re-run discovery, re-plan, or re-review. The epic plan + #81 body fully scope this work.

## Authoritative references to read first (in order)

1. [llm-wiki#81 body](https://github.com/vamseeachanta/llm-wiki/issues/81) — full scope, public anchors, target wiki output, acceptance criteria
2. [Epic plan](https://github.com/vamseeachanta/llm-wiki/blob/main/docs/plans/2026-05-15-issue-73-pe-phase-2-completions.md) — Phase 2 context, cross-link directionality discipline
3. Phase 1 reference shape: `wikis/production-engineering/wiki/concepts/electric-submersible-pumps.md` (from sub-issue [#62](https://github.com/vamseeachanta/llm-wiki/issues/62) — pattern to mirror)
4. Existing PE wiki state: `ls wikis/production-engineering/wiki/concepts/` (verify cross-link target names before installing)

## Skills to load via Skill tool

- `superpowers:using-superpowers` (auto-loads at session start)
- Read `.claude/skills/coordination/issue-planning-mode/SKILL.md` (mandatory for any issue work; but DO NOT re-plan — gate already cleared)
- Honor `.claude/rules/calc-citation-contract.md` if perforation-skin or similar standards-derived formulas appear (live pilot at `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py:check_mbl_with_safety_factor`)

## Hard constraints (anti-patterns to avoid)

- **NO** vendor-confidential perforating manuals (Halliburton/Schlumberger/Baker Hughes/Owen proprietary content). Cite vendor-by-name as "vendor archetype" only.
- **NO** verbatim copying of API RP 19B paragraphs >30 words (paraphrase + cite). Paywalled standard — extract structure, not text.
- **NO** citations of `wikis/*/wiki/sources/` per [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) deny-list. Cite the canonical standards-page or concept page, not the sources-page entry.
- **NO** Hermes dispatch — catalog feedback (2026-05-14 dispatch went 0/6) explicitly recommends `claude-main-direct` for T1/T2 wiki-content scopes. Audit issue [#2696](https://github.com/vamseeachanta/workspace-hub/issues/2696) is the blocker for future Hermes use.
- **NO** self-approval of anything (per `feedback_never_offer_to_self_label_plan_approved`). Sub-issue is already plan-approved-by-inheritance — that's the only gate signal you need.

## Out of scope

- Phase 2 sub-issues 2 (sand control) and 3 (multi-zone & smart completions) — defer until #81 lands per epic-plan sequencing
- Phase 3 #74 work (matrix acid, hydraulic fracturing, refrac) — cross-phase dependency: Phase 2 must complete first
- #40 reservoir-eng work — separate plan, separate session
- Vendor-archetype deep-dive (concept-only abstraction; no proprietary algorithm details)

## Validation gates before commit

- `uv run pytest tests/test_completion_artifacts.py -v` — schema check for new pages (frontmatter, required sections)
- `uv run pytest tests/test_governance_artifacts.py -v` — no >30-word verbatim chunks from API RP 19B
- `uv run pytest tests/test_scan_source_families_safe.py -v` — no vendor-confidential PDF references
- Manual: `grep -c "perforating" wikis/production-engineering/wiki/index.md` — verify index updated
- Manual: tail `wikis/production-engineering/wiki/log.md` — verify iter entry exists

## Memory references active

These memories shaped how the slate work was executed; the next session should honor them:

- [[feedback_llm_wiki_concept_pages_need_public_references]] — concept pages need textbook/DOI/manual references; LinkedIn-only fails day-one lint
- [[feedback_check_parallel_work]] — scan for parallel sessions on PE Phase 2 before starting (`pgrep -af "claude -p"`)
- [[feedback_multi_agent_commit_serialization]] — single-session execution; if you need to coordinate with parallel work, serialize commits
- [[feedback_discovery_first_on_stale_plan_approved]] — even though #81 just opened, do a quick `ls wikis/production-engineering/wiki/concepts/` to verify nothing's been written since #81 was created (parallel session #75/#76/#79 work was happening on llm-wiki main concurrently)
- [[feedback_inline_gh_issue_url]] — render `#NNNN` as Markdown hyperlinks in chat output
- [[feedback_html_default_artifact]] — if surfacing rich plans/reports, default to HTML; markdown for harness/skill/rule files

## Stopping points

1. After API RP 19B standards page lands: natural checkpoint — verify frontmatter schema passes
2. After main `perforating.md` overview lands: checkpoint — verify cross-link skeleton works
3. After all 5 pages land: cross-link installation phase begins (3 reverse links into Phase 1 + drilling-engineering)
4. After cross-links: index + log + commit + push direct to main
5. After push: comment on epic [#73](https://github.com/vamseeachanta/llm-wiki/issues/73) closing the sub-issue with implementation-record summary; close #81 via `Closes #81` commit trailer OR explicit `gh issue close`

## End-of-session expectations

- 5 new pages on llm-wiki main
- 3 Phase 1 / drilling-engineering pages amended with reverse cross-links
- index.md page_count updated (~28 → ~33)
- log.md has iter entry for this ingest
- Sub-issue #81 CLOSED
- Epic #73 has progress comment noting sub-issue 1 complete; sub-issues 2 + 3 ready for fresh sessions

## Repo state at session entry

```
$ cd workspace-hub && git log --oneline -3
93291a331 chore(solver): daily dashboard regeneration  # pre-existing
62d0b1aeb review(plans): Claude r1 adversarial review for 4 plans  # this session
2375ea4cc  # NOTE: in worldenergydata repo only, BSEE bridge merge

$ cd llm-wiki && git log --oneline -5
60b272a7 chore(approval): record markers for #73 + #74 plan-approved
00bba020 (parallel-session work — plans #75/#76/#79)
389ce59e plan(llm-wiki): apply Claude r1 MINOR fixes
6826df70 plan(llm-wiki): apply Claude r1 review findings
7822c731 plan(llm-wiki): add 3 plans — #40 + #73 + #74
```

Background processes: Hermes gateway (pid changes per session) — IGNORE, not relevant to wiki authoring. Do NOT dispatch anything to Hermes.

External-action status at handoff: no pending sends, no pending PRs awaiting merge in workspace-hub or llm-wiki. worldenergydata is clean (PR #413 merged, ruleset enforcement restored).
