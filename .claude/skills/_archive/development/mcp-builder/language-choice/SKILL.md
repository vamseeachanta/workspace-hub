---
name: mcp-builder-language-choice
description: 'Sub-skill of mcp-builder: Language Choice (+4).'
version: 1.2.0
category: development
type: reference
scripts_exempt: true
---

# Language Choice (+4)

## Language Choice


**TypeScript preferred** for:
- High-quality SDK support
- Good compatibility
- Strong typing

## Transport Selection


- **Streamable HTTP**: Remote servers
- **stdio**: Local servers

## Tool Naming


Use consistent, action-oriented prefixes:
```
github_create_issue
github_list_repos
slack_send_message
slack_list_channels
```

## Error Messages


Provide actionable messages with specific next steps:
```typescript
throw new Error(
  `Failed to fetch repository: ${error.message}. ` +
  `Check that the repository exists and you have access.`
);
```

## Tool Annotations


```typescript
{
  name: "delete_file",
  description: "Permanently delete a file",
  inputSchema: { /* ... */ },
  annotations: {
    destructiveHint: true,
    readOnlyHint: false,
    confirmationHint: "Are you sure you want to delete this file?"
  }
}
```
