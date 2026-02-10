# Workspace Hub - Master Agent Registry

> **Central registry for all 78+ agents across 26 repositories**
>
> **Version:** 1.0.0
> **Last Updated:** 2025-10-05

## Overview

This directory contains the **master agent registry** for workspace-hub, centralizing all agent configurations, best practices, and orchestration logic across 26+ repositories.

## Quick Start

```bash
# Navigate to any repository
cd <workspace-hub>/<repo-name>

# Use agent orchestrator for intelligent agent selection
./modules/automation/agent_orchestrator.sh code-generation "Create REST API"

# Or use Factory AI with centralized config
droid  # Automatically loads .claude/CLAUDE.md with agent references
```

## Directory Structure

```
.claude/agents/
├── registry.yaml                    # Master agent registry (THIS IS THE SOURCE OF TRUTH)
├── BEST_PRACTICES.md               # Consolidated best practices
├── README.md                       # This file
│
├── domain/                         # Domain-specific agents
│   ├── engineering/
│   │   ├── aqwa.yaml              # ANSYS AQWA hydrodynamics
│   │   ├── freecad.json           # FreeCAD automation
│   │   ├── gmsh.json              # Mesh generation
│   │   ├── orcaflex.yaml          # OrcaFlex simulation
│   │   └── orcawave.json          # Wave analysis
│   ├── energy/
│   │   ├── drilling-expert.yaml   # Drilling operations
│   │   ├── oil-and-gas-expert.yaml # O&G industry
│   │   └── financial-analysis.yaml # Energy finance
│   └── finance/
│       └── finance-analytics.yaml  # Financial analysis
│
├── general/                        # General-purpose agents
│   ├── factory-ai.yaml            # Factory AI platform
│   ├── spec-kit.yaml              # Spec-Kit platform
│   └── agent-os.yaml              # Agent OS platform
│
├── automation/                     # Workflow automation
│   ├── workflow-automation.yaml   # Enhanced specs & workflows
│   ├── file-management.yaml       # File operations
│   ├── visualization.yaml         # Chart generation
│   ├── auth-system.yaml          # Authentication
│   └── git-workflow.yaml         # Git operations
│
├── visualization/                  # Visualization specialists
│   ├── plotly.yaml               # Plotly interactive plots
│   ├── bokeh.yaml                # Bokeh dashboards
│   ├── altair.yaml               # Altair statistical viz
│   └── d3js.yaml                 # D3.js custom viz
│
└── templates/                      # Agent templates
    ├── domain-expert.yaml         # Template for domain experts
    ├── engineering-tool.json      # Template for engineering tools
    └── workflow-automation.yaml   # Template for automation
```

## Agent Inventory

### Total Agents: 78+

| Category | Count | Description |
|----------|-------|-------------|
| **Domain-Specific** | 11 | Engineering, energy, finance specialists |
| **General-Purpose (Claude Flow)** | 54 | MCP orchestration agents |
| **Workflow Automation** | 6 | Shared sub-agents from assetutilities hub |
| **Visualization** | 4 | Interactive plotting specialists |
| **Platform Agents** | 3 | Factory AI, Spec-Kit, Agent OS |

### Domain-Specific Agents (11)

**Engineering Simulation (7):**
- `aqwa` - ANSYS AQWA offshore hydrodynamics
- `freecad` - FreeCAD CAD automation
- `gmsh` - Mesh generation
- `orcaflex` - OrcaFlex mooring/riser simulation
- `orcawave` - Wave analysis
- `cad-engineering-specialist` - CAD engineering expert
- `web-test-module` - Web testing automation

**Energy Sector (3):**
- `drilling-expert` - Oil & gas drilling operations
- `oil-and-gas-expert` - O&G industry analysis
- `financial-analysis` - Energy economics & finance

**Finance (1):**
- `finance-analytics` - Financial analysis utilities

### General-Purpose Agents (54 - Claude Flow MCP)

**Core Development (5):**
- coder, reviewer, tester, planner, researcher

**Swarm Coordination (5):**
- hierarchical-coordinator, mesh-coordinator, adaptive-coordinator, collective-intelligence-coordinator, swarm-memory-manager

