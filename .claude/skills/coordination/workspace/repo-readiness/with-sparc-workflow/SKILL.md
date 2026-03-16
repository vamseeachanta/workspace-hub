---
name: repo-readiness-with-sparc-workflow
description: 'Sub-skill of repo-readiness: With SPARC Workflow (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# With SPARC Workflow (+3)

## With SPARC Workflow


Readiness check before each SPARC phase:

```bash
# Before Specification
/repo-readiness → Analyze context → /create-spec

# Before Architecture
/repo-readiness → Verify structure → /sparc-architecture

# Before Implementation
/repo-readiness → Check environment → /execute-tasks
```

## With Compliance Check


Combined health validation:

```bash
# Readiness + compliance
/repo-readiness && /compliance-check

# Report both
./scripts/health-check.sh --full
```

## With Agent Orchestration


Provide context to agents:

```javascript
// Agent receives readiness report
{
  "task": "implement-feature-X",
  "repository": "digitalmodel",
  "readiness": {
    "status": "ready",
    "score": 95,

*See sub-skills for full details.*

## With Repo Sync


Ensure readiness before bulk operations:

```bash
# Check readiness before sync
./scripts/repository_sync sync all --check-readiness
```
