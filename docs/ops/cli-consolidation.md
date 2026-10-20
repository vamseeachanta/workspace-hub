# CLI consolidation procedure

The local inventory distinguishes independently installed Claude Code and Codex
commands from aliases and proposes consolidation into a user npm prefix. All
commands printed by the tool are proposals. The inventory performs no network
requests, executes no installed CLI, and changes no files.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-20 | Add metadata-only inventory and a dry-run procedure to distinguish duplicate installations from aliases. |

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

The first additional prefix inside the user root is preferred, followed by
`.npm-global`, `.local`, and `.npm`. System prefixes may be inspected but are
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
version and winning launcher. Symlink aliases share a package identity. Snap
commands retain separate identities even when they resolve to the same Snap
executable. Only matching npm package names qualify versions; absent, malformed
or mismatched metadata is reported as `UNKNOWN`. Snap versions are read from
simple scalar fields in `meta/snap.yaml`; unsupported YAML remains unknown.
Binary version strings are never extracted or executed. Unknown installations
receive manual-review instructions rather than deletion commands.

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
components and read-only behavior. No expected value comes from running a CLI.

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
