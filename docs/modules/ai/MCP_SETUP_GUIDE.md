# MCP Setup Guide

> **Model Context Protocol (MCP) Configuration for Workspace Hub**
>
> **Version:** 1.0.0
> **Last Updated:** 2025-10-08

## Quick Start

```bash
# Run automated setup script
cd /mnt/github/workspace-hub
./modules/automation/setup_mcp_servers.sh
```

This installs all required and optional MCP servers for Claude Code and Factory AI.

---

## What are MCPs?

**Model Context Protocol (MCP)** servers extend AI capabilities by providing specialized tools and integrations:

- **Claude Flow** - 54+ development agents, SPARC methodology, swarm coordination
- **Playwright** - Browser automation, testing, screenshots
- **Ruv-Swarm** - Enhanced coordination, memory persistence
- **Flow-Nexus** - 70+ cloud tools (sandboxes, templates, storage)

---

## Prerequisites

### 1. Claude Code CLI

```bash
# Check if installed
claude --version

# Install if needed
npm install -g @anthropic/claude-code
```

### 2. Node.js (v18+)

```bash
# Check version
node --version

# Should be v18.0.0 or higher
```

### 3. NPX (comes with Node.js)

```bash
# Verify npx is available
npx --version
```

---

## Automated Setup (Recommended)

### Run Setup Script

```bash
cd /mnt/github/workspace-hub
./modules/automation/setup_mcp_servers.sh
```

### What It Does

1. **Checks prerequisites** (claude CLI, npx, Node.js)
2. **Installs required MCPs**:
   - Claude Flow (required)
3. **Installs optional MCPs**:
   - Playwright (browser automation)
   - Ruv-Swarm (enhanced coordination)
   - Flow-Nexus (cloud features, asks for confirmation)
4. **Verifies installations**
5. **Displays usage instructions**

### Expected Output

```
========================================
MCP Servers Setup
========================================

✓ Prerequisites check passed

Installing REQUIRED MCP servers...

Installing: claude-flow
  ✓ claude-flow installed successfully

Installing OPTIONAL MCP servers...

Installing: playwright
  ✓ playwright installed successfully

Installing: ruv-swarm
  ✓ ruv-swarm installed successfully

========================================
Installation Summary
========================================
Total attempted: 4
Successfully installed: 4
Failed/Skipped: 0

✓ MCP servers installed successfully!
```

---

## Manual Setup

If you prefer manual installation or the script fails:

### 1. Install Claude Flow (Required)

```bash
claude mcp add claude-flow npx claude-flow@alpha mcp start
```

**Provides:**
- 54+ development agents (coder, reviewer, tester, etc.)
- SPARC methodology (Specification, Pseudocode, Architecture, Refinement, Completion)
- Swarm coordination (hierarchical, mesh, adaptive)
- GitHub integration (PR management, code review, issue tracking)
- Memory management and neural training

### 2. Install Playwright (Optional)

```bash
claude mcp add playwright npx @playwright/mcp-server
```

**Provides:**
- Browser automation (navigation, clicks, form filling)
- Screenshot and PDF generation
- Element inspection and interaction
- Testing automation

### 3. Install Ruv-Swarm (Optional)

```bash
claude mcp add ruv-swarm npx ruv-swarm mcp start
```

**Provides:**
- Advanced swarm topologies
- Enhanced memory persistence
- Performance optimization
- Self-healing workflows

### 4. Install Flow-Nexus (Optional - Cloud)

```bash
claude mcp add flow-nexus npx flow-nexus@latest mcp start
```

**Provides:**
- 70+ cloud-based tools
- E2B sandboxes (cloud code execution)
- Template marketplace
- Neural AI features
- Real-time collaboration
- Cloud storage

**Requires registration:**
```bash
npx flow-nexus@latest register
npx flow-nexus@latest login
```

---

## Verification

### List Installed MCPs

```bash
# List all installed MCP servers
claude mcp list
```

