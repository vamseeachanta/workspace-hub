---
name: code-reviewer-1-code-quality
description: 'Sub-skill of code-reviewer: 1. Code Quality (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Code Quality (+3)

## 1. Code Quality


| Aspect | Check For |
|--------|-----------|
| Clarity | Readable, self-documenting code |
| Naming | Descriptive, consistent conventions |
| Structure | Single responsibility, appropriate abstraction |
| DRY | No unnecessary duplication |
| Complexity | Cyclomatic complexity within limits |

## 2. Security


| Aspect | Check For |
|--------|-----------|
| Input validation | All user inputs validated |
| SQL injection | Parameterized queries |
| XSS | Output encoding |
| Auth/AuthZ | Proper authentication and authorization |
| Secrets | No hardcoded credentials |
| Dependencies | Updated, no known vulnerabilities |

## 3. Performance


| Aspect | Check For |
|--------|-----------|
| Algorithms | Appropriate time complexity |
| Memory | No leaks, efficient usage |
| Database | Optimized queries, proper indexing |
| Caching | Appropriate cache usage |
| Async | Non-blocking operations where needed |

## 4. Testing


| Aspect | Check For |
|--------|-----------|
| Coverage | Critical paths tested |
| Quality | Meaningful assertions |
| Isolation | Tests don't depend on each other |
| Edge cases | Boundary conditions covered |
| Mocking | Minimal, appropriate mocking |
