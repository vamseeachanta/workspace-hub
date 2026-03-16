---
name: n8n-3-scheduled-workflows
description: 'Sub-skill of n8n: 3. Scheduled Workflows.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 3. Scheduled Workflows

## 3. Scheduled Workflows


```json
{
  "name": "Daily Report Generator",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 9 * * 1-5"
            }
          ]
        }
      },
      "id": "schedule",
      "name": "Daily Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT \n  DATE(created_at) as date,\n  COUNT(*) as total_orders,\n  SUM(amount) as revenue,\n  AVG(amount) as avg_order_value\nFROM orders\nWHERE created_at >= CURRENT_DATE - INTERVAL '7 days'\nGROUP BY DATE(created_at)\nORDER BY date DESC",
        "options": {}
      },
      "id": "postgres",
      "name": "Query Sales Data",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.3,
      "position": [460, 300],
      "credentials": {
        "postgres": {
          "id": "4",
          "name": "Production DB"
        }
      }
    },
    {
      "parameters": {
        "jsCode": "// Generate report summary\nconst data = $input.all();\n\nconst totalRevenue = data.reduce((sum, row) => sum + parseFloat(row.json.revenue), 0);\nconst totalOrders = data.reduce((sum, row) => sum + parseInt(row.json.total_orders), 0);\nconst avgOrderValue = totalRevenue / totalOrders;\n\nconst reportDate = new Date().toISOString().split('T')[0];\n\nreturn {\n  report_date: reportDate,\n  period: 'Last 7 Days',\n  summary: {\n    total_revenue: totalRevenue.toFixed(2),\n    total_orders: totalOrders,\n    avg_order_value: avgOrderValue.toFixed(2)\n  },\n  daily_breakdown: data.map(row => row.json)\n};"
      },
      "id": "transform",
      "name": "Generate Report",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [680, 300]
    },
    {
      "parameters": {
        "sendTo": "team@example.com",
        "subject": "=Weekly Sales Report - {{ $json.report_date }}",
        "emailType": "html",
        "html": "=<h1>Weekly Sales Report</h1>\n<p>Period: {{ $json.period }}</p>\n<h2>Summary</h2>\n<ul>\n  <li>Total Revenue: ${{ $json.summary.total_revenue }}</li>\n  <li>Total Orders: {{ $json.summary.total_orders }}</li>\n  <li>Average Order Value: ${{ $json.summary.avg_order_value }}</li>\n</ul>\n<h2>Daily Breakdown</h2>\n<table border=\"1\">\n  <tr><th>Date</th><th>Orders</th><th>Revenue</th></tr>\n  {{ $json.daily_breakdown.map(d => `<tr><td>${d.date}</td><td>${d.total_orders}</td><td>$${d.revenue}</td></tr>`).join('') }}\n</table>",
        "options": {}
      },
      "id": "email",
      "name": "Send Report Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2.1,
      "position": [900, 300],
      "credentials": {
        "smtp": {
          "id": "5",
          "name": "SMTP Server"
        }
      }
    }
  ],
  "connections": {
    "Daily Schedule": {
      "main": [
        [{ "node": "Query Sales Data", "type": "main", "index": 0 }]
      ]
    },
    "Query Sales Data": {
      "main": [
        [{ "node": "Generate Report", "type": "main", "index": 0 }]
      ]
    },
    "Generate Report": {
      "main": [
        [{ "node": "Send Report Email", "type": "main", "index": 0 }]
      ]
    }
  }
}
```
