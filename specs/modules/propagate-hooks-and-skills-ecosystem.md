# Plan: Propagate Hooks & Skills Across Workspace-Hub Ecosystem

## Context

The `post-task-review.sh` Stop hook exists only in workspace-hub and digitalmodel (1 of 21 repos). Skills are duplicated across submodules — the same `guidelines/`, `meta/`, `workflows/` boilerplate is copy-pasted in ~15 repos. The user wants centralized skills in workspace-hub, symlinked into all submodule repos, working seamlessly on both Linux and Windows.

**Cross-platform requirement**: All development work must be compatible with Linux, Windows, and macOS. On this Windows machine, `core.symlinks=false`. Git treats junctions as regular directories, not symlinks. Committing symlinks to git is not portable. Solution: **runtime linking** — shared skill dirs are gitignored in submodules, and a setup script creates platform-appropriate links after clone.

## Architecture

```
workspace-hub/.claude/skills/          <-- Single source of truth (committed to git)
  _internal/guidelines/
  _internal/meta/
  _internal/workflows/
  eng/marine-offshore/...
  data/energy/...
  ...

digitalmodel/.claude/skills/
  guidelines/    -> ../../.claude/skills/_internal/guidelines/  (link, gitignored)
  meta/          -> ../../.claude/skills/_internal/meta/        (link, gitignored)
  workflows/     -> ../../.claude/skills/_internal/workflows/   (link, gitignored)
  orcaflex-*/    (local, committed)                            (unique project skills)

seanation/.claude/skills/
  guidelines/    -> ../../.claude/skills/_internal/guidelines/  (link, gitignored)
  meta/          -> ../../.claude/skills/_internal/meta/        (link, gitignored)
  workflows/     -> ../../.claude/skills/_internal/workflows/   (link, gitignored)
```

**Link type by platform (all three supported):**
- Linux: `ln -s` (relative symlink, native)
- macOS: `ln -s` (relative symlink, native)
- Windows (MINGW/Git Bash): `cmd //c mklink /J` (directory junction, no elevation needed)

## Deliverables

### 1. `scripts/propagate-ecosystem.sh` (~310 lines)

Unified script replacing `scripts/propagate-hooks.sh`. Handles hooks + skill linking.

```
Usage: bash scripts/propagate-ecosystem.sh [OPTIONS]
  --hooks-only    Only propagate hooks
  --skills-only   Only propagate skill links
  --dry-run       Preview changes
  --verbose       Detailed output
```

**Key functions:**

| Function | Purpose |
|---|---|
| `detect_platform()` | Returns `windows` or `unix` |
| `create_directory_link()` | `mklink /J` on Windows, `ln -s` on Linux (relative paths) |
| `is_link()` | Detects existing symlink/junction |
| `discover_submodules()` | `git submodule status` with dir-scan fallback |
| `propagate_hooks()` | Adds Stop hook to `settings.json` via jq (ported from existing script) |
| `propagate_skills()` | Creates links for shared dirs, preserves unique local skills |
| `directory_matches_template()` | Content comparison before replacing real dirs with links |

**Shared skill dirs to link** (identical across 15+ repos):

| Submodule dir | Link target (relative) |
|---|---|
| `.claude/skills/guidelines/` | `../../../.claude/skills/_internal/guidelines/` |
| `.claude/skills/meta/` | `../../../.claude/skills/_internal/meta/` |
| `.claude/skills/workflows/` | `../../../.claude/skills/_internal/workflows/` |

**Safety rules:**
- Real dir exists + content matches template: backup to `.bak-YYYYMMDD`, replace with link
- Real dir exists + content differs: **KEEP** (log and skip — has local modifications)
- Link already exists: **SKIP** (idempotent)
- `session-logs/`, `_runtime/`, `_internal/`, `_core/` never linked
- Unique project skills (orcaflex-*, bsee-*, etc.) never touched

**Git integration per submodule:**
- Add shared dirs to `.gitignore`: `guidelines/`, `meta/`, `workflows/` under `.claude/skills/`
- Run `git rm -r --cached .claude/skills/guidelines/` etc. to untrack (one-time)
- After this, the dirs exist only as links created by the propagation script

