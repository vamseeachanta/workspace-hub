---
name: echarts-event-handling
description: 'Sub-skill of echarts: Event Handling.'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Event Handling

## Event Handling


```javascript
// Click event
myChart.on('click', function (params) {
  console.log('Clicked:', params);
  alert('You clicked on ' + params.name);
});

// Hover event
myChart.on('mouseover', function (params) {
  console.log('Hovered:', params);
});

// Custom events
myChart.dispatchAction({
  type: 'highlight',
  seriesIndex: 0,
  dataIndex: 1
});
```
