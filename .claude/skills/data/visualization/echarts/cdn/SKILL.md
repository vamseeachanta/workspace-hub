---
name: echarts-cdn
description: 'Sub-skill of echarts: CDN (+1).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# CDN (+1)

## CDN


```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
```

## NPM


```bash
npm install echarts
```

```javascript
import * as echarts from 'echarts';

// Or import specific modules
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { GridComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([LineChart, GridComponent, CanvasRenderer]);
```
