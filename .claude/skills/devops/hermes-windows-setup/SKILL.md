---
name: hermes-windows-setup
description: Install and configure a repo-centric Hermes agent workspace on Windows. Covers prerequisites, repo cloning, Python/uv environment, skills system, memory bridge, and multi-agent coordination — the Windows equivalent of the Linux workspace-hub pattern.
version: 1.0.0
tags: [hermes, windows, setup, repo-centric, workspace, installation]
related_skills: [hermes-agent, claude-code]
---

# Hermes Windows Setup

Repo-centric Hermes agent installation and configuration for Windows machines. This produces the same workspace pattern as the Linux workspace-hub: skills, memory, and configs live inside the git repo so all agents share them.

## ⚠️ Rules for This Skill

- This skill is **Windows-only**. On Linux, use the standard workspace-hub pattern.
- The workspace repo (`.claude/`) is the **source of truth** — not any global agent config.
- All skills and memory files **MUST be git-tracked**.
- Never commit `.env` files or API keys.
- Use `python` not `python3` on Windows.
- Use `uv run <script.py>` for script execution.
- Git `core.autocrlf` MUST be `true` on Windows.

## Phase 1: Prerequisites

### 1.1 — Git for Windows

```powershell
git --version
```

If not installed, download from https://git-scm.com/download/win
During install: use defaults, ensure "Git from command line" is enabled.

### 1.2 — Python 3.12+

```powershell
python --version
```

If missing, install from https://python.org
**CRITICAL:** Check "Add Python to PATH" during install.

### 1.3 — uv Package Manager

```powershell
uv --version
```

If missing:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Restart terminal after install so `uv` is on PATH.

### 1.4 — GitHub CLI

```powershell
gh --version
```

If missing:
```powershell
winget install GitHub.cli
```

Then authenticate:
```powershell
gh auth login
```
Follow interactive flow (browser-based OAuth recommended).

### 1.5 — Windows Terminal (Recommended)

Install from Microsoft Store or:
```powershell
winget install Microsoft.WindowsTerminal
```

PowerShell 7+ is strongly preferred over cmd.exe for better Unicode, pipelining, and git integration.

## Phase 2: Workspace Directory Structure

```powershell
# Create workspace root
mkdir C:\workspace-hub
cd C:\workspace-hub

# Clone the main workspace-hub repo
git clone <workspace-hub-repo-url> .

# Clone additional repos as subdirectories (if applicable)
git clone <digitalmodel-repo-url> digitalmodel
```

On Windows, paths use `\` but git/tools also accept `/`.

## Phase 3: Python Environment

```powershell
cd C:\workspace-hub

# Create virtual environment
uv venv

# Activate
.\.venv\Scripts\activate

# Install dependencies (if requirements.txt exists)
uv pip install -r requirements.txt

# Core packages if no requirements.txt:
uv pip install python-dotenv openai anthropic requests pyyaml rich click
```

On Windows, use `python` directly after activation, or `uv run script.py` without activation:
```powershell
# Both work:
python -c "import yaml; print('ok')"
uv run python -c "import yaml; print('ok')"
```

## Phase 4: Agent Installation

### Option A — Hermes Agent

```powershell
# Install via installer script
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex

# Verify
hermes --version

# Run setup wizard
hermes setup

# Configure workspace path in config.yaml
hermes config edit
```

In `config.yaml`, set external skill directories:
```yaml
skills:
  external_dirs:
    - C:\workspace-hub\.claude\skills