### 2. `scripts/skills/merge-submodule-skills.sh` (~200 lines)

One-time script to merge unique submodule skills into workspace-hub before linking.

```
Usage: bash scripts/skills/merge-submodule-skills.sh [--apply|--diff]
  (default)   Dry-run: list what would be merged
  --apply     Copy unique skills to workspace-hub
  --diff      Show content diffs for conflicts
```

**Category mapping:**

| Source | Skills (count) | Target in workspace-hub |
|---|---|---|
| digitalmodel | orcaflex-*, orcawave-*, aqwa-*, bemrosetta, etc. (42) | `eng/marine-offshore/<grouped>/` |
| worldenergydata | bsee-*, metocean-*, energy-* (16) | `data/energy/` |
| aceengineer-admin | expense-tracking, invoice-automation (8) | `business/admin/` |
| assetutilities | data-management, pdf-utils, plotly (3) | `data/` subcategories |
| aceengineer-website | website-update (1) | `business/content-design/` |

### 3. Deprecation wrapper for `scripts/propagate-hooks.sh`

Thin redirect to `propagate-ecosystem.sh --hooks-only`.

## Execution Sequence

1. **Create** `scripts/skills/merge-submodule-skills.sh`
2. **Dry-run** merge → review mapping, conflicts
3. **Apply** merge → unique skills copied to workspace-hub
4. **Create** `scripts/propagate-ecosystem.sh`
5. **Dry-run** propagation → preview hook + skill link changes across all repos
6. **Apply** propagation → hooks added, links created, shared dirs gitignored + untracked
7. **Replace** `scripts/propagate-hooks.sh` with deprecation wrapper
8. **Verify** on Windows (current machine) — links work, git status clean

## Cross-Platform Workflow

**First clone (any platform):**
```bash
git clone --recurse-submodules <workspace-hub-url>
cd workspace-hub
bash scripts/propagate-ecosystem.sh    # creates links for your platform
```

**After pulling updates:**
```bash
git pull --recurse-submodules
bash scripts/propagate-ecosystem.sh    # re-creates links if needed (idempotent)
```

**How it works:**
- Linux: `ln -s ../../../.claude/skills/_internal/guidelines guidelines` → real symlink
- Windows: `mklink /J guidelines ..\..\..\..\.claude\skills\_internal\guidelines` → junction
- Both resolve transparently — `cat digitalmodel/.claude/skills/guidelines/SKILL.md` works on either

## Critical Files

| File | Role |
|---|---|
| `scripts/propagate-hooks.sh` | Existing hook logic to port (95 lines) |
| `scripts/skills/sync-knowledge-work-plugins.sh` | CLI pattern reference (355 lines) |
| `.claude/hooks/post-task-review.sh` | Hook being propagated |
| `.claude/skills/_internal/` | Canonical shared skills (link targets) |
| `<submodule>/.claude/skills/.gitignore` | New: gitignore shared dirs |

## Verification

1. `bash scripts/skills/merge-submodule-skills.sh` — unique skills listed correctly
2. `bash scripts/skills/merge-submodule-skills.sh --apply` — files copied to workspace-hub
3. `bash scripts/propagate-ecosystem.sh --dry-run` — all repos listed for sync
4. `bash scripts/propagate-ecosystem.sh` — links created, hooks added
5. `ls -la digitalmodel/.claude/skills/guidelines/` — shows link (junction/symlink)
6. `cat digitalmodel/.claude/skills/guidelines/ai-agent-guidelines/SKILL.md` — resolves correctly
7. `grep post-task-review seanation/.claude/settings.json` — hook present
8. `git -C digitalmodel status` — no unexpected changes (shared dirs gitignored)

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Links don't survive `git clone` | By design — run propagation script after clone. Document in README. |
| Git sees link targets as untracked | `.gitignore` in each submodule's `.claude/skills/` |
| Local skill modifications lost | `directory_matches_template()` + backup before replace |
| Session-logs shared via link | Explicitly excluded (`SKIP_DIRS`) |
| Relative path breaks if repo moves | Paths are relative to workspace-hub parent structure; works as long as submodule is checked out under workspace-hub |
