# Create-Module-Agent Usage Guide

## Current Folder Structure

```
repository/
├── .agent-os/                    # Agent OS configuration directory
│   ├── instructions/             # Workflow instructions
│   │   ├── create-spec.md       # Traditional spec creation
│   │   └── enhanced-create-spec.md  # Enhanced spec creation
│   ├── standards/                # Code standards
│   ├── product/                  # Product documentation
│   ├── specs/                    # Feature specifications
│   ├── modules/                  # Module configurations
│   ├── commands/                 # Additional commands (merged)
│   └── agent_learning/           # Agent learning data
│
├── agent_os/                     # Python module (SEPARATE from .agent-os)
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── create_module_agent.py  # Main module agent logic
│       ├── ai_agent.py          # AI agent utilities
│       └── agent.py             # Base agent functionality
│
├── agents/                       # Agent configurations
│   └── various agent configs
│
├── create-module-agent.py        # Entry point script
├── create-spec-enhanced.py       # Enhanced spec entry point
└── create-spec.py               # Traditional spec entry point
```

## How to Use Create-Module-Agent

### 1. Basic Module Agent Creation

```bash
# Create a new module agent
python3 create-module-agent.py authentication --mode create

# Create with specific module path
python3 create-module-agent.py user-management \
  --mode create \
  --module-path ./specs/modules/user-management
```

### 2. Processing Documentation with Phased Approach

The phased approach is MANDATORY for large documentation sets:

```bash
# Process multiple documents with phased approach
python3 create-module-agent.py api-module \
  --mode create \
  --process-docs "./docs/*.md" \
  --phased
```

### 3. Agent Specialization Levels

Create agents with different specialization levels:

```bash
# General purpose agent
python3 create-module-agent.py general-agent --type general-purpose

# Module-specific agent
python3 create-module-agent.py auth-module \
  --type module-specific \
  --module-path ./specs/modules/authentication

# Domain expert agent
python3 create-module-agent.py security-expert \
  --type domain-expert \
  --process-docs "./security-docs/*.md" \
  --phased
```

### 4. Updating and Refreshing Agents

```bash
# Update existing agent with new documents
python3 create-module-agent.py my-module \
  --mode update \
  --add-doc "./new-requirements.md" \
  --category internal

# Refresh agent knowledge
python3 create-module-agent.py my-module --mode refresh
```

### 5. Documentation Management

```bash
# Add documentation to agent
python3 create-module-agent.py my-module \
  --mode update \
  --add-doc "./api-spec.md" \
  --category internal \
  --title "API Specification v2.0"

# List all documentation
python3 create-module-agent.py my-module --list-docs

# List by category
python3 create-module-agent.py my-module --list-docs internal
```

### 6. Multi-Repository Support

```bash
# Create agent for multiple repositories
python3 create-module-agent.py shared-module \
  --repos "aceengineer-admin,aceengineer-website,assetutilities"
```

### 7. Health Check

```bash
# Check agent health status
python3 create-module-agent.py my-module --health-check
```

## Phased Document Processing

The system uses 6 phases for processing large documentation:

1. **DISCOVERY** - Document discovery and classification
2. **QUALITY** - Quality assessment and filtering  
3. **EXTRACTION** - Knowledge extraction
4. **SYNTHESIS** - Knowledge synthesis
5. **VALIDATION** - Validation and verification
6. **INTEGRATION** - Integration into agent

## Documentation Categories

- `internal` - Internal project documentation
- `external` - External references and guides
- `web` - Web resources and URLs
- `repository` - Repository-specific docs
- `optimized` - Processed/optimized documentation
- `context` - Context engineering docs
- `memory` - Long-term memory storage
- `module` - Module-specific documentation
- `submodule` - Submodule-specific documentation

## Example Workflows

### Creating a New Feature Module

```bash
# 1. Create the module agent
python3 create-module-agent.py payment-processing \
  --mode create \
  --module-path ./specs/modules/payments

# 2. Add relevant documentation
python3 create-module-agent.py payment-processing \
  --mode update \
  --add-doc "./docs/stripe-api.md" \
  --category external \
  --title "Stripe API Documentation"

# 3. Process all payment-related docs
python3 create-module-agent.py payment-processing \
  --mode update \
  --process-docs "./docs/payments/*.md" \
  --phased
```

### Creating a Cross-Module Collaboration Agent

```bash
python3 create-module-agent.py auth-payment-bridge \
  --type cross-module \
  --repos "aceengineer-admin,assetutilities" \
  --process-docs "./specs/modules/*/auth*.md,./specs/modules/*/payment*.md" \
  --phased
```

### Creating a Domain Expert Agent

```bash
python3 create-module-agent.py security-expert \
  --type domain-expert \
  --process-docs "./security/*.md,./compliance/*.md" \
  --phased \
  --context-cache true
```

## Integration with Enhanced Specs

The create-module-agent works seamlessly with enhanced specs:

```bash
# Create enhanced spec with module
/create-spec payment-gateway payments enhanced

# Then create corresponding module agent
python3 create-module-agent.py payments \
  --module-path ./specs/modules/payments \
  --process-docs "./specs/modules/payments/**/*.md" \
  --phased
```

## Best Practices

1. **Always use `--phased` for large documentation sets** (>10 files)
2. **Organize modules in `.agent-os/specs/modules/` directory**
3. **Use appropriate documentation categories** for better organization
4. **Create module-specific agents** for complex features
5. **Use cross-module agents** for integration features
6. **Regularly refresh agents** with new documentation
7. **Check agent health** before major deployments

## Troubleshooting

### Agent not finding documents
```bash
# Check document discovery
python3 create-module-agent.py my-module --list-docs
```

### Module path issues
```bash
# Ensure module path exists
ls -la .agent-os/specs/modules/
```

### Processing stuck
```bash
# Check phase status
cat .agent-os/modules/my-module/processing/phase_status.yaml
```

## Output Structure

When you create a module agent, it generates:

```
.agent-os/
└── modules/
    └── [module-name]/
        ├── agent_config.yaml      # Agent configuration
        ├── knowledge_base.json     # Processed knowledge
        ├── processing/             # Processing data
        │   ├── phases/            # Phase outputs
        │   ├── metrics/           # Processing metrics
        │   └── phase_status.yaml  # Current status
        └── documentation/          # Organized docs
            ├── internal/
            ├── external/
            └── optimized/
```

## Next Steps

1. Start with creating a general-purpose agent for your module
2. Add relevant documentation progressively
3. Use phased processing for large document sets
4. Create specialized agents as modules grow
5. Set up cross-module agents for integrations

---

*This guide covers the enhanced Create-Module-Agent v3.0 with mandatory phased processing and modular agent management principles.*