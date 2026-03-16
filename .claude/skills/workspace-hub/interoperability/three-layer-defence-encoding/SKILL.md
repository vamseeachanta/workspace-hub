---
name: interoperability-three-layer-defence-encoding
description: 'Sub-skill of interoperability: Three-Layer Defence (encoding).'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Three-Layer Defence (encoding)

## Three-Layer Defence (encoding)


```
Layer 1: .gitattributes  — git normalises encoding on checkout (strongest)
Layer 2: pre-commit hook — blocks commits with bad-encoding files
Layer 3: post-merge hook — warns after pull if bad files arrived
```

`.gitattributes` rules (already in repo):
```
*.md   text eol=lf working-tree-encoding=UTF-8
*.yaml text eol=lf working-tree-encoding=UTF-8
*.yml  text eol=lf working-tree-encoding=UTF-8
*.json text eol=lf working-tree-encoding=UTF-8
```

`working-tree-encoding=UTF-8` tells git to re-encode to UTF-8 on checkout
even if the file was committed as UTF-16. This is the strongest layer.
