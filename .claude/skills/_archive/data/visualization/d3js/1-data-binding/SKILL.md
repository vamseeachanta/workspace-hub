---
name: d3js-1-data-binding
description: 'Sub-skill of d3js: 1. Data Binding (+3).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# 1. Data Binding (+3)

## 1. Data Binding

```javascript
// Select and bind data to elements
d3.select('#chart')
  .selectAll('circle')
  .data(dataset)
  .enter()
  .append('circle')
  .attr('cx', d => xScale(d.x))
  .attr('cy', d => yScale(d.y))
  .attr('r', d => d.radius)
  .style('fill', d => colorScale(d.category));
```


## 2. Scales and Axes

```javascript
// Create scales for positioning
const xScale = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.x)])
  .range([0, width]);

const yScale = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.y)])
  .range([height, 0]);

// Create axes
const xAxis = d3.axisBottom(xScale);
const yAxis = d3.axisLeft(yScale);

svg.append('g')
  .attr('transform', `translate(0, ${height})`)
  .call(xAxis);

svg.append('g')
  .call(yAxis);
```


## 3. Transitions and Animations

```javascript
// Smooth transitions
d3.selectAll('circle')
  .transition()
  .duration(1000)
  .attr('r', d => d.newRadius)
  .style('fill', 'steelblue');
```


## 4. Interactive Elements

```javascript
// Add interactivity
const tooltip = d3.select('body')
  .append('div')
  .attr('class', 'tooltip')
  .style('opacity', 0);

circles
  .on('mouseover', function(event, d) {
    tooltip.transition()
      .duration(200)
      .style('opacity', .9);
    tooltip.html(`Value: ${d.value}`)
      .style('left', (event.pageX + 10) + 'px')
      .style('top', (event.pageY - 28) + 'px');
  })
  .on('mouseout', function(d) {
    tooltip.transition()
      .duration(500)
      .style('opacity', 0);
  });
```
