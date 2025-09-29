# Module Agent Folder Structure

## Complete Directory Tree

```
repository_root/
│
├── 📁 .agent-os/                       # Agent OS Configuration Directory
│   ├── 📁 instructions/                # Workflow instructions
│   │   ├── 📄 create-spec.md          # Traditional spec creation
│   │   ├── 📄 enhanced-create-spec.md # Enhanced spec with modules
│   │   ├── 📄 execute-tasks.md        # Task execution workflow
│   │   ├── 📄 plan-product.md         # Product planning
│   │   └── 📄 analyze-product.md      # Product analysis
│   │
│   ├── 📁 standards/                   # Code standards & best practices
│   │   ├── 📄 code-style.md
│   │   ├── 📄 best-practices.md
│   │   └── 📄 tech-stack.md
│   │
│   ├── 📁 product/                     # Product documentation
│   │   ├── 📄 mission.md
│   │   ├── 📄 roadmap.md
│   │   ├── 📄 tech-stack.md
│   │   └── 📄 decisions.md
│   │
│   ├── 📁 specs/                       # Feature specifications
│   │   ├── 📁 modules/                 # Module-based specs
│   │   │   └── 📁 [module-name]/       # Individual module
│   │   │       ├── 📁 [YYYY-MM-DD-spec-name]/
│   │   │       │   ├── 📄 spec.md
│   │   │       │   ├── 📄 tasks.md
│   │   │       │   └── 📁 sub-specs/
│   │   │       │       ├── 📄 technical-spec.md
│   │   │       │       ├── 📄 api-spec.md
│   │   │       │       └── 📄 database-schema.md
│   │   │       └── 📄 module-index.md
│   │   │
│   │   └── 📁 [YYYY-MM-DD-spec-name]/  # Traditional specs
│   │       ├── 📄 spec.md
│   │       ├── 📄 tasks.md
│   │       └── 📁 sub-specs/
│   │
│   ├── 📁 modules/                     # Module agent configurations
│   │   ├── 📁 [module-name]/           # Created by create-module-agent
│   │   │   ├── 📄 agent_config.yaml    # Agent configuration
│   │   │   ├── 📄 knowledge_base.json  # Processed knowledge
│   │   │   ├── 📁 processing/          # Document processing
│   │   │   │   ├── 📁 phases/          # Processing phases
│   │   │   │   │   ├── 📄 1_discovery.json
│   │   │   │   │   ├── 📄 2_quality.json
│   │   │   │   │   ├── 📄 3_extraction.json
│   │   │   │   │   ├── 📄 4_synthesis.json
│   │   │   │   │   ├── 📄 5_validation.json
│   │   │   │   │   └── 📄 6_integration.json
│   │   │   │   ├── 📁 metrics/         # Processing metrics
│   │   │   │   └── 📄 phase_status.yaml
│   │   │   └── 📁 documentation/       # Organized docs
│   │   │       ├── 📁 internal/
│   │   │       ├── 📁 external/
│   │   │       ├── 📁 web/
│   │   │       ├── 📁 repository/
│   │   │       ├── 📁 optimized/
│   │   │       ├── 📁 context/
│   │   │       ├── 📁 memory/
│   │   │       └── 📁 module/
│   │   │
│   │   ├── 📄 agent_assignments.py     # Agent assignment logic
│   │   ├── 📄 agent_learning.py        # Learning capabilities
│   │   ├── 📄 progress_tracker.py      # Progress tracking
│   │   └── 📄 prompt_enhancement.py    # Prompt optimization
│   │
│   ├── 📁 agent_learning/              # Agent learning data
│   ├── 📁 cli/                         # CLI tools
│   ├── 📁 commands/                    # Additional commands
│   ├── 📁 integration/                 # Integration configs
│   ├── 📁 resources/                   # Shared resources
│   ├── 📁 sub-agents/                  # Sub-agent definitions
│   └── 📄 prompt_config.yaml           # Prompt configuration
│
├── 📁 agent_os/                        # Python Module (SEPARATE)
│   ├── 📄 __init__.py
│   └── 📁 commands/
│       ├── 📄 __init__.py
│       ├── 📄 create_module_agent.py   # Main module agent logic
│       ├── 📄 ai_agent.py              # AI agent utilities
│       └── 📄 agent.py                 # Base agent functionality
│
├── 📁 agents/                          # Agent configurations
│   └── 📄 [various agent configs]
│
├── 📄 create-module-agent.py           # Entry point for module agent
├── 📄 create-spec-enhanced.py          # Entry point for enhanced specs
├── 📄 create-spec.py                   # Entry point for traditional specs
└── 📄 CLAUDE.md                        # Project-specific instructions
```

## Key Directories Explained

### 1. `.agent-os/` - Configuration Directory
This is the main Agent OS configuration directory containing:
- **instructions/** - Workflow rules and procedures
- **standards/** - Coding standards and best practices
- **product/** - Product-level documentation
- **specs/** - Feature specifications (both traditional and module-based)
- **modules/** - Module agent data and configurations

### 2. `agent_os/` - Python Module
This is a SEPARATE directory (not inside .agent-os) containing:
- Python implementation of the module agent system
- Command implementations
- Must remain separate for Python import to work

### 3. Module Agent Data Structure
When you create a module agent, it generates:

```
.agent-os/modules/[module-name]/
├── agent_config.yaml         # Agent configuration
│   ├── agent_id
│   ├── specialization_level
│   ├── module_path
│   └── repositories
│
├── knowledge_base.json       # Processed knowledge
│   ├── concepts
│   ├── relationships
│   └── metadata
│
├── processing/               # Document processing data
│   ├── phases/              # 6-phase processing outputs
│   ├── metrics/             # Processing metrics
│   └── phase_status.yaml   # Current processing status
│
└── documentation/           # Organized documentation
    ├── internal/           # Project docs
    ├── external/           # External references
    ├── optimized/          # Processed docs
    └── [other categories]
```

## Module-Based Spec Organization

When using enhanced specs with modules:

```
.agent-os/specs/modules/
└── authentication/                    # Module name
    ├── 2025-08-22-login-flow/        # Spec 1
    │   ├── spec.md
    │   ├── tasks.md
    │   └── sub-specs/
    ├── 2025-08-23-password-reset/    # Spec 2
    │   ├── spec.md
    │   ├── tasks.md
    │   └── sub-specs/
    └── module-index.md                # Module documentation
```

## Workflow Integration

### Creating a Module with Agent

1. **Create Enhanced Spec**
   ```bash
   /create-spec feature-name module-name enhanced
   ```
   Creates: `.agent-os/specs/modules/module-name/YYYY-MM-DD-feature-name/`

2. **Create Module Agent**
   ```bash
   python3 create-module-agent.py module-name \
     --module-path ./specs/modules/module-name
   ```
   Creates: `.agent-os/modules/module-name/`

3. **Process Documentation**
   ```bash
   python3 create-module-agent.py module-name \
     --mode update \
     --process-docs "./specs/modules/module-name/**/*.md" \
     --phased
   ```
   Updates: `.agent-os/modules/module-name/knowledge_base.json`

## Important Notes

1. **`.agent-os/` vs `agent_os/`**: These are TWO SEPARATE directories
   - `.agent-os/` = Configuration and data
   - `agent_os/` = Python code

2. **Module Organization**: Modules group related specs together

3. **Phased Processing**: Large document sets are processed in 6 phases

4. **Agent Specialization**: Agents can be general, module-specific, or domain experts

5. **Cross-Repository**: Agents can work across multiple repositories

---

*This structure supports the enhanced Agent OS workflow with module-based organization and intelligent agent management.*