# Legal Compliance Rules

> Mandatory legal compliance practices for all code in this workspace.

## Client Reference Prevention

### Never Include Client Identifiers
- Client project names, codenames, and internal labels must NEVER appear in code
- Client-specific tool names and proprietary platform references are prohibited
- Client infrastructure identifiers (VPC names, cluster IDs, endpoints) must be removed
- References in comments, docstrings, variable names, and config values all count

### Deny List System
- Global deny list: `.legal-deny-list.yaml` at workspace root
- Per-project deny list: `.legal-deny-list.yaml` in each submodule
- Project lists extend (not replace) the global list
- Patterns support case-sensitive and case-insensitive matching

### Severity Levels
- **block**: Scan fails, PR cannot proceed until resolved
- **warn**: Flagged for review but does not block

## Code Porting Rules

### Immediate Scan After Import
- When porting code from a client project, run the legal scan immediately
- Do not commit ported code without first passing a legal scan
- Replace all client-specific references with generic equivalents

### Replacement Strategy
- Client project names → generic descriptive names (e.g., "safety_analysis")
- Proprietary tool names → generic equivalents (e.g., "Databricks" → "data platform")
- Client infrastructure → environment variables or config placeholders
- Client-specific file paths → relative or configurable paths

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

## Scanning Requirements

### When to Scan
- Before every PR creation (automated via pre-hook)
- After importing/porting code from external sources
- As a mandatory pre-gate in the cross-review cycle
- On demand via `scripts/legal/legal-sanity-scan.sh`

### Scan Commands
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

### Scan Failures
- Block-severity violations must be resolved before proceeding
- The scan exit code (0=pass, 1=fail) integrates with CI gates
- All violations include file path and line number for quick remediation
