# CLI consolidation procedure

The local inventory distinguishes independently installed Claude Code and Codex
commands from aliases and proposes consolidation into a user npm prefix. All
commands printed by the tool are proposals. The inventory performs no network
requests, executes no installed CLI, and changes no files. It is POSIX/Linux only;
Windows npm layouts are unsupported and the command exits with status 2 there.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-20 | Add metadata-only inventory and a dry-run procedure to distinguish duplicate installations from aliases. |
| 1 | 2026-10-21 | Retain inferred user prefixes, count adjacent binaries separately, limit metadata claims and reject unsupported Windows layouts. |
| 2 | 2026-10-22 | Detect Snap packages without launchers, group Snap aliases and add structured acceptance evidence without implying live completion. |

## Basis and scope

The installation preference and desktop-component exclusion follow repository
issue 3964. Package identifiers follow the existing
`scripts/setup/lib/install-provider-clis.sh` and `scripts/install/pin-codex.sh`.
PATH winners follow the first executable file in the supplied PATH, matching the
external-command search rule. Shell functions, aliases and command hash caches
are outside this filesystem inventory.

The script uses only the Python standard library:

```sh
python3 scripts/maintenance/cli_consolidation_plan.py
python3 scripts/maintenance/cli_consolidation_plan.py --npm-prefix "$HOME/.npm-global"
```

Additional prefixes inside the user root are preferred in argument order, followed
by metadata-matched inferred user npm prefixes, with the PATH winner first, then
`.npm-global`, `.local`, and `.npm`. Ties among inferred prefixes retain discovery
order. System prefixes may be inspected but are
never selected as the preferred user installation. An empty `--path ''` disables
PATH lookup; empty elements within a nonempty PATH denote the current directory.
`--home` and `--system-root` support isolated fixtures. Custom npm prefixes must
be supplied explicitly when they cannot be inferred from PATH launcher targets.

Search covers PATH entries, user `bin` and `.local/bin`, npm prefix launchers and
package folders, NVM/Volta/fnm installation prefixes, system `usr`, `usr/local`
and `bin` locations, and Snap wrappers. Discovery is bounded rather than a
recursive scan of the machine. Desktop application bundles are not searched;
do not add their internal directories to the inventory PATH or npm prefixes.

Each installation reports its launchers, inferred installation method, metadata
version and winning launcher. Symlink aliases share a package identity. A regular
launcher outside the package directory is counted separately and receives manual
review, even when package metadata exists beside its prefix. Launcher contents
are not used to establish ownership. Snap
commands retain separate identities even when they resolve to the same Snap
executable. Only matching npm package names qualify versions; absent, malformed
or mismatched metadata is reported as `UNKNOWN`. Snap versions are read from
simple scalar fields in `meta/snap.yaml`; unsupported YAML remains unknown.
Binary version strings are never extracted or executed. Unknown installations
receive manual-review instructions rather than deletion commands.

Snap installation roots are inspected even when their command wrappers are
absent. A root with unreadable or mismatched metadata remains an unknown
installation, so a missing launcher cannot hide a possible duplicate. Symlink
chains through a tool's Snap wrapper share that tool's Snap identity. The chain
is inspected before resolving the shared Snap executable, which does not
identify an individual package. Relative links and link cycles are handled
without executing their targets. Independent regular files remain separate.

## Structured acceptance evidence

```sh
python3 scripts/maintenance/cli_consolidation_plan.py --format json
```

Both formats inspect the same bounded roots and use the same preferred-prefix
selection. JSON contains `status`, a scope statement and a `tools` mapping keyed
by `claude` and `codex`. Each tool includes `installation_count`,
`preferred_identity` (or null), `checks` and `installations`. Each installation
includes its identity, inferred kind, metadata version, discovered paths and
supplied PATH winner (or null). Keep JSON output private: it contains local paths.

The acceptance basis is issue 3964: one independent installation per command,
canonical resolution in fresh shells and agreement with live latest metadata.
No engineering equations, empirical coefficients or version constants apply.

| Check | PASS | FAIL | NOT_EVALUATED |
| --- | --- | --- | --- |
| `bounded_uniqueness` | Exactly one discovered identity with recognized metadata | More than one identity, including unknown copies | No identity or a single unknown identity |
| `preferred_user_npm` | Matching package in the preferred user prefix | Known copies exist, but none qualifies as user npm | Evidence absent or unknown without a qualifying user prefix |
| `supplied_path` | First executable on supplied PATH belongs to the preferred package | A different installation wins while a preferred package exists | No winner or no qualified preferred package |
| `latest_release` | Not produced | Not produced | Always; live registry and executable versions are not queried |
| `fresh_shells` | Not produced | Not produced | Always; startup files, aliases and shell caches are not evaluated |
| `functionality` | Not produced | Not produced | Always; installed commands are not executed |

The report's overall status is `FAIL` when any local check fails, otherwise
`NOT_EVALUATED`. It never reports overall `PASS`: even passing bounded checks
do not establish live maintenance acceptance. The process exit status describes
successful report generation, not acceptance. Consumers must read `status` and
individual checks. Text output remains the default and retains its existing
dry-run commands.

