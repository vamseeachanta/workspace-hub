# Chart Visualization Skills

> Claude skills for creating interactive data visualizations with top chart libraries

## Overview

This directory contains Claude skills for the most popular and effective chart libraries in 2026. Each skill provides comprehensive guidance, examples, and best practices for creating interactive visualizations.

## Available Skills

### 1. **D3.js** - Maximum Customization
- **Skill**: [d3js](d3js/SKILL.md)
- **Best For**: Custom visualizations, complex interactions, unique designs
- **Learning Curve**: Steep
- **Flexibility**: ⭐⭐⭐⭐⭐ (Maximum)
- **Speed**: ⭐⭐ (Slow to develop)

**Use when:**
- Complete control over every visual element needed
- Building bespoke, one-of-a-kind visualizations
- Complex data-driven animations required
- Team has strong JavaScript expertise

### 2. **Plotly** - Scientific & Analytical
- **Skill**: [plotly](plotly/SKILL.md)
- **Best For**: Scientific charts, 3D plots, statistical analysis, dashboards
- **Learning Curve**: Moderate
- **Features**: ⭐⭐⭐⭐⭐ (40+ chart types)
- **Python Integration**: ⭐⭐⭐⭐⭐ (Excellent)

**Use when:**
- Working with scientific or analytical data
- Need 3D visualizations or statistical charts
- Using Python/R for data processing
- Building interactive dashboards (Plotly Dash)
- Handling large datasets (100k+ points with WebGL)

### 3. **Chart.js** - Quick & Simple
- **Skill**: [chartjs](chartjs/SKILL.md)
- **Best For**: Simple charts, quick implementation, small projects
- **Learning Curve**: Easy
- **Speed**: ⭐⭐⭐⭐⭐ (Up and running in minutes)
- **Size**: ⭐⭐⭐⭐⭐ (Lightweight - 60KB)

**Use when:**
- Need charts quickly with minimal configuration
- Simple chart types (line, bar, pie) are sufficient
- Small to medium projects
- Minimal dependencies preferred
- Mobile responsiveness is priority

### 4. **ECharts** - Balanced Power & Ease
- **Skill**: [echarts](echarts/SKILL.md)
- **Best For**: Balanced projects, geographic maps, mobile apps
- **Learning Curve**: Moderate
- **TypeScript**: ⭐⭐⭐⭐⭐ (Full support)
- **Customization**: ⭐⭐⭐⭐ (High)

**Use when:**
- Want balance between ease and customization
- Need broad variety of chart types (20+)
- TypeScript support required
- Building mobile-responsive dashboards
- Working with geographic/map data
- International/multilingual applications

### 5. **Highcharts** - Enterprise Grade
- **Skill**: [highcharts](highcharts/SKILL.md)
- **Best For**: Enterprise applications, stock charts, Gantt charts
- **Learning Curve**: Moderate
- **Accessibility**: ⭐⭐⭐⭐⭐ (WCAG compliant)
- **Support**: ⭐⭐⭐⭐⭐ (Commercial support available)

**Use when:**
- Building enterprise/commercial applications
- Need stock/financial charts
- Accessibility compliance (WCAG) required
- Professional support needed
- Advanced export features needed (PDF, Excel)
- Budget allows commercial licensing

## Comparison Matrix

| Feature | D3.js | Plotly | Chart.js | ECharts | Highcharts |
|---------|-------|--------|----------|---------|------------|
| **Ease of Use** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Customization** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Chart Types** | Unlimited | 40+ | 8 | 20+ | 30+ |
| **3D Support** | Manual | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Large Datasets** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **TypeScript** | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ | ✅ |
| **Python Integration** | ❌ | ⭐⭐⭐⭐⭐ | ❌ | ❌ | ❌ |
| **Mobile Responsive** | Manual | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **File Size** | ~200KB | ~3MB | 60KB | ~900KB | ~300KB |
| **License** | Free (BSD) | Free (MIT) | Free (MIT) | Free (Apache) | Commercial* |

*Highcharts: Free for non-commercial use, requires license for commercial use

## Selection Guide

### Choose D3.js if:
- ✅ Need complete customization
- ✅ Building unique, bespoke visualizations
- ✅ Have strong JavaScript team
- ✅ Time for development available
- ❌ Don't need quick prototyping

### Choose Plotly if:
- ✅ Scientific or analytical visualizations
- ✅ Working with Python/R
- ✅ Need 3D charts
- ✅ Building dashboards
- ✅ Large datasets (100k+ points)

### Choose Chart.js if:
- ✅ Need simple charts quickly
- ✅ Small to medium projects
- ✅ Minimal dependencies
- ✅ Budget/file size constraints
- ❌ Don't need advanced features

### Choose ECharts if:
- ✅ Want balance of ease and power
- ✅ TypeScript project
- ✅ Need mobile responsiveness
- ✅ Geographic/map visualizations
- ✅ International audience

### Choose Highcharts if:
- ✅ Enterprise/commercial application
- ✅ Need stock/Gantt charts
- ✅ Accessibility compliance required
- ✅ Budget for commercial license
- ✅ Professional support needed

## Quick Start Examples

### D3.js - Custom Visualization
```javascript
d3.select('#chart')
  .selectAll('circle')
  .data(dataset)
  .enter()
  .append('circle')
  .attr('cx', d => xScale(d.x))
  .attr('cy', d => yScale(d.y))
  .attr('r', 5);
```

### Plotly - Python Interactive Plot
```python
import plotly.express as px
fig = px.scatter(df, x='x', y='y', color='category')
fig.write_html('chart.html')
```

### Chart.js - Quick Line Chart
```javascript
new Chart(ctx, {
  type: 'line',
  data: { labels: labels, datasets: [{ data: values }] }
});
```

### ECharts - Balanced Approach
```javascript
echarts.init(dom).setOption({
  xAxis: { data: categories },
  yAxis: {},
  series: [{ type: 'bar', data: values }]
});
```

### Highcharts - Enterprise Chart
```javascript
Highcharts.chart('container', {
  series: [{ data: [1, 2, 3, 4, 5] }],
  exporting: { enabled: true }
});
```

## Integration with Workspace-Hub Standards

All chart skills follow workspace-hub standards:

### ✅ HTML Reporting Standards
- Interactive plots only (no static images)
- CSV data with relative paths
- Responsive design
- Accessible tooltips

### ✅ File Organization
- Charts in `reports/` directory
- Data in `data/processed/`
- Scripts in `src/visualization/`

### ✅ Development Workflow
- YAML configuration support
- Bash execution
- Version controlled outputs

## Resources

### Official Documentation
- **D3.js**: https://d3js.org/
- **Plotly**: https://plotly.com/python/
- **Chart.js**: https://www.chartjs.org/
- **ECharts**: https://echarts.apache.org/
- **Highcharts**: https://www.highcharts.com/

### Community Resources
- [Awesome D3](https://github.com/wbkd/awesome-d3)
- [Plotly Community](https://community.plotly.com/)
- [Chart.js Samples](https://www.chartjs.org/docs/latest/samples/)
- [Awesome ECharts](https://github.com/ecomfe/awesome-echarts)
- [Highcharts Demos](https://www.highcharts.com/demo)

## Contributing

To add new chart library skills:

1. Create directory: `skills/charts/library-name/`
2. Add `SKILL.md` with YAML frontmatter
3. Include comprehensive examples
4. Update this README
5. Follow workspace-hub skill format

---

**Choose the right chart library for your project needs and start visualizing!**
