# Universal Agents (Tier 1)

> **Scope:** Used across ALL repositories in workspace-hub
> **Ownership:** workspace-hub team
> **Location:** `workspace-hub/.claude/agents/universal/`

## Overview

This directory contains **universal agents** that provide general-purpose capabilities used across all 26+ repositories in workspace-hub. These agents are the foundation of the agent ecosystem and are referenced by all consumer repositories via symlinks.

## Directory Structure

```
universal/
├── core/               # Core development agents
├── sparc/              # SPARC methodology agents
├── visualization/      # Visualization and reporting agents
├── quality/            # Quality assurance and security agents
├── github/             # GitHub integration agents
├── swarm/              # Swarm coordination agents
├── consensus/          # Consensus and distributed agents
├── performance/        # Performance optimization agents
└── specialized/        # Specialized development agents
```

## Agent Categories

### Core Development (`core/`)

Basic development agents used in every project:
- **coder** - General-purpose code generation
- **reviewer** - Code review and quality checks
- **tester** - Test generation and validation
- **planner** - Project planning and task breakdown
- **researcher** - Requirements analysis and research

**Usage:** Every repository should reference these agents.

### SPARC Methodology (`sparc/`)

Agents for the SPARC development workflow:
- **specification** - Requirements specification
- **pseudocode** - Algorithm design
- **architecture** - System architecture design
- **refinement** - TDD implementation and continuous refactoring

**Usage:** Use for structured feature development following SPARC phases.

### Visualization (`visualization/`)

Interactive reporting and visualization agents:
- **plotly-visualization-agent** - General interactive plots
- **bokeh-dashboard-agent** - Complex dashboards
- **altair-analysis-agent** - Statistical visualization
- **d3js-custom-viz-agent** - Custom web visualizations

**Usage:** Required for HTML reporting standard (see docs/HTML_REPORTING_STANDARDS.md).

### Quality (`quality/`)

Quality assurance and security:
- **code-review-swarm** - Multi-agent code review
- **security-manager** - Security audits and validation

**Usage:** Use in gate-pass reviews and pre-deployment checks.

### GitHub Integration (`github/`)

GitHub operations and workflows:
- **pr-manager** - Pull request management
- **issue-tracker** - Issue tracking and triage
- **release-manager** - Release automation
- **workflow-automation** - CI/CD workflows

**Usage:** Automate GitHub operations.

### Swarm Coordination (`swarm/`)

Multi-agent coordination:
- **hierarchical-coordinator** - Hierarchical coordination
- **mesh-coordinator** - Mesh network coordination
- **adaptive-coordinator** - Adaptive coordination
- **collective-intelligence-coordinator** - Collective intelligence

**Usage:** Complex multi-agent tasks.

### Consensus (`consensus/`)

Distributed consensus and synchronization:
- **byzantine-coordinator** - Byzantine fault tolerance
- **raft-manager** - Raft consensus
- **consensus-builder** - General consensus building
- **crdt-synchronizer** - CRDT synchronization

**Usage:** Distributed system development.

### Performance (`performance/`)

Performance optimization:
- **perf-analyzer** - Performance analysis
- **performance-benchmarker** - Benchmarking
- **task-orchestrator** - Task orchestration

**Usage:** Performance optimization projects.

### Specialized (`specialized/`)

Specialized development agents:
- **backend-dev** - Backend development
- **mobile-dev** - Mobile development
- **ml-developer** - Machine learning
- **cicd-engineer** - CI/CD engineering
- **api-docs** - API documentation
- **system-architect** - System architecture

**Usage:** Domain-specific development tasks.

## How to Reference These Agents

### From Consumer Repositories

**Option 1: Via .agent-references.yaml (Declarative)**

```yaml
# your-repo/.agent-references.yaml
universal_agents:
  source: "@workspace-hub/.claude/agents/universal/"
  agents:
    - coder
    - reviewer
    - tester
    - plotly-visualization-agent
```

Then run:
```bash
/mnt/github/workspace-hub/modules/automation/setup_agent_links.sh /path/to/your-repo
```

