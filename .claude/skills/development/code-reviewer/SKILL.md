---
name: code-reviewer
description: Comprehensive code review toolkit for evaluating quality across multiple languages. Use for PR analysis, quality checking, and generating review reports. Based on alirezarezvani/claude-skills.
version: 1.0.0
category: development
last_updated: 2026-01-19
source: https://github.com/alirezarezvani/claude-skills
related_skills:
  - tdd-obra
  - systematic-debugging
  - subagent-driven
---

# Code Reviewer Skill

## Overview

This skill provides comprehensive code review capabilities across multiple programming languages including TypeScript, JavaScript, Python, Swift, and Kotlin. Focus areas: code quality, security, performance, and maintainability.

## Quick Start

1. **Identify scope** - Files or PR to review
2. **Run analysis** - Check code quality, security, performance
3. **Document findings** - Categorize by severity
4. **Provide recommendations** - Actionable improvements
5. **Generate report** - Structured review output

## When to Use

- Pull request reviews
- Pre-merge quality gates
- Code audit requirements
- Security assessments
- Performance optimization reviews
- Onboarding code familiarization

## Review Categories

### 1. Code Quality

| Aspect | Check For |
|--------|-----------|
| Clarity | Readable, self-documenting code |
| Naming | Descriptive, consistent conventions |
| Structure | Single responsibility, appropriate abstraction |
| DRY | No unnecessary duplication |
| Complexity | Cyclomatic complexity within limits |

### 2. Security

| Aspect | Check For |
|--------|-----------|
| Input validation | All user inputs validated |
| SQL injection | Parameterized queries |
| XSS | Output encoding |
| Auth/AuthZ | Proper authentication and authorization |
| Secrets | No hardcoded credentials |
| Dependencies | Updated, no known vulnerabilities |

### 3. Performance

| Aspect | Check For |
|--------|-----------|
| Algorithms | Appropriate time complexity |
| Memory | No leaks, efficient usage |
| Database | Optimized queries, proper indexing |
| Caching | Appropriate cache usage |
| Async | Non-blocking operations where needed |

### 4. Testing

| Aspect | Check For |
|--------|-----------|
| Coverage | Critical paths tested |
| Quality | Meaningful assertions |
| Isolation | Tests don't depend on each other |
| Edge cases | Boundary conditions covered |
| Mocking | Minimal, appropriate mocking |

## Review Process

### Step 1: Context Gathering

```markdown
## Review Context
- **PR/Files:** [identifier]
- **Author:** [name]
- **Purpose:** [feature/bugfix/refactor]
- **Related:** [issues/tickets]
```

### Step 2: High-Level Analysis

Scan for:
- Overall change scope
- Architectural impact
- Breaking changes
- New dependencies

### Step 3: Detailed Review

For each file:

```markdown
### [filename]

**Changes:** [summary]

**Findings:**
- [severity] [category]: [description]
  - Location: line X
  - Recommendation: [action]
```

### Step 4: Security Deep Dive

Special attention to:
- Authentication flows
- Data handling
- API endpoints
- Configuration files
- Environment variables

### Step 5: Test Verification

- Run existing tests
- Verify new test coverage
- Check test quality
- Identify missing tests

## Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| Critical | Security vulnerability, data loss risk | Block merge |
| High | Bugs, significant issues | Must fix |
| Medium | Code quality, maintainability | Should fix |
| Low | Style, minor improvements | Consider |
| Info | Suggestions, observations | Optional |

## Review Checklist

### General
- [ ] Code compiles/builds without errors
- [ ] No merge conflicts
- [ ] Branch is up to date with target
- [ ] Commit messages are clear

### Functionality
- [ ] Requirements are met
- [ ] Edge cases handled
- [ ] Error handling is appropriate
- [ ] No regression in existing functionality

### Code Quality
- [ ] Follows project coding standards
- [ ] No code smells or anti-patterns
- [ ] Appropriate comments (not excessive)
- [ ] No dead code or debug statements

### Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Output encoding where needed
- [ ] Proper error messages (no info leak)

### Testing
- [ ] New code has tests
- [ ] All tests pass
- [ ] Test coverage adequate
- [ ] Tests are meaningful

### Documentation
- [ ] README updated if needed
- [ ] API docs updated if applicable
- [ ] Breaking changes documented

## Common Anti-Patterns

### Code Smells

| Pattern | Problem | Solution |
|---------|---------|----------|
| God Object | Class does too much | Split responsibilities |
| Feature Envy | Method uses other class more | Move to appropriate class |
| Long Method | Hard to understand | Extract smaller methods |
| Magic Numbers | Unclear meaning | Use named constants |
| Deep Nesting | Hard to follow | Early returns, extraction |

### Security Issues

| Pattern | Problem | Solution |
|---------|---------|----------|
| SQL Concat | Injection risk | Parameterized queries |
| Eval Usage | Code injection | Safe alternatives |
| Weak Crypto | Breakable encryption | Strong algorithms |
| CORS * | Access control bypass | Specific origins |
| Console Secrets | Credential exposure | Remove before commit |

## Review Report Template

```markdown
# Code Review Report

## Summary
- **Reviewed:** [files/PR]
- **Date:** [date]
- **Reviewer:** [name]
- **Overall:** [APPROVE/REQUEST_CHANGES/COMMENT]

## Statistics
- Files reviewed: X
- Lines changed: +Y/-Z
- Critical issues: N
- High issues: N
- Medium issues: N

## Critical/High Findings

### [Finding Title]
- **Severity:** Critical/High
- **Category:** Security/Bug/Performance
- **Location:** file:line
- **Description:** [details]
- **Recommendation:** [action]
- **Code suggestion:**
  \`\`\`language
  // suggested fix
  \`\`\`

## Medium/Low Findings
[Grouped by category]

## Positive Observations
- [Good practices noticed]

## Recommendations
1. [Priority improvement]
2. [Secondary improvement]

## Test Coverage
- Current: X%
- Critical paths: Y%
- Recommendation: [action]
```

## Best Practices

### Do

1. Review in small batches (200-400 lines ideal)
2. Focus on logic, not style (use linters)
3. Ask questions rather than demand changes
4. Acknowledge good code
5. Provide specific, actionable feedback
6. Test the changes locally when possible

### Don't

1. Nitpick style issues
2. Rewrite author's code in comments
3. Leave vague feedback ("this is wrong")
4. Review when fatigued
5. Approve without understanding
6. Block for preferences, not issues

## Error Handling

| Situation | Action |
|-----------|--------|
| Too large PR | Request split into smaller PRs |
| Missing context | Ask author for explanation |
| Unclear requirements | Defer to requirements review |
| Disagreement | Escalate with evidence |

## Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Review turnaround | <24h | Time to first review |
| Defect detection | >80% | Issues caught before merge |
| False positive rate | <10% | Unnecessary comments |
| Review thoroughness | 100% | All critical areas covered |

## Technology-Specific Notes

### TypeScript/JavaScript
- Check for any/unknown abuse
- Verify type safety
- Review async/await handling
- Check for memory leaks in React

### Python
- PEP 8 compliance
- Type hints present
- Exception handling
- Virtual environment usage

### Go
- Error handling patterns
- Goroutine leaks
- Interface usage
- Package organization

## Related Skills

- [tdd-obra](../tdd-obra/SKILL.md) - Test-first development
- [systematic-debugging](../systematic-debugging/SKILL.md) - Debugging methodology
- [subagent-driven](../subagent-driven/SKILL.md) - Development with reviews

---

## Version History

- **1.0.0** (2026-01-19): Initial release adapted from alirezarezvani/claude-skills
