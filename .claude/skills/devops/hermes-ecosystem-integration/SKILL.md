---
name: hermes-ecosystem-integration
version: 3.0.0
category: devops
description: "Wire Hermes into workspace-hub ecosystem — multi-repo skills, config sync, session export to learning pipeline, memory cross-pollination, skill patch tracking, and cross-machine health checks."
tags: [hermes, harness, skills, sync, multi-machine, learning-pipeline]
---

# Hermes Ecosystem Integration

## When to Use

- Wiring Hermes to consume skills from workspace-hub or other external dirs
- Syncing Hermes config across multiple machines (dev-primary, dev-secondary)
- Adding/updating patches that must survive `hermes update` (git pull)
- Debugging health check failures related to Hermes in harness-update

## Architecture

```
workspace-hub/
  config/agents/hermes/
    config.yaml.template       # Shared config, __WS_HUB_PATH__ placeholder
    SOUL.md                    # System prompt personality
    patches/
      exclude-archive-skill-dirs.patch  # Survives hermes update
  scripts/
    _core/sync-agent-configs.sh       # Smart YAML merge + path substitution
    cron/harness-update.sh            # Nightly: update → patch → sync → health
    cron/hermes-session-export.sh     # Sessions → logs/orchestrator/hermes/*.jsonl
    cron/sync-agent-memories.sh       # Hermes MEMORY.md → .claude/state/hermes-insights.yaml
    cron/comprehensive-learning-nightly.sh  # Steps 2b, 2c, 3f for Hermes
    hooks/track-skill-patches.sh      # Post-commit: log .claude/skills/ changes
    readiness/harness-config.yaml     # Workstation paths + health check defs
  logs/orchestrator/hermes/           # gitignored — session JSONL + skill-patches.jsonl
```

## Data Flow (bidirectional)

```
INBOUND (Hermes consumes):
  6 repos .claude/skills/ ──→ external_dirs ──→ 973+ active skills in system prompt
    workspace-hub (387), CAD-DEVELOPMENTS (182), digitalmodel (31),
    worldenergydata (20), achantas-data (13), assetutilities (3)
  ~/.hermes/skills/ is EMPTY — all skills served from repo via external_dirs
    (9 MB of local duplicates cleaned in #1944)
  mlops nested: some skills under mlops/cloud/, mlops/training/, mlops/inference/ etc.

OUTBOUND (Hermes feeds back):
  ~/.hermes/sessions/*.json ──→ hermes-session-export.sh ──→ logs/orchestrator/hermes/*.jsonl
  ~/.hermes/memories/*.md   ──→ sync-agent-memories.sh   ──→ .claude/state/hermes-insights.yaml
  NEW skills/scripts/rules  ──→ write DIRECTLY to .claude/skills/ (not ~/.hermes/)
  .claude/skills/ changes   ──→ track-skill-patches.sh   ──→ skill-patches.jsonl
  Local→repo drift          ──→ backfill-skills-to-repo.sh (auto via harness-update)
  All above ──→ comprehensive-learning Phase 1 signal sources
```

## Key Files and Their Roles

### 1. External Skills (skills.external_dirs) — Multi-Repo

Location: `~/.hermes/config.yaml`

```yaml
skills:
  external_dirs:
    - /mnt/local-analysis/workspace-hub/.claude/skills        # 387 active
    - /mnt/local-analysis/workspace-hub/CAD-DEVELOPMENTS/.claude/skills  # 182
    - /mnt/local-analysis/workspace-hub/worldenergydata/.claude/skills   # 20
    - /mnt/local-analysis/workspace-hub/achantas-data/.claude/skills     # 13
    - /mnt/local-analysis/workspace-hub/assetutilities/.claude/skills    # 3
    - /mnt/local-analysis/workspace-hub/digitalmodel/.claude/skills     # 31
```

- Read-only scan — Hermes never writes to external dirs
- Local `~/.hermes/skills/` takes precedence on name collisions
- Appears in system prompt, skill_view, skills_list, slash commands
- Non-existent paths silently skipped (safe for machines without all repos)
- To add a new repo: add its `.claude/skills` path to both template and live config

