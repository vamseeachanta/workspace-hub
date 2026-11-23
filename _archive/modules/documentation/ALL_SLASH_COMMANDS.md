# 📚 Complete Slash Commands Reference

## Overview
Complete list of all available slash commands across the repository ecosystem.

## 🎯 Core Commands

### Git Management Commands

#### `/git-sync`
- **Purpose**: Sync local repository with remote
- **Usage**: `/git-sync`
- **Features**: Stashes changes, pulls latest, reapplies stash

#### `/git-trunk-flow`
- **Purpose**: Complete git trunk-based development workflow
- **Usage**: `/git-trunk-flow`
- **Features**: Automated branching, merging, and cleanup

#### `/git-trunk-flow-enhanced`
- **Purpose**: Enhanced trunk flow with parallel processing
- **Usage**: `/git-trunk-flow-enhanced`
- **Features**: Smart conflict resolution, policy enforcement

#### `/git-trunk-status`
- **Purpose**: Check trunk flow status across repos
- **Usage**: `/git-trunk-status`
- **Features**: Branch status, pending changes, merge readiness

#### `/git-trunk-sync-all`
- **Purpose**: Sync all repositories in parallel
- **Usage**: `/git-trunk-sync-all`
- **Features**: 5-10 parallel workers, comprehensive reporting

#### `/git-sync-all-enhanced`
- **Purpose**: Enhanced sync for all 25 repositories
- **Usage**: `/git-sync-all-enhanced`
- **Features**: Automatic stashing, conflict handling

#### `/git-commit-push-merge-all`
- **Purpose**: Batch commit, push, and merge operations
- **Usage**: `/git-commit-push-merge-all`
- **Features**: Process all repos with single command

## 📝 Specification Commands

### `/create-spec` (Updated)
- **Purpose**: Create specification documents
- **Usage**: `/create-spec <spec-name> <module-name>`
- **MANDATORY**: Module name required
- **Creates**: `specs/modules/[module-name]/YYYY-MM-DD-spec-name/`
- **Files**: spec.md, tasks.md, sub-specs/

### `/create-spec-enhanced` (Updated)
- **Purpose**: Create enhanced specifications with advanced features
- **Usage**: `/create-spec-enhanced <spec-name> <module-name> [variant]`
- **MANDATORY**: Module name required
- **Variants**: enhanced (default), research, minimal
- **Features**: Executive summaries, mermaid diagrams, comprehensive tasks

## 🚀 Task Execution Commands

### `/execute-tasks`
- **Purpose**: Execute tasks from specification
- **Usage**: `/execute-tasks @specs/modules/module/spec/tasks.md`
- **Features**: TDD approach, progress tracking

### `/execute-tasks-enhanced` (Updated)
- **Purpose**: Enhanced task execution with parallel processing
- **Usage**: `/execute-tasks-enhanced tasks.md --workers 10`
- **MANDATORY**: Uses existing repo's uv environment
- **Features**: 
  - 10-thread parallel processing
  - Time estimation
  - Automatic test verification
  - UV environment detection

## ✅ Verification Commands

### `/verify-ai-work` (Updated)
- **Purpose**: Interactive verification of AI-generated work
- **Usage**: `/verify-ai-work tasks.json`
- **MANDATORY**: Must run from spec folder
- **Features**:
  - Child-friendly interface
  - Manual confirmation required
  - LLM-style feedback collection
  - Reports to `verification_report/YYYYMMDD_HHMMSS.json`

## 🔧 Development Tools

### `/modernize-deps`
- **Purpose**: Modernize dependencies and module structure
- **Usage**: `/modernize-deps`
- **Features**: UV migration, dependency updates, lock file generation

### `/organize-structure`
- **Purpose**: Enforce module-based project organization
- **Usage**: `/organize-structure`
- **Features**: Restructure to modules pattern, update imports

### `/test-automation`
- **Purpose**: Cross-repository test automation
- **Usage**: `/test-automation`
- **Features**: Parallel test execution, coverage reports

### `/test-automation-enhanced`
- **Purpose**: Enhanced test automation with AI agents
- **Usage**: `/test-automation-enhanced`
- **Features**: Intelligent test generation, mutation testing

## 🌐 Ecosystem Commands

### `/sync-all-commands`
- **Purpose**: Synchronize slash commands across all repositories
- **Usage**: `/sync-all-commands`
- **Features**: Conflict resolution, version management

### `/propagate-commands`
- **Purpose**: Distribute commands to all repositories
- **Usage**: `/propagate-commands`
- **Features**: Selective distribution, dependency checking

### `/search-commands`
- **Purpose**: Search for commands across ecosystem
- **Usage**: `/search-commands <pattern>`
- **Features**: Regex support, cross-repo search

### `/install-ecosystem-awareness`
- **Purpose**: Install ecosystem awareness in repository
- **Usage**: `/install-ecosystem-awareness`
- **Features**: CLAUDE.md setup, command integration

## 📊 Command Statistics

### Total Commands: 18

### By Category:
- **Git Management**: 7 commands
- **Specifications**: 2 commands
- **Task Execution**: 2 commands
- **Verification**: 1 command
- **Development Tools**: 4 commands
- **Ecosystem**: 4 commands

### Recent Updates:
- `/verify-ai-work` - Now requires spec folder execution
- `/execute-tasks-enhanced` - UV environment integration
- `/create-spec` - Mandatory module structure
- `/create-spec-enhanced` - Mandatory module structure

## 🎮 Quick Usage Examples

### Creating a New Feature
```bash
# Step 1: Create specification
/create-spec user-authentication auth

# Step 2: Navigate to spec folder
cd specs/modules/auth/2025-01-15-user-authentication/

# Step 3: Execute tasks
/execute-tasks-enhanced tasks.md

# Step 4: Verify work
/verify-ai-work verification-tasks.json
```

### Git Workflow
```bash
# Sync single repo
/git-sync

# Sync all repos
/git-sync-all-enhanced

# Complete trunk flow
/git-trunk-flow
```

### Test Automation
```bash
# Run tests
/test-automation

# Enhanced testing with AI
/test-automation-enhanced
```

## 🔍 Command Locations

### Primary Location
```
.agent-os/commands/
├── create-spec.py
├── execute-tasks-enhanced.py
├── git-sync.py
├── git-trunk-flow.py
├── verify-ai-work.py
└── ... (other commands)
```

### Alternative Locations
```
digitalmodel/
├── create-spec.py
├── create-spec-enhanced.py
└── slash_commands.py (runner)
```

## 🚦 Command Status

### ✅ Active & Maintained
All 18 commands listed above

### 🔄 Recently Updated
- `/verify-ai-work` - Spec folder requirement
- `/execute-tasks-enhanced` - UV environment
- `/create-spec` - Module structure
- `/create-spec-enhanced` - Module structure

### 📋 Mandatory Requirements
1. `/create-spec` - Module name required
2. `/verify-ai-work` - Spec folder execution only
3. `/execute-tasks` - UV environment usage

## 💡 Tips

### For New Users
1. Start with `/create-spec` to plan features
2. Use `/execute-tasks` to implement
3. Verify with `/verify-ai-work`
4. Sync with `/git-sync`

### For Power Users
1. Use enhanced variants for advanced features
2. Leverage parallel processing commands
3. Automate with ecosystem commands
4. Chain commands for workflows

## 📝 Notes

- All commands support `--help` flag for detailed usage
- Commands auto-detect repository context
- Parallel commands use 5-10 workers by default
- All commands respect `.gitignore` patterns
- Commands integrate with UV environment when available

---

*Last updated: January 13, 2025*
*Total repositories: 25*
*Total unique commands: 18*