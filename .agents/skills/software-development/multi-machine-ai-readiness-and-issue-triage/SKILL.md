---
name: multi-machine-ai-readiness-and-issue-triage
description: Assess a multi-machine, multi-repo AI-enabled workspace for readiness, provider allocation, and issue prioritization.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [readiness, multi-machine, github-issues, triage, ai-harness, cron, subscriptions]
    related_skills: [github-issues, writing-plans]
---

# Multi-Machine AI Readiness and Issue Triage

Use when a workspace spans multiple machines, multiple repos, scheduled jobs, and multiple AI provider subscriptions.

## When to Use
- User wants all machines kept in a "ready" state
- There are cron jobs / scheduled tasks across machines
- There are GitHub issues in both a hub repo and individual repos
- User has multiple AI subscriptions and wants to maximize weekly usage
- Need to decide what to fix first across platform vs repo-local work

## Core Approach

### 1. Identify control-plane docs first
Read these first if present:
- `AGENTS.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- `docs/ops/scheduled-tasks.md`
- `config/scheduled-tasks/schedule-tasks.yaml`
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- session-analysis or readiness scripts under `scripts/analysis/`, `scripts/cron/`, `scripts/maintenance/`

Goal: determine machine roles, scheduled automation, provider roles, and readiness signals before touching issues.

### 2. Separate machine roles from provider roles
Do not assume every machine needs every provider.

Model the estate like this:
- **Primary machine**: orchestration/control plane, full cron suite, repo sync, learning pipeline
- **Secondary machine(s)**: contribution lanes, repo sync, selected provider/tool installs
- **Licensed/specialized machines**: minimal repo readiness first; AI harness only if needed for their role

### 3. Define readiness explicitly
A machine is "ready" only if all relevant checks pass:
- reachable
- workspace present in expected path
- repos synced / auth working
- required CLIs installed (`git`, `uv`, provider CLIs, `hermes`, etc.)
- scheduled jobs installed for that machine variant
- logs being written
- harness/tool versions not badly drifted

Useful evidence sources:
- scheduled-task inventory docs
- repo sync logs
- harness update logs
- tool-parity snapshots like `config/ai_agents/ai-tools-status.yaml`
- session-analysis / learning-report logs

### 4. Allocate providers by economic role, not evenly
For mixed subscriptions, do not spread tools uniformly across all machines.

Recommended pattern:
- **Highest-tier provider** -> orchestration, planning, cross-repo synthesis, final integration
- **Mid/low-cost duplicate seats** -> implementation lane + reviewer/overflow lane
- **Single selective seat** -> architecture review, long-context synthesis, ambiguity resolution

Default routing heuristic:
- Provider A: decide / orchestrate
- Provider B seat 1: implement
- Provider B seat 2: adversarial review / overflow
- Provider C: architecture or research-only escalation

### 5. Triage issues in three layers
Never treat all issues from all repos as one flat backlog.

#### Layer 1: Hub / ecosystem issues
Prioritize first when they affect:
- multiple machines
- multiple repos
- cron or sync health
- AI routing / harness parity
- issue/work-queue hygiene

#### Layer 2: Repo-specific issues
Prioritize by business value:
- client/delivery blockers
- shared/core repos used by others
- personal/support repos later

#### Layer 3: Umbrella/meta issues
Only prioritize early if they clearly unblock many concrete issues.
Otherwise decompose and defer until operational blockers are stable.

### 6. Score issues with a reusable rubric
For each issue, assess:
- impact
- urgency
- frequency
- blast radius
- leverage
- effort
- dependency/unblocking value

Plain rule: do first what affects many places, happens often, blocks others, and is cheap/moderate to fix.

### 7. Recommended cadence
- **Daily**: blockers, sync/auth/tool failures, active delivery issues
- **Twice weekly**: hub operational issues, harness parity, machine readiness
- **Weekly**: repo improvements, backlog grooming, skills/harness refinement
- **Monthly**: umbrella issues, broad refactors, non-urgent consolidation

## Practical Output Format
When reporting findings, produce:
1. Current machine roles
2. Current provider/subscription allocation
3. Readiness definition
4. Priority issue buckets:
   - Ready now
   - Needs plan
   - Needs dependencies
   - Defer
5. Recommended next-wave issues
6. Provider-to-task routing policy

## Good First Targets
If the ecosystem is unstable, prioritize issues about:
- provider/tool install parity across machines
- cross-machine cron health monitoring
- review/routing policy operationalization
- issue template / machine-scope hygiene

## Agent Config Parity via Repo Templates

When the ecosystem uses multiple AI agents (Claude, Codex, Gemini, Hermes, etc.), manage configs centrally:

### Pattern: config/agents/{provider}/ → sync script → ~/.{agent}/
- Store non-secret config templates in `config/agents/{provider}/` in the hub repo
- Use a sync script (e.g. `scripts/_core/sync-agent-configs.sh`) that merges templates into home dirs
- JSON configs: use `jq -s '.[0] * .[1]'` to merge (local overrides preserved)
- YAML configs (e.g. Hermes): no reliable shell-native merge — use create-or-skip strategy (copy template if target absent, skip if differs, `--force` to overwrite). This is safe when secrets live in separate files (auth.json, .env).
- TOML configs: use awk to strip managed keys, prepend defaults, append managed sections

### What IS transferable across machines (sync via repo):
- Model defaults, toolset configs, terminal settings
- Skills (bundled update handles these; custom skills version in repo)
- Agent persona files (SOUL.md, AGENTS.md)
- Plugin/extension lists

### What IS transferable via git snapshots (nightly cron → commit):
- Agent memories (Hermes MEMORY.md/USER.md, Claude project memory feedback_/project_ files)
- Learning artifacts (corrections/, patterns/, learned-patterns.json, cc-insights/)
- Cross-agent state (hermes-insights.yaml, cross-agent-memory.yaml)
- Codex learned rules (default.rules), history, session index
- Gemini state.json, projects.json
- Exported session JSONL (tool-call metadata, not full transcripts)

Pattern: snapshot to `config/agents/{agent}/state-snapshots/` or `config/agents/{agent}/memories/`,
commit nightly via `scripts/cron/commit-learning-artifacts.sh`, restore on new machine via
`sync-agent-configs.sh` (copy snapshot → home dir if local files absent).

CRITICAL: .gitignore exceptions are useless without `git add` in the pipeline. Audit that
every `!.claude/state/foo/` exception actually has files committed — discovered 5/10 exceptions
had zero files in git index despite allowing tracking.

### What is NOT transferable (machine-local, manual setup):
- Auth tokens, API keys (auth.json, .env, oauth_creds.json)
- Full session transcripts (too large for git — use rsync backup to secondary machine)
- SQLite databases (state.db, state_5.sqlite — too large, use rsync)
- File snapshots, checkpoints
- Model availability caches

### Extending to new agents:
When adding a new agent (e.g. Hermes) to the sync pipeline:
1. Create `config/agents/{agent}/config.yaml.template` (strip secrets)
2. Add sync function to sync-agent-configs.sh
3. Add agent to harness-update cron schedule for all target machines
4. Verify with `--dry-run` before live sync

## Post-OS-Update Machine Recovery

OS updates (apt upgrade, kernel updates) commonly break multi-machine readiness:

### Display/VNC failures after update:
- `/etc/gdm3/custom.conf` may re-enable Wayland (resets `WaylandEnable=false`)
- Kernel updates change DRM card numbering (card2-DP-3 → card0-DP-1)
- NVIDIA driver updates change DFP-N output mappings
- Captured EDID files (`/etc/X11/edid.bin`) become stale
- KVM switches lose EDID signal → display goes blank

### NVIDIA kernel module gap (most common post-update failure):
When `nvidia-smi` fails after a kernel upgrade, check this first:
```bash
ssh target "uname -r"                                    # running kernel
ssh target "dpkg -l | grep linux-modules-nvidia | grep -v '^rc'"  # installed nvidia module packages
# Compare: if running kernel (e.g. 6.17.0-20) has no matching nvidia module package → that's the problem
# Fix: sudo apt update && sudo apt install linux-modules-nvidia-580-open-$(uname -r)
# If package doesn't exist yet: boot into older kernel via grub-reboot
ssh target "ls /boot/vmlinuz-*"   # available kernels
```
The display falls back to `simple-framebuffer` (card0) when NVIDIA can't load — all DP outputs disappear.

### Recovery checklist (run from primary via SSH):
1. `ssh target "grep WaylandEnable /etc/gdm3/custom.conf"` — verify X11 mode
2. `ssh target "nvidia-smi"` — verify driver loaded (if fails, check kernel module gap above)
3. `ssh target "ls /sys/class/drm/ | grep DP"` — check card numbering
4. Re-run display fix script if card numbering changed
5. Re-capture EDID if monitor connection changed
6. Test VNC connection after display is confirmed

### Guard against future updates:
- Pin critical Xorg configs with `dpkg-divert` or apt conf.d hold
- Add post-update readiness check to cron (verify Wayland disabled, EDID present)
- Document hardware-level permanent fix (EDID emulator dongle) as alternative

## Post-Update Drift Detection and Health Verification

The `harness-update.sh` daily cron updates tools but has critical blind spots. Address these when extending or auditing the harness:

### Gap: No post-update smoke test
After updating a tool, **always verify it works**. `--version` is the minimum. Real-world failure: `hermes update` stashed/popped local changes, rewrote the launcher shebang to a hardcoded venv path. Reverting to the "portable" shebang (`#!/usr/bin/env python3`) broke Hermes entirely because system python3 lacks venv dependencies (`ModuleNotFoundError: No module named 'dotenv'`).

