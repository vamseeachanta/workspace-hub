---
name: echarts-1-use-responsive-design
description: 'Sub-skill of echarts: 1. Use Responsive Design (+3).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# 1. Use Responsive Design (+3)

## 1. Use Responsive Design

```javascript
// Make chart responsive
window.addEventListener('resize', function() {
  myChart.resize();
});

// Or set explicit size
myChart.resize({
  width: 800,
  height: 600
});
```


## 2. Use Loading and Empty States

```javascript
// Show loading
myChart.showLoading();

// Fetch data
fetch('../data/data.json')
  .then(response => response.json())
  .then(data => {
    myChart.hideLoading();
    myChart.setOption(option);
  });

// Handle no data
if (data.length === 0) {
  myChart.setOption({
    title: {
      text: 'No Data Available',
      left: 'center',
      top: 'center'
    }
  });
}
```


## 3. Use Themes

```javascript
// Use built-in themes
var myChart = echarts.init(document.getElementById('main'), 'dark');

// Or custom theme
var customTheme = {
  color: ['#c23531', '#2f4554', '#61a0a8'],
  backgroundColor: '#f4f4f4'
};

var myChart = echarts.init(document.getElementById('main'), customTheme);
```


## 4. Optimize for Large Datasets

```javascript
option = {
  series: [{
    type: 'line',
    // Enable sampling for large datasets
    sampling: 'lttb',
    // Use progressive rendering
    progressive: 1000,
    progressiveThreshold: 3000,
    data: largeDataArray
  }]
};
```
