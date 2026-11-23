# Hermes Weekly Cross-Machine Parity Checklist

> **Cadence:** Weekly (suggested: Monday morning or end-of-week wrap)
> **Owner:** Repo ecosystem maintainer
> **Governance issue:** [#2089](https://github.com/vamseeachanta/workspace-hub/issues/2089)

## Purpose

Verify that Hermes configuration, installed tooling, and knowledge accessibility remain consistent across all ecosystem machines. Catch drift early before it causes execution failures or silent degradation.

## Related Issues

| Issue | Role |
|-------|------|
| [#1583](https://github.com/vamseeachanta/workspace-hub/issues/1583) | Hermes config parity via repo ecosystem templates (baseline definition) |
| [#2089](https://github.com/vamseeachanta/workspace-hub/issues/2089) | Weekly review cadence and governance |
| [#1918](https://github.com/vamseeachanta/workspace-hub/issues/1918) | Windows memory parity signal/dependency |

## Machines in Scope

| Machine | OS | Hermes Role | Cron Variant |
|---------|----|-------------|--------------|
| ace-linux-1 | Linux | Primary dev | full |
| ace-linux-2 | Linux | Secondary dev | contribute |
| macbook-portable | macOS | Portable dev | none (manual) |
| licensed-win-1 | Windows | Frontier-model agent host | contribute-minimal |
| licensed-win-2 | Windows | Frontier-model agent host | contribute-minimal |

---

## 1. Consistent Hermes Settings Review

For each Linux machine (`ace-linux-1`, `ace-linux-2`):

- [ ] Hermes version matches expected (`hermes --version`)
- [ ] `~/.hermes/config.yaml` matches repo template at `config/agents/hermes/config.yaml.template`
- [ ] Model routing defaults are correct (primary model, fallback chain)
- [ ] Toolset and permissions settings are aligned
- [ ] `SOUL.md` matches repo template at `config/agents/hermes/SOUL.md`
- [ ] Auth credentials are present and valid (not expired)
- [ ] No unexpected local overrides diverging from baseline

**Evidence to capture:** `hermes --version`, `diff` of config vs template, any override notes.

## 2. Linux + macOS Hermes Machine Parity

Compare macbook-portable against the Linux baseline:

- [ ] Hermes installed and updated to same version as Linux machines
- [ ] `config.yaml` settings aligned with repo template (accounting for documented macOS-specific drift)
- [ ] `external_dirs` paths are valid and skills are visible (`hermes skills list` or equivalent)
- [ ] Knowledge paths (`llm-wikis`, resource intelligence) are accessible or have documented alternatives
- [ ] Custom skills synced or symlinked from repo
- [ ] Patch/update mechanism works (`hermes update` completes without error)
- [ ] Tool availability: key CLI tools present (`gh`, `uv`, `git`, `claude`)
- [ ] Readiness check passes or known gaps are documented

**Canonical macOS contract** (implemented in #2240):
- Machine key: `macbook-portable`
- Hostname: `Vamsees-MacBook-Air` (alias: `Vamsees-MacBook-Air.local`)
- Workspace path: `/Users/krishna/workspace-hub`
- Readiness report: `.claude/state/harness-readiness-macbook-portable.yaml`
- Harness-config: `linux_reachable: false` — unreachable from Linux hosts

**Documented unavoidable macOS drift** (update as discovered):
- Cron not available; manual or launchd-based scheduling only (`schedule_variant: none`)
- Path conventions differ (`/Users/krishna/` vs `/home/vamsee/`, `/mnt/...`)
- Some Linux-specific kernel/GPU tools not applicable
- `sed -i` requires BSD syntax (`sed -i ''`) — nightly-readiness.sh handles this
- `compare-harness-state.sh` does not yet include macOS (follow-up work)

**Evidence to capture:** `hermes --version` on macOS, skills list diff, any path resolution errors.

## 3. Windows Repo Ecosystem Parity for Frontier Models

For each Windows machine (`licensed-win-1`, `licensed-win-2`):

- [ ] Claude Code CLI installed and functional
- [ ] Codex CLI installed and functional (if applicable)
- [ ] Gemini CLI installed and functional (if applicable)
- [ ] Repo clone is current (`git pull` succeeds, no stale branch)
- [ ] Agent config sync script runs or configs manually aligned
- [ ] Memory files (`MEMORY.md`, `USER.md`) exist and are being maintained
- [ ] Key scheduled tasks running via Windows Task Scheduler
- [ ] Known Windows-specific gaps documented (reference #1918 for memory parity)

**Evidence to capture:** Agent CLI versions, `git log -1` on each machine, task scheduler export.

## 4. Outputs and Evidence to Capture Weekly

Each weekly run should produce:

- [ ] Machine-by-machine version summary (Hermes, Claude, Codex, Gemini versions)
- [ ] Config drift notes (any file diffs from repo templates)
- [ ] Skills/knowledge accessibility notes per machine
- [ ] List of newly discovered issues or regressions
- [ ] Follow-on issues filed (if any)

**Recommended output location:** Comment on #2089 or a dated entry in `logs/weekly-parity/` (once automation is established).

## 5. Follow-on Issue Creation Rules

When drift or breakage is found during the weekly review:

1. **Trivial fix** (< 5 min): Fix in place, note in weekly summary.
2. **Config drift**: File a follow-on issue labeled `cat:harness`, `machine:<affected>`, reference #1583.
3. **Missing tool/broken install**: File a follow-on issue labeled `cat:tooling`, `machine:<affected>`.
4. **Knowledge accessibility gap**: File a follow-on issue labeled `cat:knowledge`, reference #2089.
5. **Cross-machine divergence**: File a follow-on issue labeled `machine:multi`, reference #2089.

Always link follow-on issues back to #2089 for traceability.

## 6. Machine-Local vs Repo-Portable

| Artifact | Portable (in repo) | Machine-local |
|----------|-------------------|---------------|
| `config.yaml.template` | Yes | — |
| `SOUL.md` | Yes | — |
| Custom skills | Yes (`config/agents/hermes/custom-skills/`) | — |
| `MEMORY.md` / `USER.md` | — | Yes (accumulated per machine) |
| Auth credentials / `.env` | — | Yes (never in repo) |
| Cron schedule definition | Yes (`config/scheduled-tasks/`) | Installed instance |
| `hermes` binary | — | Yes (installed per machine) |

---

*Last updated: 2026-04-12*
