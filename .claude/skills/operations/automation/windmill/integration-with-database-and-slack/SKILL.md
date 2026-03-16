---
name: windmill-integration-with-database-and-slack
description: 'Sub-skill of windmill: Integration with Database and Slack.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Integration with Database and Slack

## Integration with Database and Slack


```python
# scripts/monitoring/database_health_check.py
"""
Monitor database health and alert on issues.
"""

import wmill
from datetime import datetime
import psycopg2


def main(
    check_connections: bool = True,
    check_slow_queries: bool = True,
    slow_query_threshold_ms: int = 5000,
    alert_channel: str = "#database-alerts",
):
    """
    Run database health checks and alert on issues.

    Args:
        check_connections: Check connection pool status
        check_slow_queries: Check for slow running queries
        slow_query_threshold_ms: Threshold for slow query alerts
        alert_channel: Slack channel for alerts

    Returns:
        Health check results
    """
    db = wmill.get_resource("u/admin/production_db")
    slack = wmill.get_resource("u/admin/slack_webhook")

    results = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "alerts": []
    }

    conn = psycopg2.connect(**db)

    try:
        with conn.cursor() as cur:
            # Check active connections
            if check_connections:
                cur.execute("""
                    SELECT
                        count(*) as total,
                        count(*) FILTER (WHERE state = 'active') as active,
                        count(*) FILTER (WHERE state = 'idle') as idle,
                        count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_txn
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                """)
                conn_stats = cur.fetchone()

                results["checks"]["connections"] = {
                    "total": conn_stats[0],
                    "active": conn_stats[1],
                    "idle": conn_stats[2],
                    "idle_in_transaction": conn_stats[3]
                }

                # Alert if too many connections
                if conn_stats[0] > 80:
                    results["alerts"].append({
                        "type": "high_connections",
                        "message": f"High connection count: {conn_stats[0]}/100",
                        "severity": "warning"
                    })

            # Check slow queries
            if check_slow_queries:
                cur.execute("""
                    SELECT
                        pid,
                        now() - pg_stat_activity.query_start AS duration,
                        query,
                        state
                    FROM pg_stat_activity
                    WHERE (now() - pg_stat_activity.query_start) > interval '%s milliseconds'
                    AND state != 'idle'
                    AND query NOT LIKE '%%pg_stat_activity%%'
                """, (slow_query_threshold_ms,))

                slow_queries = cur.fetchall()

                results["checks"]["slow_queries"] = {
                    "count": len(slow_queries),
                    "threshold_ms": slow_query_threshold_ms,
                    "queries": [
                        {
                            "pid": q[0],
                            "duration": str(q[1]),
                            "query": q[2][:200],
                            "state": q[3]
                        }
                        for q in slow_queries[:5]
                    ]
                }

                if slow_queries:
                    results["alerts"].append({
                        "type": "slow_queries",
                        "message": f"Found {len(slow_queries)} slow queries",
                        "severity": "warning"
                    })

    finally:
        conn.close()

    # Send Slack alerts
    if results["alerts"]:
        send_slack_alert(slack, alert_channel, results)

    return results


def send_slack_alert(slack, channel, results):
    """Send health check alerts to Slack."""
    import requests

    alert_texts = [
        f"*{a['severity'].upper()}*: {a['message']}"
        for a in results["alerts"]
    ]

    requests.post(slack["url"], json={
        "channel": channel,
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Database Health Alert"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(alert_texts)
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Timestamp: {results['timestamp']}"
                    }
                ]
            }
        ]
    })
```
