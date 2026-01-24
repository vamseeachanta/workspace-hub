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

## Pull Request Process

### Before Creating PR
- Rebase on latest main branch
- Run all tests locally
- Self-review your changes
- Remove debug code and console logs

### PR Requirements
- Descriptive title following commit convention
- Link to related issue/ticket
- Summary of changes made
- Testing instructions
- Screenshots for UI changes

### Review Process
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