### Gap: No pre-update security/compatibility gate
Updates are applied blindly — no `npm audit`, no changelog review, no major-version-bump guard. A malicious or breaking npm update propagates to all machines within 24 hours.

### Gap: harness-update.sh coverage is incomplete
As of 2026-04, it covers 4 tools (GStack, Hermes, Superpowers, GSD) but **misses the 3 primary AI CLIs** (Claude Code, Codex, Gemini CLI) which are npm globals.

### Machine-specific vs. portable changes in git-based tools
Some files MUST differ per machine (e.g., Hermes `hermes` launcher with venv shebang). Others are portable (e.g., `package-lock.json`). When checking for drift:

```yaml
# Drift classification pattern:
hermes:
  machine_specific:    # NEVER revert or sync — intentionally different per machine
    - "hermes"         # shebang must point to local .venv/bin/python3
  portable:            # SHOULD be identical across machines
    - "package-lock.json"
  never_sync:          # secrets, accumulated state
    - "auth.json"
    - ".env"
    - "memories/"
```

**Key lesson**: Don't blindly `git checkout` files in git-based tools after update. Classify first, revert only machine-specific artifacts that were accidentally made portable, and flag portable changes for commit to a fork.

### Recommended harness-update extensions (tracked in issue #1668)
1. Post-update: `tool --version` smoke test; mark BROKEN + rollback on failure
2. Pre-update: block major version bumps; flag npm audit critical/high
3. Post-update: `git status --porcelain` on git-based tools; log dirty files
4. Coverage: add Claude Code, Codex, Gemini CLI update functions
5. Rollback: `npm install -g pkg@previous` for npm; `git stash` for git tools

