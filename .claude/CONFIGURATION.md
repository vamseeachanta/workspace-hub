# Context Management Configuration

> Zero-installation context management available workspace-wide
> Version: 1.0.0
> Last Updated: 2026-01-14

## Overview

Context management tools are **automatically available** in all workspace-hub repositories with **zero installation required**. Simply clone the repository and start using context management features.

**No pip install. No environment configuration. No PYTHONPATH setup. Just git clone and use.**

## Quick Start

```bash
# Clone workspace-hub
git clone <url> workspace-hub
cd workspace-hub

# Python anywhere in the repository - context management works
python -c "from context_manager import ContextManager; print(ContextManager())"

# Or using discovery mechanism
python -c "from discovery import add_tools_to_path; add_tools_to_path(); from context_manager import ContextManager"
```

## Import Patterns

### Pattern 1: Direct Import (Recommended)

Works when running from workspace-hub root or any repository:

```python
from context_manager import ContextManager
from task_context_wrapper import TaskContextWrapper
from worker_contract import WorkerResponse, WorkerContractValidator

# Usage
context_manager = ContextManager()
status = context_manager.get_status(current_tokens=50000)
```

**When it works**: Automatic sys.path configuration via .claude/tools/__init__.py

**Supported locations**:
- workspace-hub/ (project root)
- Any subdirectory within workspace-hub
- External repositories that symlink or reference workspace-hub/.claude/tools/

### Pattern 2: Discovery-Based (For External Repositories)

For repositories outside workspace-hub that need context management:

```python
from discovery import add_tools_to_path
add_tools_to_path()  # One-time call - adds workspace-hub/.claude/tools/ to sys.path

from context_manager import ContextManager
from task_context_wrapper import TaskContextWrapper

# Usage
context_manager = ContextManager()
```

**When to use**: External repositories need to import context management tools

**How it works**:
1. Discovery mechanism walks up directory tree from current location
2. Looks for workspace-hub marker (.git directory with .claude/tools/)
3. Adds found path to sys.path automatically
4. Subsequent imports work without configuration

**Supported depths**: Up to 10 directory levels (reasonable limit for nested repos)

### Pattern 3: CLI Usage (No Import)

For scripts that don't need Python imports:

```bash
# Check context health
python workspace-hub/.claude/tools/context_manager.py status 50000

# Create checkpoint
python workspace-hub/.claude/tools/context_manager.py checkpoint "my-task" "complete"

# Show trim guidelines
python workspace-hub/.claude/tools/context_manager.py trim
```

## Per-Machine State Directories

Context management maintains **per-machine directories** that are NOT synced to git:

### .claude/state/

**Purpose**: Current task state and agent results

**Directory structure**:
```
.claude/state/
├── context_state.json       # Current context health state
└── agent_results/           # Worker agent output files
    ├── worker-1-result.json
    └── worker-2-result.json
```

**Why local?**: Each machine has different task execution history and state persistence. State is automatically managed by context_manager.py.

**Automatic cleanup**: Files older than 7 days are archived or deleted. No manual intervention needed.

### .claude/checkpoints/

**Purpose**: Task recovery and context snapshots

**Directory structure**:
```
.claude/checkpoints/
├── 20260114_143500_task-name.md
├── 20260114_145200_another-task.md
└── archive/
    └── older-checkpoints/
```

**Why local?**: Checkpoints are machine-specific recovery artifacts. Each machine maintains its own checkpoint history.

**Git exclusion**: Never committed to repository (.gitignore: `.claude/checkpoints/`)

### .claude/outputs/

**Purpose**: Large output artifacts from context management operations

**Directory structure**:
```
.claude/outputs/
├── reports/
│   └── context-health-report.md
└── data/
    └── archived-exchanges.json
```

**Why local?**: Prevents large output files from bloating repository. Each machine stores outputs locally.

**Git exclusion**: Never committed to repository (.gitignore: `.claude/outputs/`)