**Option 2: Via Orchestrator (Automatic)**

```bash
/mnt/github/workspace-hub/modules/automation/agent_orchestrator.sh \
  --agent coder \
  --description "Create user authentication API"
```

**Option 3: Via Symlink (Direct)**

```bash
# After running setup_agent_links.sh
claude-flow agent run coder --description "Create API endpoint"
```

## How to Add New Universal Agents

### Step 1: Determine if Agent is Universal

Use the decision matrix from `docs/AGENT_ORGANIZATION_GUIDE.md`:

| Question | Yes → | No → |
|----------|-------|------|
| Used by all/most repos? | Universal (here) | Continue |
| Domain-specific? | Domain hub | Continue |
| Only one repo needs it? | Local agent | Reconsider |

### Step 2: Create Agent File

```bash
# Choose appropriate category
cd .claude/agents/universal/<category>/

# Create agent YAML file
vim new-agent.yaml
```

**Template:**

```yaml
name: new-agent
version: "1.0.0"
type: specialist  # specialist | workflow | orchestrator
domain: general-purpose
description: "What this agent does"

capabilities:
  capability_1: 95
  capability_2: 90

context: |
  Detailed context about what this agent does and how to use it.

  Key features:
  - Feature 1
  - Feature 2

examples:
  - description: "Example 1"
    command: "claude-flow agent run new-agent --config example1.yaml"

  - description: "Example 2"
    command: "claude-flow agent run new-agent --description 'task'"

dependencies:
  - dependency1
  - dependency2

best_practices:
  - Practice 1
  - Practice 2
```

### Step 3: Update Central Registry

```bash
vim ../.claude/agents/registry.yaml
# Add new-agent under appropriate category
```

### Step 4: Sync to Consumer Repos

```bash
./modules/automation/sync_agent_configs.sh push
```

### Step 5: Test

```bash
# Test from workspace-hub
claude-flow agent run new-agent --test

# Test from consumer repo
cd /path/to/consumer-repo
ls -la .claude/agents/universal/<category>/new-agent.yaml
claude-flow agent run new-agent --description "test task"
```

## Agent Development Guidelines

### Naming Conventions

- **Use descriptive names** - `code-reviewer` not `cr1`
- **Use kebab-case** - `api-generator` not `API_Generator`
- **Avoid platform names** - `visualizer` not `plotly-agent`
- **Avoid temporal terms** - `parser` not `new-parser`

### Version Control

- **Use semantic versioning** - `1.0.0`, `1.1.0`, `2.0.0`
- **Update version on changes** - Increment appropriately
- **Document changes** - In agent YAML or CHANGELOG.md

### Documentation

Every agent MUST have:
- **Name and version**
- **Clear description**
- **Capability scores**
- **Usage examples**
- **Dependencies**
- **Best practices**

### Quality Standards

- **Test before committing** - Ensure agent works
- **Update registry** - Keep central registry current
- **Document well** - Clear context and examples
- **Follow standards** - See `.claude/agents/BEST_PRACTICES.md`

## Maintenance

### Ownership

- **Owner:** workspace-hub team
- **Maintainers:** Listed in `registry.yaml`
- **Contact:** Via workspace-hub GitHub issues

### Updates

- **Frequency:** As needed
- **Breaking changes:** Major version bump
- **Deprecation:** 90-day notice minimum

### Support

- **Issues:** GitHub issues in workspace-hub
- **Questions:** Team chat or engineering@example.com
- **Documentation:** See `docs/AGENT_ORGANIZATION_GUIDE.md`

## Related Documentation

- **Agent Organization Guide:** `docs/AGENT_ORGANIZATION_GUIDE.md`
- **Agent Best Practices:** `.claude/agents/BEST_PRACTICES.md`
- **Agent Registry:** `.claude/agents/registry.yaml`
- **Orchestration System:** `docs/modules/automation/AI_AGENT_ORCHESTRATION.md`

---

**Last Updated:** 2025-10-29
**Version:** 1.0.0
**Maintained by:** workspace-hub team
