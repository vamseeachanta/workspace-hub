---
name: chartjs-custom-colors
description: 'Sub-skill of chartjs: Custom Colors (+2).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Custom Colors (+2)

## Custom Colors


```javascript
const colors = [
  'rgba(255, 99, 132, 0.7)',
  'rgba(54, 162, 235, 0.7)',
  'rgba(255, 206, 86, 0.7)',
  'rgba(75, 192, 192, 0.7)',
  'rgba(153, 102, 255, 0.7)'
];
```

## Custom Tooltips


```javascript
options: {
  plugins: {
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }

*See sub-skills for full details.*

## Custom Legends


```javascript
options: {
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        font: {
          size: 14
        },
        usePointStyle: true
      }
    }
  }
}
```
