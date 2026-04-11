---
name: issue-tree-decomposition
description: Break a large umbrella GitHub issue into a layered tree of focused follow-on issues using read-only subagent analysis, then create the issues locally and update docs/parent issue with the issue map.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Issue Tree Decomposition

Use when a broad initiative or recurring review needs to be turned into a structured set of future GitHub issues.

## When to use
- User asks to "create future gh issues"
- There is one umbrella issue but implementation needs multiple focused tracks
- You want to split work by lanes such as operations, knowledge, automation, reporting
- You want Claude subagents to help with analysis, but repo writes must stay in the main session

## Core pattern
1. Identify the umbrella issue and current related issues.
2. Add or update a single documentation page that describes the initiative and its current issue map.
3. Use `delegate_task` with Claude subagents for READ-ONLY gap analysis by lane.
4. Ask each subagent for:
   - 2-5 non-duplicate child issue proposals
   - title
   - rationale
   - deliverables
5. Create the selected issues locally in the main session with `gh issue create`.
6. Update the initiative doc with the new issue links.
7. Comment on the umbrella issue summarizing the new split.
8. Verify the issue URLs and the doc updates.

Use `todo` to manage each wave explicitly:
- delegate analysis
- create issues
- update doc/parent issue
- verify

This makes repeated decomposition waves much safer when you are going 3-5 layers deep.
## Important constraint
Subagents are for analysis only.
Do NOT rely on delegate_task subagents to write repo files or create GitHub issues. They run in isolated sandboxes and returned summaries are compressed. Use them to think; do the writes yourself.

Two practical lessons:
- Local/open-issue snapshots can lag behind newly created issues. For the latest parent/child grounding, prefer live `gh issue view` calls in the main session.
- If the initiative doc has been linked from README files but is unexpectedly missing in the working tree, recreate it immediately from the current issue map instead of stalling. Then re-link or re-patch the README surfaces as needed.

## Recommended lane split
A good first pass is 3 parallel subagents:
- machine readiness / execution operations
- intelligence accessibility / knowledge systems
- automation / reporting / governance

A good second pass is to recurse one level deeper on the strongest tracks:
- schema/contracts
- evidence artifacts
- entry points / registry
- runner / artifact schema

A good third pass is to split the most implementation-heavy children into platform-specific or integration-specific issues. In practice, these often become:
- Windows no-SSH implementation slices: native PowerShell collector, Git Bash launcher/path bridge, local drop-path handling
- reporting/publication slices: fixture corpus, history index/latest manifest, publication bundle assembler, renderer, navigation tests
- registry integration slices: audit-ingestion path, machine/path alias schema, shared resolver library, coherence validator

Pick only the best 1-3 proposals per lane per round. Do not create every possible issue the subagent suggests. Prefer an issue tree that is deep enough to be executable, but still legible.
## Issue-writing template
Each child issue should usually contain:
- Summary
- Why
- Scope
- Deliverables
- Parent / related issues

Keep titles specific and implementation-ready. Prefer one concrete artifact or contract per issue.

## Good child issue shapes
- define schema
- create registry
- add runner
- add validator
- emit evidence bundles
- create entry-point page
- add fixture coverage
- define artifact layout

## Avoid
- duplicate issues that restate the umbrella issue
- vague issues like "improve intelligence accessibility"
- mixing multiple implementation layers in one issue
- relying on subagent-written files

## Verification checklist
- `gh issue view <id>` works for each created issue
- initiative doc links all new issues
- umbrella issue has a summary comment with the latest split
- issue titles are non-overlapping and map cleanly to parents

## Minimal execution recipe
1. Read umbrella issue and existing related docs.
2. Create or update a single initiative doc in `docs/`.
3. Run 3 Claude subagents with lane-specific prompts.
4. Pick the best 1-3 proposals per lane.
5. Write issue bodies to `/tmp/*.md`.
6. Use parallel tool calls where safe:
   - write multiple `/tmp` issue bodies in parallel
   - create multiple `gh issue create` calls in parallel
7. Patch the initiative doc with the expanded issue map.
8. Comment on the umbrella issue with the new issue numbers after each wave.
9. Verify with `gh issue view` and `read_file`.
10. If continuing deeper, recurse from the strongest new children rather than reopening the whole umbrella scope.

## Example outputs this pattern tends to produce
- umbrella recurring review
- framework layer: checklist, matrix, map, automation, artifact model
- operational refinement layer: routing, heartbeat, query packs, scorecard
- implementation child layer: schema, entry page, evidence bundle, runner, validator
