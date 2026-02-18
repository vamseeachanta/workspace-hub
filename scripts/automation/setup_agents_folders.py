#!/usr/bin/env python3
"""
Setup agents folders in all repositories and organize AI agents.

Each repository will have:
- agents/                     # Main agents folder
  ├── security/              # Security-related agents
  ├── performance/           # Performance optimization agents
  ├── testing/               # Test generation and validation agents
  ├── documentation/         # Documentation agents
  ├── devops/               # CI/CD and infrastructure agents
  ├── data/                 # Data engineering agents
  ├── code_quality/         # Code review and refactoring agents
  └── README.md             # Agent usage documentation
"""

import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Agent folder structure template
AGENT_CATEGORIES = [
    "security",
    "performance", 
    "testing",
    "documentation",
    "devops",
    "data",
    "code_quality"
]

# README content for agents folder
AGENTS_README = """# AI Agents Library

This folder contains specialized AI agents for various development tasks.
Agents are sourced from AITmpl and Claude Code Templates.

## Folder Structure

```
agents/
├── security/          # Security audit and penetration testing
├── performance/       # Performance optimization agents
├── testing/          # Test generation and E2E testing
├── documentation/    # API and code documentation
├── devops/          # CI/CD and infrastructure
├── data/            # Data engineering and ETL
└── code_quality/    # Code review and refactoring
```

## Usage

### Automatic Agent Selection

Agents are automatically selected based on your current task:

```bash
# During spec creation
/spec create api-gateway  # Automatically uses API Security Agent

# During testing
/test generate  # Uses Test Generation Agent

# During optimization
/project optimize  # Uses Performance Optimization Agents
```

### Manual Agent Usage

```bash
# List all available agents
/ai-agent list

# Get recommendations for current context
/ai-agent recommend

# Use specific agent
/ai-agent use "API Security Audit Agent"

# Get agent information
/ai-agent info "Test Generation Agent"
```

## Available Agents by Category

### 🔒 Security
- API Security Audit Agent
- Penetration Testing Agent
- Vulnerability Scanner Agent

### ⚡ Performance
- React Performance Optimization Agent
- Database Optimization Agent
- Bundle Size Analyzer Agent

### 🧪 Testing
- Test Generation Agent
- E2E Testing Agent
- Coverage Analysis Agent

### 📚 Documentation
- API Documentation Agent
- Code Documentation Agent
- README Generator Agent

### 🔧 DevOps
- CI/CD Pipeline Agent
- Infrastructure as Code Agent
- Docker Configuration Agent

### 📊 Data
- ETL Pipeline Agent
- Data Analysis Agent
- Data Validation Agent

### ✨ Code Quality
- Code Review Agent
- Refactoring Agent
- Best Practices Agent

## Integration Points

Agents integrate with these commands:
- `/spec create` - Automatic agent recommendations
- `/task execute` - Agent assistance during implementation
- `/test run` - Testing agents for quality assurance
- `/project optimize` - Performance agents
- `/git commit` - Code review agents

## Best Practices

1. **Let agents recommend themselves** - The system knows which agents to use
2. **Chain agents for better results** - Use multiple agents in sequence
3. **Review agent suggestions** - Don't apply blindly
4. **Customize for your project** - Adapt agent outputs to your standards
5. **Share improvements** - Contribute agent enhancements back

## Adding Custom Agents

To add your own agents:

1. Create agent file in appropriate category folder
2. Follow the agent template structure
3. Update this README with agent details
4. Test agent integration

## Resources

- AITmpl: https://www.aitmpl.com/
- Claude Code Templates: https://github.com/davila7/claude-code-templates
- Agent Catalog: .agent-os/resources/aitmpl_agents_catalog.yaml
"""

# Sample agent template
AGENT_TEMPLATE = """# {agent_name}

## Purpose
{purpose}

## Capabilities
{capabilities}

## When to Use
{when_to_use}

## Integration Points
{integration_points}

## Usage Example
```bash
/ai-agent use "{agent_name}"
```

## Implementation
```python
# Agent implementation would go here
# This is a placeholder for the actual agent code
class {agent_class}:
    def __init__(self):
        self.name = "{agent_name}"
        self.category = "{category}"
    
    def analyze(self, context):
        # Agent logic here
        pass
    
    def recommend(self):
        # Recommendations here
        pass
```
"""

