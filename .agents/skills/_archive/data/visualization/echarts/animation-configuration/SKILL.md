---
name: echarts-animation-configuration
description: 'Sub-skill of echarts: Animation Configuration (+2).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Animation Configuration (+2)

## Animation Configuration


```javascript
option = {
  animation: true,
  animationDuration: 1000,
  animationEasing: 'cubicOut',
  animationDelay: function (idx) {
    return idx * 50;
  }
};
```

## DataZoom (Zoom/Pan)


```javascript
option = {
  dataZoom: [
    {
      type: 'inside', // Mouse wheel zoom
      start: 0,
      end: 100
    },
    {
      type: 'slider', // Slider zoom

*See sub-skills for full details.*

## Brush Selection


```javascript
option = {
  brush: {
    toolbox: ['rect', 'polygon', 'lineX', 'lineY', 'keep', 'clear'],
    xAxisIndex: 0
  },
  // ... rest of option
};

myChart.on('brushSelected', function (params) {
  var brushComponent = params.batch[0];
  var selected = brushComponent.selected[0].dataIndex;
  console.log('Selected data indices:', selected);
});
```
