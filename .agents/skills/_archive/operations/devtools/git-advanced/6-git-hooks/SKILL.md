---
name: git-advanced-6-git-hooks
description: 'Sub-skill of git-advanced: 6. Git Hooks.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 6. Git Hooks

## 6. Git Hooks


**Available Hooks:**
```
client-side:
  pre-commit      # Before commit message prompt
  prepare-commit-msg  # Edit default message
  commit-msg      # Validate commit message
  post-commit     # After commit completes
  pre-push        # Before push

server-side:
  pre-receive     # Before accepting push
  update          # Per-branch check
  post-receive    # After push completes
```

**Pre-commit Hook Example:**
```bash
#!/bin/bash
# .git/hooks/pre-commit
# ABOUTME: Pre-commit hook for code quality
# ABOUTME: Runs linting and tests before commit

set -e

echo "Running pre-commit checks..."

# Check for debug statements
if git diff --cached --name-only | xargs grep -l 'console.log\|debugger\|binding.pry' 2>/dev/null; then
    echo "ERROR: Debug statements found. Remove before committing."
    exit 1
fi

# Run linter
if [ -f "package.json" ] && grep -q '"lint"' package.json; then
    echo "Running linter..."
    npm run lint --quiet || exit 1
fi

# Run tests
if [ -f "package.json" ] && grep -q '"test"' package.json; then
    echo "Running tests..."
    npm test --quiet || exit 1
fi

echo "Pre-commit checks passed!"
```

**Commit-msg Hook Example:**
```bash
#!/bin/bash
# .git/hooks/commit-msg
# ABOUTME: Validates commit message format
# ABOUTME: Enforces conventional commits

COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Conventional commit pattern
PATTERN="^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: .{1,50}"

if ! echo "$COMMIT_MSG" | grep -qE "$PATTERN"; then
    echo "ERROR: Invalid commit message format."
    echo ""
    echo "Expected format: <type>(<scope>): <subject>"
    echo "Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert"
    echo ""
    echo "Examples:"
    echo "  feat(auth): add login functionality"
    echo "  fix(api): handle null response"
    echo "  docs: update README"
    exit 1
fi
```

**Pre-push Hook Example:**
```bash
#!/bin/bash
# .git/hooks/pre-push
# ABOUTME: Pre-push hook for safety checks
# ABOUTME: Prevents pushing to protected branches

BRANCH=$(git rev-parse --abbrev-ref HEAD)
PROTECTED_BRANCHES="^(main|master|production)$"

if echo "$BRANCH" | grep -qE "$PROTECTED_BRANCHES"; then
    echo "ERROR: Direct push to $BRANCH is not allowed."
    echo "Please create a pull request instead."
    exit 1
fi

# Run full test suite before push
echo "Running tests before push..."
npm test || exit 1

echo "Pre-push checks passed!"
```

**Using pre-commit Framework:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8

  - repo: local
    hooks:
      - id: run-tests
        name: Run tests
        entry: npm test
        language: system
        pass_filenames: false
        always_run: true
```

**Install pre-commit hooks:**
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Install commit-msg hook
pre-commit install --hook-type commit-msg

# Run manually
pre-commit run --all-files
```
