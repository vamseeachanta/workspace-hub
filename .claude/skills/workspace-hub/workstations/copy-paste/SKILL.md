---
name: workstations-copy-paste
description: 'Sub-skill of workstations: Copy / Paste (+5).'
version: 3.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Copy / Paste (+5)

## Copy / Paste


| Action | Linux Terminal | Windows Terminal Git Bash |
|--------|---------------|---------------------------|
| Copy selected text | Select text → right-click → Copy | `Ctrl+C` (with text selected) |
| Paste | `Shift+Insert` | `Ctrl+V` or `Shift+Insert` |
| Copy (keyboard) | `Ctrl+Shift+C` (GNOME Terminal) | `Ctrl+C` (with selection) |
| Paste (keyboard) | `Ctrl+Shift+V` (GNOME Terminal) | `Ctrl+V` |

> **Windows Git Bash note**: `Ctrl+C` is context-sensitive — with text selected it copies; without selection it sends interrupt signal.


## New Line (Multi-line Input)


| Context | Linux | Windows Git Bash |
|---------|-------|-----------------|
| AI agent multi-line input | `\` + Enter or `Shift+Enter` (claude/gemini) | Same |
| New line in terminal | `Alt+Enter` | `Shift+Enter` |
| Bash shell continuation | `\` + Enter | Same |
| Heredoc | `<<'EOF'` … `EOF` | Same (via Git Bash) |


## Terminal Tabs / Windows


| Action | Linux (GNOME Terminal) | Windows Terminal |
|--------|------------------------|-----------------|
| New tab | `Ctrl+Shift+T` | `Ctrl+Shift+T` |
| Close tab | `Ctrl+Shift+W` | `Ctrl+Shift+W` |
| Next tab | `Ctrl+PgDn` or `Ctrl+Tab` | `Ctrl+Tab` |
| Previous tab | `Ctrl+PgUp` or `Ctrl+Shift+Tab` | `Ctrl+Shift+Tab` |
| Switch to tab N | `Alt+N` (1–9) | `Ctrl+Alt+N` (1–9) |
| New window | `Ctrl+Shift+N` | `Ctrl+Shift+N` |
| Split pane (Windows Terminal) | — | `Alt+Shift+D` |


## AI Agent CLI Commands


| Action | claude | codex | gemini |
|--------|--------|-------|--------|
| Start (permissive) | `claude --dangerously-skip-permissions` | `codex --yolo` | `gemini --yolo` |
| Resume session | `claude --resume <id>` | `codex resume <id>` | — |
| Submit single-line | `Enter` | `Enter` | `Enter` |
| Multi-line input | `Shift+Enter` or `\`+Enter | `\`+Enter | `Shift+Enter` |
| Interrupt running task | `Ctrl+C` | `Ctrl+C` | `Ctrl+C` |
| Exit REPL | `exit` or `Ctrl+D` or `/exit` | `exit` or `Ctrl+D` | `exit` or `Ctrl+D` |
| Clear screen | `Ctrl+L` | `Ctrl+L` | `Ctrl+L` |
| Update CLI | `claude update` | `codex update` | `sudo npm install -g @google/gemini-cli` |


## General Productivity Shortcuts


| Action | Shortcut | Notes |
|--------|----------|-------|
| Clear screen | `Ctrl+L` or `clear` | Cross-platform; `cls` is Windows-only — use `clear` on Linux |
| Cancel / interrupt | `Ctrl+C` | Sends SIGINT to foreground process |
| End-of-file / exit shell | `Ctrl+D` | Exits agent REPL or shell |
| Move to line start | `Ctrl+A` | readline — works in Git Bash too |
| Move to line end | `Ctrl+E` | readline — works in Git Bash too |
| Reverse history search | `Ctrl+R` | Type to search; Enter to run |
| Insert last argument | `Alt+.` | Linux bash; not in Git Bash |
| Background process | `Ctrl+Z` then `bg` | Linux only |
| Persistent session | `tmux new -s <name>` | Survives disconnects; critical for long agent runs |
| Reattach tmux | `tmux attach -t <name>` | After reconnect |
| Search command history | `history \| grep <cmd>` | Cross-platform |


## Interrupt vs. Quit (Linux)


| Signal | Keys | Effect |
|--------|------|--------|
| SIGINT | `Ctrl+C` | Interrupt foreground process |
| SIGQUIT | `Ctrl+\` | Quit + core dump |
| SIGTSTP | `Ctrl+Z` | Suspend to background |
| EOF | `Ctrl+D` | Close stdin / exit shell |

---
