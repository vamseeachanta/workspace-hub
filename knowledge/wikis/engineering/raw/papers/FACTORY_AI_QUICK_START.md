# Factory.ai Quick Start Guide

> Get started with AI-powered Droids in 5 minutes

## 🚀 Quick Start

### 1. Verify Installation

```bash
droid --version
# Output: 0.18.0
```

### 2. Navigate to Any Repository

```bash
cd /mnt/github/workspace-hub/your-repository
```

### 3. Start Interactive Mode

```bash
droid
```

On first run, a browser will open for authentication. Sign in and return to terminal.

### 4. Give Your First Task

```
You: Add docstrings to all Python functions
```

The Droid will analyze your code and add comprehensive docstrings.

### 5. Review Changes

```bash
git diff
```

## 💡 Common Tasks

### Code Tasks

```bash
# Refactor code
droid exec "refactor user_service.py to use dependency injection"

# Add features
droid exec "add pagination to the API endpoints"

# Fix bugs
droid exec "fix the race condition in payment_processor.py"
```

### Testing Tasks

```bash
# Write tests
droid exec "write pytest tests for all functions in utils.py"

# Increase coverage
droid exec "add tests to reach 90% code coverage"
```

### Documentation Tasks

```bash
# Generate docs
droid exec "create README with installation and usage instructions"

# API documentation
droid exec "generate OpenAPI spec from Flask routes"
```

## 🎯 Best Practices

1. **Be Specific:** "Fix authentication bug in login.py line 45" > "fix bugs"
2. **Review Changes:** Always review droid's changes before committing
3. **Use Branches:** Work on feature branches for easy rollback
4. **Start Small:** Begin with simple tasks to understand capabilities

## 📚 Learn More

- **Full Guide:** `/docs/FACTORY_AI_GUIDE.md`
- **Official Docs:** https://docs.factory.ai
- **AI Ecosystem:** `/docs/AI_ECOSYSTEM.md`

## 🆘 Need Help?

```bash
droid --help           # Show help
droid exec --help      # Show exec options
```

---

**You're ready to automate development with factory.ai! 🚀**
