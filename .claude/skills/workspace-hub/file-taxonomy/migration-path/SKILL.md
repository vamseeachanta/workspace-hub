---
name: file-taxonomy-migration-path
description: 'Sub-skill of file-taxonomy: Migration Path.'
version: 1.6.0
category: workspace
type: reference
scripts_exempt: true
---

# Migration Path

## Migration Path


```bash
# If MODULE_INDEX.md or module-manifest.yaml exist at root:
git mv MODULE_INDEX.md specs/modules/INDEX.md        # or specs/index.md
git mv module-manifest.yaml specs/modules/manifest.yaml
# Update any references in README.md
```

---
