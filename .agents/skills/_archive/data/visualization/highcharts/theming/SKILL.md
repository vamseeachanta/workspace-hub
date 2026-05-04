---
name: highcharts-theming
description: 'Sub-skill of highcharts: Theming.'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Theming

## Theming


```javascript
// Apply custom theme
Highcharts.setOptions({
  colors: ['#058DC7', '#50B432', '#ED561B', '#DDDF00'],
  chart: {
    backgroundColor: '#f4f4f4',
    style: {
      fontFamily: 'Arial, sans-serif'
    }
  },
  title: {
    style: {
      color: '#000',
      font: 'bold 16px Arial'
    }
  }
});
```
