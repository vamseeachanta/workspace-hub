# Repository Sync Manager - Visual Menu Guide

## 🎯 Dual Interface Modes

| Mode | Usage | Description |
|------|-------|-------------|
| **Interactive Menu** | `./repository_sync` | Navigate through 3-level menus visually |
| **Command-Based** | `./repository_sync <command> <scope>` | Direct CLI commands for automation |

---

## 📊 Complete 3-Level Menu Structure

### Level 1: Main Menu

```
╔════════════════════════════════════════════════════════════════╗
║           Repository Sync Manager - Interactive Menu          ║
╚════════════════════════════════════════════════════════════════╝

Repository Statistics:
  Total repositories: 73
  Work repositories: 17
  Personal repositories: 9

Main Menu:

  1) Repository Operations
  2) Git Operations
  3) Branch Management
  4) Configuration
  5) Help

  0) Exit
```

| Option | Category | Leads To | Description |
|--------|----------|----------|-------------|
| **1** | Repository Operations | Level 2 Menu | View, clone, and check repository status |
| **2** | Git Operations | Level 2 Menu | Commit, push, pull, and sync changes |
| **3** | Branch Management | Level 2 Menu | Manage branches across all repositories |
| **4** | Configuration | Level 2 Menu | Edit settings and refresh lists |
| **5** | Help | Help Screen | Display command reference |
| **0** | Exit | - | Exit the program |

---

### Level 2: Repository Operations Menu

```
Repository Operations

  1) List All Repositories
  2) List Work Repositories
  3) List Personal Repositories
  4) Clone Repositories          → Level 3 submenu
  5) Repository Status           → Level 3 submenu

  0) Back to Main Menu
```

| Option | Action | Leads To | Description |
|--------|--------|----------|-------------|
| **1** | List All | Display & Return | Show all repositories with status |
| **2** | List Work | Display & Return | Show work repositories only |
| **3** | List Personal | Display & Return | Show personal repositories only |
| **4** | Clone | Level 3 Submenu | Go to clone scope selection |
| **5** | Status | Level 3 Submenu | Go to detailed status selection |
| **0** | Back | Level 1 | Return to main menu |

#### Level 3: Clone Repositories Submenu

```
Clone Repositories

  1) Clone All Repositories
  2) Clone Work Repositories Only
  3) Clone Personal Repositories Only

  0) Back
```

| Option | Scope | Action | Result |
|--------|-------|--------|--------|
| **1** | All | Clone operation | Clone all repositories not yet cloned |
| **2** | Work | Clone operation | Clone work repositories only |
| **3** | Personal | Clone operation | Clone personal repositories only |
| **0** | - | Navigate back | Return to Repository Operations |

#### Level 3: Repository Status Submenu

```
Repository Status

  1) Status All Repositories
  2) Status Work Repositories
  3) Status Personal Repositories

  0) Back
```

| Option | Scope | Action | Result |
|--------|-------|--------|--------|
| **1** | All | Show detailed status | Git status for all repos |
| **2** | Work | Show detailed status | Git status for work repos |
| **3** | Personal | Show detailed status | Git status for personal repos |
| **0** | - | Navigate back | Return to Repository Operations |

---

### Level 2: Git Operations Menu

```
Git Operations

  1) Commit Changes              → Level 3 submenu
  2) Push to Remote              → Level 3 submenu
  3) Pull from Remote            → Level 3 submenu
  4) Full Sync (Commit + Push)   → Level 3 submenu

  0) Back to Main Menu
```

| Option | Operation | Leads To | Description |
|--------|-----------|----------|-------------|
| **1** | Commit | Level 3 Submenu | Stage and commit changes |
| **2** | Push | Level 3 Submenu | Push commits to remote |
| **3** | Pull | Level 3 Submenu | Pull updates from remote |
| **4** | Sync | Level 3 Submenu | Commit + push in one operation |
| **0** | Back | Level 1 | Return to main menu |

#### Level 3: Commit Changes Submenu

```
Commit Changes

  1) Commit All Repositories
  2) Commit Work Repositories
  3) Commit Personal Repositories

  0) Back

→ Prompts for commit message after selection
```

| Option | Scope | Prompts | Action |
|--------|-------|---------|--------|
| **1** | All | Commit message | Commit all repos with message |
| **2** | Work | Commit message | Commit work repos with message |
| **3** | Personal | Commit message | Commit personal repos with message |
| **0** | - | - | Return to Git Operations |

#### Level 3: Push to Remote Submenu

```
Push to Remote

  1) Push All Repositories
  2) Push Work Repositories
  3) Push Personal Repositories

  0) Back
```

