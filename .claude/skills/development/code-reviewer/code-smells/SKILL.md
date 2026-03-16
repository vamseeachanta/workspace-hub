---
name: code-reviewer-code-smells
description: 'Sub-skill of code-reviewer: Code Smells (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Code Smells (+1)

## Code Smells


| Pattern | Problem | Solution |
|---------|---------|----------|
| God Object | Class does too much | Split responsibilities |
| Feature Envy | Method uses other class more | Move to appropriate class |
| Long Method | Hard to understand | Extract smaller methods |
| Magic Numbers | Unclear meaning | Use named constants |
| Deep Nesting | Hard to follow | Early returns, extraction |

## Security Issues


| Pattern | Problem | Solution |
|---------|---------|----------|
| SQL Concat | Injection risk | Parameterized queries |
| Eval Usage | Code injection | Safe alternatives |
| Weak Crypto | Breakable encryption | Strong algorithms |
| CORS * | Access control bypass | Specific origins |
| Console Secrets | Credential exposure | Remove before commit |
