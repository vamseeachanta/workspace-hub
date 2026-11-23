---
name: echarts-1-basic-line-chart
description: 'Sub-skill of echarts: 1. Basic Line Chart (+2).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# 1. Basic Line Chart (+2)

## 1. Basic Line Chart

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
</head>
<body>
  <div id="main" style="width: 600px; height: 400px;"></div>
  <script>
    var myChart = echarts.init(document.getElementById('main'));

    var option = {
      title: {
        text: 'Monthly Sales'
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['Sales']
      },
      xAxis: {
        type: 'category',
        data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        name: 'Sales',
        type: 'line',
        data: [120, 200, 150, 80, 70, 110],
        smooth: true
      }]
    };

    myChart.setOption(option);
  </script>
</body>
</html>
```


## 2. Bar Chart with Multiple Series

```javascript
var option = {
  title: {
    text: 'Quarterly Revenue Comparison'
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {
    data: ['2023', '2024']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['Q1', 'Q2', 'Q3', 'Q4']
  },
  yAxis: {
    type: 'value',
    name: 'Revenue (k$)'
  },
  series: [
    {
      name: '2023',
      type: 'bar',
      data: [120, 200, 150, 80],
      itemStyle: {
        color: '#5470C6'
      }
    },
    {
      name: '2024',
      type: 'bar',
      data: [180, 250, 200, 120],
      itemStyle: {
        color: '#91CC75'
      }
    }
  ]
};

myChart.setOption(option);
```


## 3. Pie Chart with Rich Formatting

```javascript
var option = {
  title: {
    text: 'Traffic Sources',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: 'Access From',
      type: 'pie',
      radius: '50%',
      data: [
        { value: 1048, name: 'Search Engine' },
        { value: 735, name: 'Direct' },
        { value: 580, name: 'Email' },
        { value: 484, name: 'Affiliate' },
        { value: 300, name: 'Video Ads' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
};

myChart.setOption(option);
```
