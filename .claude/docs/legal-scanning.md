# Legal Scanning Reference

> Detailed scan commands and deny list management for legal compliance.
> Rule statements live in `.claude/rules/legal-compliance.md`.

## Scan Commands

```bash
# Scan a specific repo
./scripts/legal/legal-sanity-scan.sh --repo=worldenergydata

# Scan all submodules
./scripts/legal/legal-sanity-scan.sh --all

# Scan only changed files (fast, for PRs)
./scripts/legal/legal-sanity-scan.sh --repo=worldenergydata --diff-only

# JSON output for CI/CD
./scripts/legal/legal-sanity-scan.sh --repo=worldenergydata --json
```

## Deny List Management

### Every Repository Must Have
- A `.legal-deny-list.yaml` if it contains ported or client-adjacent code
- Patterns for all known client project names and proprietary tools
- Appropriate exclusions for files that legitimately reference terms (e.g., docs)

### Adding New Patterns
1. Add the pattern to the appropriate deny list (global or per-project)
2. Set `case_sensitive` based on the pattern's nature
3. Include a clear `description` for audit purposes
4. Run a full scan to check for existing violations
