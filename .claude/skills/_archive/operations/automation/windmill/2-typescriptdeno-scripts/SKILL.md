---
name: windmill-2-typescriptdeno-scripts
description: 'Sub-skill of windmill: 2. TypeScript/Deno Scripts.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 2. TypeScript/Deno Scripts

## 2. TypeScript/Deno Scripts


```typescript
// scripts/api/webhook_handler.ts
/**
 * Handle incoming webhooks with validation and routing.
 * Uses Deno runtime with TypeScript support.
 */

import * as wmill from "npm:windmill-client@1";

// Define input types for auto-generated UI
type WebhookPayload = {
  event_type: string;
  data: Record<string, unknown>;
  timestamp: string;
  signature?: string;
};

type HandlerConfig = {
  validate_signature: boolean;
  allowed_events: string[];
  forward_to_slack: boolean;
};

export async function main(
  payload: WebhookPayload,
  config: HandlerConfig = {
    validate_signature: true,
    allowed_events: ["order.created", "order.updated", "payment.completed"],
    forward_to_slack: true,
  }
): Promise<{
  processed: boolean;
  event_type: string;
  actions_taken: string[];
}> {
  const actions: string[] = [];

  // Get webhook secret from resources
  const webhookSecret = await wmill.getResource("u/admin/webhook_secret");

  // Validate signature if required
  if (config.validate_signature && payload.signature) {
    const crypto = await import("node:crypto");
    const expectedSignature = crypto
      .createHmac("sha256", webhookSecret.secret)
      .update(JSON.stringify(payload.data))
      .digest("hex");

    if (payload.signature !== expectedSignature) {
      throw new Error("Invalid webhook signature");
    }
    actions.push("signature_validated");
  }

  // Check if event is allowed
  if (!config.allowed_events.includes(payload.event_type)) {
    return {
      processed: false,
      event_type: payload.event_type,
      actions_taken: ["event_filtered"],
    };
  }

  // Route based on event type
  switch (payload.event_type) {
    case "order.created":
      await handleOrderCreated(payload.data);
      actions.push("order_processed");
      break;

    case "order.updated":
      await handleOrderUpdated(payload.data);
      actions.push("order_updated");
      break;

    case "payment.completed":
      await handlePaymentCompleted(payload.data);
      actions.push("payment_recorded");
      break;
  }

  // Forward to Slack if configured
  if (config.forward_to_slack) {
    const slackWebhook = await wmill.getResource("u/admin/slack_webhook");
    await fetch(slackWebhook.url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: `Webhook received: ${payload.event_type}`,
        blocks: [
          {
            type: "section",
            text: {
              type: "mrkdwn",
              text: `*Event:* ${payload.event_type}\n*Timestamp:* ${payload.timestamp}`,
            },
          },
        ],
      }),
    });
    actions.push("slack_notified");
  }

  return {
    processed: true,
    event_type: payload.event_type,
    actions_taken: actions,
  };
}

async function handleOrderCreated(data: Record<string, unknown>) {
  console.log("Processing new order:", data);
  // Implementation
}

async function handleOrderUpdated(data: Record<string, unknown>) {
  console.log("Processing order update:", data);
  // Implementation
}

async function handlePaymentCompleted(data: Record<string, unknown>) {
  console.log("Processing payment:", data);
  // Implementation
}
```

```typescript
// scripts/data/aggregate_metrics.ts
/**
 * Aggregate metrics from multiple sources into unified dashboard data.
 */

import * as wmill from "npm:windmill-client@1";

type MetricsSource = "database" | "api" | "cache";
type AggregationPeriod = "hourly" | "daily" | "weekly" | "monthly";

interface MetricConfig {
  sources: MetricsSource[];
  period: AggregationPeriod;
  include_comparisons: boolean;
  custom_dimensions?: string[];
}

interface AggregatedMetrics {
  period: string;
  total_revenue: number;
  total_orders: number;
  avg_order_value: number;
  unique_customers: number;
  top_products: Array<{ name: string; revenue: number; quantity: number }>;
  by_dimension: Record<string, Record<string, number>>;
  comparisons?: {
    previous_period: Record<string, number>;
    change_percent: Record<string, number>;
  };
}

export async function main(
  start_date: string,
  end_date: string,
  config: MetricConfig = {
    sources: ["database"],
    period: "daily",
    include_comparisons: true,
  }
): Promise<AggregatedMetrics> {
  // Get database connection
  const dbConfig = await wmill.getResource("u/admin/analytics_db");

  // Dynamic import for database client
  const { Client } = await import("npm:pg@8");
  const client = new Client(dbConfig);
  await client.connect();

  try {
    // Fetch base metrics
    const metricsQuery = `
      SELECT
        DATE_TRUNC('${config.period}', created_at) as period,
        COUNT(*) as total_orders,
        SUM(total_amount) as total_revenue,
        COUNT(DISTINCT customer_id) as unique_customers
      FROM orders

*Content truncated — see parent skill for full reference.*
