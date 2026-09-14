# Legal Scanning Reference

> Detailed scan commands and deny list management for legal compliance.
> Rule statements live in `.claude/rules/legal-compliance.md`.

## Runtime contract and coverage

Require Bash 4.4+ and ripgrep (`rg`) on PATH. Provider-bundled executable discovery
and the grep fallback are removed. `--help` and usage diagnostics work without rg.
Missing rg reports `RIPGREP_REQUIRED` and exits 2; search backend errors preserve
stderr, report `LEGAL_SCAN_INCOMPLETE` and exit 2. A completed search with block
findings exits 1; no block findings exits 0. Reject every nonzero status.
An incomplete scan takes precedence over partial findings. User ripgrep config
is ignored with `--no-config` so it cannot silently suppress matches.

Coverage retains ripgrep's existing exclusions, 1 MB file limit and default binary
file handling. Tree traversal skips dot-files and dot-directories, including
`.claude/` and `.github/`, and does not follow recursively encountered links.
Explicit diff-file arguments can include hidden paths. File contents are searched;
filenames are not themselves searched. The deny list excludes `scripts/legal/`.
This is not coverage parity with the former grep fallback, which ignored exclusion
arguments. Empty/unparseable pattern sets and empty/fully excluded diffs can still
exit 0 without searching; those cases remain separate hardening work.
Git-diff failures (including missing HEAD or a non-repository target) are also
suppressed by the existing diff-selection code and can report PASS without a search.
The backend repair does not qualify that path; a PASS requires a verified nonempty
selection and active patterns.

The same-repository strict-scan CI job verifies/provisions rg and runs `tests/legal`
before its full-root scan, which omits those hidden directories. This does not
establish machine-fleet readiness.
Machine prerequisite qualification belongs in `scripts/setup/verify-setup.sh`;
this repair does not change machine settings or install local hooks.

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

## Historical pre-commit integration (CP-stream repos)

The following table records the historical WRK-278 wiring, not verified current
installation. The 2026-09-13 caller audit found digitalmodel using a different
public-surface hook; the other two checkouts were unavailable on this machine.

| Repo | Deny list | Hook entry |
|---|---|---|
| `digitalmodel` | `.legal-deny-list.yaml` (158 lines) | `../scripts/legal/legal-sanity-scan.sh --repo=digitalmodel` |
| `client-d` | `.legal-deny-list.yaml` (67 lines) | `../scripts/legal/legal-sanity-scan.sh --repo=client-d` |
| `mkt-a` | `.legal-deny-list.yaml` (146 lines) | `../scripts/legal/legal-sanity-scan.sh --repo=mkt-a` |

The hook uses `language: script` with `pass_filenames: false` so it always scans the full repo tree against the merged global + local deny lists. The `entry` path is relative to the submodule root (one level up `../` reaches the workspace-hub `scripts/` tree).

### Hook behaviour
- Exits 0 (pass) when no block-severity violations found
- Exits 1 (fail) when block violations found — commit is blocked
- Exits 2 on usage, resolution, dependency or incomplete-scan errors — commit is blocked
- The script anchors global policy to its own workspace root. Named repositories
  resolve through explicit registered roots or nested/sibling/walk-up defaults.

Phase D/E document-index callers reject nonzero scanner status, but currently
pass unsupported positional targets and permit missing-script bypasses. Phase E
also permits timeout/OSError bypasses. Their effective coverage requires separate
qualification; caller presence alone is not evidence of enforcement.

### Running manually from workspace root
```bash
./scripts/legal/legal-sanity-scan.sh --repo=digitalmodel
./scripts/legal/legal-sanity-scan.sh --repo=client-d
./scripts/legal/legal-sanity-scan.sh --repo=mkt-a
```
