# Factory.ai Setup with Claude and OpenAI Models

> Complete guide for setting up factory.ai with both Claude and OpenAI model support
>
> Version: 1.0.0
> Last Updated: 2025-10-22

## Overview

This guide covers the complete setup of factory.ai (Droids) with support for both Claude (Anthropic) and OpenAI models in the workspace-hub environment.

## Prerequisites

- Linux or macOS operating system
- Bash shell (version 4.0+)
- Git installed
- Internet connection
- API keys for Claude and/or OpenAI

## 🚀 Installation

### Step 1: Install Factory.ai CLI

Install the factory.ai Droid CLI:

```bash
# Install factory.ai CLI
curl -fsSL https://app.factory.ai/cli | sh
```

This will install the `droid` command to `~/.local/bin/droid`.

### Step 2: Verify Installation

```bash
# Check installation
droid --version

# Expected output: v0.18.0 or higher
```

### Step 3: Ensure CLI is in PATH

```bash
# Add to PATH if not already there
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or for zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## 🔑 API Key Configuration

### Claude (Anthropic) API Key

Factory.ai requires authentication through their platform, but you may need Claude API keys for direct API access:

```bash
# Set Claude API key (optional for direct API use)
export ANTHROPIC_API_KEY="sk-ant-..."

# Make permanent
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
```

To get a Claude API key:
1. Visit https://console.anthropic.com/
2. Sign in or create an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and save it securely

### OpenAI API Key

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-..."

# Make permanent
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
```

To get an OpenAI API key:
1. Visit https://platform.openai.com/
2. Sign in or create an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and save it securely

### Factory.ai Authentication

On first use, factory.ai will:
1. Open your browser automatically
2. Prompt you to sign in
3. Store credentials locally in `~/.factory/`

```bash
# First-time authentication
cd /mnt/github/workspace-hub
droid

# Follow the browser authentication flow
```

## 📝 Model Configuration

The workspace-hub droids.yml configuration has been set up to support multiple AI models.

### Current Configuration

**Location:** `/mnt/github/workspace-hub/.drcode/droids.yml`

**Current Models Configured:**
- `claude-sonnet-3-5` (default)
- `claude-sonnet-4-0` (for complex tasks)

### Adding OpenAI Models

Update the droids.yml to include OpenAI models:

```yaml
# Default model configuration
defaults:
  model: claude-sonnet-3-5  # or gpt-4-turbo, gpt-4o
  temperature: 0.7
  max_tokens: 4096

# Specialized droids with different models
droids:
  # Claude models
  claude-refactor:
    model: claude-sonnet-3-5
    temperature: 0.3

  claude-feature:
    model: claude-sonnet-4-0
    temperature: 0.7

  # OpenAI models
  openai-refactor:
    model: gpt-4-turbo
    temperature: 0.3

  openai-feature:
    model: gpt-4o
    temperature: 0.7

  openai-fast:
    model: gpt-3.5-turbo
    temperature: 0.7
```

## 🎯 Available Models

### Claude Models

| Model | Best For | Context | Speed | Cost |
|-------|----------|---------|-------|------|
| claude-sonnet-3-5 | General development | 200K tokens | Fast | Medium |
| claude-sonnet-4-0 | Complex tasks, architecture | 200K tokens | Medium | High |
| claude-opus-3 | Highest quality | 200K tokens | Slow | Highest |

### OpenAI Models

| Model | Best For | Context | Speed | Cost |
|-------|----------|---------|-------|------|
| gpt-4o | Latest, fastest GPT-4 | 128K tokens | Fast | Medium |
| gpt-4-turbo | Complex reasoning | 128K tokens | Medium | High |
| gpt-4 | High quality | 8K tokens | Slow | High |
| gpt-3.5-turbo | Simple, fast tasks | 16K tokens | Very Fast | Low |

## 🔧 Usage Examples

### Using Default Model (Claude)

```bash
cd /mnt/github/workspace-hub/your-repo
droid exec "refactor this code to use async/await"
```

### Using Specific Claude Model

```bash
# Use Claude Sonnet 4.0 for complex architecture
droid --droid claude-feature exec "design a microservices architecture for user management"
```

### Using OpenAI Models

