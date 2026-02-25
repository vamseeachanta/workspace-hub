# Factory AI Enhanced Configuration Guide

> **Workspace Hub** - Advanced Droids Configuration
>
> Factory.ai Version: v0.18.0
> Configuration Version: 2.0.0
> Last Updated: 2025-10-04

## Overview

This guide covers the **enhanced Factory AI configuration** implemented across workspace-hub, including droids.yml configurations, repository-specific behaviors, and integration with the AI orchestration system.

## What's New in Enhanced Configuration

### 1. Droids.yml Configuration Files

All 26 repositories now have `droids.yml` configuration files that define:
- Repository-specific droid behaviors
- Custom system prompts and context
- Model preferences and parameters
- Code style and testing preferences
- Integration with workspace-hub systems

### 2. Repository Type Specialization

Repositories are categorized by type with specialized configurations:

- **python_analysis** (12 repos): Data analysis, visualization, reporting
- **engineering** (7 repos): Engineering calculations, simulations
- **web_app** (7 repos): Web applications, frontend development

### 3. Workspace-Level Coordination

Central `.drcode/droids.yml` in workspace-hub root provides:
- Shared defaults across all repositories
- Integration with Claude Flow, Spec-Kit, Agent OS
- AI orchestration system integration
- Interactive reporting standards

## Configuration Structure

```
workspace-hub/
├── .drcode/
│   ├── config.json                    # Basic Factory config
│   ├── config-enhanced.json           # Enhanced config with AI features
│   ├── droids.yml                     # Workspace-level droid config
│   └── droids-repo-template.yml       # Template for new repos
│
└── [repositories]/
    └── .drcode/
        ├── config.json                # Basic repo config
        └── droids.yml                 # Repo-specific droid config
```

## Droids.yml Configuration Reference

### Workspace-Level Configuration

**Location:** `/mnt/github/workspace-hub/.drcode/droids.yml`

**Key Sections:**

#### 1. Defaults

```yaml
defaults:
  model: claude-sonnet-3-5
  temperature: 0.7
  max_tokens: 4096

  system_prompt: |
    You are an AI development assistant working in the workspace-hub...
    [Comprehensive context about workspace structure, standards, methodologies]

  file_preferences:
    protected:
      - .git/**
      - .drcode/**
      - .agent-os/product/decisions.md

    auto_format:
      - "*.py"
      - "*.js"
      - "*.ts"
```

#### 2. Specialized Droids

Pre-configured droids for specific tasks:

- **refactor** (temp: 0.3): Code quality improvements
- **feature** (temp: 0.7): New feature development with SPARC
- **bugfix** (temp: 0.4): Systematic bug fixing
- **docs** (temp: 0.6): Documentation generation
- **testing** (temp: 0.5): Test suite creation
- **migration** (temp: 0.3, model: claude-sonnet-4-0): Complex migrations

#### 3. Repository Types

```yaml
repository_types:
  python_analysis:
    file_extensions: [".py", ".ipynb"]
    primary_frameworks: [pandas, numpy, plotly]
    context: |
      - Use UV for environment management
      - Interactive plots with Plotly/Bokeh/Altair
      - CSV data import with relative paths
```

#### 4. Integrations

```yaml
integrations:
  claude_flow:
    enabled: true
    mcp_tools: [swarm_init, agent_spawn, task_orchestrate]

  ai_orchestrator:
    enabled: true
    registry: modules/config/ai-agents-registry.json
    gate_pass: modules/automation/gate_pass_review.sh
```

#### 5. Reporting Standards

```yaml
reporting:
  interactive_plots_required: true
  allowed_libraries: [plotly, bokeh, altair, d3.js]
  forbidden_libraries:
    - matplotlib (static)
    - seaborn (static)
```

#### 6. Security

```yaml
security:
  secret_patterns:
    - "password\\s*=\\s*['\"].*['\"]"
    - "api_key\\s*=\\s*['\"].*['\"]"

  safe_mode: true
  require_approval_for:
    - database_migrations
    - file_deletions
    - system_commands
```

### Repository-Level Configuration

**Location:** `<repo>/.drcode/droids.yml`

**Structure:**

```yaml
repository:
  name: worldenergydata
  type: python_analysis
  workspace: workspace-hub
  parent_config: ../../.drcode/droids.yml

inherit:
  - workspace_defaults
  - repository_type_config

overrides:
  additional_context: |
    Repository-specific context:
    - Project: World Energy Data Analysis
    - Focus: Energy data visualization and reporting
    - Key Technologies: Python, Pandas, Plotly, UV
```

## Repository Type Configurations

