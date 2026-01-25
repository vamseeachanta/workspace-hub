---
name: web-artifacts-builder
description: Build self-contained interactive web applications as single HTML files. Use for creating demos, prototypes, interactive tools, and standalone web experiences that work without external servers.
version: 2.0.0
category: builders
last_updated: 2026-01-02
related_skills:
  - frontend-design
  - algorithmic-art
  - theme-factory
---

# Web Artifacts Builder Skill

## Overview

Create self-contained, interactive web applications as single HTML files. These artifacts require no server, no build process, and can be shared as standalone files that run in any modern browser.

## When to Use

- Creating interactive demos or prototypes
- Building standalone calculators or tools
- Data visualization dashboards
- Interactive documentation
- Shareable proof-of-concepts
- Any web experience that needs to work offline

## Quick Start

1. **Create single HTML file** with all CSS/JS inline
2. **Use CDN for libraries** (Chart.js, Plotly, etc.)
3. **Embed data directly** as JSON or JS objects
4. **Test locally** by opening file in browser
5. **Share** as single file attachment

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Web Artifact</title>
  <style>
    body { font-family: system-ui; padding: 20px; }
    .btn { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
  </style>
</head>
<body>
  <h1>Interactive Tool</h1>
  <button class="btn" onclick="calculate()">Calculate</button>
  <div id="result"></div>
  <script>
    function calculate() {
      document.getElementById('result').textContent = 'Result: ' + (Math.random() * 100).toFixed(2);
    }
  </script>
</body>
</html>
```

## Core Principles

### Self-Contained Architecture

Everything in one HTML file:
- HTML structure
- CSS styles (inline or in `<style>` tags)
- JavaScript functionality (inline or in `<script>` tags)
- Data (embedded JSON or JavaScript objects)
- Assets (inline SVG, base64 images, or CDN links)

### No External Dependencies Required

```html
<!-- Use CDN for libraries when needed -->
<script src="https://cdn.jsdelivr.net/npm/library@version"></script>

<!-- Or embed everything inline -->
<script>
// All JavaScript here
</script>
```

## Basic Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Artifact</title>
    <style>
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Component styles */
        .card {
            background: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.2s;
        }

        .btn:hover {
            background: #0056b3;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>Web Artifact</h1>
            <p>Self-contained interactive application</p>
            <button class="btn" onclick="handleClick()">Click Me</button>
            <div id="output"></div>
        </div>
    </div>

    <script>
        // Application state
        const state = {
            count: 0
        };

        // Event handlers
        function handleClick() {
            state.count++;
            render();
        }

        // Render function
        function render() {
            document.getElementById('output').innerHTML = `
                <p>Clicked ${state.count} times</p>
            `;
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', render);
    </script>
</body>
</html>
```

## Common Artifact Types

### 1. Interactive Dashboard

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: system-ui, sans-serif;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .card {
            background: #16213e;
            border-radius: 12px;
            padding: 20px;
        }
        .stat-card {
            text-align: center;
        }
        .stat-value {
            font-size: 3em;
            font-weight: bold;
            color: #e94560;
        }
        .stat-label {
            color: #888;
            margin-top: 8px;
        }
        .chart-container {
            position: relative;
            height: 300px;
        }
        h1 {
            text-align: center;
            padding: 20px;
            color: #e94560;
        }
    </style>
</head>
<body>
    <h1>Analytics Dashboard</h1>
    <div class="dashboard">
        <div class="card stat-card">
            <div class="stat-value" id="users">0</div>
            <div class="stat-label">Active Users</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value" id="revenue">$0</div>
            <div class="stat-label">Revenue</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value" id="growth">0%</div>
            <div class="stat-label">Growth</div>
        </div>
        <div class="card" style="grid-column: span 2;">
            <h3 style="margin-bottom: 15px;">Weekly Trend</h3>
            <div class="chart-container">
                <canvas id="trendChart"></canvas>
            </div>
        </div>
        <div class="card">
            <h3 style="margin-bottom: 15px;">Distribution</h3>
            <div class="chart-container">
                <canvas id="pieChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        // Embedded data
        const data = {
            users: 12847,
            revenue: 94520,
            growth: 23.5,
            weekly: [65, 72, 86, 81, 90, 95, 110],
            distribution: [35, 25, 20, 15, 5]
        };

        // Animate counting
        function animateValue(id, end, prefix = '', suffix = '') {
            const el = document.getElementById(id);
            const duration = 1500;
            const start = 0;
            const startTime = performance.now();

            function update(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                const current = Math.floor(start + (end - start) * eased);
                el.textContent = prefix + current.toLocaleString() + suffix;
                if (progress < 1) requestAnimationFrame(update);
            }
            requestAnimationFrame(update);
        }

        // Initialize charts
        document.addEventListener('DOMContentLoaded', () => {
            // Animate stats
            animateValue('users', data.users);
            animateValue('revenue', data.revenue, '$');
            animateValue('growth', data.growth, '', '%');

            // Line chart
            new Chart(document.getElementById('trendChart'), {
                type: 'line',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Users',
                        data: data.weekly,
                        borderColor: '#e94560',
                        backgroundColor: 'rgba(233, 69, 96, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { grid: { color: '#333' }, ticks: { color: '#888' } },
                        x: { grid: { display: false }, ticks: { color: '#888' } }
                    }
                }
            });

            // Pie chart
            new Chart(document.getElementById('pieChart'), {
                type: 'doughnut',
                data: {
                    labels: ['Product A', 'Product B', 'Product C', 'Product D', 'Other'],
                    datasets: [{
                        data: data.distribution,
                        backgroundColor: ['#e94560', '#0f3460', '#16213e', '#533483', '#1a1a2e']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right', labels: { color: '#888' } }
                    }
                }
            });
        });
    </script>
