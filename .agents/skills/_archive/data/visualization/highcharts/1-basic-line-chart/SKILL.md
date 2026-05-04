---
name: highcharts-1-basic-line-chart
description: 'Sub-skill of highcharts: 1. Basic Line Chart (+2).'
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
  <script src="https://code.highcharts.com/highcharts.js"></script>
</head>
<body>
  <div id="container" style="width: 100%; height: 400px;"></div>
  <script>
    Highcharts.chart('container', {
      title: {
        text: 'Monthly Sales'
      },
      subtitle: {
        text: 'Source: Sales Department'
      },
      xAxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
      },
      yAxis: {
        title: {
          text: 'Sales (units)'
        }
      },
      series: [{
        name: 'Product A',
        data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0]
      }],
      credits: {
        enabled: false
      }
    });
  </script>
</body>
</html>
```


## 2. Column Chart with Multiple Series

```javascript
Highcharts.chart('container', {
  chart: {
    type: 'column'
  },
  title: {
    text: 'Quarterly Revenue Comparison'
  },
  xAxis: {
    categories: ['Q1', 'Q2', 'Q3', 'Q4']
  },
  yAxis: {
    min: 0,
    title: {
      text: 'Revenue (thousands)'
    }
  },
  tooltip: {
    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
      '<td style="padding:0"><b>{point.y:.1f}</b></td></tr>',
    footerFormat: '</table>',
    shared: true,
    useHTML: true
  },
  plotOptions: {
    column: {
      pointPadding: 0.2,
      borderWidth: 0
    }
  },
  series: [{
    name: '2023',
    data: [49.9, 71.5, 106.4, 129.2]
  }, {
    name: '2024',
    data: [83.6, 78.8, 98.5, 93.4]
  }]
});
```


## 3. Pie Chart with Drilldown

```javascript
Highcharts.chart('container', {
  chart: {
    type: 'pie'
  },
  title: {
    text: 'Browser Market Share'
  },
  tooltip: {
    pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
  },
  accessibility: {
    point: {
      valueSuffix: '%'
    }
  },
  plotOptions: {
    pie: {
      allowPointSelect: true,
      cursor: 'pointer',
      dataLabels: {
        enabled: true,
        format: '<b>{point.name}</b>: {point.percentage:.1f} %'
      },
      showInLegend: true
    }
  },
  series: [{
    name: 'Share',
    colorByPoint: true,
    data: [{
      name: 'Chrome',
      y: 61.41,
      sliced: true,
      selected: true
    }, {
      name: 'Firefox',
      y: 11.84
    }, {
      name: 'Edge',
      y: 4.67
    }, {
      name: 'Safari',
      y: 4.18
    }, {
      name: 'Other',
      y: 17.9
    }]
  }]
});
```
