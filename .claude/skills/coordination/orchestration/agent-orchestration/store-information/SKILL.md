---
name: agent-orchestration-store-information
description: 'Sub-skill of agent-orchestration: Store Information (+2).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Store Information (+2)

## Store Information


```javascript
    action: "store",
    key: "project-context",
    value: JSON.stringify(projectData),
    namespace: "project-alpha"
})
```

## Retrieve Information


```javascript
    action: "retrieve",
    key: "project-context",
    namespace: "project-alpha"
})
```

## Search Memory


```javascript
    pattern: "api-*",
    namespace: "project-alpha",
    limit: 10
})
```
