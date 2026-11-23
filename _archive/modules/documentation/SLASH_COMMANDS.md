# Complete Slash Commands Reference

## 🎯 Primary Unified Commands (7 Main Commands)

These are the main consolidated commands that replace the previous 21+ variations:

### 1. `/git` - Unified Git Operations
**Subcommands:**
- `/git status` - Show status of all repositories
- `/git sync` - Sync all repos with origin
- `/git trunk` - Switch to trunk-based development
- `/git commit [message]` - Commit changes
- `/git clean` - Clean up branches and stale references

**Replaces:** git-sync-all, git-trunk-flow, git-trunk-status, git-commit-push-merge-all

---

### 2. `/spec` - Specification Management
**Subcommands:**
- `/spec create [name] [module]` - Create new spec with AI templates
- `/spec list` - List all specifications
- `/spec tasks [name]` - Show tasks for a spec
- `/spec templates` - Show available AI templates

**Features:**
- AI template integration (Claude Code Templates + AITmpl)
- Module-based organization
- Automatic agent recommendations
- UV environment support

**Replaces:** create-spec, create-spec-enhanced

---

### 3. `/task` - Task Execution
**Subcommands:**
- `/task execute [id]` - Execute specific task
- `/task execute --all` - Execute all pending tasks
- `/task status` - Show task completion status
- `/task verify` - Verify AI-generated work

**Features:**
- UV environment detection
- Module-aware execution
- Automatic test running
- Progress tracking

**Replaces:** execute-tasks, execute-tasks-enhanced

---

### 4. `/test` - Testing Operations
**Subcommands:**
- `/test run [module]` - Run tests (all or specific module)
- `/test fix` - Auto-fix test failures
- `/test summary` - Generate test summaries
- `/test coverage` - Show coverage report

**Features:**
- UV environment usage
- Module-level testing
- Intelligent test discovery
- Auto-fix capabilities

**Replaces:** test-automation, test-automation-enhanced

---

### 5. `/project` - Project Management
**Subcommands:**
- `/project status` - Overall project status
- `/project setup` - Initialize project structure
- `/project optimize` - Run optimization agents
- `/project docs` - Generate documentation

**Features:**
- Cross-repository management
- Performance optimization
- Documentation generation

---

### 6. `/data` - Data Operations
**Subcommands:**
- `/data context [folder]` - Generate engineering data context
- `/data analyze` - Analyze data files
- `/data pipeline` - Create ETL pipelines
- `/data optimize` - Optimize data operations

**Features:**
- Supports 25+ engineering formats (CSV, HDF5, CAD, etc.)
- Web research integration
- Module assignment
- JSON/YAML/Markdown output

---

### 7. `/ai-agent` - AI Agent Management
**Subcommands:**
- `/ai-agent list [--category]` - List all 48+ agents
- `/ai-agent recommend [context]` - Get agent recommendations
- `/ai-agent use [agent-name]` - Activate specific agent
- `/ai-agent info [agent-name]` - Show agent details
- `/ai-agent workflow [type]` - Show agent workflows

**Agent Categories:**
- Security (API audit, penetration testing)
- Performance (React optimization, database)
- Testing (test generation, E2E)
- Documentation (API docs, code docs)
- DevOps (CI/CD, infrastructure)
- Data (ETL, analysis)
- Code Quality (review, refactoring)

---

## 🔧 Utility Commands

### `/uv-env` - UV Environment Manager
**Subcommands:**
- `/uv-env info` - Show UV environment information
- `/uv-env ensure` - Ensure UV environment exists
- `/uv-env sync` - Sync dependencies
- `/uv-env add [package]` - Add dependency
- `/uv-env enhance --spec [file]` - Enhance for spec

---

### `/verify` - Verify AI Work
Standalone command that verifies AI-generated code in spec folders.
- Mandatory for specs in module folders
- Checks code quality and completeness
- Ensures test coverage

---

## 📊 Command Integration Map

```
Spec Creation → AI Agent Recommendations → Task Execution → Test Running
     ↓                    ↓                      ↓              ↓
  Templates           Auto-select            UV Env         Coverage
     ↓                    ↓                      ↓              ↓
  Modules            Context-aware          Verify         Summary
```

## 🚀 Quick Start Examples

```bash
# Create a new API spec with AI assistance
/spec create user-auth authentication

# Get AI agent recommendations for current work
/ai-agent recommend

# Run tests using UV environment
/test run

# Sync all repositories
/git sync

# Execute pending tasks
/task execute --all

# Generate engineering data context
/data context ./engineering-files

# Verify AI work in specs
/verify
```

## 🔄 Command Aliases

Some commands have shorter aliases for convenience:
- `/g` → `/git`
- `/s` → `/spec`
- `/t` → `/test`
- `/p` → `/project`

## 📦 Resources & Templates

### AI Template Sources
- **Claude Code Templates**: https://github.com/davila7/claude-code-templates
- **AITmpl**: https://www.aitmpl.com/
- **Local Catalog**: `.agent-os/resources/aitmpl_agents_catalog.yaml`

### Agent Storage
- All agents stored in `agents/` folder in each repository
- Organized by category (security, performance, testing, etc.)
- Custom agents can be added per repository

## 🎨 Command Features

### UV Environment Support
All commands now:
- Detect existing UV environments automatically
- Use UV Python interpreter when available
- Enhance environments with spec dependencies
- Prevent duplicate virtual environment creation

### Module Organization
- Specs organized by modules
- Module-aware testing
- Module-specific documentation
- Cross-module dependencies tracked

### AI Integration
- 48+ specialized agents available
- Automatic agent selection based on context
- Agent chaining for complex tasks
- Template recommendations

## 📝 Notes

1. **All commands are UV-aware** - They automatically use UV environments when available
2. **AI agents integrate seamlessly** - Agents are recommended based on your current task
3. **Commands are modular** - Each command can work independently or chain with others
4. **Cross-repository support** - Commands work across all 25+ repositories
5. **Intelligent defaults** - Commands make smart decisions based on context

---

*Last Updated: 2024-01-13*
*Total Commands: 7 primary + 2 utility = 9 main commands (simplified from 21+)*