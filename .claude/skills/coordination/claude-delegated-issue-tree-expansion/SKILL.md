---
name: claude-delegated-issue-tree-expansion
description: Use Claude subagents for read-only gap analysis to expand an umbrella GitHub issue into a layered tree of focused child issues, then create the issues locally and update the issue map/docs.
version: 1.0.0
---

# Claude-delegated issue-tree expansion

Use when:
- the user wants "future GH issues" or a roadmap expanded into child issues
- there is already an umbrella issue and a growing issue tree
- you want parallel reasoning from Claude, but repo writes must remain in the main session

## Why this pattern works

`delegate_task` subagents are good at read-only analysis and decomposition, but they should not be trusted for repo writes. Have Claude teams analyze different lanes in parallel, then create issues/doc updates yourself in the main session.

This worked well for expanding the weekly ecosystem execution/intelligence review initiative into multiple layers:
- umbrella issue
- framework issues
- operational refinement issues
- implementation child issues

## Pattern

1. Ground the tree first
- Read the umbrella doc/issue map.
- Inspect existing GitHub issues to avoid duplicates.
- Verify the canonical doc actually exists in the current worktree before delegating. If links were added earlier but the file is missing locally, recreate/fix it in the main session first.
- Identify decomposition lanes, e.g.:
  - machine readiness / operations
  - intelligence accessibility / knowledge systems
  - automation / reporting / governance

2. Delegate read-only analysis to Claude in parallel
- Use `delegate_task` with `acp_command='claude'` and `toolsets=['terminal','file']`.
- Ask each subagent for:
  - 3-5 non-duplicate child issues
  - title
  - rationale
  - deliverables
- Keep each lane self-contained and explicit about already-existing issues.

Example subagent framing:
- "Propose concrete child GitHub issues under #2138... avoid duplicates... return issue titles, rationale, deliverables."

3. Synthesize locally
- Review subagent summaries.
- Select only the strongest, non-overlapping child issues.
- Prefer implementation slices over vague umbrella restatements.

4. Create issues yourself in the main session
- Write each issue body to `/tmp/*.md`.
- Use `gh issue create ... --body-file ...` from the real repo.
- Create a small, coherent batch each round (about 4-7 issues worked well; 6 was a reliable default) rather than dumping dozens of siblings at once.
- Use parallel tool calls when creating a batch of issue-body temp files or multiple `gh issue create` calls that are independent.
- Do not ask subagents to create files/issues; keep all persistence local.

5. Update the canonical issue map
- Patch the main planning/review doc to add the new issue IDs.
- Add a comment to the umbrella issue summarizing the newly created child issues after every wave, not just at the end.
- Verify by reading the updated doc section and `gh issue view` for each created issue.
- If a doc link was added earlier but the target file is now missing locally, recreate the file first, then restore README/doc links before continuing the tree expansion. This happened in practice: README links existed while the canonical weekly-review doc was missing from the worktree.
- After each round, identify the next best split points (for example: Linux vs Windows writer, schema vs validator, runner vs schedule registration) before launching another delegation wave.
- Once the tree gets deep, explicitly branch the next wave by implementation pressure. A pattern that worked well was:
  - Windows/tool-validation branch
  - publication/promotion-hardening branch
  - registry/governance branch
- Keep the doc's related-issues list append-only and ordered by dependency depth so later waves stay legible.

5a. Favor operationally meaningful children over more umbrella restatements
- Prefer issues like `rollback journal`, `pre-promotion gate`, `shared-asset placement`, `suppression renewal queue`, or `provider-specific budgets` over generic restatements like `improve automation`.
- Good deep-child issues usually do one of four things:
  1. define a narrow contract/schema
  2. implement one adapter/writer/runner
  3. add a targeted fixture/smoke/snapshot suite
  4. enforce a governance gate or recovery path

6. Recurse only on the strongest branches
- Do not deepen every branch at once.
- Pick the branches with the clearest implementation path and the highest dependency pressure.
- A practical pattern that worked well was:
  - round 1: umbrella -> 3 broad lanes
  - round 2: lane-level child issues
  - round 3+: split only the hottest branches (for example Windows evidence, publication hardening, registry integration)
- Keep each wave small enough that the canonical issue map stays readable.

## Recommended lane structure

For broad ecosystem initiatives, use three Claude lanes in parallel:
1. machine readiness / execution routing
2. intelligence accessibility / freshness / discoverability
3. automation / reporting / governance

Then, if needed, do another round splitting the best new issues into implementation-level children.

As the tree gets deeper, a highly reusable second-stage branch pattern is:
1. Windows/tool-validation or machine-specific execution branch
2. publication/promotion hardening branch
3. registry/governance/actionability branch

This branch pattern worked well because each lane had a distinct failure mode:
- Windows/tool-validation: adapters, smoke fixtures, launcher/scheduler plumbing, mixed-state reporting
- publication/promotion: staged promotion, rollback, checksums, shared-asset lifecycle, recovery-state tests
- registry/governance: drift budgets, suppressions, lineage, owner assignment, escalation

## Good child-issue characteristics

Prefer issues that are:
- directly buildable
- narrow enough for one implementation pass
- clearly parented to an existing issue
- not duplicative of schema/template/automation issues already open

Good examples:
- schema + generated view
- validator CLI
- seeded registry generator
- Linux writer vs Windows writer
- runner wrapper vs schedule registration

## Pitfalls

- Do not rely on delegate_task for file writes or repo changes.
- Do not create too many sibling issues at once if they overlap heavily.
- Avoid duplicating existing umbrella issues with slightly different wording.
- Always update the canonical doc/issue map after issue creation; otherwise the tree becomes invisible.

## Minimal verification checklist

- [ ] new issues exist via `gh issue view`
- [ ] canonical doc lists the new issue IDs
- [ ] umbrella issue has a summary comment linking the new children
- [ ] no obvious duplicate with already-open issues in the same tree
- [ ] branch names in the latest wave are still meaningful (avoid tiny sibling issues with no independent value)

## Stop condition

Stop deepening the tree when the next issues become mostly one of these anti-patterns:
- implementation steps too small to stand alone
- multiple proposed issues would land in the same file/PR anyway
- the next child issue is just a rewording of its parent
- governance/reporting branches are producing more tracking than execution value

A good stopping point is when each remaining issue is clearly assignable to a single implementation pass or review pass without further decomposition.

## Reusable output structure

When reporting back, group by lane:
- Machine readiness / operations
- Intelligence accessibility
- Automation / reporting

Then list:
- issue number
- title
- URL

This makes it easy to continue decomposition in the next round.