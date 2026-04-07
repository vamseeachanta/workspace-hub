---
name: hermes-windows-setup
description: Install and configure a repo-centric Hermes agent workspace on Windows. Covers prerequisites, repo cloning, Python/uv environment, skills system, memory bridge, and multi-agent coordination — the Windows equivalent of the Linux workspace-hub pattern.
version: 1.0.0
tags: [hermes, windows, setup, repo-centric, workspace, installation]
related_skills: [hermes-agent, claude-code]
---

# Hermes Windows Setup

Repo-centric Hermes agent installation and configuration for Windows machines. This produces the same workspace pattern as the Linux workspace-hub: skills, memory, and configs live inside the git repo so all agents share them.

## Rules for This Skill

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
mkdir C:\workspace-hub
cd C:\workspace-hub
git clone <workspace-hub-repo-url> .
git clone <digitalmodel-repo-url> digitalmodel
```

## Phase 3: Python Environment

```powershell
cd C:\workspace-hub
uv venv
.\.venv\Scripts\activate
uv pip install -r requirements.txt
```

Core packages if no requirements.txt:
```powershell
uv pip install python-dotenv openai anthropic requests pyyaml rich click
```

## Phase 4: Agent Installation

### Option A — Hermes Agent

```powershell
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex
hermes --version
hermes setup
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

## Phase 5: Skills System (Repo-Centric)

```powershell
mkdir -p C:\workspace-hub\.claude\skills
mkdir -p C:\workspace-hub\.claude\memory
```

Key skills to ensure exist in `.claude/skills/`:
- `workspace-cli/` — CLI conventions
- `repo-structure/` — source layout conventions  
- `clean-code/` — coding standards
- `memory-bridge-operation/` — Hermes ↔ repo memory sync

## Phase 6: Memory Bridge

```powershell
New-Item -Path "C:\workspace-hub\.claude\memory\user.md" -ItemType File -Force
New-Item -Path "C:\workspace-hub\.claude\memory\project.md" -ItemType File -Force
```

Configure in config.yaml:
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
Start-Service ssh-agent
```

## Phase 8: Verification

```powershell
git status
uv run python -c "import sys; print(sys.version)"
gh auth status
hermes chat -q "List all .md files in .claude/skills/"
```

## Windows vs Linux Differences

| Aspect | Linux | Windows |
|--------|-------|---------|
| Python | `python3` or `uv run python3` | `python` or `uv run python` |
| Paths | `/` | `\` (both work) |
| Shebangs | `#!/usr/bin/env python3` | Use `uv run` |
| Git line endings | `core.autocrlf=input` | `core.autocrlf=true` |
| Background | `&` / `nohup` | `Start-Process` |
| Terminal | bash/zsh | PowerShell 7+ |
| Home dir | `~/.hermes/` | `%USERPROFILE%\.hermes\` |

## Common Pitfalls

- **Antivirus** blocking binaries — add exclusion for `C:\workspace-hub`
- **Execution policy** — `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
- **Path length** — Enable long paths in registry: `LongPathsEnabled=1`
- **uv path** — Restart terminal after uv install to pick up PATH
- **Python path** — Ensure "Add to PATH" was checked during Python install
