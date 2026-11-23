---
name: core-context-management-quick-reference
description: 'Sub-skill of core-context-management: Quick Reference.'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# Quick Reference

## Quick Reference


```
CLAUDE.md Limits:
- Global (~/.claude/CLAUDE.md): 2KB max
- Workspace CLAUDE.md: 4KB max
- Project CLAUDE.md: 8KB max
- CLAUDE.local.md: 2KB max
- Total Active: 16KB (~4K tokens)

Runtime Context:
- %ctx = (current_tokens / 200000) * 100
- Alert: >60% = archive older exchanges
- Critical: >80% = trim to essentials only
```

---
