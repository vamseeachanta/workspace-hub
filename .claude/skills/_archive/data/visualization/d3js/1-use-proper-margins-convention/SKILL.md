---
name: d3js-1-use-proper-margins-convention
description: 'Sub-skill of d3js: 1. Use Proper Margins Convention (+3).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# 1. Use Proper Margins Convention (+3)

## 1. Use Proper Margins Convention

```javascript
const margin = { top: 20, right: 20, bottom: 30, left: 40 };
const width = 960 - margin.left - margin.right;
const height = 500 - margin.top - margin.bottom;

const svg = d3.select('body').append('svg')
  .attr('width', width + margin.left + margin.right)
  .attr('height', height + margin.top + margin.bottom)
  .append('g')
  .attr('transform', `translate(${margin.left},${margin.top})`);
```


## 2. Use Method Chaining

```javascript
// Good - readable chaining
svg.selectAll('circle')
  .data(data)
  .enter()
  .append('circle')
  .attr('cx', d => xScale(d.x))
  .attr('cy', d => yScale(d.y))
  .attr('r', 5);
```


## 3. Separate Data from Presentation

```javascript
// Load data separately
d3.json('../data/data.json').then(data => {
  visualize(data);
});

function visualize(data) {
  // Visualization logic here
}
```


## 4. Use Responsive Design

```javascript
// Make chart responsive
function resize() {
  const container = d3.select('#chart').node();
  const width = container.getBoundingClientRect().width;

  xScale.range([0, width]);
  svg.attr('width', width);
  // Update chart elements
}

window.addEventListener('resize', resize);
```
