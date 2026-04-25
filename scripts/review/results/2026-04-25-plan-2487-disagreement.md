# Disagreement report — plan #2487 (2026-04-25)

## Verdicts

| Provider | Verdict |
|---|---|
| codex | MAJOR |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### codex

- The plan is backdated relative to the issue it is supposed to implement. The plan header says `Date: 2026-04-24` and the derived artifact is fixed to `docs/reports/inventory-readiness-matrix-2026-04-24.md`, but GitHub issue `#2487` was created on `2026-04-25T02:48:59Z`. That makes the plan’s dating and artifact naming stale before implementation starts and weakens the credibility of the plan’s “verified 2026-04-25” evidence trail inside the same document. Citation: plan header / artifact map vs issue `#2487` metadata.
- A correctness-critical dependency is cited as if it were a retrievable source, but the file does not exist. The plan’s `Standards / contracts` table says `#2471 / docs/plans/2026-04-23-issue-2471-wiki-standards-path.md is required to define objective llm_wiki and calculation_code readiness`, yet fetching that path returns 404. If the plan treats that artifact as the basis for objective readiness scoring, the retrieval basis is incomplete. Citation: plan `Standards / contracts` table and failed fetch of `docs/plans/2026-04-23-issue-2471-wiki-standards-path.md`.
- The validator is specified to enforce quota targets that are not supported by current queue evidence and therefore can force fabricated “readiness.” The plan pseudocode and acceptance criteria require `at least 8 Codex candidates` and `at least 5 Gemini task entries across batches`, while `docs/reports/provider-work-queue.md` currently reports only `Execution-ready candidates: 3` for Codex and `1` for Gemini. A readiness matrix should measure present state; this contract instead hard-fails until the YAML invents enough candidates/tasks to satisfy the quota. Citation: plan `Pseudocode` / `Acceptance Criteria` vs `docs/reports/provider-work-queue.md`.
- The plan says readiness scoring “must not invent incompatible wiki metadata,” but it does not resolve a live schema contradiction in the very wiki contract it cites. `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` §8.1 makes `doc_key` a parent-mandated required frontmatter field for every wiki, while `knowledge/wikis/engineering/CLAUDE.md` lists only `title`, `tags`, `added`, and `last_updated` as required. Any readiness logic that uses wiki metadata as objective evidence without first handling that live contract violation is underspecified. Citation: plan `LLM Wiki pages consulted` section, operating model §8.1, and `knowledge/wikis/engineering/CLAUDE.md`.
- The plan’s implementation surface is internally stale: `Files to Change` says `Create | docs/plans/2026-04-24-issue-2487-inventory-readiness-spine.md`, but that file already exists and is the plan under review. That is a smaller defect than the blockers above, but it is still a concrete mismatch between the plan’s execution contract and repo state. Citation: plan `Files to Change` table vs fetched existing plan file.

### gemini

- Plan § `Evidence` claims `EXISTS: docs/plans/2026-04-24-issue-2481-calc-output-citation-contract.md`. This is empirically false. A `glob` search confirms no such file exists anywhere in the repository at HEAD.
- Plan § `Standards / contracts` claims `#2471 / docs/plans/2026-04-23-issue-2471-wiki-standards-path.md is required` for wiki schema definition. This relies on a non-existent file; a search confirms `docs/plans/2026-04-23-issue-2471-wiki-standards-path.md` is absent from the repository.
- Plan § `Pseudocode` states `validate dispatch_board: require at least 8 Codex candidates with issue IDs and rationale`. However, the cited `docs/reports/provider-work-queue.md` source explicitly states there are only `Execution-ready candidates: 3` for Codex. Mandating a minimum of 8 will mathematically fail or force the dispatch board to include unready candidates.
- Plan § `Evidence` claims "Issue statuses verified 2026-04-25T02:49:47Z via `gh issue view`: `#2487` OPEN". However, a grep search for issue `2487` across the local workspace issue JSON caches (`workspace_hub_issues.json`, `all_open_issues.json`, `workspacehub-open-issues.json`) returned zero matches, indicating the spine issue is not recorded or the cache is out-of-sync.