**Expected output:**
```
Installed MCP servers:
  • claude-flow
  • playwright
  • ruv-swarm
  • flow-nexus
```

### Check MCP Status

```bash
# Check status of specific MCP
claude mcp status claude-flow
```

### Test MCP Access

```bash
# Start a Claude Code session and try MCP tools
claude

# In the session, MCPs are automatically available
# Example: Use Claude Flow to list agents
# The AI can now access mcp__claude-flow__agent_list
```

---

## MCP Configuration Location

MCP configurations are stored per-machine, not per-repository:

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

---

## Available MCP Tools

### Claude Flow MCP

#### Coordination
- `swarm_init` - Initialize swarm topology (mesh, hierarchical, adaptive)
- `agent_spawn` - Spawn specialized agents
- `task_orchestrate` - High-level task orchestration

#### Monitoring
- `swarm_status` - Real-time swarm status
- `agent_list` - List active agents
- `agent_metrics` - Performance metrics
- `task_status` - Task execution status
- `task_results` - Retrieve task results

#### Memory & Neural
- `memory_usage` - Memory management
- `neural_status` - Neural network status
- `neural_train` - Train patterns from successful workflows
- `neural_patterns` - Retrieve learned patterns

#### GitHub Integration
- `github_swarm` - GitHub swarm coordination
- `repo_analyze` - Repository analysis
- `pr_enhance` - Pull request enhancement
- `issue_triage` - Automated issue triage
- `code_review` - Automated code reviews

#### System
- `benchmark_run` - Performance benchmarking
- `features_detect` - Feature detection
- `swarm_monitor` - Continuous swarm monitoring

### Playwright MCP

- `playwright_navigate` - Navigate to URL
- `playwright_screenshot` - Capture screenshot
- `playwright_click` - Click element
- `playwright_fill` - Fill form field
- `playwright_evaluate` - Execute JavaScript
- `playwright_pdf` - Generate PDF

### Ruv-Swarm MCP

- Enhanced versions of Claude Flow tools
- Additional topology options
- Advanced memory persistence
- Performance optimization features

### Flow-Nexus MCP (70+ tools)

#### Swarm & Agents
- `swarm_init`, `swarm_scale`, `agent_spawn`, `task_orchestrate`

#### Sandboxes
- `sandbox_create`, `sandbox_execute`, `sandbox_upload`

#### Templates
- `template_list`, `template_deploy`

#### Neural AI
- `neural_train`, `neural_patterns`, `seraphina_chat`

#### GitHub
- `github_repo_analyze`, `github_pr_manage`

#### Real-time
- `execution_stream_subscribe`, `realtime_subscribe`

#### Storage
- `storage_upload`, `storage_list`

---

## Troubleshooting

### Issue: "claude: command not found"

**Solution:**
```bash
# Install Claude Code CLI
npm install -g @anthropic/claude-code

# Verify installation
claude --version
```

### Issue: "npx: command not found"

**Solution:**
```bash
# Install Node.js (includes npx)
# Visit: https://nodejs.org

# Verify Node.js installation
node --version
npx --version
```

### Issue: MCP installation fails

**Solution:**
```bash
# Remove existing MCP
claude mcp remove <mcp-name>

# Reinstall
claude mcp add <mcp-name> <command>

# Check logs
claude mcp logs <mcp-name>
```

### Issue: MCP tools not available in session

**Solution:**
1. Verify MCP is installed: `claude mcp list`
2. Check MCP status: `claude mcp status <mcp-name>`
3. Restart Claude Code
4. Try manual installation commands

### Issue: Flow-Nexus requires authentication

**Solution:**
```bash
# Register account
npx flow-nexus@latest register

# Login
npx flow-nexus@latest login

# Verify authentication
npx flow-nexus@latest whoami
```

---

## MCP Management

### List All MCPs

```bash
claude mcp list
```

### Remove an MCP