## Architecture Confirmation

### Zero Installation Verification

The infrastructure requires:
- ✅ **Python 3.8+** (standard library only, no pip packages)
- ✅ **Git** (for repository cloning)
- ✅ **No PYTHONPATH configuration** (automatic via discovery)
- ✅ **No environment setup** (works immediately after clone)
- ✅ **No pip install** (stdlib only)

### What's Synced to Git

**TRACKED in repository** (distributed via git clone):
- `.claude/tools/__init__.py` - Python package initialization
- `.claude/tools/context_manager.py` - Core context management
- `.claude/tools/task_context_wrapper.py` - Task integration
- `.claude/tools/worker_contract.py` - Worker coordination
- `.claude/tools/discovery.py` - Import discovery mechanism
- `.claude/CLAUDE.md` - Context management configuration
- `.claude/CONFIGURATION.md` - This documentation
- `.gitignore` - Explicit per-machine directory exclusions

**NOT TRACKED in repository** (stay per-machine):
- `.claude/state/` - Task execution state
- `.claude/checkpoints/` - Recovery checkpoints
- `.claude/outputs/` - Large output artifacts
- `~/.claude/` - User-level configuration

## Core Components

### ContextManager

Provides token tracking, health monitoring, and checkpoint creation:

```python
from context_manager import ContextManager

manager = ContextManager()

# Check context health
status = manager.get_status(current_tokens=50000)
print(f"Health: {status['status']}")  # 🟢 Healthy, 🟡 Elevated, 🟠 High, 🔴 Critical
print(f"Used: {status['percent_used']}%")
print(f"Should archive: {status['should_archive']}")  # Boolean

# Create checkpoint
checkpoint_path = manager.create_checkpoint(
    task_name="data-analysis",
    status="in_progress",
    key_findings=["Found 15 anomalies", "3 outliers detected"],
    next_action="Investigate anomalies and prepare report",
    metrics={"anomaly_count": 15, "processing_time_sec": 45.3}
)

# Restore state
state = manager.load_state()
manager.save_state({"task_id": "123", "status": "running"})
```

**Health Indicators**:
| %ctx | Status | Action |
|------|--------|--------|
| 0-40% | 🟢 Healthy | Normal operation |
| 40-60% | 🟡 Elevated | Consider summarizing |
| 60-80% | 🟠 High | Archive older exchanges |
| 80-100% | 🔴 Critical | Trim to essentials immediately |

### TaskContextWrapper

Wraps task execution with automatic context management:

```python
from task_context_wrapper import TaskContextWrapper

wrapper = TaskContextWrapper()

# Pre-execution setup
pre_state = wrapper.before_task_execution(
    task_id="task-123",
    task_name="data_processing",
    description="Process and analyze 10,000 records"
)

# Post-execution cleanup
post_state = wrapper.after_task_execution(
    task_result={"status": "success", "records_processed": 10000},
    task_status="completed",
    key_findings=["All records valid", "Found 5 duplicates"],
    next_action="Generate report and archive results"
)
```

### WorkerContractValidator

Validates worker responses in swarm coordination:

```python
from worker_contract import WorkerResponse, WorkerContractValidator

# Create response
response = WorkerResponse(
    worker_id="validator-1",
    status="complete",
    summary="Validated 1000 records, 2 errors found",  # Max 300 chars
    output_file=".claude/outputs/validation_results.json",
    next_action="Review errors and retry",  # Max 150 chars
    key_metrics={"total": 1000, "errors": 2, "success_rate": 0.998}
)

# Validate
validator = WorkerContractValidator()
is_valid, errors = validator.validate(response)

if is_valid:
    response.save_result()
```

### Discovery Mechanism

Enables automatic import discovery from any directory depth:

```python
from discovery import add_tools_to_path

# One-time call at script start
add_tools_to_path()

# Now imports work from any repository location
from context_manager import ContextManager
from task_context_wrapper import TaskContextWrapper
```