def setup_agents_in_repo(repo_name: str) -> tuple:
    """Setup agents folder structure in a single repository."""
    try:
        repo_path = Path(f"/mnt/github/github/{repo_name}")
        
        if not repo_path.exists():
            return (repo_name, False, "Repository not found")
        
        # Create main agents folder
        agents_dir = repo_path / "agents"
        agents_dir.mkdir(exist_ok=True)
        
        # Create category folders
        for category in AGENT_CATEGORIES:
            category_dir = agents_dir / category
            category_dir.mkdir(exist_ok=True)
            
            # Create a sample agent file in each category
            sample_agent = category_dir / f"sample_{category}_agent.md"
            if not sample_agent.exists():
                agent_content = AGENT_TEMPLATE.format(
                    agent_name=f"Sample {category.replace('_', ' ').title()} Agent",
                    purpose=f"Placeholder for {category} agents",
                    capabilities=f"- {category.replace('_', ' ').title()} analysis\n- Recommendations\n- Automation",
                    when_to_use=f"When working on {category.replace('_', ' ')} tasks",
                    integration_points=f"- /spec create\n- /task execute\n- /test run",
                    agent_class=f"{category.title().replace('_', '')}Agent",
                    category=category
                )
                sample_agent.write_text(agent_content)
        
        # Create README
        readme_path = agents_dir / "README.md"
        readme_path.write_text(AGENTS_README)
        
        # Create agents index file
        index_file = agents_dir / "index.yaml"
        index_content = f"""# Agent Index for {repo_name}

agents:
  total: 0  # Will be populated as agents are added
  categories:
    security: []
    performance: []
    testing: []
    documentation: []
    devops: []
    data: []
    code_quality: []

custom_agents: []  # Repository-specific custom agents

integration:
  enabled: true
  auto_select: true
  commands:
    - /spec
    - /task
    - /test
    - /project
"""
        index_file.write_text(index_content)
        
        return (repo_name, True, "Agents folder structure created")
        
    except Exception as e:
        return (repo_name, False, str(e))

def main():
    """Setup agents folders in all repositories."""
    repos = [d.name for d in Path("/mnt/github/github").iterdir() 
             if d.is_dir() and (d / '.git').exists()]
    
    print(f"🤖 Setting up agents folders in {len(repos)} repositories...\n")
    
    success_count = 0
    failed_repos = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(setup_agents_in_repo, repo) for repo in repos]
        
        for future in as_completed(futures):
            repo_name, success, message = future.result()
            
            if success:
                print(f"✅ {repo_name}: {message}")
                success_count += 1
            else:
                print(f"❌ {repo_name}: {message}")
                failed_repos.append(repo_name)
    
    print(f"\n📊 Summary:")
    print(f"   Successfully setup: {success_count}/{len(repos)}")
    
    if failed_repos:
        print(f"   Failed repositories: {', '.join(failed_repos)}")
    
    if success_count == len(repos):
        print("\n✨ All repositories now have agents folder structure!")
        print("\n📋 Next Steps:")
        print("   1. Agents will be automatically selected during development")
        print("   2. Use '/ai-agent list' to see available agents")
        print("   3. Use '/ai-agent recommend' for context-based suggestions")
        print("   4. Add custom agents to the agents/ folder as needed")
    
    # Create documentation
    doc_path = Path("/mnt/github/github/AGENTS_SETUP.md")
    doc_content = f"""# AI Agents Setup Complete

## Date: 2024-01-13

Successfully set up agents folder structure in {success_count} repositories.

## Structure Created

Each repository now has:
```
agents/
├── security/
├── performance/
├── testing/
├── documentation/
├── devops/
├── data/
├── code_quality/
├── README.md
└── index.yaml
```

## Usage

### Automatic Agent Selection
Agents are automatically selected based on context during:
- Spec creation (`/spec create`)
- Task execution (`/task execute`)
- Testing (`/test run`)
- Optimization (`/project optimize`)

### Manual Agent Commands
```bash
/ai-agent list              # List all agents
/ai-agent recommend         # Get recommendations
/ai-agent use [agent]       # Use specific agent
/ai-agent info [agent]      # Get agent details
```

## Integration

Agents integrate with:
- **Claude Code Templates**: https://github.com/davila7/claude-code-templates
- **AITmpl**: https://www.aitmpl.com/
- **Local agents folder**: Each repo's agents/ directory

## Adding Custom Agents

1. Navigate to appropriate category folder in agents/
2. Create new agent file (markdown or Python)
3. Follow the template structure
4. Update agents/index.yaml
5. Test with `/ai-agent use [your-agent]`

## Resources

- Agent Catalog: `.agent-os/resources/aitmpl_agents_catalog.yaml`
- Agent Manager: `.agent-os/commands/ai_agent.py`
- Templates: `.agent-os/resources/ai_templates.yaml`
"""
    
    doc_path.write_text(doc_content)
    print(f"\n📝 Documentation saved to: {doc_path}")

if __name__ == "__main__":
    main()