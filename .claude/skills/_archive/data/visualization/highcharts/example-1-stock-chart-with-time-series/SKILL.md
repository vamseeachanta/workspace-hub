---
name: highcharts-example-1-stock-chart-with-time-series
description: 'Sub-skill of highcharts: Example 1: Stock Chart with Time Series (+5).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Example 1: Stock Chart with Time Series (+5)

## Example 1: Stock Chart with Time Series


```html
<script src="https://code.highcharts.com/stock/highstock.js"></script>
<div id="container"></div>

<script>
// Load stock data from CSV
fetch('../data/stock_prices.csv')
  .then(response => response.text())
  .then(csvText => {
    const lines = csvText.split('\n');

*See sub-skills for full details.*

## Example 2: Combination Chart (Column + Line)


```javascript
Highcharts.chart('container', {
  title: {
    text: 'Sales vs Profit Margin'
  },
  xAxis: {
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  },
  yAxis: [{
    title: {

*See sub-skills for full details.*

## Example 3: Heatmap


```javascript
Highcharts.chart('container', {
  chart: {
    type: 'heatmap'
  },
  title: {
    text: 'Sales per employee per weekday'
  },
  xAxis: {
    categories: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

*See sub-skills for full details.*

## Example 4: Gantt Chart


```html
<script src="https://code.highcharts.com/gantt/highcharts-gantt.js"></script>
<div id="container"></div>

<script>
Highcharts.ganttChart('container', {
  title: {
    text: 'Project Timeline'
  },
  xAxis: {

*See sub-skills for full details.*

## Example 5: 3D Chart


```html
<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="https://code.highcharts.com/highcharts-3d.js"></script>
<div id="container"></div>

<script>
Highcharts.chart('container', {
  chart: {
    type: 'column',
    options3d: {

*See sub-skills for full details.*

## Example 6: Live Updating Chart


```javascript
Highcharts.chart('container', {
  chart: {
    type: 'spline',
    animation: Highcharts.svg,
    marginRight: 10,
    events: {
      load: function () {
        var series = this.series[0];
        setInterval(function () {

*See sub-skills for full details.*
