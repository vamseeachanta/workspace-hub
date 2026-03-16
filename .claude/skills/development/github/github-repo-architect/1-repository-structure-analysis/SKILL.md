---
name: github-repo-architect-1-repository-structure-analysis
description: 'Sub-skill of github-repo-architect: 1. Repository Structure Analysis
  (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Repository Structure Analysis (+2)

## 1. Repository Structure Analysis


```javascript
// Initialize architecture analysis swarm

// Orchestrate structure optimization
    task: "Analyze and optimize repository structure for scalability and maintainability",
    strategy: "adaptive",
    priority: "medium"
})
```

## 2. Analyze Current Structure


```bash
# List repository contents
ls -la

# Find all config files
find . -name "*.json" -o -name "*.yml" -o -name "*.yaml" | head -20

# Analyze package dependencies
cat package.json | jq '.dependencies, .devDependencies'


*See sub-skills for full details.*

## 3. Create Repository Template


```bash
# Create template repository
gh repo create claude-project-template \
  --public \
  --description "Standardized template for Claude Code projects" \
  --template

# Clone and setup structure
gh repo clone owner/claude-project-template
cd claude-project-template

*See sub-skills for full details.*
