---
name: chartjs-cdn-quick-start
description: 'Sub-skill of chartjs: CDN (Quick Start) (+2).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# CDN (Quick Start) (+2)

## CDN (Quick Start)


```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

## NPM


```bash
npm install chart.js
```

```javascript
import Chart from 'chart.js/auto';
```

## ES Modules


```html
<script type="module">
  import Chart from 'https://cdn.jsdelivr.net/npm/chart.js@4/+esm';

  const ctx = document.getElementById('myChart');
  new Chart(ctx, {...});
</script>
```
