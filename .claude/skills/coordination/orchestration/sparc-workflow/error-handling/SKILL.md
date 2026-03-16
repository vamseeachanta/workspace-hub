---
name: sparc-workflow-error-handling
description: 'Sub-skill of sparc-workflow: Error Handling.'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


\`\`\`
TRY:
    [Main logic]
CATCH ValidationError:
    [Handle validation]
CATCH ProcessingError:
    [Handle processing]
FINALLY:
    [Cleanup]
\`\`\`
