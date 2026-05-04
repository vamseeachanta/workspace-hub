---
name: chartjs-example-1-multi-dataset-line-chart
description: 'Sub-skill of chartjs: Example 1: Multi-Dataset Line Chart (+5).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Example 1: Multi-Dataset Line Chart (+5)

## Example 1: Multi-Dataset Line Chart


```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    .chart-container {
      position: relative;
      height: 400px;
      width: 80%;

*See sub-skills for full details.*

## Example 2: Stacked Bar Chart


```javascript
const ctx = document.getElementById('stackedBar').getContext('2d');
const stackedChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    datasets: [
      {
        label: 'Revenue',
        data: [100, 120, 115, 134],

*See sub-skills for full details.*

## Example 3: Radar Chart


```javascript
const ctx = document.getElementById('radarChart').getContext('2d');
const radarChart = new Chart(ctx, {
  type: 'radar',
  data: {
    labels: ['Speed', 'Reliability', 'Comfort', 'Safety', 'Efficiency'],
    datasets: [
      {
        label: 'Vehicle A',
        data: [85, 90, 70, 95, 80],

*See sub-skills for full details.*

## Example 4: Loading Data from CSV


```javascript
// Using Fetch API to load CSV
fetch('../data/sales.csv')
  .then(response => response.text())
  .then(csvText => {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',');

    const labels = [];
    const data = [];

*See sub-skills for full details.*

## Example 5: Real-Time Updating Chart


```javascript
const ctx = document.getElementById('realtimeChart').getContext('2d');
const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [{
      label: 'Real-time Data',
      data: [],
      borderColor: 'rgb(75, 192, 192)',

*See sub-skills for full details.*

## Example 6: Mixed Chart Types


```javascript
const ctx = document.getElementById('mixedChart').getContext('2d');
const mixedChart = new Chart(ctx, {
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [
      {
        type: 'bar',
        label: 'Sales',
        data: [50, 60, 70, 80, 90],

*See sub-skills for full details.*
