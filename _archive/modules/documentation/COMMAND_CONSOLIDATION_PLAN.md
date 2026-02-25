# Slash Command Consolidation Plan

## Current Problems
- 21 total commands with many variations
- Multiple "enhanced" versions (confusing)
- Similar git commands with slight differences
- Hard to remember which command does what

## Proposed Consolidated Structure (7 Core Commands)

### 1. `/git` - All Git Operations
```bash
/git status                    # Check all repos status
/git sync                      # Sync current repo
/git sync --all                # Sync all repos  
/git trunk                     # Ensure trunk-based development
/git commit "message"          # Smart commit with push
/git clean                     # Clean branches and stale data
```

### 2. `/spec` - Specification Management  
```bash
/spec create [name] [module]   # Create new spec
/spec list                     # List all specs
/spec tasks [spec-name]        # Show tasks for spec
/spec verify                   # Verify spec completion
```

### 3. `/task` - Task Execution
```bash
/task execute [task-id]        # Execute specific task
/task execute --all            # Execute all pending tasks
/task status                   # Show task status
/task verify                   # Verify AI work
```

### 4. `/test` - Testing Suite
```bash
/test run                      # Run all tests
/test run [module]             # Run module tests
/test fix                      # Auto-fix failures
/test summary                  # Generate test summaries
/test coverage                 # Show coverage report
```

### 5. `/data` - Engineering Data Management
```bash
/data scan [folder]            # Scan for engineering data
/data context [folder]         # Generate context
/data research [topics]        # Add research
/data query "search term"      # Query data
```

### 6. `/project` - Project Management
```bash
/project setup                 # Initialize project structure
/project deps                  # Modernize dependencies
/project structure             # Organize file structure
/project health                # Health check
```

### 7. `/agent` - Agent OS Management
```bash
/agent sync                    # Sync all agent commands
/agent list                    # List available commands
/agent help [command]          # Get command help
/agent install                 # Install ecosystem awareness
```

## Migration Mapping

### Git Commands (7 → 1)
- `/git-commit-push-merge-all` → `/git commit`
- `/git-sync` → `/git sync`
- `/git-sync-all-enhanced` → `/git sync --all`
- `/git-trunk-flow` → `/git trunk`
- `/git-trunk-flow-enhanced` → `/git trunk`
- `/git-trunk-status` → `/git status`
- `/git-trunk-sync-all` → `/git sync --all`

### Spec Commands (2 → 1)
- `/create-spec` → `/spec create`
- `/create-spec-enhanced` → `/spec create`

### Task Commands (2 → 1)
- `/execute-tasks` → `/task execute`
- `/execute-tasks-enhanced` → `/task execute`

### Test Commands (2 → 1)
- `/test-automation` → `/test run`
- `/test-automation-enhanced` → `/test run`

### Data Commands (1 → 1)
- `/engineering-data-context` → `/data`

### Project Commands (3 → 1)
- `/modernize-deps` → `/project deps`
- `/organize-structure` → `/project structure`
- `/install-ecosystem-awareness` → `/agent install`

### Agent Commands (4 → 1)
- `/propagate-commands` → `/agent sync`
- `/search-commands` → `/agent list`
- `/slash-commands` → `/agent list`
- `/sync-all-commands` → `/agent sync`

## Benefits

1. **Reduced from 21 to 7 commands** - 67% reduction
2. **Logical grouping** - Related functions under one command
3. **Consistent patterns** - All follow `/command subcommand` pattern
4. **Easy to remember** - Short, meaningful names
5. **No more "enhanced" confusion** - Best features integrated by default
6. **Discoverable** - `/agent help` shows everything

## Implementation Plan

### Phase 1: Create Unified Commands
1. Create new unified command handlers
2. Integrate best features from enhanced versions
3. Add subcommand routing

### Phase 2: Migration
1. Update existing commands to call new unified versions
2. Add deprecation notices
3. Update documentation

### Phase 3: Cleanup (Future)
1. Remove old commands after transition period
2. Update all references in documentation
3. Final sync to all repos

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│         AGENT OS COMMANDS (v2.0)        │
├─────────────────────────────────────────┤
│ Git:     /git [status|sync|trunk|commit]│
│ Specs:   /spec [create|list|tasks]      │
│ Tasks:   /task [execute|status|verify]  │
│ Tests:   /test [run|fix|summary]        │
│ Data:    /data [scan|context|query]     │
│ Project: /project [setup|deps|health]   │
│ Agent:   /agent [sync|list|help]        │
└─────────────────────────────────────────┘
```