```bash
# Use GPT-4 Turbo for refactoring
droid --droid openai-refactor exec "optimize this code for performance"

# Use GPT-4o for features
droid --droid openai-feature exec "add authentication with JWT tokens"

# Use GPT-3.5 for simple tasks
droid --droid openai-fast exec "add docstrings to all functions"
```

### Model Selection Strategy

```bash
# Simple tasks → gpt-3.5-turbo (fastest, cheapest)
droid --droid openai-fast exec "fix typos in comments"

# Standard tasks → claude-sonnet-3-5 or gpt-4o (balanced)
droid exec "implement user profile endpoint"

# Complex tasks → claude-sonnet-4-0 or gpt-4-turbo (highest quality)
droid --droid claude-feature exec "design distributed caching system"
```

## 🎨 Interactive Mode

Start an interactive session with model selection:

```bash
# Interactive with default model
cd your-repository
droid

# Interactive with specific model
droid --droid openai-feature
```

In interactive mode:
- Ask questions naturally
- Request code changes
- Get explanations
- Iterate on solutions

## 🔄 Model Switching

You can switch models mid-workflow:

```bash
# Research with GPT-4
droid --droid openai-feature exec "research best practices for API rate limiting"

# Implementation with Claude (better at code)
droid --droid claude-feature exec "implement rate limiting based on research"

# Documentation with GPT-3.5 (cost-effective)
droid --droid openai-fast exec "document the rate limiting implementation"
```

## 📊 Cost Optimization

### Cost-Effective Strategies

1. **Use cheaper models for simple tasks:**
   ```bash
   # gpt-3.5-turbo for docstrings, comments, simple refactoring
   droid --droid openai-fast exec "add type hints"
   ```

2. **Use mid-tier models for standard work:**
   ```bash
   # claude-sonnet-3-5 or gpt-4o for features, bug fixes
   droid exec "fix authentication bug"
   ```

3. **Reserve expensive models for complex tasks:**
   ```bash
   # claude-sonnet-4-0 or gpt-4-turbo for architecture, migrations
   droid --droid claude-feature exec "migrate from REST to GraphQL"
   ```

### Estimated Costs (per 1M tokens)

| Model | Input | Output |
|-------|-------|--------|
| gpt-3.5-turbo | $0.50 | $1.50 |
| gpt-4o | $2.50 | $10.00 |
| gpt-4-turbo | $10.00 | $30.00 |
| claude-sonnet-3-5 | $3.00 | $15.00 |
| claude-sonnet-4-0 | $8.00 | $24.00 |

## 🧪 Testing Configuration

### Test Claude Models

```bash
cd /mnt/github/workspace-hub

# Test default Claude model
droid exec "echo 'Hello from Claude'"

# Test Claude Sonnet 4.0
droid --droid claude-feature exec "echo 'Hello from Claude Sonnet 4.0'"
```

### Test OpenAI Models

```bash
# Test GPT-4o
droid --droid openai-feature exec "echo 'Hello from GPT-4o'"

# Test GPT-3.5-turbo
droid --droid openai-fast exec "echo 'Hello from GPT-3.5-turbo'"
```

### Verify Model Selection

```bash
# Check which model is being used
droid --droid openai-feature exec "which AI model are you?"
```

## 🔍 Troubleshooting

### Issue: "droid: command not found"

```bash
# Verify installation
ls -la ~/.local/bin/droid

# If missing, reinstall
curl -fsSL https://app.factory.ai/cli | sh

# Check PATH
echo $PATH | grep ".local/bin"

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

### Issue: Authentication Failed

```bash
# Clear credentials and re-authenticate
rm -rf ~/.factory
droid

# Follow browser authentication flow
```

### Issue: API Key Not Working

```bash
# Verify API keys are set
echo $ANTHROPIC_API_KEY | head -c 20
echo $OPENAI_API_KEY | head -c 20

# Reload shell configuration
source ~/.bashrc  # or ~/.zshrc

# Test API keys
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-3-5-20241022","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'
```

### Issue: Model Not Available

```bash
# Check available models in factory.ai
droid --help

# Verify model name in droids.yml
cat /mnt/github/workspace-hub/.drcode/droids.yml | grep model:

# Use correct model names from the table above
```

### Issue: Slow Response

```bash
# Use faster models
droid --droid openai-fast exec "..."  # gpt-3.5-turbo
droid --droid openai-feature exec "..."  # gpt-4o