</body>
</html>
```

### 2. Interactive Calculator/Tool

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculator Tool</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .calculator {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.2s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            text-align: center;
            display: none;
        }
        .result.show { display: block; }
        .result-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        .result-label {
            color: #666;
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <div class="calculator">
        <h1>Savings Calculator</h1>
        <div class="form-group">
            <label for="principal">Initial Investment ($)</label>
            <input type="number" id="principal" value="10000" min="0">
        </div>
        <div class="form-group">
            <label for="monthly">Monthly Contribution ($)</label>
            <input type="number" id="monthly" value="500" min="0">
        </div>
        <div class="form-group">
            <label for="rate">Annual Interest Rate (%)</label>
            <input type="number" id="rate" value="7" min="0" max="100" step="0.1">
        </div>
        <div class="form-group">
            <label for="years">Investment Period (Years)</label>
            <input type="number" id="years" value="10" min="1" max="50">
        </div>
        <button class="btn" onclick="calculate()">Calculate</button>
        <div class="result" id="result">
            <div class="result-value" id="total">$0</div>
            <div class="result-label">Future Value</div>
            <div style="margin-top: 15px; color: #666;">
                <div>Total Contributions: <strong id="contributions">$0</strong></div>
                <div>Interest Earned: <strong id="interest">$0</strong></div>
            </div>
        </div>
    </div>

    <script>
        function calculate() {
            const principal = parseFloat(document.getElementById('principal').value) || 0;
            const monthly = parseFloat(document.getElementById('monthly').value) || 0;
            const rate = (parseFloat(document.getElementById('rate').value) || 0) / 100;
            const years = parseInt(document.getElementById('years').value) || 0;

            const monthlyRate = rate / 12;
            const months = years * 12;

            // Future value calculation
            let futureValue = principal * Math.pow(1 + monthlyRate, months);
            if (monthlyRate > 0) {
                futureValue += monthly * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate);
            } else {
                futureValue += monthly * months;
            }

            const totalContributions = principal + (monthly * months);
            const interestEarned = futureValue - totalContributions;

            // Update display
            document.getElementById('total').textContent = formatCurrency(futureValue);
            document.getElementById('contributions').textContent = formatCurrency(totalContributions);
            document.getElementById('interest').textContent = formatCurrency(interestEarned);
            document.getElementById('result').classList.add('show');
        }

        function formatCurrency(value) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(value);
        }

        // Calculate on input change
        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', calculate);
        });

        // Initial calculation
        calculate();
    </script>
</body>
</html>
```