## Agent Learnings Portability Audit

When assessing whether learnings survive machine loss, run a 3-parallel-subagent audit:

1. **Subagent A: Home directory inventory** — scan `~/.claude/`, `~/.hermes/`, `~/.codex/`, `~/.gemini/` for all state files. For each: size, git-tracked?, export pipeline?, risk if lost. Focus on files <1MB that contain unique learnings (corrections, rules, patterns, memories) vs large regenerable caches.

2. **Subagent B: Project memory audit** — scan `~/.claude/projects/*/memory/` for all per-project memory files. These are the highest-value-per-byte files (user corrections in feedback_*.md). Check if backup/rsync covers them vs git tracking.

3. **Subagent C: Nightly pipeline artifact audit** — trace every script in `scripts/cron/` that produces output. For each output file: where written, gitignore status, actually committed?, survives clone? The most common failure: `.gitignore` has `!` exception but pipeline never runs `git add`.

### The gitignore-exception gap pattern
This is the #1 discovery from the audit. `.gitignore` allows:
```
!.claude/state/corrections/
!.claude/state/patterns/
```
But if the nightly pipeline never runs `git add .claude/state/corrections/`, those files accumulate locally and are NEVER committed. The exception is dead code. Always verify exceptions have matching files in `git ls-files`.

### Three-tier portability model
- **Tier 1 (git-committed)**: Small files <10MB. Memories, patterns, corrections, rules, insights. Survives `git clone`.
- **Tier 2 (rsync backup)**: Large files 10MB-1GB. Session transcripts, SQLite databases. Survives single-machine failure.
- **Tier 3 (regenerable)**: Caches, plugins, debug logs. No backup needed.

### Legal gate
ALL agent memory snapshots must pass `legal-sanity-scan.sh` before commit. Memory files and correction records routinely contain file paths, commands, or project names that reference client work.

## Pitfalls
- Don't optimize repo-local issues before hub blockers that affect every session
- Don't install every provider on every machine without a role-based reason
- Don't treat umbrella issues as execution-ready without decomposition
- Don't confuse "reachable" with "ready"
- Don't burn premium provider quota on bounded implementation tasks
- Don't copy auth/secrets via repo sync — always manual per-machine setup
- Don't assume display configs survive OS updates — always re-verify after apt upgrade
- Don't revert shebang lines in git-based tools without checking if the venv path is intentional — system python3 likely lacks tool dependencies
- Don't assume `harness-update.sh` exit 0 means all tools work — it always exits 0 even when tools are broken
