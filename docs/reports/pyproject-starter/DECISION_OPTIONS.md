# pyproject-starter archived remote decision memo

Date: 2026-04-13
Issue: #2259
Repo: `pyproject-starter`
Ahead commit: `cd6eae9 chore(sync): auto-sync 2026-02-23`

## Executive summary
The archived/read-only remote means `pyproject-starter` cannot be normalized by the standard repo-sync workflow. The only local ahead commit is large and destructive, removing substantial Agent OS and project-template content. It should not be replayed automatically into any successor location.

Recommended default: Option B (`archive-only`) unless a human explicitly wants to retire `pyproject-starter` and port a curated subset into a new template home.

## Facts
- Remote is archived/read-only
- Local branch: `master`
- Ahead by 1 commit: `cd6eae9`
- Diff size:
  - 137 files changed
  - 2 insertions
  - 37,493 deletions
- Preservation artifact exported to:
  - `docs/reports/pyproject-starter/cd6eae9-auto-sync-2026-02-23.patch`

## What the commit appears to do
The commit removes broad swaths of:
- `.agent-os/`
- `agent_os/`
- `agents/`
- top-level docs and command wrappers
- packaging/build files

This looks closer to a mass retirement or failed sync/prune event than a normal maintenance change.

## Decision options

### Option A — Abandon
Meaning:
- Treat `cd6eae9` as unwanted local drift
- Keep patch artifact only for historical reference
- Do not migrate any part of it anywhere

Use when:
- `pyproject-starter` is obsolete
- the deleted content has already been replaced elsewhere
- no consumer depends on this repo as a canonical template

Pros:
- simplest
- no risk of reintroducing destructive changes elsewhere

Cons:
- permanently drops any potentially intentional cleanup embodied in the commit
- future readers may wonder whether useful intent was discarded

Recommended safeguards:
- close #2259 with explicit note: "commit intentionally abandoned; patch retained for audit"

### Option B — Archive-only
Meaning:
- Preserve the patch and decision notes in workspace-hub
- Do not replay the commit into any repo
- Mark the exception as known and documented

Use when:
- there is no clear successor repo
- the commit is too destructive to trust automatically
- you want reversible preservation without operational rollout

Pros:
- safest default
- preserves evidence without contaminating active repos
- supports future selective review

Cons:
- does not resolve whether some subset should survive long-term

Recommended safeguards:
- keep #2259 open until an explicit preserve/abandon decision is recorded
- reference the patch artifact and this memo in the issue

### Option C — Selective port
Meaning:
- manually inspect `cd6eae9`
- identify small intentional pieces worth preserving
- port only those pieces into a new writable home, likely a template path/repo

Use when:
- `pyproject-starter` still matters as a template lineage source
- a successor location is chosen explicitly
- there is confidence that only a subset of the commit is valuable

Candidate destination classes:
- `templates/pyproject-starter/` in workspace-hub
- a new dedicated writable template repo
- documentation-only historical migration note if code should not move

Pros:
- salvages intentional value without replaying the full destructive diff

Cons:
- requires manual analysis
- highest human effort
- easiest option to get wrong if rushed

Recommended safeguards:
- review by diff section, not just commit message
- port in small commits with justification
- do not use blind cherry-pick/replay

## Recommendation
Current recommendation: Option B (`archive-only`) as the immediate operational stance.

Why:
1. remote is archived/read-only
2. no clear successor repo was identified automatically
3. the ahead commit is too destructive for automatic migration
4. archive-only preserves future optionality without spreading risk

## Exit criteria for #2259
Choose and record one:
- `abandon`
- `archive-only`
- `selective-port`

Minimum closure note should include:
- chosen option
- rationale
- whether the patch artifact remains the canonical preservation record
- whether any follow-up migration issue is required
