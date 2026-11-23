---
name: github-sync-version-alignment-strategy
description: 'Sub-skill of github-sync: Version Alignment Strategy (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Version Alignment Strategy (+1)

## Version Alignment Strategy


```javascript
const syncStrategy = {
  nodeVersion: ">=20.0.0",  // Align to highest requirement
  dependencies: {
    "typescript": "^5.0.0",  // Use latest stable
    "jest": "^29.0.0"
  },
  engines: {
    aligned: true,
    strategy: "highest_common"
  }
};
```

## Documentation Sync Pattern


```javascript
const docSyncPattern = {
  sourceOfTruth: "primary-repo/CLAUDE.md",
  targets: [
    "secondary-repo/CLAUDE.md",
    "tertiary-repo/CLAUDE.md"
  ],
  customSections: {
    "secondary-repo": "Package-Specific Configuration",
    "tertiary-repo": "Local Customizations"
  }
};
```
