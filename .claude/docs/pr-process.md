# Pull Request Process

> Extracted from `rules/git-workflow.md` for detailed reference.

## Before Creating PR
- Rebase on latest main branch
- Run all tests locally
- Self-review your changes
- Remove debug code and console logs

## PR Requirements
- Descriptive title following commit convention
- Link to related issue/ticket
- Summary of changes made
- Testing instructions
- Screenshots for UI changes

## Review Process
- Minimum 1 approval required
- Address all comments before merge
- Re-request review after changes
- Keep PRs small (< 400 lines changed)

## Merge Strategy

### Main Branch
- Use **squash merge** for feature branches
- Creates clean, linear history
- Commit message should summarize all changes

### Release Branches
- Use **merge commit** to preserve history
- Tag releases with semantic versions

### Hotfixes
- Cherry-pick to affected branches
- Document in commit message

## Branch Protection

### Main Branch Rules
- Require PR for all changes
- Require passing CI checks
- Require up-to-date branch
- No force pushes
