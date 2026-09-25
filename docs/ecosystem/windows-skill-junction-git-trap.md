# Windows junction-backed skill directories and git

## What

On Windows machines, provider skill directories are NTFS junctions pointing at the
shared ecosystem skills source, not real directories:

- `.codex/skills` -> ecosystem skills source (marker: `.codex/.skills-link-marker`)
- `.gemini/skills` -> ecosystem skills source (marker: `.gemini/.skills-link-marker`)
- `.claude/skills/{guidelines,meta,workflows}` -> linked subdirs
  (markers: `.claude/skills/.meta-link-marker`, `.claude/skills/.workflows-link-marker`)

The marker files (content: `ecosystem-link`) are the repo record. The junction
contents are machine-local and must stay untracked:

- `.codex/.gitignore` and `.gemini/.gitignore` ignore `skills/`
- `.claude/skills/.gitignore` ignores `guidelines/`, `meta/`, `workflows/`

## The trap

Git does not treat NTFS junctions as symlinks. `git add -A` (or `git add .`)
follows the junction and stages every target file as a regular file.

2026-09-22 (ACMA-HOU-RDS02): this vendored 8,375 skill files (~1M insertions) into
`codex/3524-rdp-mic-plan` in a single commit. Caught in verification the same day;
the commit was rebuilt without the vendored files and the branch force-pushed
(it was minutes old and lease-protected).

## Rules

1. Never `git add` a junction-backed path. If in doubt, check first:
   `(Get-Item .codex\skills).LinkType` should report `Junction`, and
   `git check-ignore -v .codex/skills` should show the gitignore rule.
2. The machine-branch sync (`scripts/sync/sync-machine-branch.sh`) and any
   Windows-side automation must treat junction-backed dirs as un-addable.
3. If vendored files do get staged: `git rm -r --cached <path>` before committing.
   If already committed on a fresh, unshared branch: rebuild the commit and
   `git push --force-with-lease`.

## See also

- `scripts/memory/bridge-hermes-claude.sh` (memory bridge that owns the generated agents.md)
- `docs/setup/FRESH_MACHINE_SETUP.md`, `docs/setup/TROUBLESHOOTING.md`
