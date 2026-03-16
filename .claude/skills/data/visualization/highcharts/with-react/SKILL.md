---
name: highcharts-with-react
description: 'Sub-skill of highcharts: With React (+1).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# With React (+1)

## With React

```jsx
import { useEffect, useRef } from 'react';
import Highcharts from 'highcharts';

function HighchartsComponent({ options }) {
  const chartRef = useRef(null);

  useEffect(() => {
    const chart = Highcharts.chart(chartRef.current, options);

    return () => {
      chart.destroy();
    };
  }, [options]);

  return <div ref={chartRef} />;
}
```


## With Vue

```vue
<template>
  <div ref="chartContainer"></div>
</template>

<script>
import Highcharts from 'highcharts';

export default {
  props: ['options'],
  mounted() {
    this.chart = Highcharts.chart(this.$refs.chartContainer, this.options);
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy();
    }
  },
  watch: {
    options: {
      deep: true,
      handler(newOptions) {
        this.chart.update(newOptions);
      }
    }
  }
};
</script>
```