**Discovery process**:
1. Starts at current working directory
2. Walks up directory tree (max 10 levels)
3. Looks for .git directory with .claude/tools/ subdirectory
4. Adds discovered tools path to sys.path
5. Raises ImportError if not found within 10 levels

## Troubleshooting

### Import Error: "Could not discover .claude/tools/ directory"

**Cause**: Not running from within workspace-hub or subdirectories, or discovery depth exceeded

**Solution**:
```bash
# Option 1: Ensure you're in workspace-hub
cd workspace-hub
python your_script.py

# Option 2: Use absolute path
python /path/to/workspace-hub/your_script.py

# Option 3: Manually add path
export PYTHONPATH="/path/to/workspace-hub/.claude/tools:$PYTHONPATH"
python your_script.py
```

### "No module named 'context_manager'"

**Cause**: __init__.py not found or discovery mechanism failed

**Solution**:
```bash
# Verify __init__.py exists
ls -la workspace-hub/.claude/tools/__init__.py

# Try discovery explicitly
python -c "from discovery import add_tools_to_path; add_tools_to_path(); from context_manager import ContextManager"
```

### State files not found in ~/.claude/

**Cause**: First-time usage - directories auto-create on first use

**Solution**: First call to ContextManager will auto-create directories:
```bash
python -c "from context_manager import ContextManager; ContextManager()"
```

Check with:
```bash
ls -la ~/.claude/state/
ls -la ~/.claude/checkpoints/
```

## Implementation Details

### Stdlib-Only Dependencies

All context management tools use **only Python standard library**:
- json - State persistence
- os - File operations
- datetime - Timestamps
- pathlib - Path operations
- typing - Type hints
- dataclasses - Data structures
- enum - Status enumerations

**No external pip packages required.**

### Performance

- **Startup time**: <10ms (pure Python, no dependencies)
- **Token counting**: O(1) operation (simple arithmetic)
- **Checkpoint creation**: O(n) where n = messages to archive (typically <100)
- **Discovery mechanism**: O(d) where d = directory depth (typically <5)

### Thread Safety

Context management tools are **NOT thread-safe**. For concurrent operations:
- Use separate ContextManager instances per thread
- Or synchronize access with threading.Lock()

Example:
```python
import threading
from context_manager import ContextManager

lock = threading.Lock()
shared_manager = ContextManager()

def worker_task():
    with lock:
        status = shared_manager.get_status(current_tokens=50000)
```

## Integration with SPARC Methodology

Context management integrates with SPARC workflows:

```python
# In specification phase
wrapper.before_task_execution("spec-001", "Specification", "Define requirements")

# In pseudocode phase
wrapper.before_task_execution("pseudo-001", "Pseudocode", "Design algorithm")

# In architecture phase
wrapper.before_task_execution("arch-001", "Architecture", "System design")

# In refinement phase
wrapper.before_task_execution("refine-001", "Refinement", "TDD implementation")

# In completion phase
wrapper.after_task_execution(result, "completed", ["All phases complete"], "Deploy")
```

## Next Steps

1. **Verify installation**: Run `python -c "from context_manager import ContextManager"`
2. **Check state directory**: `ls ~/.claude/state/`
3. **Review CLAUDE.md**: Full context management rules at `/mnt/local-analysis/workspace-hub/.claude/CLAUDE.md`
4. **Try checkpoint creation**: `python .claude/tools/context_manager.py checkpoint "test" "complete"`

## Support

For issues or questions:
- Review error messages - they provide specific guidance
- Check CLAUDE.md for context management rules
- Verify .claude/tools/ files exist in workspace-hub repository
- Ensure Python 3.8+ is installed

---

**Portability Status**: ✅ Fully portable
**Installation Required**: ❌ None
**Setup Time**: ~10 seconds (git clone)
**Workspace Availability**: ✅ All repositories
**Team Adoption**: Ready
