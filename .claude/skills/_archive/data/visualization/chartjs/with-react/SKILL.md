---
name: chartjs-with-react
description: 'Sub-skill of chartjs: With React (+1).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# With React (+1)

## With React

```javascript
import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

function ChartComponent({ data }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: data,
      options: { responsive: true }
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data]);

  return <canvas ref={chartRef} />;
}
```


## With Vue

```vue
<template>
  <canvas ref="chartCanvas"></canvas>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  props: ['chartData'],
  mounted() {
    this.renderChart();
  },
  methods: {
    renderChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: this.chartData,
        options: { responsive: true }
      });
    }
  }
};
</script>
```
