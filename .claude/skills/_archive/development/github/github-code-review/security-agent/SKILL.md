---
name: github-code-review-security-agent
description: 'Sub-skill of github-code-review: Security Agent (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Security Agent (+3)

## Security Agent


| Check | Description |
|-------|-------------|
| SQL injection | Detect SQL injection vulnerabilities |
| XSS | Cross-site scripting attack vectors |
| Authentication | Auth bypasses and flaws |
| Cryptographic | Weak crypto implementations |
| Secrets | Exposed credentials or API keys |
| CORS | Misconfiguration issues |

## Performance Agent


| Metric | Description |
|--------|-------------|
| Algorithm complexity | Big-O analysis |
| Query efficiency | N+1 queries, slow queries |
| Memory patterns | Allocation and leaks |
| Cache utilization | Caching opportunities |
| Bundle size | Impact on bundle size |

## Style Agent


| Check | Description |
|-------|-------------|
| Code formatting | Consistent formatting |
| Naming conventions | Variable/function naming |
| Documentation | Comment quality |
| Test coverage | Missing tests |
| Error handling | Proper error patterns |

## Architecture Agent


| Pattern | Description |
|---------|-------------|
| SOLID principles | Single responsibility, etc. |
| DRY violations | Code duplication |
| Coupling metrics | Component dependencies |
| Layer violations | Architecture boundaries |
| Circular dependencies | Dependency cycles |