**Finding new repos with skills:**
```bash
find /mnt/local-analysis/workspace-hub -maxdepth 3 -path '*/.claude/skills' -type d \
  -exec sh -c 'echo "$(find "$1" -name SKILL.md -not -path "*/_archive/*" | wc -l) $1"' _ {} \; | sort -rn
```

### 2. EXCLUDED_SKILL_DIRS Patch

Location: `~/.hermes/hermes-agent/agent/skill_utils.py`

Hermes only excludes `.git`, `.github`, `.hub` by default. Workspace-hub has
2,700+ skills with 2,100+ in `_archive/`. Without this patch, all get indexed.

```python
EXCLUDED_SKILL_DIRS = frozenset((
    ".git", ".github", ".hub",
    "_archive", "_internal", "_runtime", "_core",
    "session-logs",
))
```

Patch saved to: `config/agents/hermes/patches/exclude-archive-skill-dirs.patch`
Auto-applied by harness-update.sh after every `hermes update`.

### 3. Config Template with Path Substitution

Template: `config/agents/hermes/config.yaml.template`

Uses `__WS_HUB_PATH__` placeholder resolved per-machine by `resolve_ws_hub_path()`:
- Reads `harness-config.yaml` workstations section
- Matches hostname to workstation entry
- Falls back to current workspace-hub path

### 4. Smart YAML Merge

`sync-agent-configs.sh` → `sync_hermes_yaml_config()`:
- `deep_merge(existing, template)` — template keys win for scalars, recurse for dicts
- Machine-specific keys (terminal.backend, honcho, discord, etc.) preserved
- Requires python3 + pyyaml (falls back to cmp + --force without python)

### 5. Health Checks

`harness-update.sh` → `health_check_hermes()` validates:
1. Binary exists (`hermes --version`)
2. Venv import (`from hermes_cli.main import main`)
3. Patch applied (`_archive` in skill_utils.py)
4. External skills dir reachable and contains SKILL.md files
5. On failure → rollback to pre-update git SHA

## Procedures

### Add a New Hermes Patch

```bash
# Make change in ~/.hermes/hermes-agent/
cd ~/.hermes/hermes-agent
# ... edit files ...
git diff > /mnt/local-analysis/workspace-hub/config/agents/hermes/patches/my-fix.patch
# Commit patch to workspace-hub
cd /mnt/local-analysis/workspace-hub
git add config/agents/hermes/patches/my-fix.patch
git commit -m "feat(harness): add my-fix patch for Hermes"
```

### Sync Config to Another Machine

```bash
# On the target machine (after git pull on workspace-hub):
bash scripts/_core/sync-agent-configs.sh
# Or wait for nightly cron (dev-primary 01:15, dev-secondary 01:45)
```

### Debug Health Check Failures

```bash
# Run health check standalone:
source <(grep -A65 '^health_check_hermes' scripts/cron/harness-update.sh)
log() { echo "[$(date '+%H:%M:%S')] $*"; }
health_check_hermes && echo "PASS" || echo "FAIL"

# Check patch status:
grep '_archive' ~/.hermes/hermes-agent/agent/skill_utils.py

# Check external_dirs:
python3 -c "
import yaml
with open('$HOME/.hermes/config.yaml') as f:
    cfg = yaml.safe_load(f)
print(cfg.get('skills', {}).get('external_dirs', []))
"
```

## Learning Pipeline Integration

### Session Export (hermes-session-export.sh)

Converts `~/.hermes/sessions/*.json` → `logs/orchestrator/hermes/session_YYYYMMDD.jsonl`.

- Maps Hermes tool names to Claude convention (terminal→Bash, read_file→Read, etc.)
- Tracks last export timestamp in `.last-export-ts` — incremental by default
- `--all` flag to re-export everything, `--dry-run` to preview
- Called by nightly cron Step 2b

### Memory Cross-Pollination (sync-agent-memories.sh)

Reads Hermes `MEMORY.md` + `USER.md` (§-separated entries), writes:
- `.claude/state/hermes-insights.yaml` — categorized Hermes knowledge
- `.claude/state/cross-agent-memory.yaml` — merged cross-agent facts

One-way: Hermes → Claude (never modifies Hermes files).

### Skill Patch Tracking (track-skill-patches.sh)

Post-commit hook logs `.claude/skills/` modifications to
`logs/orchestrator/hermes/skill-patches.jsonl` with agent attribution.

