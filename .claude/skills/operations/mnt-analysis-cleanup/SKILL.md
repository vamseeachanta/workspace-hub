---
name: mnt-analysis-cleanup
description: Survey, classify, and clean up `/mnt/local-analysis/` (or any sibling-to-workspace-hub
  directory holding orphan worktrees, codex-burn artifacts, agent log accumulations,
  and outer-clone duplicates) without losing useful code/work. Surfaces a tiered approval
  menu rather than baking decisions; defers all destructive ops until user confirms.
when_to_use: '- User asks to "clean up local-analysis", "free up disk", "remove stale
  repos", "what''s still useful in /mnt/local-analysis"

  - User mentions "disk pressure", "orphan worktree", "codex-burn", "outer-clone duplicates",
  "agent-log accumulation"

  - After a Hermes codex-burn run completes (post-run artifact sweep)

  - Routinely (monthly or after disk pressure) to keep the workspace-hub sibling area
  lean

  - Whenever `df -P /mnt/local-analysis` crosses a warning threshold (configurable)

  '
tags:
- disk-cleanup
- local-analysis
- codex-burn
- orphan-worktrees
- outer-clones
- agent-logs
- hermes-coordination
---

# `/mnt/local-analysis/` cleanup

A reusable routine for the dirty work that accumulates alongside `workspace-hub/`: orphan worktrees from completed Hermes codex-burn runs, outer-clone duplicates of nested repos, monitoring evidence from past audit passes, and agent log accumulations.

> This skill was revised on 2026-05-12 after an adversarial cross-review by Hermes returned REJECT on its first draft. The 8 required patches are now applied; see `references/hermes-adversarial-review-2026-05-12.md` for the original findings and `references/case-study-2026-05-12.md` for the worked example.

## Iron Law: NEVER skip the verification step

The single most-load-bearing rule. Before deleting anything that looks like a repo clone or worktree:

