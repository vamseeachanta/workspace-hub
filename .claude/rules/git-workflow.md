# Git Workflow Rules

> Consistent git practices enable efficient collaboration and clean history.

## Branch Naming

### Prefixes
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Urgent production fixes
- `chore/` - Maintenance, dependencies, configs
- `docs/` - Documentation only changes
- `refactor/` - Code refactoring without behavior change

### Format
```
<prefix>/<ticket-id>-<short-description>

Examples:
- feature/PROJ-123-user-authentication
- bugfix/PROJ-456-fix-login-redirect
- hotfix/PROJ-789-security-patch
- chore/update-dependencies
```

### Rules
- Use lowercase and hyphens
- Keep descriptions short but meaningful
- Include ticket ID when applicable

## Commit Messages

### Conventional Commits Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code change without feature/fix
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Rules
- Subject line: 50 characters max
- Use imperative mood ("add" not "added")
- Body: Wrap at 72 characters
- Reference issues in footer: `Fixes #123`

### Examples
```
feat(auth): add OAuth2 login support

Implement Google and GitHub OAuth providers with
secure token storage and refresh handling.

Fixes #234
```

## Pull Requests & Merging

See `.claude/docs/pr-process.md` for PR requirements, review process, merge strategy, and branch protection.

## Solo / Multi-Workstation Policy

> Single developer, multiple machines (ace-linux-1, ace-linux-2, acma-ansys05).

**Default: commit directly to `main`, push immediately after every commit.**
Never leave commits unpushed — push is part of the commit step.

| Situation | Action |
|---|---|
| Single-session WRK (most work) | Commit to `main` → push |
| Multi-session complex WRK (3+ files, >1 session) | Short branch → merge + push same day |
| Cross-machine work-in-progress | Push branch; pull on other machine |
| Nightly cron / automation | Commit to `main` → push |
| Experimental spike | Branch; discard or merge within 1 session |

**`finishing-a-development-branch` skill:** use only for multi-session branches.
For single-session work, skip it — just commit and push to main directly.

## Operational Guidelines

- Submodules: commit inside submodule first, then update pointer at hub level
- Never rebase diverged branches — use merge or `reset --hard origin/<branch>` after user confirmation
- Force-pushed refs: detect via `git rev-list --count HEAD..origin/main`; always fetch first
- Stash before pull when uncommitted changes exist; report stash pop conflicts, don't auto-resolve
- Windows: report path limitations (trailing spaces, long paths, symlinks) immediately, don't retry
- Shell scripts: use `#!/usr/bin/env bash`, ensure LF line endings (CRLF breaks MINGW)