### Python Analysis Repositories (12)

**Repositories:**
- worldenergydata
- digitalmodel
- pyproject-starter
- energy
- assetutilities
- achantas-data
- doris
- ai-native-traditional-eng
- investments
- sabithaandkrishnaestates
- seanation

**Specialized Configuration:**
- UV environment management
- Interactive plotting (Plotly primary)
- CSV data handling with relative paths
- HTML report generation
- Data directories: /data/raw/, /data/processed/, /data/results/

**Example Usage:**
```bash
cd worldenergydata
droid exec "Create interactive dashboard from energy_production.csv"
```

### Engineering Repositories (7)

**Repositories:**
- aceengineercode
- OGManufacturing
- rock-oil-field
- frontierdeepwater
- saipem
- acma-projects
- sd-work

**Specialized Configuration:**
- Numerical accuracy emphasis
- Engineering calculation documentation
- Unit tests for critical calculations
- Formula and assumption tracking

**Example Usage:**
```bash
cd aceengineercode
droid exec "Implement stress analysis calculation with ASME standards"
```

### Web Application Repositories (7)

**Repositories:**
- aceengineer-admin
- aceengineer-website
- assethold
- achantas-media
- client_projects
- hobbies
- teamresumes

**Specialized Configuration:**
- Modern JavaScript/TypeScript patterns
- Component-based architecture
- Responsive design
- Accessibility (a11y) compliance

**Example Usage:**
```bash
cd aceengineer-admin
droid exec "Add authentication with JWT and refresh tokens"
```

## Using Specialized Droids

### Invoke Specific Droid by Name

```bash
# Use refactoring droid
droid --droid refactor exec "improve code quality in src/"

# Use feature droid
droid --droid feature exec "add user profile page"

# Use testing droid
droid --droid testing exec "create comprehensive test suite"

# Use documentation droid
droid --droid docs exec "generate API documentation"
```

### Droid Selection Guide

| Task Type | Recommended Droid | Temperature | Notes |
|-----------|------------------|-------------|-------|
| Refactoring | refactor | 0.3 | Consistent, conservative changes |
| New Features | feature | 0.7 | Creative, follows SPARC methodology |
| Bug Fixes | bugfix | 0.4 | Focused, systematic approach |
| Testing | testing | 0.5 | Comprehensive coverage |
| Documentation | docs | 0.6 | Clear, user-friendly |
| Migrations | migration | 0.3 | Uses claude-sonnet-4-0 for complexity |

## Integration with AI Orchestration

### Gate-Pass Review Integration

Droids automatically integrate with gate-pass reviews:

```bash
# Feature implementation with gate-pass review
cd your-repo
droid exec "implement user authentication feature"

# Trigger gate-pass review
../../modules/automation/gate_pass_review.sh implementation . --auto
```

### AI Agent Selection

Droids can leverage the AI agent orchestrator:

```bash
# Droid can call orchestrator for specialized tasks
# Example: HTML report generation routes to plotly-visualization-agent

cd worldenergydata
droid exec "Create interactive energy trends report from data/processed/energy_data.csv"

# Internally routes to:
# - plotly-visualization-agent for plotting
# - data-quality-agent for validation
# - gate-pass review for quality checks
```

### Multi-Agent Workflows

```bash
# Complex workflow leveraging multiple agents
cd digitalmodel

droid exec "Implement FDAS analysis module with:
1. Data validation from CSV
2. Statistical analysis
3. Interactive Plotly dashboard
4. Comprehensive tests
5. API documentation"

# Droids coordinate with:
# - data-validation-agent
# - statistical-analysis-agent
# - plotly-visualization-agent
# - pytest-specialist-agent
# - api-documentation-agent
```

## Enhanced Configuration Benefits

### 1. Context-Aware Development

Droids understand:
- Repository type and purpose
- Project-specific standards
- Integration requirements
- Testing expectations

### 2. Consistent Quality

Enforced through configuration:
- Code style standards
- Test coverage requirements
- Documentation standards
- Security patterns

### 3. Specialized Behaviors

Different droids for different needs:
- Lower temperature for refactoring (0.3)
- Higher temperature for feature development (0.7)
- Specialized prompts per task type

### 4. Integration Excellence

Seamless integration with:
- Claude Flow MCP
- Spec-Kit specifications
- Agent OS workflows
- AI orchestration system
- Gate-pass review system

### 5. Safety and Security

Built-in protections:
- Protected file patterns
- Secret detection
- Safe mode for dangerous operations
- Approval requirements for critical changes

## Best Practices

### 1. Use Appropriate Droids