**Consensus & Distributed (7):**
- byzantine-coordinator, raft-manager, gossip-coordinator, consensus-builder, crdt-synchronizer, quorum-manager, security-manager

**Performance (5):**
- perf-analyzer, performance-benchmarker, task-orchestrator, memory-coordinator, smart-agent

**GitHub Integration (9):**
- github-modes, pr-manager, code-review-swarm, issue-tracker, release-manager, workflow-automation, project-board-sync, repo-architect, multi-repo-swarm

**SPARC Methodology (6):**
- sparc-coord, sparc-coder, specification, pseudocode, architecture, refinement

**Specialized Development (8):**
- backend-dev, mobile-dev, ml-developer, cicd-engineer, api-docs, system-architect, code-analyzer, base-template-generator

**Testing & Validation (2):**
- tdd-london-swarm, production-validator

**Migration & Planning (2):**
- migration-planner, swarm-init

**Visualization (4):**
- plotly-visualization-agent, bokeh-dashboard-agent, altair-analysis-agent, d3js-custom-viz-agent

### Workflow Automation Sub-Agents (6 - assetutilities hub)

- `workflow-automation` - Enhanced specs & documentation
- `file-management-automation` - File operations
- `visualization-automation` - Chart generation
- `auth-system` - Authentication & authorization
- `git-workflow-automation` - Git operations
- `free-agent-templates` - Free tier agent templates

## Repository Mappings

### Primary Agent Repositories

**digitalmodel** (7 agents)
- Specialization: Engineering simulation
- Agents: aqwa, freecad, gmsh, orcaflex, orcawave, cad-engineering-specialist, web-test-module

**worldenergydata** (3 agents)
- Specialization: Energy analysis
- Agents: drilling-expert, oil-and-gas-expert, financial-analysis

**assetutilities** (2 agents + hub)
- Specialization: Financial utilities
- Agents: finance-analytics, test-interactive
- **Hub for:** 6 workflow automation sub-agents

**workspace-hub** (central)
- Specialization: Multi-repo orchestration
- Provides: Master registry, orchestration, best practices

## Agent Selection & Orchestration

### Intelligent Agent Selection

Use the agent orchestrator for automatic agent selection based on task type and complexity:

```bash
# Basic usage
./modules/automation/agent_orchestrator.sh <task-type> "<description>"

# With review
./modules/automation/agent_orchestrator.sh code-generation "Create API" --with-review

# Specify complexity
./modules/automation/agent_orchestrator.sh architecture-design "Design microservices" --complexity complex

# Force specific agent
./modules/automation/agent_orchestrator.sh code-review "Review auth module" --agent code-review-swarm
```

### Task Types & Primary Agents

| Task Type | Primary Agent | Alternatives |
|-----------|---------------|--------------|
| code-review | code-review-swarm | claude-sonnet-4.5, factory-ai-droid |
| spec-creation | spec-kit-analyzer | agent-os-planner, claude-sonnet-4.5 |
| requirement-analysis | agent-os-planner | claude-sonnet-4.5, researcher |
| migration | migration-planner | claude-sonnet-4.5, system-architect |
| performance-opt | perf-analyzer | claude-sonnet-4.5, performance-benchmarker |
| security-audit | security-manager | claude-sonnet-4.5, code-review-swarm |

## Cross-Repository Integration

### Reference Formats

```yaml
# Workspace-hub central registry
"@workspace-hub/.claude/agents/domain/engineering/aqwa.yaml"

# Assetutilities hub (workflow automation)
"@assetutilities/agents/registry/sub-agents/workflow-automation"

# Specific repository
"@digitalmodel/agents/orcaflex"

# Relative (within same repo)
"../orcaflex"
```

### Hub Repository Pattern

**assetutilities** serves as the hub for shared workflow automation:

```yaml
# Reference shared sub-agents
workflow_automation: "@assetutilities/agents/registry/sub-agents/workflow-automation"
visualization: "@assetutilities/agents/registry/sub-agents/visualization-automation"
```

## Configuration Patterns

