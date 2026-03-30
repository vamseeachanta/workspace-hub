---
name: echarts-typescript-support
description: 'Sub-skill of echarts: TypeScript Support.'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# TypeScript Support

## TypeScript Support


```typescript
import * as echarts from 'echarts';

type EChartsOption = echarts.EChartsOption;

const option: EChartsOption = {
  title: {
    text: 'TypeScript Example'
  },
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [120, 200, 150, 80, 70, 110, 130],
      type: 'line'
    }
  ]
};

const chartDom = document.getElementById('main')!;
const myChart = echarts.init(chartDom);
myChart.setOption(option);
```
