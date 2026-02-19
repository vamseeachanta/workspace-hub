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