1. **Confirm content is on origin** — for git repos/worktrees:
   - Identify branch: `git -C <bundle> branch --show-current` (or read `.git` if it's a file: `cat <bundle>/.git`)
   - Verify upstream exists: `git -C <canonical> ls-remote --heads origin <branch>`
   - Compare tracked files: `git -C <bundle> status --porcelain=v1 --untracked-files=all`
   - Diff working tree vs `git archive FETCH_HEAD`-extracted branch tip with `diff -rq`
   - Explicitly list ignored files: `git -C <bundle> status --ignored --short`
2. **Classify residue** — the `diff -rq` residue goes into three buckets (see §3 below), not one blunt filter
3. **Archive non-derived unique content** — anything in the "evidence-bearing" or "inspect-first" bucket goes into the cleanup tarball before delete; with manifest, checksum, and atomic move
4. **No `rm -rf` until** a `cleanup-verification.json` artifact exists with `delete_allowed: true`

Reason for the law: it's how you honor "don't lose useful code/work" in a deletion-heavy routine.

## Skill structure (numbered steps)

### 1. Survey

```bash
ls -la /mnt/local-analysis/
for d in /mnt/local-analysis/*/; do timeout 20 du -sh "$d" 2>/dev/null; done
df -P /mnt/local-analysis      # -P for machine-parseable, NOT -h
```

Capture: top-level entries, sizes, last-modified dates, mount usage %.

### 2. Classify each entry

Use this taxonomy (apply order matters — most-specific first):

| Class | Signal | Example |
|---|---|---|
| **system (allowlisted)** | exact-name match: `.pnpm-store/`, `.Trash-*/`, `.cache/`, `.cargo/`, `.npm/` | Leave alone |
| **dotdir (unclassified)** | dotfile/dotdir NOT on the system allowlist | Tier 3 until classified — never auto-treat as system |
| **workspace-hub canonical** | the workspace-hub repo itself | `workspace-hub/` |
| **outer-clone duplicate** | a repo dir at top-level that also exists nested under `workspace-hub/<same-name>/` | `assetutilities/`, `digitalmodel/` (historical pattern) |
| **clean duplicate clone** | a full `.git/` clone of a canonical repo under an ad-hoc/staging/reconcile name; local branch is clean, upstream configured, ahead=0, and local HEAD is contained in origin history | `reconcile-workspace-hub-YYYYMMDD-HHMMSS/` |
| **orphan worktree** | `.git` is a file (`gitdir:` pointing at a path that no longer exists) | `codex-burn-YYYYMMDD/<repo>-bundle/` after parent clone is gone |
| **codex-burn run artifact** | dated dir matching `codex-burn-YYYYMMDD/` containing per-repo bundles, monitoring-evidence, logs, prompts | full Hermes codex-burn run output |
| **agent log accumulation** | dir holding `provider-capacity-aware-YYYYMMDD-*` or `workspace-hub-{exit,closeout}-handoff-*.md` | `agent-logs/` |
| **top-level reconstructible Python dependency dir** | dir contains `pyvenv.cfg`, no `.git`, mostly `lib/` and `bin/` | `marker-env/`, `capytaine-env/`, `raft-env/` |
| **nested open-issue Python dependency dir** | dependency dir inside a workspace tied to an OPEN GitHub issue | `ace2-gis-timelapse/.venv/` |
| **empty coordination meta-dir** | dir created for an agent run that left no artifacts | `agent-worktrees/`, `worktrees/` |

### 3. Derived-artifact classification (THREE buckets, not one)

When running `diff -rq` to identify residue, apply this **three-bucket** filter:

**Bucket A — always disposable after diff** (filter out, do not archive):
```
__pycache__/  *.pyc  *.pyo  .pytest_cache/  .mypy_cache/  .pyre/  .ruff_cache/
.tox/  .nox/  .hypothesis/  .ipynb_checkpoints/  .coverage  .DS_Store
node_modules/  .next/cache/  .turbo/  .vite/  .parcel-cache/
```

**Bucket B — evidence-bearing, archive with manifest summary** (don't blindly discard):
```
logs/  *.log  test_output/  test-results/  playwright-report/  results/
coverage.xml  htmlcov/  junit.xml  *.db  *.sqlite*
```

**Bucket C — never filter without inspection** (size + type check, then decide):
```
data/  results/Data/  downloads/  cache/  *.parquet  *.csv  *.xlsx  *.ipynb
```

Inspection commands:
```bash
find <residue> -maxdepth 3 -type f -printf '%p|%s|%TY-%Tm-%Td %TH:%TM\n'
file <db> ; sqlite3 <db> '.tables'  # if sqlite3 available
```

Build-output dirs (`build/`, `dist/`, `target/`, `bin/`, `*.egg-info/`, `.eggs/`) go in Bucket A only if their parent is unambiguously a build context; otherwise Bucket C.

### 4. Per-class verification

| Class | Verification |
|---|---|
| outer-clone duplicate | Compare HEAD of outer vs nested. Check `for-each-ref refs/heads/ --format='%(upstream:track)'` for unpushed work. Check `git stash list`. Check `git status --short` for dirty. |
| clean duplicate clone | Fetch/prune first. Confirm remote URL matches the canonical repo; branch has upstream; `git status --short` is empty; `git stash list` is empty; `git rev-list --left-right --count HEAD...@{upstream}` returns `0 N` (ahead=0); and `git branch -r --contains HEAD` includes the upstream/default branch. If clean but behind origin, deletion is acceptable after approval because origin already contains local HEAD. |
| orphan worktree | Read `.git` (file, contents = `gitdir: <path>`). If that path doesn't exist, orphan confirmed. Fetch the branch the orphan was tracking into a sibling clone, `git archive` it, `diff -rq` with bucket-A filter, build residue list, archive bucket-B/C, then delete. |
| codex-burn run artifact | Cross-check with Hermes via the full coordination protocol in §6 below. **An old dated dir is a candidate, not vestigial-by-default.** |
| agent log accumulation | Inspect timestamps; threshold for prune is the `mtime` policy below. |
| top-level reconstructible Python dependency dir | Confirm no active process has cwd/open files inside it; identify package intent from `pyvenv.cfg` and a small import probe; delete only after user confirms it is not a long-lived environment they still use. Archive normally not required because dependencies are reconstructible. |
| nested open-issue Python dependency dir | If parent workspace is tied to an OPEN GitHub issue, preserve `outputs/`, `reports/`, `scripts/`, logs, and other evidence-bearing artifacts; remove only the reconstructible dependency directory. |
| empty coordination meta-dir | `find "$dir" -xdev -mindepth 1 -print -quit` returns empty AND no permission errors. Fail closed if errors. |

### 5. Risk-tier the proposal

Always present four tiers; let the user reject any.

- **Tier 0 — safe deletes**: orphan worktrees with verified-clean origin-diff (residue is bucket-A only), clean duplicate clones with ahead=0/dirty=0/stash=0/HEAD-contained-on-origin, empty coordination meta-dirs (per find -quit check).
- **Tier 1 — archive then delete**: codex-burn monitoring evidence, prompts, logs — anything in bucket B or C unique to the bundle. Archive workflow per §7.
- **Tier 2 — reduce in place**: agent-logs with mtime policy (default: prune subdirs >14 days, keep standalone .md handoffs).
- **Tier 3 — leave alone**: outer-clone duplicates with any unpushed/dirty/stashed state; anything Hermes coordination flagged; unclassified dotdirs; **any orphan worktree whose branch is unmerged and parent issue is still open** (call this evidence-preserving defer, not vestigial).

### 6. Hermes coordination protocol — old dirs are CANDIDATES, not vestigial

A dated `codex-burn-YYYYMMDD/` dir can still matter even if Hermes will not poll it again. **An old dated dir is deletable only after ALL of these are true:**

```bash
# 1. No running process has cwd or open files under the dir
lsof +D <dir> 2>/dev/null || fuser -vm <dir> 2>/dev/null
pgrep -af 'hermes|codex|tui_gateway|slash_worker|tmux' | grep -F "<dir>"

# 2. No Hermes cron/job/session/goal references the dir
grep -R --fixed-strings "<dir>" ~/.hermes/goals ~/.hermes/sessions ~/.hermes/logs 2>/dev/null
hermes cron list --all 2>&1 | grep -F "<dir>"

# 3. No canonical repo still lists it in git worktree metadata
for repo in /mnt/local-analysis/workspace-hub/*/; do
  git -C "$repo" worktree list --porcelain 2>/dev/null | grep -F "<dir>"
done

# 4. All branches named by the bundles exist on origin (verify per-branch, not just per-repo)
# 5. Any GitHub issues referenced by prompts/logs are closed OR explicitly deferred with archive comment
# 6. Archive verified before deletion (per §7)
```

Failure of ANY check → demote from Tier 0/1 to Tier 3 (defer).

**Note on the orchestration skill location**: the Hermes skill at `~/.hermes/skills/autonomous-ai-agents/agent-cli-delegation-operations/references/codex-background-burn-orchestration.md` is a **reference to an archived skill** (`.archive/umbrella-2026-04-29`). The active orchestration source-of-truth may evolve. Treat this path as fragile; if it disappears, do not assume the protocol changed — re-derive via `hermes skills list` first.

### 7. Archive workflow — atomic, manifested, checksummed

```bash
ARCHIVE_BASE="workspace-hub/docs/sessions/archives"
ARCHIVE_NAME="YYYY-MM-DD-<topic>"
TMP="${ARCHIVE_BASE}/.tmp"
mkdir -p "$TMP"

# Step 1: pre-archive manifest (BEFORE writing archive)
find <targets> -xdev -printf '%y\t%s\t%T@\t%p\n' | sort > "$TMP/${ARCHIVE_NAME}.manifest.tsv"
TOTAL_BYTES=$(awk -F'\t' '$1=="f"{s+=$2} END{print s}' "$TMP/${ARCHIVE_NAME}.manifest.tsv")

# Step 2: free-space check (need source bytes + 10% overhead)
NEED=$((TOTAL_BYTES + TOTAL_BYTES/10))
FREE=$(df -P "$ARCHIVE_BASE" | awk 'NR==2 {print $4 * 1024}')
[ "$FREE" -gt "$NEED" ] || { echo "INSUFFICIENT SPACE: need $NEED bytes, have $FREE"; exit 1; }

# Step 3: write archive to .partial
tar czf "$TMP/${ARCHIVE_NAME}.tar.gz.partial" -C <base-dir> <targets>

# Step 4: verify
tar tzf "$TMP/${ARCHIVE_NAME}.tar.gz.partial" | sort > "$TMP/${ARCHIVE_NAME}.archive-list.txt"
sha256sum "$TMP/${ARCHIVE_NAME}.tar.gz.partial" > "$TMP/${ARCHIVE_NAME}.sha256"
# Compare expected file entries to archive list; abort if mismatch

# Step 5: atomic move to final
mv "$TMP/${ARCHIVE_NAME}.tar.gz.partial" "$ARCHIVE_BASE/${ARCHIVE_NAME}.tar.gz"
mv "$TMP/${ARCHIVE_NAME}.manifest.tsv" "$ARCHIVE_BASE/"
mv "$TMP/${ARCHIVE_NAME}.sha256" "$ARCHIVE_BASE/"
```

**Archive tracking in git**: `*.tar.gz` is **globally gitignored** at `.gitignore:330-332`. Therefore:

- The archive `.tar.gz` will NOT be committed by default
- Commit the **manifest + checksum** (the `.tsv` and `.sha256` are not gitignored) — these prove the cleanup happened
- Only `git add -f` the archive itself after:
  1. Secret scan: `git secrets`, `gitleaks`, or `grep -RE '(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|password|token|secret)' <extracted-archive>`
  2. Manual classification of any client names, prospect data, downloaded data licensing
  3. Size review (committing >5 MB archives to git is generally wrong; prefer LFS or non-git storage)

### 8. Pre-delete final gate

Immediately before `rm -rf` (between approval and execution):

```bash
# Re-run race-detection checks
lsof +D <target> 2>/dev/null
pgrep -af 'hermes|codex|tui_gateway|slash_worker|tmux' | grep -F "<target>"
grep -R --fixed-strings "<target>" ~/.hermes/goals ~/.hermes/sessions 2>/dev/null

# Acquire cleanup lock
LOCK=/mnt/local-analysis/.cleanup-lock
if [ -e "$LOCK" ]; then
  echo "Cleanup already in progress: $(cat $LOCK)"; exit 1
fi
echo "pid=$$ host=$(hostname) date=$(date -Iseconds) targets=$*" > "$LOCK"

# Two-phase delete: move to trash-stage first
TRASH=/mnt/local-analysis/.cleanup-trash/$(date +%Y%m%d-%H%M%S)
mkdir -p "$TRASH"
mv <target> "$TRASH/"
# Verify system behavior post-move (next codex-burn run, agent operations, etc.) before final rm
# Final rm only after the trash-stage has lived for at least one cycle OR disk pressure justifies
rm -rf "$TRASH"
rm "$LOCK"

# Write verification artifact
cat > "$ARCHIVE_BASE/${ARCHIVE_NAME}-cleanup-verification.json" <<EOF
{
  "target_paths": [...],
  "branch_compared": "...",
  "diff_command": "...",
  "residue_buckets": {"A": N, "B": N, "C": N},
  "archive_path": "${ARCHIVE_BASE}/${ARCHIVE_NAME}.tar.gz",
  "archive_sha256": "...",
  "delete_allowed": true,
  "approver": "user",
  "timestamp": "$(date -Iseconds)"
}
EOF
```

Under severe disk pressure, the trash-stage MAY be skipped, but only after the archive is verified and the `cleanup-verification.json` is written.

### 9. User approval

Present the four-tier proposal to the user using **the available user-interaction mechanism for the current agent harness**:

- Claude Code: `AskUserQuestion` tool
- Hermes CLI: `clarify` tool
- Codex CLI / non-interactive contexts: stop after writing the proposal to disk; do NOT delete

One question per tier (so user can reject independently). Always include "show me the diffs first" as an option for the tiers that delete content. Never auto-execute without per-tier approval.

If no user-interaction tool is available, halt and emit a proposal document to `docs/sessions/YYYY-MM-DD-cleanup-proposal.md` for a human to review later.

### 10. Handoff documentation

Write `workspace-hub/docs/sessions/YYYY-MM-DD-mnt-analysis-cleanup.md` capturing:
- before/after disk usage (from `df -P`)
- table of entries acted on, with class + verdict + residue-bucket breakdown
- archive path, manifest path, checksum
- `cleanup-verification.json` path
- items deferred (and why — be specific: which check failed)
- any follow-up GitHub issues filed

Commit the handoff + manifest + checksum. Do NOT commit the archive `.tar.gz` itself by default (it's globally gitignored; force-adding requires the security review above).

## Disk-pressure trigger

If invoked autonomously (e.g. from a cron health check), gate execution on:
```bash
df -P /mnt/local-analysis | awk 'NR==2 {gsub("%",""); print $5}'
```
exceeding a threshold (default 75%). Below that, defer. **Use `-P` not `-h`** — human-readable parsing is brittle.

## What NOT to clean

- Anything under `workspace-hub/` itself — different skill (per-repo housekeeping)
- System-allowlisted caches: `.pnpm-store/`, `.cache/`, `.cargo/`, `.npm/` — but NOT all dotdirs (unknown ones go Tier 3)
- XDG `.Trash-*` (system-managed)
- Any path referenced by an active Hermes goal, cron job, session, or process (per §6 protocol)
- Any orphan worktree whose origin-diff bucket-C residue isn't classified
- Any orphan worktree whose branch is unmerged AND parent issue is still open — that's evidence-preserving defer, not vestigial

## Memory hooks

When this skill completes a successful run, optionally update auto-memory at `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/`:
- `feedback_mnt_analysis_cleanup_gotcha.md` — if a new gotcha surfaced (e.g., a check that should be in §6 but wasn't)
- `project_mnt_analysis_state.md` — post-run state snapshot if useful for future sessions

The case-study reference (`references/case-study-2026-05-12.md`) captures the worked example that produced this skill. The Hermes adversarial review at `references/hermes-adversarial-review-2026-05-12.md` produced the patch set that hardened it. The clean duplicate clone deletion pattern is illustrated in `references/clean-duplicate-clone-2026-05-18.md`. Top-level reconstructible Python dependency cleanup and open-issue workspace reduction are covered in `references/top-level-venv-and-open-issue-workspace-cleanup.md`.
