---
name: highcharts-typescript-support
description: 'Sub-skill of highcharts: TypeScript Support.'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# TypeScript Support

## TypeScript Support


```typescript
import * as Highcharts from 'highcharts';

const options: Highcharts.Options = {
  title: {
    text: 'TypeScript Example'
  },
  series: [{
    type: 'line',
    data: [1, 2, 3, 4, 5]
  }]
};

Highcharts.chart('container', options);
```