### Worked structured example

Use a synthetic user npm fixture and add a Codex Snap metadata root whose
launcher is missing. For Codex, the inputs are a user npm package with metadata
version `user-fixture`, a Snap package with version `snap-fixture`, and PATH
selecting the user npm launcher. The method groups by installation identity,
counts the distinct roots and compares the winning root with the preferred root.

The independent hand calculation is: one npm root plus one Snap root gives two
installations; two exceeds the issue's acceptance count of one. The selected
root equals the preferred root. The resulting Codex summary is:

```json
{
  "installation_count": 2,
  "checks": {
    "bounded_uniqueness": "FAIL",
    "preferred_user_npm": "PASS",
    "supplied_path": "PASS",
    "latest_release": "NOT_EVALUATED",
    "fresh_shells": "NOT_EVALUATED",
    "functionality": "NOT_EVALUATED"
  }
}
```

The overall status is `FAIL`. A correct PATH does not establish uniqueness.
`test_report_duplicate_fails_even_when_path_is_correct` constructs these inputs
and asserts the independently counted outcome. The fixture versions are labels,
not release claims. No package removal is performed by this example.

## Procedure and rollback

1. Run the inventory locally in each shell environment being checked. Keep the
   output private because it contains local paths. Record the original package
   versions, installation methods, npm prefixes, PATH and shell startup files.
   Preserve rollback copies of any startup files before editing them.
2. Review the proposed canonical user prefix. Install or update the official
   packages using the printed `npm install --global --prefix ...` commands.
   These operations require separate maintainer execution and network access.
3. Preserve existing PATH entries while placing the canonical prefix's `bin`
   directory first. Check noninteractive, login and interactive shell startup
   separately; an early return in a startup file can prevent later assignments.
4. Validate the replacement commands in fresh shells before removal. The
   maintainers shall separately check functionality and release agreement against
   current package metadata. Local installed metadata establishes neither.
5. Review each proposed uninstall command against the recorded package manager
   and prefix. System npm removal may require privileges; obtain authorization
   through the normal privilege mechanism. Snap removal is printed only when
   its metadata name matches the command. Leave desktop-managed components,
   authentication and unrelated configuration unchanged.
6. Re-run the inventory after removal. Accept consolidation only when each CLI
   has one independently installed command and all required shell environments
   select the canonical user installation. Aliases to that same installation
   are not additional copies. Unresolved manual-review rows prevent a uniqueness
   claim.

Rollback is performed by the maintainers using the recorded package manager,
prefix and exact prior version. For npm, the command form is
`npm install --global --prefix "$PREFIX" "$PACKAGE@$PREVIOUS_VERSION"`.
For Snap, preserve the revision and availability of a restorable package before
removal; a retained Snap snapshot alone is not a copy of the executable package.
If the prior package cannot be restored, postpone removal. Restore the preserved
shell startup files and recheck fresh shells. Do not delete authentication files
or desktop components as part of rollback.

## Worked example

Inputs below are synthetic relative fixture paths, not measured installations:

| Input | Value |
| --- | --- |
| User root | `example/user` |
| Preferred npm prefix | `example/user/.npm-global` |
| Other npm prefix | `example/system/usr/local` |
| PATH order | other prefix `bin`, then preferred prefix `bin` |
| Claude metadata versions | `system-fixture`, `user-fixture` |
| Codex installation | absent |

The method selects the first executable launcher on PATH, then groups resolved
package identities. The consolidation recommendation independently selects the
preferred user npm installation. Therefore the system Claude launcher wins
currently, the user Claude installation is retained, and the other Claude npm
package is proposed for removal after replacement validation. Codex requires an
installation before any removal can be proposed.

Representative proposed commands are:

```sh
npm install --global --prefix example/user/.npm-global @anthropic-ai/claude-code@latest
npm install --global --prefix example/user/.npm-global @openai/codex@latest
npm uninstall --global --prefix example/system/usr/local @anthropic-ai/claude-code
```

The focused test `test_user_npm_keep_system_remove` constructs this ordering in a
temporary filesystem and asserts the winner, retained prefix and uninstall
command directly. Other tests cover missing tools, aliases, version managers,
Snap shared executables, malformed metadata, nonexecutable launchers, excluded desktop
components and read-only behavior. Regressions also cover inferred-prefix
preference, independent adjacent binaries, metadata wording and Windows rejection.
Tests requiring POSIX shell or executable semantics are skipped on Windows; the
platform-rejection test remains enabled. No expected value comes from running a CLI.

```sh
python3 -m pytest tests/maintenance/test_cli_consolidation_plan.py -q -p no:cacheprovider
ruff check --no-cache scripts/maintenance/cli_consolidation_plan.py tests/maintenance/test_cli_consolidation_plan.py
```

## Limits

This is a plan, not evidence that a workstation has been consolidated or updated.
Custom native installers, package ownership databases, nonstandard prefixes,
shell functions and desktop internals require separate review. Inferred package
ownership is not cryptographic authentication. Files can change during discovery;
recheck evidence immediately before applying commands. Only the supplied shell
PATH is observed, and installed metadata can differ from executable behavior.