| Option | Scope | Action | Result |
|--------|-------|--------|--------|
| **1** | All | Push operation | Push all repos to remote |
| **2** | Work | Push operation | Push work repos to remote |
| **3** | Personal | Push operation | Push personal repos to remote |
| **0** | - | Navigate back | Return to Git Operations |

#### Level 3: Pull from Remote Submenu

```
Pull from Remote

  1) Pull All Repositories
  2) Pull Work Repositories
  3) Pull Personal Repositories

  0) Back
```

| Option | Scope | Action | Result |
|--------|-------|--------|--------|
| **1** | All | Pull operation | Pull all repos from remote |
| **2** | Work | Pull operation | Pull work repos from remote |
| **3** | Personal | Pull operation | Pull personal repos from remote |
| **0** | - | Navigate back | Return to Git Operations |

#### Level 3: Full Sync Submenu

```
Full Sync (Commit + Push)

  1) Sync All Repositories
  2) Sync Work Repositories
  3) Sync Personal Repositories

  0) Back

→ Prompts for commit message after selection
```

| Option | Scope | Prompts | Action |
|--------|-------|---------|--------|
| **1** | All | Commit message | Commit + push all repos |
| **2** | Work | Commit message | Commit + push work repos |
| **3** | Personal | Commit message | Commit + push personal repos |
| **0** | - | - | Return to Git Operations |

---

### Level 2: Branch Management Menu

```
Branch Management

  1) List Branches               → Level 3 submenu
  2) Fetch Remote Branches       → Level 3 submenu
  3) Sync with Main Branch       → Level 3 submenu
  4) Switch Branch               → Level 3 submenu

  0) Back to Main Menu
```

| Option | Operation | Leads To | Description |
|--------|-----------|----------|-------------|
| **1** | List Branches | Level 3 Submenu | View branches in repositories |
| **2** | Fetch Branches | Level 3 Submenu | Fetch and track remote branches |
| **3** | Sync with Main | Level 3 Submenu | Merge/rebase main into current |
| **4** | Switch Branch | Level 3 Submenu | Switch to different branch |
| **0** | Back | Level 1 | Return to main menu |

#### Level 3: List Branches Submenu

```
List Branches

  1) List All Repositories
  2) List Work Repositories
  3) List Personal Repositories

  0) Back
```

| Option | Scope | Action | Result |
|--------|-------|--------|--------|
| **1** | All | Display branches | Show branches for all repos |
| **2** | Work | Display branches | Show branches for work repos |
| **3** | Personal | Display branches | Show branches for personal repos |
| **0** | - | Navigate back | Return to Branch Management |

#### Level 3: Fetch Remote Branches Submenu

```
Fetch Remote Branches

  1) Fetch All Repositories
  2) Fetch Work Repositories
  3) Fetch Personal Repositories

  0) Back
```

| Option | Scope | Action | Result |
|--------|-------|--------|--------|
| **1** | All | Fetch + track | Fetch all remote branches (all repos) |
| **2** | Work | Fetch + track | Fetch all remote branches (work repos) |
| **3** | Personal | Fetch + track | Fetch all remote branches (personal repos) |
| **0** | - | Navigate back | Return to Branch Management |

#### Level 3: Sync with Main Branch Submenu

```
Sync with Main Branch

  Merge Strategy:
  1) Sync All (Merge)
  2) Sync Work (Merge)
  3) Sync Personal (Merge)

  Rebase Strategy:
  4) Sync All (Rebase)
  5) Sync Work (Rebase)
  6) Sync Personal (Rebase)

  0) Back
```

| Option | Scope | Strategy | Action |
|--------|-------|----------|--------|
| **1** | All | Merge | Merge main into all repos |
| **2** | Work | Merge | Merge main into work repos |
| **3** | Personal | Merge | Merge main into personal repos |
| **4** | All | Rebase | Rebase all repos with main |
| **5** | Work | Rebase | Rebase work repos with main |
| **6** | Personal | Rebase | Rebase personal repos with main |
| **0** | - | - | Return to Branch Management |

#### Level 3: Switch Branch Submenu

```
Switch Branch

  1) Switch All Repositories
  2) Switch Work Repositories
  3) Switch Personal Repositories

  0) Back

→ Prompts for branch name after selection
```

| Option | Scope | Prompts | Action |
|--------|-------|---------|--------|
| **1** | All | Branch name | Switch all repos to branch |
| **2** | Work | Branch name | Switch work repos to branch |
| **3** | Personal | Branch name | Switch personal repos to branch |
| **0** | - | - | Return to Branch Management |

