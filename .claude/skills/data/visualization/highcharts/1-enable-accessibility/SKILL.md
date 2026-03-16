---
name: highcharts-1-enable-accessibility
description: 'Sub-skill of highcharts: 1. Enable Accessibility (+3).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# 1. Enable Accessibility (+3)

## 1. Enable Accessibility

```javascript
Highcharts.chart('container', {
  accessibility: {
    enabled: true,
    description: 'Chart showing sales trends over time',
    keyboardNavigation: {
      enabled: true
    }
  },
  // ... rest of config
});
```


## 2. Customize Tooltips

```javascript
tooltip: {
  formatter: function () {
    return '<b>' + this.series.name + '</b><br/>' +
           this.x + ': ' + this.y.toFixed(2);
  }
}
```


## 3. Use Responsive Options

```javascript
Highcharts.chart('container', {
  chart: {
    height: (9 / 16 * 100) + '%' // 16:9 ratio
  },
  responsive: {
    rules: [{
      condition: {
        maxWidth: 500
      },
      chartOptions: {
        legend: {
          align: 'center',
          verticalAlign: 'bottom',
          layout: 'horizontal'
        },
        yAxis: {
          labels: {
            align: 'left',
            x: 0,
            y: -5
          },
          title: {
            text: null
          }
        }
      }
    }]
  }
});
```


## 4. Export Functionality

```javascript
exporting: {
  enabled: true,
  buttons: {
    contextButton: {
      menuItems: [
        'downloadPNG',
        'downloadJPEG',
        'downloadPDF',
        'downloadSVG',
        'separator',
        'downloadCSV',
        'downloadXLS'
      ]
    }
  }
}
```
