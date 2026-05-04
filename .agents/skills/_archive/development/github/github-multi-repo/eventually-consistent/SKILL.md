---
name: github-multi-repo-eventually-consistent
description: 'Sub-skill of github-multi-repo: Eventually Consistent (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Eventually Consistent (+2)

## Eventually Consistent


```javascript
{
    "sync": {
        "strategy": "eventual",
        "max-lag": "5m",
        "retry": {
            "attempts": 3,
            "backoff": "exponential"
        }
    }
}
```

## Strongly Consistent


```javascript
{
    "sync": {
        "strategy": "strong",
        "consensus": "raft",
        "quorum": 0.51,
        "timeout": "30s"
    }
}
```

## Hybrid Approach


```javascript
{
    "sync": {
        "default": "eventual",
        "overrides": {
            "security-updates": "strong",
            "dependency-updates": "strong",
            "documentation": "eventual"
        }
    }
}
```