---

### Level 2: Configuration Menu

```
Configuration

  1) Edit Repository Configuration
  2) Refresh Repository List
  3) View Statistics

  0) Back to Main Menu
```

| Option | Action | Result | Description |
|--------|--------|--------|-------------|
| **1** | Edit Config | Opens editor | Edit repos.conf with URLs |
| **2** | Refresh | Reload data | Re-parse .gitignore and config |
| **3** | View Stats | Display counts | Show repository statistics |
| **0** | Back | Level 1 | Return to main menu |

---

## 🎮 Navigation Controls

| Key | Action | Description |
|-----|--------|-------------|
| **1-9** | Select option | Choose menu item by number |
| **0** | Go back | Return to previous menu level |
| **ENTER** | Continue | After viewing results, return to menu |
| **Ctrl+C** | Exit | Exit program at any time |

---

## 🔄 Example Navigation Flows

### Flow 1: Commit All Repositories

```
./repository_sync
  ↓
Main Menu → Select: 2 (Git Operations)
  ↓
Git Operations → Select: 1 (Commit Changes)
  ↓
Commit Submenu → Select: 1 (Commit All)
  ↓
[Prompt] → Enter: "Update dependencies"
  ↓
[Execute] → Commit operation runs
  ↓
[Pause] → Press ENTER
  ↓
Commit Submenu → Select: 0 (Back)
  ↓
Git Operations → Select: 0 (Back)
  ↓
Main Menu
```

### Flow 2: Fetch Remote Branches for Work Repos

```
./repository_sync
  ↓
Main Menu → Select: 3 (Branch Management)
  ↓
Branch Management → Select: 2 (Fetch Remote Branches)
  ↓
Fetch Submenu → Select: 2 (Fetch Work)
  ↓
[Execute] → Fetch operation runs
  ↓
[Pause] → Press ENTER
  ↓
Fetch Submenu → Select: 0 (Back)
  ↓
Branch Management
```

### Flow 3: Clone Personal Repositories

```
./repository_sync
  ↓
Main Menu → Select: 1 (Repository Operations)
  ↓
Repository Operations → Select: 4 (Clone Repositories)
  ↓
Clone Submenu → Select: 3 (Clone Personal Only)
  ↓
[Execute] → Clone operation runs
  ↓
[Pause] → Press ENTER
  ↓
Clone Submenu → Select: 0 (Back)
  ↓
Repository Operations
```

---

## 📝 Command-Based Mode (Alternative)

All interactive menu operations are also available as direct commands:

| Interactive Path | Command Equivalent |
|-----------------|-------------------|
| Main → Repo Ops → List All | `./repository_sync list all` |
| Main → Repo Ops → Clone → Work | `./repository_sync clone work` |
| Main → Git Ops → Commit → All | `./repository_sync commit all -m "message"` |
| Main → Git Ops → Push → Work | `./repository_sync push work` |
| Main → Git Ops → Sync → Personal | `./repository_sync sync personal -m "message"` |
| Main → Branch → List → All | `./repository_sync branches all` |
| Main → Branch → Fetch → Work | `./repository_sync fetch-branches work` |
| Main → Branch → Sync-Main → All (Merge) | `./repository_sync sync-main all` |
| Main → Branch → Sync-Main → All (Rebase) | `./repository_sync sync-main all --rebase` |
| Main → Branch → Switch → Work | `./repository_sync switch work feature-branch` |
| Main → Config → Edit | `./repository_sync config` |
| Main → Config → Refresh | `./repository_sync refresh` |

---

## 🎨 Visual Features

- **Color Coding:**
  - `CYAN` - Menu headers and options
  - `GREEN` - Success messages and statistics
  - `RED` - Errors and exit option
  - `YELLOW` - Warnings and "Back" option
  - `BLUE` - Menu titles
  - `MAGENTA` - Personal repos

- **Clear Screen:** Each menu clears the screen for clean display

- **Statistics:** Main menu shows repository counts

- **Pause:** Operations pause after completion to view results

- **Prompts:** Interactive prompts for messages and branch names

---

## 💡 Best Practices

1. **Start with Interactive Mode** for learning and exploration
2. **Use Command Mode** for scripts and automation
3. **View Help (Option 5)** to see all available commands
4. **Check Statistics (Config → 3)** to verify repository discovery
5. **Edit Config First** before cloning repositories

---

## 🚀 Quick Start

```bash
# Launch interactive menu (recommended for first-time users)
./repository_sync

# Or use direct commands (for experienced users)
./repository_sync list work
./repository_sync clone all
./repository_sync commit all -m "Your message"
```
