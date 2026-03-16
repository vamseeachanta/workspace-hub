---
name: chartjs-1-use-responsive-containers
description: 'Sub-skill of chartjs: 1. Use Responsive Containers (+3).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# 1. Use Responsive Containers (+3)

## 1. Use Responsive Containers

```html
<div style="position: relative; height: 400px; width: 100%;">
  <canvas id="myChart"></canvas>
</div>
```

```javascript
options: {
  responsive: true,
  maintainAspectRatio: false
}
```


## 2. Destroy Charts Before Recreating

```javascript
let myChart;

function createChart(data) {
  // Destroy existing chart
  if (myChart) {
    myChart.destroy();
  }

  const ctx = document.getElementById('myChart').getContext('2d');
  myChart = new Chart(ctx, {
    type: 'line',
    data: data
  });
}
```


## 3. Use Plugins for Extended Functionality

```javascript
// Example: Chart.js Data Labels Plugin
import ChartDataLabels from 'chartjs-plugin-datalabels';

const chart = new Chart(ctx, {
  plugins: [ChartDataLabels],
  data: {...},
  options: {
    plugins: {
      datalabels: {
        color: '#fff',
        display: true
      }
    }
  }
});
```


## 4. Optimize for Performance

```javascript
options: {
  // Disable animations for large datasets
  animation: {
    duration: 0
  },
  // Use decimation for large datasets
  parsing: false,
  normalized: true
}
```
