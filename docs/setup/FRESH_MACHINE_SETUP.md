# Fresh machine setup

End-to-end walkthrough for bootstrapping a new machine into the workspace-hub fleet. Tested on Linux (ace-linux-1), validated on macOS + Windows per acceptance criteria of issue [#2751](https://github.com/vamseeachanta/workspace-hub/issues/2751).

## Prerequisites (you provide)

| Item | Why |
|---|---|
| Working internet connection | OAuth flows + npm/brew/choco package install |
| Git ≥ 2.30 | Clone + submodules + worktrees |
| Bash (built into Linux/macOS; `Git Bash` on Windows) | The bootstrap is a bash script |
| Sudo / admin rights | Step 10 (auto-install) needs elevation for system-package installs |
| Anthropic, OpenAI, GitHub, Google accounts | Step 11 (auth orchestration) launches their OAuth flows |
| Optional: macOS Homebrew, Windows Chocolatey or winget | Package managers for Step 10 on macOS/Windows respectively |

## Single-command bootstrap

```bash
git clone https://github.com/vamseeachanta/workspace-hub.git
cd workspace-hub
bash scripts/setup/new-machine-setup.sh
```

That's it. The script is idempotent — safe to re-run any time.

On Windows native PowerShell (Phase 5 of #2751, post-merge):

```powershell
pwsh scripts\setup\new-machine-setup.ps1
```

## What runs (14 steps)

| # | Step | Interactivity | Notes |
|---|---|---|---|
| 1 | Submodule init | unattended | `git submodule update --init --recursive` |
| 2 | Git hooks | unattended | `install-all-hooks.sh` (pre-commit / post-merge / post-rewrite / post-commit) |
| 3 | Claude statusline | unattended | `claude config set statusBarEnabled true` or JSON fallback |
| 3b | Claude keybindings | unattended | Copies `config/claude/keybindings.json` to `~/.claude/keybindings.json` (Ctrl+Enter = submit) |
| 4 | Shell aliases | unattended | Sources `config/shell/bashrc-snippets.sh` from `~/.bashrc` |
| 5 | npm PATH | unattended | `npm config set prefix ~/.npm-global` |
| 5b | Codex CLI pin | unattended | Runs `scripts/install/pin-codex.sh` for version-pinning |
| 6 | Crontab / Task Scheduler | unattended | Linux: cron entries; Windows: prints Task Scheduler instructions |
| 7 | SSH key | unattended | Generates `ed25519` key if missing |
| 8 | `.env` template | unattended | Copies `.env.example → .env` |
| 8b | tmux | unattended | Linux/macOS only; copies tmux config |
| **9** | **AI-provider harness** | unattended | Runs `scripts/memory/bootstrap-machine.sh` → creates `~/.claude/CLAUDE.md` pointer + unconditional SOUL symlink install for `~/.hermes/SOUL.md`, `~/.codex/AGENTS.md` |
| **10** | **Auto-install provider CLIs** | **may sudo** | Channel-branched: `gh` via system pkg; `claude`/`gemini` via npm; `codex` via `pin-codex.sh` |
| **11** | **Auth orchestration** | **browser** | Launches `claude auth login`, `codex auth login`, `gh auth login`, `gemini -p ping` in sequence; Hermes `.env` via `read -s` (values never echoed) |
| **12** | **Hermes config** | unattended | Renders `~/.hermes/config.yaml` from template (idempotent) |
| **13** | **Emit machine-status** | unattended | Writes `config/machine-baselines/<token>.{md,yaml}` with 22-dim status |
| 14 | Verify | unattended | Runs `scripts/setup/verify-setup.sh` for final PASS/WARN/FAIL report |

## UX phases (what to expect interactively)

Per the plan's UX Contract:

- **Phase A — Fully unattended** (Steps 1-9, 12-14): zero user input.
- **Phase B — Elevation-required** (Step 10): sudo password prompt on Linux/macOS, UAC on Windows. Install confirmations (`-y`) are auto-supplied; elevation itself is unavoidable on most OSes.
- **Phase C — Browser-blocking** (Step 11): each `<cli> auth login` opens a browser. Complete the OAuth flow, return to terminal. Up to 4 browser flows in sequence (~30 seconds of attention each). Hermes `.env` field prompts use `read -s` so values are never echoed.
- **Phase D — Side-effect emission** (Step 13): writes to `config/machine-baselines/<token>.{md,yaml}`. Idempotent — re-runs only change `last_updated` timestamp.

Total wall-clock: ~3-8 minutes (mostly Phase B/C user interaction).

## After setup: post the baseline to operational tracker

```bash
git add config/machine-baselines/
git commit -m "chore(setup): bootstrap <hostname> via #2751 setup"
git push
```

Then open [operational tracker #2753](https://github.com/vamseeachanta/workspace-hub/issues/2753) and post the contents of `config/machine-baselines/<token>.md` as a comment. The control plane (`ace-linux-1`) reads both the git-tracked YAML and the issue comments to assess fleet drift.

## Canonical harness-parity coverage table (4 × 22)

This is the **load-bearing table** for understanding what each stage of setup achieves. Each cell shows what state the dimension is in after that stage.

Legend: ✅ = present; ❌ = absent; (•) = machine-local-by-design (never replicates); n/a = not applicable on this OS.

| Dimension | Fresh clone alone | + bootstrap (Step 9) | + auth (Step 11) | + Hermes config (Step 12) |
|---|---|---|---|---|
| **AI-provider harness (13)** | | | | |
| 1. soul_contracts | ✅ (git-tracked) | ✅ | ✅ | ✅ |
| 2. skills (`.claude/skills/`) | ✅ (git-tracked) | ✅ | ✅ | ✅ |
| 3. rules (`.claude/rules/`) | ✅ (git-tracked) | ✅ | ✅ | ✅ |
| 4. bridged_memory (`.claude/memory/`) | ✅ (git-tracked) | ✅ | ✅ | ✅ |
| 5. claude_global_pointer (`~/.claude/CLAUDE.md`) | ❌ | ✅ | ✅ | ✅ |
| 6. codex_agents_symlink (`~/.codex/AGENTS.md` → repo) | ❌ | ✅ | ✅ | ✅ |
| 7. hermes_soul_symlink (`~/.hermes/SOUL.md` → repo) | ❌ | ✅ | ✅ | ✅ |
| 8. claude_cli_auth (`~/.claude/.credentials.json`) | ❌ | ❌ | ✅ | ✅ |
| 9. codex_cli_auth (`~/.codex/auth.json`) | ❌ | ❌ | ✅ | ✅ |
| 10. gh_cli_auth (`gh auth status`) | ❌ | ❌ | ✅ | ✅ |
| 11. gemini_cli_auth (`~/.gemini/oauth_creds.json`) | ❌ | ❌ | ✅ | ✅ |
| 12. hermes_can_boot (`~/.hermes/config.yaml` valid) | ❌ | ❌ | ❌ | ✅ |
| 13. raw_session_state | (•) | (•) | (•) | (•) |
| **Repo + tooling (9 added per r2 C6)** | | | | |
| 14. submodules_initialized | ❌ | ✅ (Step 1) | ✅ | ✅ |
| 15. git_hooks_installed | ❌ | ✅ (Step 2) | ✅ | ✅ |
| 16. shell_profile_wired | ❌ | ✅ (Step 4) | ✅ | ✅ |
| 17. npm_global_prefix | ❌ | ✅ (Step 5) | ✅ | ✅ |
| 18. scheduler_entries (Linux cron / Windows Task Scheduler) | ❌ | ✅ (Step 6) | ✅ | ✅ |
| 19. ssh_key_present (`~/.ssh/id_*`) | ❌ | ✅ (Step 7) | ✅ | ✅ |
| 20. env_file_present (`.env` from template) | ❌ | ✅ (Step 8) | ✅ | ✅ |
| 21. uv_or_python_available | ❌* | ❌* | ❌* | ❌* |
| 22. git_bash_available (Windows only; n/a elsewhere) | varies | varies | varies | varies |

\* `uv` install is currently a manual step — `curl -LsSf https://astral.sh/uv/install.sh \| sh`. Future v1.1 may bundle this into Step 10.

### How to read this table

- **"+ bootstrap" column = end of Steps 1-9** — what you have after running `bash scripts/setup/new-machine-setup.sh` if you skip the auth prompts (Step 11 fails closed but other steps complete).
- **"+ auth" column = end of Step 11** — what you have after completing the 4 browser OAuth flows.
- **"+ Hermes config" column = end of Step 12** — what you have for end-to-end Hermes runtime parity.
- **Step 13** writes the actual per-machine status snapshot to `config/machine-baselines/<token>.{md,yaml}` so the table above is empirically verifiable per machine.

## What does NOT transfer with the clone (intentional)

By design, the following remain machine-local and are never committed:

- `~/.claude/projects/<dir>/memory/` — Claude Code per-project auto-memory (each machine's session learnings stay local).
- `~/.claude/history.jsonl` — session history.
- `~/.codex/sessions/`, `~/.codex/logs_2.sqlite` — Codex execution logs.
- `~/.hermes/state.db`, `~/.hermes/sessions/` — Hermes runtime state + session checkpoints.
- `~/.gemini/history/` — Gemini query history.
- All auth tokens — `~/.claude/.credentials.json`, `~/.codex/auth.json`, `~/.gemini/oauth_creds.json`, `~/.hermes/.env`, `~/.config/gh/hosts.yml`. These require per-machine re-authentication.

This is the explicit design — institutional knowledge (skills, rules, memory) replicates via git; per-machine learned state stays local.

## Cross-references

- [README.md](README.md) — index
- [EXISTING_MACHINE_AUDIT.md](EXISTING_MACHINE_AUDIT.md) — for in-place machines
- [PROVIDER_AUTH_GUIDE.md](PROVIDER_AUTH_GUIDE.md) — per-provider auth details
- [MACHINE_REGISTRY.md](MACHINE_REGISTRY.md) — control-plane fleet assessment
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — known issues
- Plan: [`docs/plans/2026-05-19-issue-2751-cross-platform-harness-setup.md`](../plans/2026-05-19-issue-2751-cross-platform-harness-setup.md)
