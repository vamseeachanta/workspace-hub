# Development Module

Development tools, hooks, and utilities for improving the development workflow.

## 📁 Contents

### Git Hooks
- `hooks/baseline-auto-fix.sh` - Automatic code fixes
- `hooks/baseline-quick-check.sh` - Quick validation checks
- `hooks/baseline-validation.sh` - Full validation suite

### Sample Files
- `sample-tasks.md` - Sample task definitions

## 🪝 Git Hooks

### Pre-commit Hook
```bash
./hooks/baseline-quick-check.sh
```

### Pre-push Hook
```bash
./hooks/baseline-validation.sh
```

### Post-merge Hook
```bash
./hooks/baseline-auto-fix.sh
```

## 🚀 Setup Hooks

### Install Hooks
```bash
# Link hooks to .git/hooks
ln -s ../../modules/development/hooks/* .git/hooks/
```

### Configure Hooks
Edit hook scripts to match your requirements:
- Code formatting rules
- Testing requirements
- Validation criteria

## 📋 Features

- **Automated Validation**: Check code before commits
- **Quick Checks**: Fast validation for rapid feedback
- **Auto-fixing**: Automatically fix common issues
- **Customizable**: Adapt hooks to your workflow

## 🔧 Hook Configuration

Each hook can be configured with:
- File patterns to check
- Validation rules
- Auto-fix behaviors
- Skip conditions

## 📝 Best Practices

- Keep hooks fast for better developer experience
- Provide clear error messages
- Allow bypassing when necessary
- Document hook behaviors
- Test hooks thoroughly