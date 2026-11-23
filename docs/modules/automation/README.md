# Automation Module Documentation

This module contains documentation for AI agent orchestration, swarm coordination, and automation workflows.

## Overview

The automation module encompasses AI agent management, centralized orchestration, and factory AI integration for intelligent task automation across the workspace-hub ecosystem.

## Documents

### Agent Orchestration
- **[AI_AGENT_ORCHESTRATION.md](AI_AGENT_ORCHESTRATION.md)** - Comprehensive guide to AI agent orchestration system with 54+ specialized agents
- **[AI_ECOSYSTEM.md](AI_ECOSYSTEM.md)** - AI ecosystem architecture and integration patterns
- **[AGENT_CENTRALIZATION_COMPLETE.md](AGENT_CENTRALIZATION_COMPLETE.md)** - Agent centralization implementation summary

### Factory AI Integration
- **[FACTORY_AI_GUIDE.md](FACTORY_AI_GUIDE.md)** - Complete guide to Factory AI integration
- **[FACTORY_AI_ENHANCED_GUIDE.md](FACTORY_AI_ENHANCED_GUIDE.md)** - Enhanced Factory AI features and capabilities
- **[FACTORY_AI_QUICK_START.md](FACTORY_AI_QUICK_START.md)** - Quick start guide for Factory AI setup

### Analysis & Planning
- **[CENTRALIZATION_ANALYSIS.md](CENTRALIZATION_ANALYSIS.md)** - Analysis of centralization patterns and strategies
- **[CENTRALIZATION_IMPACT_PRIORITIZATION.md](CENTRALIZATION_IMPACT_PRIORITIZATION.md)** - Impact prioritization for centralization initiatives

## Key Features

### AI Agent Types (54 Total)
- **Core Development**: coder, reviewer, tester, planner, researcher
- **Swarm Coordination**: hierarchical-coordinator, mesh-coordinator, adaptive-coordinator
- **Consensus & Distributed**: byzantine-coordinator, raft-manager, gossip-coordinator
- **Performance**: perf-analyzer, performance-benchmarker, task-orchestrator
- **GitHub Integration**: pr-manager, code-review-swarm, issue-tracker
- **SPARC Methodology**: sparc-coord, specification, pseudocode, architecture, refinement

### Automation Scripts
Located in `../../../modules/automation/`:
- `agent_orchestrator.sh` - Intelligent agent selection and orchestration
- `gate_pass_review.sh` - SPARC phase gate-pass reviews
- `update_ai_agents_daily.sh` - Daily agent capability updates
- `sync_agent_configs.sh` - Agent configuration synchronization
- `setup_claude_memory_all_repos.sh` - Claude memory setup across repositories

## Quick Start

```bash
# Select best agent for task
./modules/automation/agent_orchestrator.sh <task-type> "<description>" --with-review

# Run gate-pass review
./modules/automation/gate_pass_review.sh <phase> . --auto

# Update agent capabilities
./modules/automation/update_ai_agents_daily.sh
```

## Related Documentation
- [Claude Interaction Guide](../../guides/CLAUDE_INTERACTION_GUIDE.md)
- [MCP Setup Guide](../../guides/MCP_SETUP_GUIDE.md)
- [Factory AI Enhanced Guide](FACTORY_AI_ENHANCED_GUIDE.md)

---
*Part of the workspace-hub automation infrastructure*