```bash
# ✅ Good: Use refactor droid for code quality
droid --droid refactor exec "improve function naming"

# ❌ Bad: Use feature droid for simple refactoring
droid --droid feature exec "rename variables"
```

### 2. Leverage Repository Types

```bash
# ✅ Good: Let droid use repository type configuration
cd worldenergydata  # python_analysis type
droid exec "create report"  # Automatically uses Plotly, CSV paths

# ❌ Bad: Override repository type in every command
droid exec "use Plotly and CSV relative paths to create report"
```

### 3. Trust the Integration

```bash
# ✅ Good: Simple commands, let configuration handle details
droid exec "add authentication"

# ❌ Bad: Over-specify when config already knows
droid exec "add authentication using JWT with tests following SPARC methodology with 80% coverage"
```

### 4. Review Before Committing

```bash
# Always review droid changes
git diff

# Use gate-pass reviews
../../modules/automation/gate_pass_review.sh implementation .
```

## Advanced Usage

### Custom Droid for Specific Repository

Add to `<repo>/.drcode/droids.yml`:

```yaml
local_droids:
  custom_analyzer:
    enabled: true
    model: claude-sonnet-3-5
    temperature: 0.6
    context: |
      Specialized droid for this repository:
      - Focus on performance optimization
      - Use repository-specific patterns
      - Integrate with custom tooling
```

Usage:
```bash
droid --droid custom_analyzer exec "optimize database queries"
```

### Override Workspace Defaults

In repository's `droids.yml`:

```yaml
overrides:
  code_style:
    python:
      line_length: 120  # Override workspace default of 100

  testing:
    coverage_threshold: 90  # Stricter than workspace default
```

### Environment-Specific Configuration

```bash
# Development environment
export DROID_ENV=development
droid exec "configure dev database"

# Production environment
export DROID_ENV=production
droid exec "configure prod database with SSL"
```

## Troubleshooting

### Droid Not Using Configuration

```bash
# Verify droids.yml exists
ls -la .drcode/droids.yml

# Check configuration syntax
cat .drcode/droids.yml | head -20

# Use explicit droid
droid --droid feature exec "add feature"
```

### Configuration Not Inheriting

```bash
# Verify parent_config path is correct
grep parent_config .drcode/droids.yml

# Should point to: ../../.drcode/droids.yml
```

### Wrong Repository Type

Edit `<repo>/.drcode/droids.yml`:

```yaml
repository:
  type: python_analysis  # Change to correct type
```

## Migration from Basic Configuration

Existing repositories with only `config.json` automatically inherit workspace-level droids.yml. No migration needed.

To add repository-specific configuration:

```bash
cd your-repo
cp ../../.drcode/droids-repo-template.yml .drcode/droids.yml

# Edit .drcode/droids.yml to customize
```

## Configuration Files Reference

### Workspace-Level Files

- `.drcode/config.json` - Basic Factory config
- `.drcode/config-enhanced.json` - Enhanced config with AI features
- `.drcode/droids.yml` - Workspace-level droid configuration (5.2 KB)
- `.drcode/droids-repo-template.yml` - Template for new repositories

### Repository-Level Files

- `<repo>/.drcode/config.json` - Basic repo config
- `<repo>/.drcode/droids.yml` - Repo-specific droid configuration (~1.5 KB)

### Supporting Files

- `modules/config/ai-agents-registry.json` - 14 AI agents with capabilities
- `modules/automation/gate_pass_review.sh` - Gate-pass review system
- `modules/automation/agent_orchestrator.sh` - AI agent selection
- `modules/automation/update_ai_agents_daily.sh` - Daily agent updates

## Next Steps

1. **Test Enhanced Configuration:**
   ```bash
   cd worldenergydata
   droid --droid feature exec "test configuration"
   ```

2. **Customize Repository Configs:**
   Edit `<repo>/.drcode/droids.yml` for specific needs

3. **Use Specialized Droids:**
   Experiment with different droids for different tasks

4. **Integrate with Workflows:**
   Combine droids with gate-pass reviews and AI orchestration

5. **Monitor and Refine:**
   Track droid performance and adjust configurations

## Resources

- **Factory AI Docs:** https://docs.factory.ai
- **Workspace Hub Docs:** `/docs/FACTORY_AI_GUIDE.md`
- **AI Orchestration:** `/docs/AI_AGENT_ORCHESTRATION.md`
- **Reporting Standards:** `/docs/HTML_REPORTING_STANDARDS.md`

---

**Enhanced Factory AI configuration is now active across all 26 repositories!**

Use specialized droids, leverage repository types, and integrate with workspace-hub's AI orchestration system for maximum productivity.
