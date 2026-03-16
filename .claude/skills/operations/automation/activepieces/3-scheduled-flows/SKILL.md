---
name: activepieces-3-scheduled-flows
description: 'Sub-skill of activepieces: 3. Scheduled Flows.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 3. Scheduled Flows

## 3. Scheduled Flows


```typescript
// Scheduled flow with cron expression
const scheduledFlow = {
  "displayName": "Daily Sales Report",
  "schedule": {
    "cronExpression": "0 9 * * 1-5",  // 9 AM Mon-Fri
    "timezone": "America/New_York"
  },
  "trigger": {
    "name": "schedule",
    "type": "SCHEDULE",
    "settings": {},
    "displayName": "Daily Schedule"
  },
  "steps": [
    {
      "name": "get_date_range",
      "type": "CODE",
      "settings": {
        "sourceCode": {
          "code": `
export const code = async () => {
  const now = new Date();
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);

  return {
    start_date: yesterday.toISOString().split('T')[0],
    end_date: now.toISOString().split('T')[0],
    report_date: now.toISOString()
  };
};`
        }
      },
      "displayName": "Calculate Date Range"
    },
    {
      "name": "fetch_sales_data",
      "type": "PIECE",
      "settings": {
        "pieceName": "@activepieces/piece-http",
        "pieceVersion": "~0.4.0",
        "actionName": "send_request",
        "input": {
          "method": "GET",
          "url": "{{connections.sales_api.base_url}}/api/v1/sales",
          "headers": {
            "Authorization": "Bearer {{connections.sales_api.api_key}}"
          },
          "queryParams": {
            "start_date": "{{get_date_range.start_date}}",
            "end_date": "{{get_date_range.end_date}}"
          }
        }
      },
      "displayName": "Fetch Sales Data"
    },
    {
      "name": "generate_report",
      "type": "CODE",
      "settings": {
        "input": {
          "sales": "{{fetch_sales_data.body.data}}",
          "report_date": "{{get_date_range.report_date}}"
        },
        "sourceCode": {
          "code": `
export const code = async (inputs) => {
  const { sales, report_date } = inputs;

  const totalRevenue = sales.reduce((sum, sale) => sum + sale.amount, 0);
  const totalOrders = sales.length;
  const avgOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;

  const byCategory = sales.reduce((acc, sale) => {
    const cat = sale.category || 'Other';
    acc[cat] = (acc[cat] || 0) + sale.amount;
    return acc;
  }, {});

  return {
    report_date,
    summary: {
      total_revenue: totalRevenue.toFixed(2),
      total_orders: totalOrders,
      avg_order_value: avgOrderValue.toFixed(2)
    },
    by_category: Object.entries(byCategory)
      .map(([category, amount]) => ({ category, amount }))
      .sort((a, b) => b.amount - a.amount),
    top_products: sales
      .sort((a, b) => b.amount - a.amount)
      .slice(0, 5)
  };
};`
        }
      },
      "displayName": "Generate Report Summary"
    },
    {
      "name": "send_report",
      "type": "PIECE",
      "settings": {
        "pieceName": "@activepieces/piece-gmail",
        "pieceVersion": "~0.5.0",
        "actionName": "send_email",
        "input": {
          "to": ["sales-team@example.com", "management@example.com"],
          "subject": "Daily Sales Report - {{get_date_range.start_date}}",
          "body": "<h1>Daily Sales Report</h1><h2>Summary</h2><ul><li>Total Revenue: ${{generate_report.summary.total_revenue}}</li><li>Total Orders: {{generate_report.summary.total_orders}}</li><li>Average Order Value: ${{generate_report.summary.avg_order_value}}</li></ul>"
        }
      },
      "displayName": "Send Report Email"
    }
  ]
};
```
