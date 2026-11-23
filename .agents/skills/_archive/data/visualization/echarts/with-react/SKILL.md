---
name: echarts-with-react
description: 'Sub-skill of echarts: With React (+1).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# With React (+1)

## With React

```jsx
import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

function EChartsComponent({ option }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    chartInstance.current.setOption(option);

    const handleResize = () => chartInstance.current.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chartInstance.current?.dispose();
    };
  }, [option]);

  return <div ref={chartRef} style={{ width: '100%', height: '400px' }} />;
}
```


## With Vue

```vue
<template>
  <div ref="chart" style="width: 600px; height: 400px;"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  props: ['option'],
  mounted() {
    this.chart = echarts.init(this.$refs.chart);
    this.chart.setOption(this.option);

    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
    this.chart.dispose();
  },
  methods: {
    handleResize() {
      this.chart.resize();
    }
  },
  watch: {
    option: {
      deep: true,
      handler(newOption) {
        this.chart.setOption(newOption);
      }
    }
  }
};
</script>
```
