---
name: echarts-example-1-loading-data-from-csv
description: 'Sub-skill of echarts: Example 1: Loading Data from CSV (+5).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Example 1: Loading Data from CSV (+5)

## Example 1: Loading Data from CSV


```javascript
// Fetch CSV data
fetch('../data/sales.csv')
  .then(response => response.text())
  .then(csvText => {
    // Parse CSV
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',');

    const categories = [];

*See sub-skills for full details.*

## Example 2: Multi-Axis Chart


```javascript
var option = {
  title: {
    text: 'Temperature and Precipitation'
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }

*See sub-skills for full details.*

## Example 3: Heatmap Calendar


```javascript
// Generate data for a year
function getVirtulData(year) {
  const date = +echarts.time.parse(year + '-01-01');
  const end = +echarts.time.parse(+year + 1 + '-01-01');
  const dayTime = 3600 * 24 * 1000;
  const data = [];
  for (let time = date; time < end; time += dayTime) {
    data.push([
      echarts.time.format(time, '{yyyy}-{MM}-{dd}', false),

*See sub-skills for full details.*

## Example 4: Gauge Chart


```javascript
var option = {
  title: {
    text: 'Performance Score'
  },
  tooltip: {
    formatter: '{a} <br/>{b} : {c}%'
  },
  series: [
    {

*See sub-skills for full details.*

## Example 5: Geographic Map (China)


```javascript
// Load map data
fetch('https://cdn.jsdelivr.net/npm/echarts/map/json/china.json')
  .then(response => response.json())
  .then(chinaJson => {
    echarts.registerMap('china', chinaJson);

    var option = {
      title: {
        text: 'Sales by Province',

*See sub-skills for full details.*

## Example 6: Dynamic Real-Time Data


```javascript
var data = [];
var now = new Date();

function randomData() {
  now = new Date(+now + 1000);
  return {
    name: now.toString(),
    value: [
      [now.getFullYear(), now.getMonth() + 1, now.getDate()].join('/') + ' ' +

*See sub-skills for full details.*
