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

## Pre-commit Integration (CP-stream repos)

The following CP-stream repositories have the legal scan wired into `.pre-commit-config.yaml` as a local hook (WRK-278):

| Repo | Deny list | Hook entry |
|---|---|---|
| `digitalmodel` | `.legal-deny-list.yaml` (158 lines) | `../scripts/legal/legal-sanity-scan.sh --repo=digitalmodel` |
| `saipem` | `.legal-deny-list.yaml` (67 lines) | `../scripts/legal/legal-sanity-scan.sh --repo=saipem` |
| `acma-projects` | `.legal-deny-list.yaml` (146 lines) | `../scripts/legal/legal-sanity-scan.sh --repo=acma-projects` |

The hook uses `language: script` with `pass_filenames: false` so it always scans the full repo tree against the merged global + local deny lists. The `entry` path is relative to the submodule root (one level up `../` reaches the workspace-hub `scripts/` tree).

### Hook behaviour
- Exits 0 (pass) when no block-severity violations found
- Exits 1 (fail) when block violations found — commit is blocked
- The script resolves `WORKSPACE_ROOT` from its own location, so the `--repo=<name>` argument must match the submodule directory name at workspace root

### Running manually from workspace root
```bash
./scripts/legal/legal-sanity-scan.sh --repo=digitalmodel
./scripts/legal/legal-sanity-scan.sh --repo=saipem
./scripts/legal/legal-sanity-scan.sh --repo=acma-projects
```
