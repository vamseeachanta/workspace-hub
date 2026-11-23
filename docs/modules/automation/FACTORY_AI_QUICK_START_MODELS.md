# Factory.ai Quick Start - Claude & OpenAI Models

> Get started with factory.ai using Claude and OpenAI models in 5 minutes

## 🚀 Quick Installation

### Step 1: Install Factory.ai

```bash
# Run the installation script
/mnt/github/workspace-hub/scripts/install_factory_ai.sh

# Or install manually
curl -fsSL https://app.factory.ai/cli | sh
```

### Step 2: Set API Keys

```bash
# Claude API Key
export ANTHROPIC_API_KEY="sk-ant-..."
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc

# OpenAI API Key
export OPENAI_API_KEY="sk-..."
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc

# Reload shell
source ~/.bashrc
```

### Step 3: Authenticate Factory.ai

```bash
cd /mnt/github/workspace-hub
droid
# Browser will open for authentication
```

## ⚡ Quick Usage

### Using Claude Models (Default)

```bash
# Default Claude model
droid exec "add docstrings to all functions"

# Claude Sonnet 4.0 for complex tasks
droid --droid claude-feature exec "design microservices architecture"
```

### Using OpenAI Models

```bash
# GPT-4.1 (latest, fast)
droid --droid openai-feature exec "implement user authentication"

# GPT-4.1 (complex reasoning)
droid --droid openai-refactor exec "optimize algorithm performance"

# GPT-4.1 Mini (fast, cost-effective)
droid --droid openai-fast exec "add type hints to Python code"
```

## 🎯 Model Selection Cheatsheet

| Task Type | Best Model | Command |
|-----------|-----------|---------|
| Simple fixes, docs | GPT-4.1 Mini | `droid --droid openai-fast exec "..."` |
| Standard features | Claude Sonnet 3.5 | `droid exec "..."` (default) |
| Web development | GPT-4.1 | `droid --droid openai-feature exec "..."` |
| Complex architecture | Claude Sonnet 4.0 | `droid --droid claude-feature exec "..."` |
| Refactoring | GPT-4.1 | `droid --droid openai-refactor exec "..."` |

## 💰 Cost Comparison

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| gpt-4.1-mini | ⚡⚡⚡ | ⭐⭐⭐ | $ | Simple tasks |
| gpt-4.1 | ⚡⚡ | ⭐⭐⭐⭐ | $$ | Balanced performance |
| claude-sonnet-3-5 | ⚡⚡ | ⭐⭐⭐⭐ | $$ | General development |
| gpt-4.1 | ⚡ | ⭐⭐⭐⭐⭐ | $$$ | Complex tasks |
| claude-sonnet-4-0 | ⚡ | ⭐⭐⭐⭐⭐ | $$$ | Architecture, planning |

## 🔄 Common Workflows

### Workflow 1: Feature Development

```bash
# 1. Research with GPT-4.1 (fast)
droid --droid openai-feature exec "research best practices for caching"

# 2. Architecture with Claude (thorough)
droid --droid claude-feature exec "design caching layer architecture"

# 3. Implementation with Claude (default)
droid exec "implement Redis caching layer"

# 4. Documentation with GPT-3.5 (cost-effective)
droid --droid openai-fast exec "document caching implementation"
```

### Workflow 2: Refactoring

```bash
# 1. Analysis with Claude
droid exec "analyze code duplication in auth module"

# 2. Refactoring with GPT-4.1
droid --droid openai-refactor exec "refactor auth module to remove duplication"

# 3. Testing with Claude
droid exec "write tests for refactored auth module"
```

### Workflow 3: Bug Fixing

```bash
# 1. Reproduce with Claude (thorough)
droid exec "write test that reproduces authentication bug"

# 2. Fix with GPT-4.1 (fast)
droid --droid openai-feature exec "fix authentication bug in auth.py:45"

# 3. Verify with Claude
droid exec "verify all auth tests pass"
```

## 🎨 Interactive Mode

```bash
# Start interactive session with default model
droid

# Start with specific model
droid --droid openai-feature
droid --droid claude-feature
```

In interactive mode, you can:
- Have a conversation with the AI
- Iterate on solutions
- Ask clarifying questions
- Request code changes

## 🔍 Verify Setup

```bash
# Check installation
droid --version

# Test Claude model
droid exec "echo 'Testing Claude model'"

# Test OpenAI model
droid --droid openai-feature exec "echo 'Testing OpenAI model'"

# Check available droids
cat /mnt/github/workspace-hub/.drcode/droids.yml | grep -A 2 "^  [a-z]"
```

## ⚙️ Configuration Files

### Main Configuration
- **Location:** `/mnt/github/workspace-hub/.drcode/droids.yml`
- **Content:** Model configurations, system prompts, preferences

### AI Agents Registry
- **Location:** `/mnt/github/workspace-hub/modules/config/ai-agents-registry.json`
- **Content:** Agent capabilities, scoring, task mapping

## 🆘 Troubleshooting

### Issue: "command not found: droid"

```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc

# Verify
which droid
```

### Issue: Authentication fails

```bash
# Clear credentials
rm -rf ~/.factory

# Re-authenticate
droid
```

### Issue: API key not working

```bash
# Verify keys are set
echo $ANTHROPIC_API_KEY | head -c 20
echo $OPENAI_API_KEY | head -c 20

# If empty, set them
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
```

### Issue: Model not available

```bash
# Check available models in config
cat /mnt/github/workspace-hub/.drcode/droids.yml | grep "model:"

# Use correct droid name
droid --droid openai-feature exec "..."  # ✓ Correct
droid --droid gpt-4.1 exec "..."          # ✗ Wrong
```

## 📚 Learn More

### Documentation
- **Full Setup Guide:** `docs/modules/automation/FACTORY_AI_SETUP_CLAUDE_OPENAI.md`
- **Factory.ai Guide:** `docs/modules/automation/FACTORY_AI_GUIDE.md`
- **AI Orchestration:** `docs/modules/automation/AI_AGENT_ORCHESTRATION.md`

### Official Resources
- **Factory.ai Docs:** https://docs.factory.ai
- **Claude API:** https://docs.anthropic.com
- **OpenAI API:** https://platform.openai.com/docs

## 🎓 Next Steps

1. ✅ **Complete Installation**
   ```bash
   /mnt/github/workspace-hub/scripts/install_factory_ai.sh
   ```

2. ✅ **Set API Keys**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   export OPENAI_API_KEY="sk-..."
   ```

3. ✅ **Test Both Models**
   ```bash
   droid exec "test Claude"
   droid --droid openai-feature exec "test OpenAI"
   ```

4. ✅ **Start Development**
   ```bash
   cd your-repository
   droid exec "your first task"
   ```

## 💡 Pro Tips

1. **Cost Optimization:** Use GPT-3.5 for simple tasks, save expensive models for complex work
2. **Model Strengths:** Claude excels at code quality, OpenAI excels at web development
3. **Interactive Mode:** Use for exploratory work and complex multi-step tasks
4. **Batch Processing:** Chain simple tasks with GPT-3.5, review with Claude
5. **Documentation:** Always review and customize AI-generated code

---

**You're ready to use factory.ai with both Claude and OpenAI models! 🚀**

For more details, see the [full setup guide](FACTORY_AI_SETUP_CLAUDE_OPENAI.md).