```

### Option B — Claude Code

```powershell
npm install -g @anthropic-ai/claude-code
claude --help
```

Claude Code reads `.claude/CLAUDE.md` and `.claude/skills/` automatically from the workspace directory.

## Phase 5: Skills System (Repo-Centric)

The skills system is the core of repo-centric agent memory. Skills live in the repo, not in a global directory, so all agents share them.

### 5.1 — Create Structure

```powershell
mkdir -p C:\workspace-hub\.claude\skills
mkdir -p C:\workspace-hub\.claude\memory
```

### 5.2 — Key Skill Files to Ensure Exist

Copy or create these in `.claude/skills/`:
- `workspace-cli/` — CLI conventions
- `repo-structure/` — source layout conventions
- `clean-code/` — coding standards
- `memory-bridge-operation/` — Hermes ↔ repo memory sync
- `repo-structure/` — project directory conventions

If cloning from an existing workspace-hub repo, these are already present.

### 5.3 — How External Skills Work

Hermes indexes `.claude/skills/` as an external skill directory:
- **Read-only** — Hermes reads but never writes to external skills
- **Full integration** — appear in system prompt, skills_list, and slash commands
- **Local precedence** — local `~/.hermes/skills/` overrides external if same name

## Phase 6: Memory Bridge

The memory bridge syncs agent memory into git-tracked files:

```powershell
# Create memory files
New-Item -Path "C:\workspace-hub\.claude\memory\user.md" -ItemType File -Force
New-Item -Path "C:\workspace-hub\.claude\memory\project.md" -ItemType File -Force
```

These files are git-tracked and serve as persistent memory accessible to ALL agents working in this workspace.

Configure your agent to read these files at session start. For Hermes, add to config:
```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
```

## Phase 7: Git Configuration

```powershell
cd C:\workspace-hub
git config user.name "Your Name"
git config user.email "your@email.com"
git config core.autocrlf true
git config core.eol crlf

# SSH agent (if using SSH)
Start-Service ssh-agent
```

Create `.gitignore` if not present:
```
.venv/
__pycache__/
*.pyc
.env
node_modules/
*.log
.DS_Store
```

## Phase 8: Verification

Run these checks in order:

```powershell
# 1. Clean working tree
git status

# 2. Python version
uv run python -c "import sys; print(sys.version)"

# 3. GitHub auth
gh auth status

# 4. Agent test — simple task
hermes chat -q "List all .md files in .claude/skills/"
```

Expected:
1. `git status` → clean working tree (or untracked `.env` is OK)
2. Python 3.12+ shown
3. "Logged in to github.com" shown
4. Agent completes task without errors

## Phase 9: First Run

Start your agent pointing at `C:\workspace-hub`:

```powershell
cd C:\workspace-hub
hermes
```

Test prompt: "Read .claude/AGENTS.md and confirm you understand the workspace conventions."

## Multi-Agent Coordination on Windows

### Running Multiple Agents

All agents (Hermes, Claude Code, Codex) point at the same `C:\workspace-hub` directory and read from the same `.claude/skills/` and `.claude/memory/`.

### Git Contention Prevention

When running multiple agents simultaneously:

```powershell
# Use git worktree mode in Hermes
hermes -w  # or --worktree

# Or use separate worktrees for each agent
git worktree add ../workspace-hub-agent-a
git worktree add ../workspace-hub-agent-b
```

### Windows-Specific Notes for Background Processes

```powershell
# Background with Start-Process (PowerShell)
Start-Process -NoNewWindow -FilePath "uv" -ArgumentList "run", "script.py"

