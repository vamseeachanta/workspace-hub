---
name: git-advanced-9-monorepo-patterns
description: 'Sub-skill of git-advanced: 9. Monorepo Patterns.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 9. Monorepo Patterns

## 9. Monorepo Patterns


**Sparse Checkout:**
```bash
# Enable sparse checkout
git sparse-checkout init

# Set patterns
git sparse-checkout set packages/app packages/shared

# Add more patterns
git sparse-checkout add docs

# Disable sparse checkout
git sparse-checkout disable
```

**Working with Monorepos:**
```bash
# Clone specific directory only
git clone --filter=blob:none --sparse https://github.com/user/monorepo
cd monorepo
git sparse-checkout set packages/my-package

# Shallow clone for faster checkout
git clone --depth 1 --filter=blob:none --sparse https://github.com/user/monorepo

# Partial clone (fetch objects on demand)
git clone --filter=blob:none https://github.com/user/monorepo
```

**Monorepo Commit Strategy:**
```bash
# Commit message with scope
git commit -m "feat(package-name): add feature X"

# Using conventional commits
feat(api): add new endpoint
fix(web): resolve routing issue
chore(deps): update dependencies
docs(shared): improve API documentation
```
