# WRK-5104: GitHub Issue as Human Gate — Plan

## Approach: Comment-Based Approval + Stage Audit Trail

At every stage exit, `exit_stage.py` posts a stage-completion comment on the GitHub issue.
At human gate stages, it additionally posts an "awaiting approval" comment and the hook
blocks until user confirmation is found.

## Implementation Steps

1. Add `--comment` and `--read-comments` modes to `update-github-issue.py`
2. Post stage comments from `exit_stage.py` at every stage exit
3. Update `enforce-human-gate.sh` to read GitHub comments before local evidence
4. Add `wait-for-approval.sh` polling script (60s interval, 30min timeout)
5. Offline fallback: `SKIP_GATE_GITHUB_CHECK=1` env var + gh auth check

## Acceptance Criteria

- [ ] Every stage exit posts a completion comment on the GitHub issue
- [ ] Human gate stages (1, 5, 7, 17) post "AWAITING APPROVAL" comment
- [ ] `enforce-human-gate.sh` reads GitHub comments for approval before checking local files
- [ ] Offline fallback: local evidence still works when `gh` unavailable
- [ ] Works with existing issue body updates (no regression)

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Exit non-gate stage → comment posted | happy | `gh issue view` shows stage completion comment |
| Exit gate stage without approval → blocked | happy | Hook returns exit 2 with message |
| Post approval comment → gate passes | happy | Hook returns exit 0 |
| `gh` unavailable → local fallback | edge | Local evidence check runs, gate works as before |
| `SKIP_GATE_GITHUB_CHECK=1` → skip | edge | GitHub check skipped entirely |
| Approval comment before awaiting → rejected | edge | Only comments after "AWAITING" count |

## Pseudocode

1. `update-github-issue.py --comment`: extract issue number from frontmatter → `gh issue comment <num> --body <msg>`
2. `exit_stage.py._post_stage_comment()`: check issue ref → build comment text (DONE vs AWAITING) → call update-github-issue.py --comment
3. `enforce-human-gate.sh._check_github_approval()`: read frontmatter → gh auth check → gh issue view --json comments → jq: find last AWAITING index → check for approved after it → return 0/1/2
4. `wait-for-approval.sh`: loop 30x → gh issue view → jq approval check → sleep 60s → timeout after 30min
