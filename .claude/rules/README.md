# Rules Directory

> Coding standards and guidelines for this workspace.

## Available Rule Files

| File | Description |
|------|-------------|
| [security.md](./security.md) | Secret management, input validation, injection prevention |
| [testing.md](./testing.md) | TDD mandate, coverage targets, test organization |
| [coding-style.md](./coding-style.md) | Naming conventions, size limits, imports |
| [git-workflow.md](./git-workflow.md) | Branch naming, commits, PR process |
| [patterns.md](./patterns.md) | Allowed/prohibited patterns, error handling, logging |

## Loading Rules On-Demand

Reference specific rules in your conversations:

```
@.claude/rules/security.md
@.claude/rules/testing.md
```

Or load all rules:
```
@.claude/rules/
```

## Referencing Rules

When discussing code that violates these rules:

1. Cite the specific rule file and section
2. Explain why the rule exists
3. Suggest the compliant alternative

Example:
> This violates `security.md > Secrets Management`.
> API keys must be loaded from environment variables, not hardcoded.

## Updating Rules

1. Discuss proposed changes with the team
2. Update the relevant rule file
3. Commit with message: `docs(rules): update <rule-file>`
4. Notify team of changes

## Rule Precedence

1. Project-specific CLAUDE.md overrides
2. These rule files
3. General best practices
