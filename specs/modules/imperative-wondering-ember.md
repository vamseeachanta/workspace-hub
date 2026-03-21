# WRK-5104: GitHub Issue as Human Gate — Stage Approval via Issue Confirmation

## Context

Local human gates (stages 1, 5, 7, 17) are enforced by `enforce-human-gate.sh` checking local YAML evidence files. Agents bypass these by skipping `start_stage.py`/`exit_stage.py` and committing directly (observed in WRK-5101/5102/5103). GitHub is external state the agent cannot fake.

**Additional requirement**: GitHub issue should be updated at every stage (not just human gates), and stage comments should be posted to the issue at every stage transition to create an audit trail.

## Design

### Approach: Comment-Based Approval + Stage Audit Trail

At **every stage exit**, `exit_stage.py` posts a stage-completion comment on the GitHub issue. At **human gate stages**, it additionally posts an "awaiting approval" comment and the hook blocks until user confirmation is found.

### Key Files to Modify

| File | Change |
|------|--------|
| `scripts/work-queue/exit_stage.py` | Post stage comment on every exit; post "awaiting approval" at human gates |
| `scripts/knowledge/update-github-issue.py` | Add `--comment` mode for posting comments (currently only body edits) |
| `.claude/hooks/enforce-human-gate.sh` | Read approval from GitHub issue comments via `gh`, fall back to local |

### Implementation Steps

#### Step 1: Add `--comment` mode to `update-github-issue.py`

Add a new CLI flag `--comment "message"` that calls:
```
gh issue comment <issue-number> --body "message"
```

Also add `--read-comments` that returns recent comments for parsing:
```
gh issue view <issue-number> --comments --json comments
```

Reuse existing `_gh_run()` helper and `_get_issue_number()` from frontmatter.

#### Step 2: Post stage comments from `exit_stage.py`

In `_regenerate_lifecycle_html()` (or a new companion function), after the body update:
- Post a comment: `"## Stage {N}: {name} — DONE\n\nCompleted at {timestamp}"`
- At human gate stages (1, 5, 7, 17), post instead: `"## Stage {N}: {name} — AWAITING APPROVAL\n\nReview the issue sections above and comment 'approved' to proceed."`
- Non-blocking: failures log warnings but don't halt

#### Step 3: Update `enforce-human-gate.sh` to read GitHub comments

Before checking local evidence files, the hook:
1. Reads `github_issue_ref` from WRK frontmatter
2. Calls `gh issue view <number> --comments --json comments`
3. Searches for an "approved" comment posted **after** the "AWAITING APPROVAL" comment
4. If found → exit 0 (allow)
5. If not found → fall back to local evidence file check (existing logic)
6. If `gh` unavailable → fall back to local evidence file check

#### Step 4: Offline fallback

- `gh auth status` check at start of GitHub path
- If offline/unauthenticated → skip GitHub check, use local files
- Env var `SKIP_GATE_GITHUB_CHECK=1` as explicit escape hatch

### Approval Comment Format

```
approved
```

Simple lowercase "approved" anywhere in a comment body posted by the repo owner. This matches the existing pattern used in conversation ("i approve stage N").

### Acceptance Criteria

1. Every stage exit posts a completion comment on the GitHub issue
2. Human gate stages (1, 5, 7, 17) post "AWAITING APPROVAL" comment
3. `enforce-human-gate.sh` reads GitHub comments for approval before checking local files
4. Offline fallback: local evidence still works when `gh` unavailable
5. Works with existing issue body updates (no regression)

### Test Plan

| Test | Type | Expected |
|------|------|----------|
| Exit non-gate stage → comment posted | happy | `gh issue view` shows stage completion comment |
| Exit gate stage without approval → blocked | happy | Hook returns exit 2 with message |
| Post approval comment → gate passes | happy | Hook returns exit 0 |
| `gh` unavailable → local fallback | edge | Local evidence check runs, gate works as before |
| `SKIP_GATE_GITHUB_CHECK=1` → skip | edge | GitHub check skipped entirely |
| Approval comment before awaiting → rejected | edge | Only comments after "AWAITING" count |

### Scripts to Create

| Script | Purpose | Created in |
|--------|---------|-----------|
| (none — extends existing scripts) | | |

All changes extend `update-github-issue.py`, `exit_stage.py`, and `enforce-human-gate.sh`. No new scripts needed.

## Verification

1. Run a test WRK through stages 1-3, verify comments appear on GitHub issue
2. At stage 5 (human gate), verify "AWAITING APPROVAL" comment appears
3. Post "approved" comment on issue, verify hook allows exit
4. Test with `gh auth logout` → verify local fallback works
5. Run `bash scripts/work-queue/validate-wrk-frontmatter.sh WRK-5104` → exit 0