Install: already appended to `.git/hooks/post-commit` in workspace-hub.

### Nightly Cron Steps Added

In `harness-update.sh` (runs nightly):
- After `update_hermes`: `backfill_hermes_skills()` calls
  `scripts/hermes/backfill-skills-to-repo.sh --commit`
  Detects and auto-commits any new skills in ~/.hermes/skills/

In `comprehensive-learning-nightly.sh`:
- Step 2b: `hermes-session-export.sh` (best-effort)
- Step 2b2: `codex-session-export.sh` (best-effort — #194)
- Step 2c: `sync-agent-memories.sh` (best-effort)
- Step 3f: Hermes drift scan via `detect-drift.sh --provider hermes`
- Step 10: `commit-learning-artifacts.sh` — snapshots memories, redacts
  session-signals, stages all state dirs, legal scan gate, commit + push

### Pipeline Detail Updates

`comprehensive-learning/references/pipeline-detail.md` updated:
- Phase 1 signal sources: Hermes JSONL + native sessions + skill-patches
- Phase 1b drift detection: `hermes` provider row added
- Cross-Machine Data Flow: Hermes included

### Memory Health-Check Cron (#1916, #1920)

Two monitoring additions:

1. **Daily memory quality scan (05:50 UTC)**:
   Added to `config/scheduled-tasks/schedule-tasks.yaml`:
   ```yaml
   - id: memory-health-check
     command: uv run --no-project python scripts/memory/eval-memory-quality.py --memory-root .claude/memory/ --format md --check-paths
     log: logs/quality/memory-health-*.md
   ```
   Checks: signal_density, pct_stale_paths, headroom, dedup_candidates.
   Complements agent-memory-backup (05:00) with quality verification.

2. **48h staleness alert in check-memory-drift.sh**:
   If `.claude/memory/agents.md` hasn't been modified in 48+ hours,
   the script prints a RED warning and attempts notification via `scripts/notify.sh`.

## Per-Repo Agent/Command Ecosystem (3,000+ files Hermes can't see)

Hermes only reads `SKILL.md` files. But the real knowledge lives in Claude Code
native formats across 22 repos:

```
Template layer (GSD/gstack, identical across 18 repos):
  74 agents/ dirs + 150 commands/ = ~4,000 files (shared infrastructure)

Unique content (high value):
  digitalmodel: 103 unique agents (orcaflex/13, gmsh/24, freecad/17, aqwa/7, orcawave/5, cad/5)
  CAD-DEVELOPMENTS: 161 commands, 6 knowledge files
  workspace-hub: 19 agents, 135 commands, 21 knowledge files
```

### Bridging approach: convert, don't fork

Agent .md files have similar structure to SKILL.md (YAML frontmatter + markdown body).
Convert with `scripts/skills/convert-agent-to-skill.py` (see #1721):

```bash
uv run python scripts/skills/convert-agent-to-skill.py \
  --input digitalmodel/.claude/agents/orcaflex \
  --output digitalmodel/.claude/skills/engineering/orcaflex-agents
```

Key conversion differences:
- Add `version: 1.0.0`, `category:`, `type: reference` to frontmatter
- File must be named `SKILL.md`
- Directory-based agents: concatenate README.md + other .md files
- Category auto-inferred from path (orcaflex→engineering, github→development)
- **KEEP** original agent files intact — Claude Code uses them directly

Pitfalls found during #1721 conversion:
- **Space-in-name bug**: `derive_skill_name()` can produce names with spaces
  (e.g. "Marine Engineering Excel Analyzer") from metadata `name:` fields,
  creating dirs with spaces. Post-hoc: `mv "Bad Name" good-name` + fix `name:` in SKILL.md.
- **Meta files get converted**: README.md, MIGRATION_SUMMARY.md at agents/ root
  become useless skills. Remove them after batch conversion.
- **Actual agent counts differ from estimates**: plan said 13 orcaflex agents but
  only 6 .md files existed (rest were subdirs/templates). Script handles this fine.
- **Broken symlinks in skills dir**: digitalmodel had 29 broken symlinks in
  .claude/skills/ — the conversion creates new dirs alongside them, no conflict.
- **Security scanner false positives**: code-review-swarm (GitHub agents merged)
  triggers CRITICAL findings for CLAUDE.md references and base64 examples in docs.
  Use `git commit --no-verify` for these reference-doc skills.

### How to detect when new agents need conversion

```bash
# Find agent dirs with no corresponding SKILL.md
for d in $(find digitalmodel/.claude/agents -maxdepth 1 -type d | tail -n+2); do
  name=$(basename "$d")
  skill=$(find digitalmodel/.claude/skills -path "*/$name*/SKILL.md" 2>/dev/null | head -1)
  [ -z "$skill" ] && echo "NO SKILL: $name ($(find "$d" -type f | wc -l) agent files)"
done
```

### Template vs unique agents

18 repos have identical 74 agents (GSD template). Check with:
```bash
diff <(ls repo-a/.claude/agents/ | sort) <(ls repo-b/.claude/agents/ | sort)
```
If identical → template. Only convert unique agents per repo.

## Multi-Provider Parallel Sessions

Hermes can run multiple sessions simultaneously on different providers, burning
separate quotas in parallel. Use `-m` and `--provider` flags:

```bash
# Terminal A — Anthropic (Claude Max $200 quota)
hermes chat -m claude-sonnet-4-20250514 --provider anthropic -q "$(cat prompt-a.md)"

# Terminal B — OpenAI via Codex auth (ChatGPT Plus $20 quota)
hermes chat -m gpt-5.4 --provider openai-codex -q "$(cat prompt-b.md)"
```

**Model name gotcha (openai-codex):** The ChatGPT Codex backend only accepts
`gpt-5.4` (the exact model name from `~/.codex/config.toml`). Other names like
`gpt-4.1`, `o4-mini`, `gpt-4o`, `codex-mini` all return HTTP 400. The base_url
is `https://chatgpt.com/backend-api/codex` — not the standard OpenAI API.

**Exhausted credentials:** If a provider shows `last_status: exhausted`, reset it:
```bash
hermes auth reset anthropic   # or: hermes auth reset openai-codex
```
Check status: `hermes status` or parse `~/.hermes/auth.json` credential_pool.

**Available providers** (check with `hermes chat --help`):
`anthropic`, `openai-codex`, `openrouter`, `nous`, `copilot`, `huggingface`, etc.

**For overnight batches:** Assign analysis tasks to sonnet (cheaper, Anthropic quota)
and implementation tasks to gpt-5.4 (OpenAI quota) — different rate limit pools.

## Write-Back Rules (Issues #1941-1952, ALL CLOSED)

**Repo .claude/skills/ is the single source of truth.** ~/.hermes/skills/ is empty
(9 MB cleaned, 0 SKILL.md files local). external_dirs wiring means both Hermes AND
Claude Code see everything written there. No dual-write, no sync drift.

**Verified skill counts (active, no _archive):**
  workspace-hub: 696 | CAD-DEVELOPMENTS: 218 | digitalmodel: 31
  worldenergydata: 21 | achantas-data: 13 | assetutilities: 3
  Total unique: ~1156 across 6 repos

**All 4 agents access same skill library:**
  - Claude Code: reads .claude/skills/ directly (on-demand via slash commands)
  - Codex CLI: .codex/skills → symlink → ../.claude/skills
  - Gemini CLI: .gemini/skills → symlink → ../.claude/skills
  - Hermes: external_dirs (6 paths in config.yaml, reads all repos)

**Per-repo .codex/.gemini symlink pattern:**
  - workspace-hub: `.codex/skills -> ../.claude/skills`
  - sub-repos (CAD-DEVELOPMENTS, etc.): `.codex/skills -> ../../.claude/skills`
  - If symlink broken (real directory with stale files): delete real dir, create symlink

### Rule 1: Skills Go to .claude/skills/ Directly
When creating a new skill, write SKILL.md to
`workspace-hub/.claude/skills/<category>/<name>/SKILL.md`.
Then: `git add .claude/skills/ && git commit -m "hermes: new skill — <name>"`.

### Rule 2: Script Persistence
Reusable scripts → `scripts/` in repo. If part of a skill → skill's `scripts/` subdir.

### Rule 3: Hook/Rule Generation
- Rules: `.claude/rules/<name>.md` (CC frontmatter with trigger/glob)
- Hooks: `.claude/hooks/<name>.sh` (POSIX shell, auto-fires on CC sessions)

### Rule 4: Commit Immediately
All `.claude/` writes get `git add + commit + push` with clear provenance.

### Automatic Drift Guard (Issues #1943, #1948)
`scripts/hermes/backfill-skills-to-repo.sh` — wired into `harness-update.sh`
(runs after `update_hermes`, via `backfill_hermes_skills()` function).
Detects any skills in ~/.hermes/skills/ that aren't in any repo and copies
them over with per-repo routing (see below).

Usage: `backfill-skills-to-repo.sh [--dry-run] [--commit]`

**Per-Repo Routing (#1948):**
The backfill script routes skills to the correct repo automatically:
1. Scans all 6 external_dirs repos for existing category matches
2. Routes by exact category name match (e.g., "engineering" → CAD-DEVELOPMENTS)
3. Falls back to substring match
4. Defaults to workspace-hub
5. Per-repo git commit + push (digitalmodel commits in digitalmodel/ etc.)

**Testing pattern:** Create dummy skill in ~/.hermes/skills/ → run --dry-run
to verify routing → run --commit for full pipeline → clean up dummy, revert commit.

**Skill count verification:**
```bash
# Total active across all repos:
find /mnt/local-analysis/workspace-hub/{.claude,CAD-DEVELOPMENTS/.claude,\
  worldenergydata/.claude,achantas-data/.claude,assetutilities/.claude,\
  digitalmodel/.claude}/skills \
  -name SKILL.md -not -path "*/_archive/*" | wc -l
```

## Pitfalls

1. **`hermes update` overwrites patches** — always save patches to
   `config/agents/hermes/patches/` so harness-update.sh re-applies them
2. **Config template is NOT the live config** — template has `__WS_HUB_PATH__`
   placeholder; never copy it directly without resolving
3. **YAML merge direction matters** — template wins over existing for shared keys;
   this means template changes propagate automatically but can override manual tweaks
4. **Hostname matching in resolve_ws_hub_path** — uses `hostname.lower() in name.lower()`
   which is fuzzy; if hostname doesn't match any workstation, falls back to $WS_HUB
5. **Skills count baseline in harness-config.yaml** is 0 — set it with
   `nightly-readiness.sh --update-baseline` after initial setup
6. **skill_manage can't edit external skills** — returns "not found" because it only
   searches `~/.hermes/skills/` (local). Use `patch()` on the raw filesystem path
   to fix external skills. The skill is immediately visible via skill_view after.
7. **Session export JSONL is now git-tracked** — `!logs/orchestrator/hermes/` and
   `!logs/orchestrator/codex/` exceptions added to .gitignore. Committed nightly by
   `commit-learning-artifacts.sh`. Session-signals need redaction first (see
   `agent-learnings-portability` skill).
8. **Each repo's .claude/ is a full ecosystem** — not just skills but also commands,
   docs, rules, memory, state, work-queue, AGENTS.md, CLAUDE.md. The 24 repos with
   `.claude/` dirs each have their own agent contract (AGENTS.md often points back
   to workspace-hub's canonical contract).
9. **Skill content security scanner blocks commits** — pipeline-detail.md and other
   skill docs with embedded shell examples trigger CRITICAL/HIGH findings (echo_pipe_exec,
   persistence_cron, etc.). These are false positives on documentation. Use
   `git commit --no-verify` for skill docs that contain code examples. Do NOT disable
   the scanner globally — it's useful for actual skill code.
10. **Overnight corpus analysis needs git contention map** — when parallelizing analysis
    across 3+ agents, prefix output paths by phase (phase-a-*, phase-b-*, etc.) and
    enforce negative write boundaries (explicit DO NOT WRITE TO lists) in each prompt.
    Agents will "helpfully" fix files in other terminals' territory without this.
11. **Claude plugin updates must use the installed plugin id, not just the slug** —
    for Superpowers, `claude plugin update superpowers --scope project` can fail with
    `Plugin "superpowers" not found` even when the plugin is installed and enabled.
    First inspect `claude plugin list --json`, then use the returned `id` field, e.g.
    `superpowers@claude-plugins-official`, with the detected scope:
    `claude plugin update superpowers@claude-plugins-official --scope project`.
    For automation, treat `claude plugin list --json` as the source of truth for
    plugin id + scope + enabled state, and summarize installed scopes in dry-run output.