# Reduce max_tokens in droids.yml
# temperature: 0.7
# max_tokens: 2048  # Reduced from 4096
```

## 🔐 Security Best Practices

### API Key Security

1. **Never commit API keys to git:**
   ```bash
   # Add to .gitignore
   echo '**/*api_key*' >> .gitignore
   echo '**/*secret*' >> .gitignore
   echo '.env' >> .gitignore
   ```

2. **Use environment variables:**
   ```bash
   # Store in shell profile, not in code
   export ANTHROPIC_API_KEY="sk-ant-..."
   export OPENAI_API_KEY="sk-..."
   ```

3. **Rotate keys regularly:**
   - Change API keys every 90 days
   - Immediately rotate if compromised
   - Use separate keys for dev/prod

4. **Monitor usage:**
   - Set up billing alerts
   - Review API usage regularly
   - Track costs by project

### Factory.ai Security

```yaml
# In droids.yml
security:
  safe_mode: true
  require_approval_for:
    - database_migrations
    - file_deletions
    - system_commands
    - external_api_calls
```

## 📚 Integration with Workspace Hub

### AI Agent Orchestration

Factory.ai integrates with the workspace-hub AI orchestration system:

```bash
# Use orchestrator to select best agent
/mnt/github/workspace-hub/modules/automation/agent_orchestrator.sh \
  code-refactoring \
  "Refactor authentication module" \
  --with-review

# Orchestrator will choose between:
# - factory-ai-droid (best for refactoring)
# - claude-sonnet-4.5 (best for complex tasks)
# - claude-flow-coder (best for TDD)
```

### Gate-Pass Reviews

Run quality checks after using factory.ai:

```bash
# After code generation
/mnt/github/workspace-hub/modules/automation/gate_pass_review.sh \
  implementation-phase \
  . \
  --auto
```

### SPARC Methodology

Factory.ai droids follow SPARC phases:

```bash
# Specification
droid --droid claude-feature exec "analyze requirements for user management"

# Pseudocode
droid exec "write pseudocode for authentication flow"

# Architecture
droid --droid claude-feature exec "design system architecture"

# Refinement (TDD)
droid exec "implement with tests first"

# Completion
droid exec "integrate and document"
```

## 📖 Quick Reference

### Command Cheatsheet

```bash
# Basic usage
droid exec "task description"

# Specific model
droid --droid <droid-name> exec "task"

# Interactive mode
droid
droid --droid <droid-name>

# Available droids
claude-refactor      # Claude Sonnet 3.5, temp 0.3
claude-feature       # Claude Sonnet 4.0, temp 0.7
openai-refactor      # GPT-4 Turbo, temp 0.3
openai-feature       # GPT-4o, temp 0.7
openai-fast          # GPT-3.5 Turbo, temp 0.7

# Help
droid --help
droid exec --help
droid --version
```

### Model Selection Guide

| Task Type | Recommended Model | Command |
|-----------|------------------|---------|
| Simple fixes | gpt-3.5-turbo | `--droid openai-fast` |
| Standard features | claude-sonnet-3-5 | (default) |
| Complex architecture | claude-sonnet-4-0 | `--droid claude-feature` |
| Refactoring | gpt-4-turbo | `--droid openai-refactor` |
| Latest OpenAI | gpt-4o | `--droid openai-feature` |

## 🎓 Next Steps

1. **Complete Installation:**
   ```bash
   curl -fsSL https://app.factory.ai/cli | sh
   droid --version
   ```

2. **Set Up API Keys:**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   export OPENAI_API_KEY="sk-..."
   ```

3. **Test Both Models:**
   ```bash
   droid exec "test Claude"
   droid --droid openai-feature exec "test OpenAI"
   ```

4. **Update Configuration:**
   - Edit `.drcode/droids.yml` to add OpenAI models
   - Update `modules/config/ai-agents-registry.json`

5. **Integrate with Workflow:**
   - Use orchestrator for agent selection
   - Run gate-pass reviews
   - Follow SPARC methodology

## 📞 Support

- **Factory.ai Docs:** https://docs.factory.ai
- **Claude API:** https://docs.anthropic.com
- **OpenAI API:** https://platform.openai.com/docs
- **Workspace Hub:** See `docs/modules/automation/`

---

**Factory.ai is now configured with both Claude and OpenAI models! 🚀**