### Three Configuration Formats

**1. Domain Expert (YAML):**
```yaml
name: "agent-name"
version: "3.0.0"
type: "domain-expert"
specialization: "specific-domain"
capabilities: [...]
processing_config: {...}
```

**2. Engineering Tool (JSON):**
```json
{
  "name": "Tool Agent",
  "version": "1.0.0",
  "type": "engineering-tool",
  "capabilities": [...],
  "api": {...}
}
```

**3. MCP Registry (JSON):**
```json
{
  "type": "orchestrator",
  "capabilities": {...}
}
```

## Best Practices

📚 **Full documentation:** `BEST_PRACTICES.md`

**Key Principles:**
1. ✅ Semantic versioning (MAJOR.MINOR.PATCH)
2. ✅ Clear capability declarations
3. ✅ Context optimization (16K max)
4. ✅ Phased processing (6 phases)
5. ✅ Quality thresholds (0.7-0.8)
6. ✅ Cross-repo references with @ notation
7. ✅ No hardcoded secrets
8. ✅ Comprehensive error handling
9. ✅ Performance monitoring
10. ✅ Security-first design

## Automation & Maintenance

### Sync Agent Configs

```bash
# Update central registry from all repos
bash modules/automation/sync_agent_configs.sh --pull

# Push central registry updates to all repos
bash modules/automation/sync_agent_configs.sh --push

# Validate all configurations
bash modules/automation/sync_agent_configs.sh --validate
```

### Daily Updates

```bash
# Auto-run daily at 00:00 UTC
bash modules/automation/update_ai_agents_daily.sh
```

### Validation

```bash
# Validate agent configurations
bash modules/automation/validate_agent_configs.sh
```

## Usage Examples

### Example 1: Use Domain-Specific Agent

```bash
# In digitalmodel repository
cd <workspace-hub>/digitalmodel

# Use AQWA agent
droid exec --agent aqwa "Analyze floating platform hydrodynamics"
```

### Example 2: Cross-Repository Reference

```yaml
# In any repository's CLAUDE.md or agent config
agents:
  primary: "@workspace-hub/.claude/agents/domain/engineering/aqwa.yaml"
  support:
    - "@digitalmodel/agents/orcaflex"
    - "@assetutilities/agents/registry/sub-agents/visualization-automation"
```

### Example 3: Workflow Automation

```bash
# Use shared workflow automation from hub
./modules/automation/agent_orchestrator.sh spec-creation "Design payment API" \
  --agent workflow-automation \
  --domain python
```

### Example 4: Intelligent Selection

```bash
# Let orchestrator choose best agent
./modules/automation/agent_orchestrator.sh architecture-design \
  "Design microservices for e-commerce platform" \
  --complexity complex \
  --with-review
```

## Migration & Rollback

### Phased Migration Strategy

**Phase 1** (Week 1): Test with 2 repos (digitalmodel, worldenergydata)
**Phase 2** (Week 2): Expand to 10 repositories
**Phase 3** (Week 3-4): Full rollout to all 26 repositories

### Backup & Rollback

```bash
# Backups stored in
.claude/agents/.backup/

# Rollback if needed
bash modules/automation/rollback_agent_configs.sh
```

## Metrics & Monitoring

**Dashboard:** http://localhost:3000/agent-metrics

**Tracked Metrics:**
- Agent usage (execution count, success rate)
- Performance (response time, throughput)
- Quality (output score, validation pass rate)
- Resource utilization (memory, tokens)

## Support & Documentation

- **Registry:** `registry.yaml` (master reference)
- **Best Practices:** `BEST_PRACTICES.md`
- **Orchestrator:** `modules/automation/agent_orchestrator.sh`
- **MCP Registry:** `modules/config/ai-agents-registry.json`

## Version History

### v1.0.0 (2025-10-05)
- Initial master registry creation
- Consolidated 78+ agents from 26 repositories
- Established best practices documentation
- Implemented centralized orchestration

---

**This registry is the single source of truth for all agent configurations in workspace-hub.**

For questions or issues, refer to the workspace-hub documentation or contact the development team.
