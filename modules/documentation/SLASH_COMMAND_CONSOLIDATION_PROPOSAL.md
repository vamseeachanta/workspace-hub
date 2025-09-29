# Slash Command Consolidation Proposal

## Current State: 20+ Commands with Overlapping Functions

### Problems Identified:
1. **Too many git variations**: 7 different git commands with similar functions
2. **Duplicate spec creation**: create-spec vs create-spec-enhanced
3. **Duplicate task execution**: execute-tasks vs execute-tasks-enhanced  
4. **Duplicate test automation**: test-automation vs test-automation-enhanced
5. **Multiple sync commands**: sync-all-commands, propagate-commands, git-sync-all-enhanced
6. **Confusing naming**: git-trunk-flow vs git-trunk-flow-enhanced vs git-trunk-sync-all

## Proposed Consolidated Command Set (8 Commands Total)

### 1. `/spec` - Unified Spec Management
**Replaces:** `/create-spec`, `/create-spec-enhanced`
```bash
/spec create MODULE_NAME [--enhanced] [--variant minimal|standard|api|research]
/spec list [--module MODULE_NAME]
/spec validate
```

### 2. `/execute` - Unified Task Execution
**Replaces:** `/execute-tasks`, `/execute-tasks-enhanced`
```bash
/execute [--spec SPEC_PATH] [--module MODULE_NAME]
/execute --status  # Show current task status
/execute --uv     # Auto-detect and use UV environment
```

### 3. `/test` - Unified Test Automation
**Replaces:** `/test-automation`, `/test-automation-enhanced`
```bash
/test run [--module MODULE_NAME] [--parallel] [--coverage] [--auto-fix]
/test summary [--module MODULE_NAME]  # New module summaries
/test validate-aaa  # Validate AAA pattern
/test generate FILE_PATH  # Generate AAA tests
```

### 4. `/git` - Unified Git Operations
**Replaces:** All 7 git commands
```bash
/git sync [--all]  # Sync current or all repos
/git trunk  # Ensure trunk-based development
/git status  # Show trunk status for all repos
/git commit-push [--merge]  # Commit, push, optionally merge
```

### 5. `/verify` - AI Work Verification
**Keeps:** `/verify-ai-work` (already good)
```bash
/verify  # Must be run in spec folder
         # Saves to verification_report/YYYYMMDD_HHMMSS.json
```

### 6. `/sync` - Cross-Repository Command Sync
**Replaces:** `/sync-all-commands`, `/propagate-commands`
```bash
/sync commands  # Sync all slash commands across repos
/sync structure  # Sync folder structures
```

### 7. `/search` - Unified Search
**Keeps:** `/search-commands` functionality
```bash
/search commands [PATTERN]
/search modules [PATTERN]
/search specs [PATTERN]
```

### 8. `/setup` - Repository Setup & Maintenance
**Replaces:** `/install-ecosystem-awareness`, `/modernize-deps`, `/organize-structure`
```bash
/setup ecosystem  # Install ecosystem awareness
/setup deps  # Modernize dependencies with UV
/setup structure  # Organize repository structure
```

## Migration Strategy

### Phase 1: Create Unified Commands
1. Create new consolidated command files
2. Each new command imports functionality from old commands
3. Add intelligent routing based on subcommands

### Phase 2: Deprecation Notices
1. Old commands show deprecation warning
2. Suggest new command to use
3. Still functional for 30 days

### Phase 3: Remove Old Commands
1. After 30 days, remove old command files
2. Keep only consolidated commands

## Benefits of Consolidation

1. **Easier to Remember**: 8 commands vs 20+
2. **Logical Grouping**: Related functions under single command
3. **Consistent Interface**: All commands follow same pattern
4. **Better Discoverability**: `/command --help` shows all options
5. **Reduced Confusion**: No more "enhanced" vs regular versions

## Implementation Example

```python
# /spec command implementation
class SpecCommand:
    def __init__(self):
        self.legacy_create_spec = CreateSpec()
        self.enhanced_create_spec = EnhancedCreateSpec()
    
    def execute(self, args):
        if args.subcommand == 'create':
            if args.enhanced or self._should_use_enhanced():
                return self.enhanced_create_spec.create(
                    args.module_name,
                    variant=args.variant
                )
            else:
                return self.legacy_create_spec.create(args.module_name)
        
        elif args.subcommand == 'list':
            return self._list_specs(args.module)
        
        elif args.subcommand == 'validate':
            return self._validate_specs()
```

## Command Mapping Reference

| Old Command | New Command | Notes |
|------------|-------------|-------|
| `/create-spec` | `/spec create` | Auto-detects enhanced mode |
| `/create-spec-enhanced` | `/spec create --enhanced` | Explicit enhanced mode |
| `/execute-tasks` | `/execute` | Uses UV by default |
| `/execute-tasks-enhanced` | `/execute --enhanced` | Legacy compatibility |
| `/test-automation` | `/test run` | Unified testing |
| `/test-automation-enhanced` | `/test run --enhanced` | With AAA validation |
| `/git-sync` | `/git sync` | Current repo |
| `/git-sync-all-enhanced` | `/git sync --all` | All repos |
| `/git-trunk-flow` | `/git trunk` | Trunk workflow |
| `/git-trunk-status` | `/git status` | Status check |
| `/sync-all-commands` | `/sync commands` | Command sync |
| `/propagate-commands` | `/sync commands` | Same as above |
| `/install-ecosystem-awareness` | `/setup ecosystem` | Setup task |
| `/modernize-deps` | `/setup deps` | Dependency update |
| `/organize-structure` | `/setup structure` | Structure setup |

## Next Steps

1. **Review & Approve** this consolidation proposal
2. **Implement** new unified commands with backward compatibility
3. **Test** in one repository first
4. **Deploy** across all repositories
5. **Deprecate** old commands with notices
6. **Remove** old commands after transition period

---

*This consolidation will reduce cognitive load and make the slash command ecosystem much more maintainable and user-friendly.*