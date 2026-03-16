---
name: highcharts-cdn
description: 'Sub-skill of highcharts: CDN (+1).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# CDN (+1)

## CDN


```html
<!-- Basic Highcharts -->
<script src="https://code.highcharts.com/highcharts.js"></script>

<!-- Stock Charts -->
<script src="https://code.highcharts.com/stock/highstock.js"></script>

<!-- Maps -->
<script src="https://code.highcharts.com/maps/highmaps.js"></script>


*See sub-skills for full details.*

## NPM


```bash
npm install highcharts
```

```javascript
import Highcharts from 'highcharts';
import HighchartsStock from 'highcharts/modules/stock';
import HighchartsMap from 'highcharts/modules/map';

HighchartsStock(Highcharts);
HighchartsMap(Highcharts);
```
