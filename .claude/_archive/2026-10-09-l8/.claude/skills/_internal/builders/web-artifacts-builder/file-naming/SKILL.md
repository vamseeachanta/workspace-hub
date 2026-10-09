---
name: web-artifacts-builder-file-naming
description: 'Sub-skill of web-artifacts-builder: File Naming (+2).'
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# File Naming (+2)

## File Naming


```
project-name_v1.0.html
dashboard_2024-01-15.html
calculator-tool.html
```

## Embedding Data


```javascript
// Embed JSON data directly
const DATA = {
    items: [...],
    config: {...}
};

// Or base64 encode binary data
const imageData = 'data:image/png;base64,iVBORw0KGgo...';
```

## Export Functionality


```javascript
function downloadData() {
    const data = JSON.stringify(state, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'export.json';
    a.click();
    URL.revokeObjectURL(url);
}
```