# Background with hermes
hermes chat -q "Long running task"  # Fire-and-forget mode
```

## Windows vs Linux Differences

| Aspect | Linux | Windows |
|--------|-------|---------|
| Python command | `uv run python3` or `python3` | `python` or `uv run python` |
| Path separator | `/` | `\` (but `/` works too) |
| Shebangs | `#!/usr/bin/env python3` | Don't rely — use `uv run` |
| Git line endings | `core.autocrlf=input` | `core.autocrlf=true` |
| Background | `&` or `nohup` | `Start-Process` |
| Terminal | bash/zsh | PowerShell 7+ |
| SSH agent | `eval $(ssh-agent)` | `Start-Service ssh-agent` |
| Home dir | `~/.hermes/` | `%USERPROFILE%\.hermes\` |

## Workspace-Hub Parity Audit Findings (2026-04-11)

When using Claude Code directly on a Windows machine inside the workspace-hub ecosystem, the repo preserves most Hermes advantages via git-tracked `.claude/skills/`, `.claude/memory/`, `.claude/state/`, and exported orchestrator logs. However, full parity is **not automatic** yet. Apply these checks before calling the setup complete:

### Required for high-confidence parity

1. **Git Bash is required** — current Claude project hooks invoke `bash` commands extensively.
2. **Node.js + Claude Code auth must be working** — verify with `claude --version` and `claude auth status --text`.
3. **Install `uv` on Windows Git Bash unless you have patched the hooks** — several tracked hooks still call `uv run ...`.
4. **Provide a `python3` shim/alias or patch hooks to use `python`** — some hooks still call `python3` even though Windows conventions say `python`.
5. **`jq` should be installed in Git Bash** — readiness and hook scripts expect it.

### Repo-side caveats to check

- `scripts/readiness/harness-config.yaml` may still have `licensed-win-1.ws_hub_path: null`. Set the actual Windows workspace path (for example `D:\\workspace-hub`) when hardening a real machine.
- A tracked readiness proof file should exist after setup: `.claude/state/harness-readiness-licensed-win-1.yaml`.
- Windows write-back parity is still incomplete if issue `#1918` (Windows auto-memory sync back to repo) is still open. Windows can consume shared context now, but may not automatically publish all new learnings back into the ecosystem.
- Treat Windows as **repo-parity first**: Claude Code reads `.claude/` directly, so you retain most Hermes advantages even without installing Hermes locally.

### Practical interpretation

If the machine can:
- `git pull`
- run Claude Code from repo root
- execute `.claude/settings.json` hooks successfully under Git Bash
- see shared `.claude/skills/`, `.claude/memory/`, `.claude/state/`

then it is good enough for productive Claude-on-Windows work, even if full Hermes runtime parity is not yet complete.

## Common Windows Pitfalls

### Antivirus Blocking

Windows Defender or enterprise AV may block `uv`, `hermes`, or Python scripts. Add exclusions:
```powershell
# Example: Add Windows Defender exclusion
Add-MpPreference -ExclusionPath "C:\workspace-hub"
```

### PowerShell Execution Policy

If scripts won't run:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Path Length Limit

Windows has MAX_PATH=260. Enable long paths:
```powershell
# Registry
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
# Or group policy: Computer Configuration → Administrative Templates → System → Filesystem → Enable Win32 long paths
```

### Python in VS Code Terminal

If Python isn't found in VS Code integrated terminal:
1. VS Code may use cmd.exe by default — switch to PowerShell
2. Ensure Python is in system PATH (not just user PATH)
3. Restart VS Code after PATH changes

### WSL2 (Optional)

If you need Linux compatibility:
```powershell
wsl --install
```

Keep workspace files on Windows filesystem (`/mnt/c/workspace-hub`) for cross-tool accessibility. WSL2 tools can access Windows files, but Windows tools CANNOT access WSL2 files (`\\wsl$\`).

## Troubleshooting

### "uv is not recognized"
- The installer added uv to user PATH but terminal wasn't restarted
- Close and reopen PowerShell, or run: `$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")`

### "python is not recognized"
- Python wasn't added to PATH during install
- Reinstall Python and check "Add to PATH", or manually add to PATH

### Git SSL certificate errors
- Corporate proxy may be interfering
- Configure git proxy: `git config --global http.proxy http://proxy.company.com:8080`
- Or disable SSL verification (not recommended): `git config --global http.sslVerify false`

### Skills not loading
- Check `hermes config edit` → `skills.external_dirs` points to correct path
- Verify `.claude/skills/` exists and has `SKILL.md` files
- Restart Hermes session with `/new` to reload skills

### Memory not persisting
- Check `.claude/memory/` files exist and are not empty
- Verify config has `memory.memory_enabled: true`
- Check the memory bridge script runs on session start
