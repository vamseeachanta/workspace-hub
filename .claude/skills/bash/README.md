# Bash Skills Library

> Reusable bash patterns extracted from workspace-hub's 25+ repository ecosystem
> Version: 1.0.0 | Last Updated: 2026-01-14

## Overview

This library contains 8 battle-tested bash skills extracted from real-world scripts managing multi-repository workflows, AI orchestration, and automation. Each skill follows the Anthropic Skills format with examples, best practices, and complete implementations.

## Quick Start

```bash
# Browse available skills
ls skills/bash/

# Read a skill
cat skills/bash/parallel-batch-executor/SKILL.md

# Skills are documentation - copy patterns into your scripts
```

## Available Skills

| Skill | Description | Key Patterns |
|-------|-------------|--------------|
| [bash-cli-framework](./bash-cli-framework/SKILL.md) | Build professional CLI tools | Argument parsing, help generation, subcommands |
| [parallel-batch-executor](./parallel-batch-executor/SKILL.md) | 300% performance with xargs | Parallel execution, progress tracking, error collection |
| [interactive-menu-builder](./interactive-menu-builder/SKILL.md) | Multi-level menu systems | Color output, navigation, input validation |
| [state-directory-manager](./state-directory-manager/SKILL.md) | Temporary and persistent state | Temp files, lock files, cleanup traps |
| [usage-tracker](./usage-tracker/SKILL.md) | Log and monitor operations | Pipe-delimited logs, statistics, alerting |
| [complexity-scorer](./complexity-scorer/SKILL.md) | Analyze task complexity | Keyword matching, scoring algorithms, model selection |
| [git-sync-manager](./git-sync-manager/SKILL.md) | Multi-repo git operations | Batch pull/commit/push, status checks, branch management |
| [json-config-loader](./json-config-loader/SKILL.md) | Parse configuration files | Key=value, JSON/jq, environment overrides |

## Skill Categories

### CLI & User Interface
- **bash-cli-framework** - Professional command-line tools
- **interactive-menu-builder** - Interactive navigation menus

### Performance & Parallelization
- **parallel-batch-executor** - High-performance batch operations

### State & Configuration
- **state-directory-manager** - File and directory state management
- **json-config-loader** - Multi-format configuration parsing

### Monitoring & Analytics
- **usage-tracker** - Operation logging and monitoring
- **complexity-scorer** - Task analysis and scoring

### Version Control
- **git-sync-manager** - Multi-repository git operations

## Common Patterns Across Skills

### Color Output
```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}✓${NC} Success"
echo -e "${RED}✗${NC} Error" >&2
```

### Script Directory Resolution
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```

### Cleanup Traps
```bash
cleanup() {
    rm -f "$TEMP_FILE"
}
trap cleanup EXIT INT TERM
```

### Default Values
```bash
PARALLEL="${PARALLEL:-5}"
LOG_DIR="${LOG_DIR:-./logs}"
```

### Error Handling
```bash
set -e  # Exit on error
set -u  # Error on undefined variables
set -o pipefail  # Catch pipe failures
```

## Integration with Workspace-Hub

These skills power the workspace-hub infrastructure:

```
workspace-hub/
├── scripts/
│   ├── repository_sync         # Uses: git-sync-manager, interactive-menu-builder
│   ├── workspace               # Uses: bash-cli-framework, interactive-menu-builder
│   ├── monitoring/
│   │   ├── suggest_model.sh    # Uses: complexity-scorer
│   │   └── check_claude_usage.sh  # Uses: usage-tracker
│   ├── batchtools/
│   │   └── batch_runner.sh     # Uses: parallel-batch-executor
│   └── ai-workflow/
│       └── run-workflow.sh     # Uses: json-config-loader, state-directory-manager
└── config/
    └── repos.conf              # Uses: json-config-loader patterns
```

## Usage Examples

### Build a CLI Tool
```bash
# See bash-cli-framework for complete patterns
source skills/bash/bash-cli-framework/SKILL.md  # Read patterns

# Your script:
show_usage() {
    cat << 'EOF'
Usage: mytool <command> [options]
Commands:
    start    Start the service
    stop     Stop the service
EOF
}

main() {
    case "${1:-}" in
        start) do_start "${@:2}" ;;
        stop)  do_stop "${@:2}" ;;
        *)     show_usage; exit 1 ;;
    esac
}
```

### Run Parallel Operations
```bash
# See parallel-batch-executor for complete patterns
PARALLEL=10

# Process items in parallel
cat items.txt | xargs -I {} -P "$PARALLEL" bash -c '
    if process_item "{}"; then
        echo "✓ {}"
    else
        echo "✗ {}" >&2
    fi
'
```

### Load Configuration
```bash
# See json-config-loader for complete patterns
declare -A CONFIG

parse_config() {
    while IFS= read -r line; do
        [[ "$line" =~ ^# ]] && continue
        [[ "$line" =~ ^([^=]+)=(.*)$ ]] && CONFIG["${BASH_REMATCH[1]}"]="${BASH_REMATCH[2]}"
    done < "$1"
}

parse_config "config.conf"
echo "Value: ${CONFIG[key]:-default}"
```

## Best Practices

### 1. Always Include ABOUTME Comments
```bash
#!/bin/bash
# ABOUTME: Brief description of what this script does
# ABOUTME: Second line with additional context
```

### 2. Use Strict Mode
```bash
set -euo pipefail
```

### 3. Provide Help
```bash
[[ "${1:-}" =~ ^(-h|--help|help)$ ]] && { show_usage; exit 0; }
```

### 4. Clean Up Resources
```bash
trap 'rm -f "$TEMP_FILE"' EXIT
```

### 5. Use Colors Judiciously
```bash
# Only if terminal supports it
[[ -t 1 ]] && GREEN='\033[0;32m' || GREEN=''
```

## Testing Skills

Each skill includes testable examples. Create test scripts:

```bash
#!/bin/bash
# test_skill.sh

source_skill() {
    # Extract and source code blocks from SKILL.md
    sed -n '/```bash/,/```/p' "$1" | sed '1d;$d'
}

# Test a specific pattern
test_pattern() {
    local skill="$1"
    echo "Testing: $skill"
    # Add your tests here
}

test_pattern "parallel-batch-executor"
```

## Contributing

When adding new skills:

1. **Extract from real scripts** - Don't create artificial examples
2. **Follow the format** - YAML frontmatter, sections, examples
3. **Include complete implementations** - Patterns should be copy-paste ready
4. **Add to this README** - Update the skills table and categories
5. **Version history** - Track changes at the bottom of SKILL.md

## Related Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [GNU Bash Manual](https://www.gnu.org/software/bash/manual/)
- [Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/)
- [ShellCheck](https://www.shellcheck.net/) - Shell script analysis

## Version History

- **1.0.0** (2026-01-14): Initial release with 8 bash skills extracted from workspace-hub

---

*These skills represent patterns refined across 25+ repositories and thousands of script executions in production environments.*
