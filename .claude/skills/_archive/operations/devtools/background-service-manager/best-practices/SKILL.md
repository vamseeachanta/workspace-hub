---
name: background-service-manager-best-practices
description: 'Sub-skill of background-service-manager: Best Practices.'
version: 2.0.0
category: operations
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Always use PID files** - Track running processes reliably
2. **Implement graceful shutdown** - Handle SIGTERM properly
3. **Log to files** - Use `/tmp/` or dedicated log directory
4. **Check before start** - Prevent duplicate instances
5. **Clean stale PIDs** - Remove orphaned PID files
6. **Add status monitoring** - Show resource usage
7. **Support restart** - Stop + start in one command
8. **Environment variables** - Configure via env, not hardcoded
