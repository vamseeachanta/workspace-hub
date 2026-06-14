# Untracked Preservation Proposal - 2026-06-14

Generated after the repo-ecosystem closeout wave. This proposal covers remaining
untracked repo-local artifacts only. It does not cover tracked git work, stashes,
remote divergence, or git worktrees; those were handled separately.

Manifest: `docs/sessions/2026-06-14-untracked-residue-manifest.tsv`

## Current Verified Context

- All known stale `llm-wiki` and `workspace-hub` worktrees discovered in this wave were removed or preserved first.
- `workspace-hub` work from stale branches was preserved on `main`:
  - `ffe4f8603` — agy Gemini statusline snapshot path for #3087.
  - `3dde510cb` — mission-spine decisions and weekly skills audit `pyyaml` fix.
  - `dbc5cd195` — solver watcher `git pull --ff-only`.
  - `2fd0d071b` — provider ASCP pointer docs.
  - `6b96f1739` — #2421 draft plan and r1 review artifacts.
- Issue comments were posted on #3087, #3079, #3057, and #2421.

## Residue Summary

The manifest contains 79 untracked entries after excluding this proposal and the
manifest itself.

Main material entries:

- `workspace-hub/knowledge/dark-intelligence/xlsx-poc/cc-23-6h-flowback-calculator-4/tests/` — 166M, 2 files.
- `worldenergydata/data/modules/marine_safety/database/` — 60M, 1 file.
- `workspace-hub/data/standards/` — 28M, 10,681 files.
- `worldenergydata/tests/unit/bsee/analysis/comprehensive-report-system/` — 18M, 13 files.
- `worldenergydata/.archived/` — 15M, 3 files.
- `workspace-hub/knowledge/wikis/marine-engineering/` — 4.6M, 6 files.
- `workspace-hub/config/search/` — 3.8M, 1 file.
- `workspace-hub/data/document-index/logs/` — 975K, 69 files.

Most remaining entries are empty local state directories, placeholder directories,
or small provider/runtime-local files.

## Proposed Tiers

### Tier 0 - Safe Empty-Directory Deletes

Delete entries whose manifest `file_count` is `0` after a fresh pre-delete check.
These have no file payload to preserve. Examples:

- `.planning/`, `.benchmarks/`, `.claude/checkpoints/`, `.agents/`, `.codex/`
  entries that have zero files.
- Empty generated/example placeholders such as `modules/reporting/examples/`,
  `assets/img/case-studies/`, `sports/waterpolo/`, and `business/`.
- Empty accidental Windows-style path directories under `assethold` and
  `digitalmodel`.

Execution rule: use a cleanup lock, re-run `find <path> -type f -print -quit`,
then remove only paths still reporting no files.

### Tier 1 - Archive Then Remove Evidence/Data Outputs

Archive with manifest + checksum before moving/removing:

- `workspace-hub/data/standards/`
- `workspace-hub/data/document-index/logs/`
- `workspace-hub/data/domain-tag/`
- `workspace-hub/data/modules/`
- `workspace-hub/knowledge/dark-intelligence/`
- `workspace-hub/knowledge/wikis/`
- `workspace-hub/config/search/`
- `worldenergydata/data/modules/marine_safety/`
- `worldenergydata/data/modules/vessel_hull_models/`
- `worldenergydata/tests/unit/bsee/analysis/`
- `worldenergydata/logs/overnight/`
- `worldenergydata/.archived/`

Execution rule: write archive under `docs/sessions/archives/`, commit the
manifest + checksum only, and do not commit the tarball unless a separate
size/license/secrets review explicitly approves it.

### Tier 2 - Inspect Before Reducing Local Agent/Provider State

Do not delete without inspection:

- `workspace-hub/.agents/skills/...`
- `workspace-hub/.claude/skills/...`
- `workspace-hub/.ops/`
- `workspace-hub/.local/`
- `worldenergydata/.claude/commands/`
- `worldenergydata/.claude/skills/_internal/`
- `worldenergydata/.agent-os/`

These may be runtime-local state, candidate skill content, or repo-specific
provider adapters. They should be either committed intentionally, archived, or
left alone with a reason.

### Tier 3 - Defer Possible Source/Project Content

Leave in place until a repo owner decides whether it should be committed,
archived, or deleted:

- `workspace-hub/examples/claude-code-course/uigen/prisma/`
- `workspace-hub/examples/claude-code-course/uigen/src/`
- `teamresumes/src/external/`
- `teamresumes/src/modules/`
- `teamresumes/tests/modules/`

These paths look like source/project structure, even when some entries are
currently empty.

## Approval Needed

Approve one or more tiers explicitly:

- "Approve Tier 0 only"
- "Approve Tier 0 and Tier 1 archive/remove"
- "Approve Tier 2 inspection"
- "Leave Tier 3 deferred"

No destructive movement should run from this proposal without that tier-specific
approval.