## Best Practices

### Performance

1. **Minimize dependencies**: Only include what you need
2. **Use CDN with version pinning**: `library@4.4.0` not `library@latest`
3. **Lazy load when possible**: Defer non-critical scripts
4. **Optimize images**: Use SVG or base64 for small images

### Accessibility

```html
<!-- Always include -->
<html lang="en">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Use semantic HTML -->
<main>, <nav>, <article>, <section>, <header>, <footer>

<!-- Add ARIA labels -->
<button aria-label="Close dialog">x</button>

<!-- Ensure color contrast -->
/* Minimum 4.5:1 for normal text */
```

### Responsive Design

```css
/* Mobile-first approach */
.container {
    padding: 10px;
}

@media (min-width: 768px) {
    .container {
        padding: 20px;
    }
}

@media (min-width: 1024px) {
    .container {
        max-width: 1200px;
        margin: 0 auto;
    }
}
```

## Common CDN Libraries

```html
<!-- Charts -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>

<!-- UI Frameworks -->
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- Utilities -->
<script src="https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dayjs@1.11.10/dayjs.min.js"></script>

<!-- Animation -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.2/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/animejs@3.2.1/lib/anime.min.js"></script>

<!-- 3D/Graphics -->
<script src="https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"></script>

<!-- Maps -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<!-- Markdown -->
<script src="https://cdn.jsdelivr.net/npm/marked@9.1.0/marked.min.js"></script>

<!-- Icons -->
<script src="https://unpkg.com/lucide@latest"></script>
```

## Execution Checklist

- [ ] All CSS and JS inline or from CDN
- [ ] No server dependencies
- [ ] Works offline (or gracefully degrades)
- [ ] Responsive across devices
- [ ] Accessible (ARIA labels, contrast, keyboard nav)
- [ ] Data embedded or loaded from CDN
- [ ] File size reasonable (< 500KB ideal)
- [ ] Tested in multiple browsers
- [ ] Clear user instructions

## Error Handling

### Common Issues

**Issue: CDN library not loading**
- Cause: Network issue or wrong URL
- Solution: Pin version, add fallback, test offline

**Issue: File doesn't open in browser**
- Cause: Browser blocking local file access
- Solution: Use a simple HTTP server or data: URLs

**Issue: Charts not rendering**
- Cause: DOM not ready when script runs
- Solution: Use DOMContentLoaded event

**Issue: Styles not applying**
- Cause: CSS specificity or load order
- Solution: Use more specific selectors, check order

## Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| File Size | < 500 KB | File properties |
| Load Time | < 2 seconds | Browser DevTools |
| Accessibility | > 90 | Lighthouse |
| Mobile Usability | 100% | Manual testing |
| Browser Support | 95%+ | caniuse.com |

## Sharing & Distribution

### File Naming

```
project-name_v1.0.html
dashboard_2024-01-15.html
calculator-tool.html
```

### Embedding Data

```javascript
// Embed JSON data directly
const DATA = {
    items: [...],
    config: {...}
};

// Or base64 encode binary data
const imageData = 'data:image/png;base64,iVBORw0KGgo...';
```

### Export Functionality

```javascript
function downloadData() {
    const data = JSON.stringify(state, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'export.json';
    a.click();
    URL.revokeObjectURL(url);
}
```

## Related Skills

- [frontend-design](../../content-design/frontend-design/SKILL.md) - Advanced UI design
- [algorithmic-art](../../content-design/algorithmic-art/SKILL.md) - Generative visuals
- [theme-factory](../../content-design/theme-factory/SKILL.md) - Color and typography

---

## Version History

- **2.0.0** (2026-01-02): Upgraded to v2 template - added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections
- **1.0.0** (2024-10-15): Initial release with basic template, dashboard, calculator, data visualization examples, CDN library references, best practices