```bash
claude mcp remove <mcp-name>

# Example
claude mcp remove playwright
```

### Update an MCP

```bash
# Remove old version
claude mcp remove <mcp-name>

# Reinstall latest
claude mcp add <mcp-name> <command>
```

### View MCP Logs

```bash
claude mcp logs <mcp-name>

# Example
claude mcp logs claude-flow
```

---

## Per-Developer Setup

### Team Onboarding

Each developer needs to run MCP setup on their machine:

```bash
# 1. Clone workspace-hub
git clone <repo-url>
cd workspace-hub

# 2. Run MCP setup
./modules/automation/setup_mcp_servers.sh

# 3. Verify installation
claude mcp list
```

### Why Per-Machine?

- MCP configurations are **machine-specific**, not repository-specific
- Each developer's `claude_desktop_config.json` is local
- MCPs run as local processes on each machine
- This ensures consistent tooling across the team

---

## Integration with Workspace Hub

### Agent Orchestrator

The agent orchestrator automatically uses MCP tools:

```bash
# Uses Claude Flow MCP to select best agent
./modules/automation/agent_orchestrator.sh code-generation "Create REST API"
```

### SPARC Methodology

SPARC workflow uses Claude Flow MCP:

```bash
# Run complete TDD workflow
npx claude-flow sparc tdd "User authentication"
```

### Factory AI (droid)

Factory AI also has access to installed MCPs:

```bash
# Start droid session (MCPs automatically available)
droid

# MCPs work across all AI models (Claude, GPT-5 Codex, etc.)
```

---

## Best Practices

### 1. Install Required MCPs First

Always install **claude-flow** - it's required for the workspace-hub orchestration system.

### 2. Install Optional MCPs Based on Needs

- **Playwright** - If you do browser testing or automation
- **Ruv-Swarm** - If you need advanced coordination features
- **Flow-Nexus** - If you want cloud execution and templates

### 3. Keep MCPs Updated

```bash
# Remove old version
claude mcp remove claude-flow

# Install latest
claude mcp add claude-flow npx claude-flow@alpha mcp start
```

### 4. Document Custom MCPs

If you add custom MCPs, document them in this file.

### 5. Verify After Updates

```bash
# After system updates or Claude Code updates
claude mcp list
claude mcp status claude-flow
```

---

## Security Considerations

### MCP Permissions

- MCPs run with your user permissions
- They can access files, network, and system resources
- Only install MCPs from trusted sources

### Recommended MCPs (Trusted)

✅ **claude-flow** - Official Claude Flow MCP (@alpha)
✅ **playwright** - Official Playwright MCP (@playwright/mcp-server)
✅ **ruv-swarm** - Community MCP (ruv-swarm)
✅ **flow-nexus** - Flow Nexus platform (flow-nexus)

### Custom MCPs

⚠️ Before installing custom MCPs:
- Review source code
- Check community reputation
- Verify package authenticity

---

## Resources

### Documentation

- **Workspace Hub Summary:** `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md`
- **Agent Registry:** `.claude/agents/registry.yaml`
- **Best Practices:** `.claude/agents/BEST_PRACTICES.md`
- **AI Orchestration:** `docs/AI_AGENT_ORCHESTRATION.md`

### External Links

- **Claude Flow:** https://github.com/ruvnet/claude-flow
- **Playwright MCP:** https://github.com/microsoft/playwright
- **Flow-Nexus:** https://flow-nexus.ruv.io
- **MCP Specification:** https://modelcontextprotocol.io

### Support

- **Issues:** GitHub Issues in workspace-hub
- **Team Chat:** Internal communication channels

---

## Version History

### v1.0.0 (2025-10-08)
- Initial MCP setup guide
- Automated setup script created
- Documented all 4 recommended MCPs
- Added troubleshooting section

---

**Status:** ✅ **Ready for Team Deployment**

**Each developer should run `./modules/automation/setup_mcp_servers.sh` to enable full MCP capabilities.**
