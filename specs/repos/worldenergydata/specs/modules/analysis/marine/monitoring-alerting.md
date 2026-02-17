# Marine Safety Incidents Database - Monitoring & Alerting Specification

**Version:** 1.0.0
**Date:** 2025-10-03
**Status:** Planning
**Module:** HSE (Health, Safety, Environment) - Marine Safety
**Component:** Monitoring & Alerting

---

## Executive Summary

This specification defines a comprehensive monitoring and alerting system for the Marine Safety Incidents Database. The system provides real-time visibility into operational health, data collection performance, API reliability, and business metrics. Built on industry-standard tools (Prometheus, Grafana, ELK Stack, OpenTelemetry), it ensures high availability, rapid incident response, and continuous system optimization.

---

## Table of Contents

1. [Monitoring Architecture](#monitoring-architecture)
2. [Metrics Collection](#metrics-collection)
3. [Dashboards](#dashboards)
4. [Alert Definitions](#alert-definitions)
5. [Alert Routing](#alert-routing)
6. [Health Checks](#health-checks)
7. [Log Aggregation](#log-aggregation)
8. [Distributed Tracing](#distributed-tracing)
9. [Performance Monitoring](#performance-monitoring)
10. [SLO/SLA Tracking](#slosla-tracking)
11. [Implementation Roadmap](#implementation-roadmap)
12. [Configuration Examples](#configuration-examples)

---

## Monitoring Architecture

### Stack Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Monitoring Stack                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Prometheus │  │   Grafana   │  │  AlertMgr   │         │
│  │   Metrics   │→│  Dashboards │→│   Routing    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │Elasticsearch│  │   Kibana    │  │  Logstash   │         │
│  │    Store    │→│    Logs     │←│  Collector   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Jaeger    │  │OpenTelemetry│  │     APM     │         │
│  │   Traces    │←│   Collector  │←│  Instrumt   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                           ↑
                           │ (scrape/push)
                           │
┌─────────────────────────────────────────────────────────────┐
│              Marine Safety Database System                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   API    │  │ Database │  │ Scrapers │  │  Worker  │   │
│  │  Server  │  │   Pool   │  │  (7x)    │  │  Queues  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Components

#### 1. **Prometheus Stack**
- **Prometheus Server**: Time-series metrics storage
- **Alertmanager**: Alert routing and grouping
- **Node Exporter**: System-level metrics
- **PostgreSQL Exporter**: Database metrics
- **Redis Exporter**: Cache metrics
- **Custom Exporters**: Application metrics

#### 2. **ELK Stack**
- **Elasticsearch**: Log storage and indexing
- **Logstash**: Log processing and enrichment
- **Kibana**: Log visualization and search
- **Filebeat**: Log shipping

#### 3. **OpenTelemetry**
- **OTEL Collector**: Unified telemetry collection
- **Jaeger Backend**: Distributed tracing storage
- **Jaeger UI**: Trace visualization
- **APM Integration**: Application performance monitoring

#### 4. **Additional Tools**
- **Grafana**: Unified dashboards
- **PagerDuty**: Incident management
- **Slack**: Team notifications
- **Uptime Robot**: External monitoring
- **Sentry**: Error tracking

---

## Metrics Collection

### Application Metrics

#### API Server Metrics

```yaml
# Prometheus exposition format
# Endpoint: http://api-server:9090/metrics

# Request metrics
http_requests_total{method="GET", endpoint="/api/v1/incidents", status="200"}
http_request_duration_seconds{method="GET", endpoint="/api/v1/incidents", quantile="0.95"}
http_requests_in_flight{endpoint="/api/v1/incidents"}

# Business metrics
incidents_scraped_total{source="uscg"}
incidents_processed_total{source="uscg", status="success"}
incidents_database_total{type="collision", severity="major"}

# Database metrics
db_connection_pool_active{pool="main"}
db_connection_pool_idle{pool="main"}
db_query_duration_seconds{query="incidents_list", quantile="0.99"}
db_connection_errors_total{pool="main"}

# Cache metrics
cache_hits_total{cache="redis"}
cache_misses_total{cache="redis"}
cache_size_bytes{cache="redis"}
cache_evictions_total{cache="redis"}

# Worker metrics
celery_tasks_total{task="scrape_uscg", state="success"}
celery_task_duration_seconds{task="scrape_uscg", quantile="0.95"}
celery_workers_active{queue="scraping"}
celery_queue_length{queue="scraping"}
```

#### Scraper Metrics

```yaml
# Scraper-specific metrics

# Collection metrics
scraper_runs_total{source="uscg", status="success"}
scraper_duration_seconds{source="uscg", quantile="0.99"}
scraper_incidents_collected{source="uscg"}
scraper_pages_processed{source="uscg"}
scraper_errors_total{source="uscg", error_type="timeout"}

# Data quality metrics
scraper_data_quality_score{source="uscg"}
scraper_duplicates_detected{source="uscg"}
scraper_validation_failures{source="uscg", field="latitude"}

# Rate limiting
scraper_rate_limit_hits{source="uscg"}
scraper_retry_attempts{source="uscg"}
scraper_backoff_seconds{source="uscg"}
```

#### Database Metrics

```yaml
# PostgreSQL metrics (via postgres_exporter)

# Connection metrics
pg_stat_database_numbackends{database="marine_safety"}
pg_stat_database_xact_commit{database="marine_safety"}
pg_stat_database_xact_rollback{database="marine_safety"}

# Table metrics
pg_stat_user_tables_seq_scan{table="incidents"}
pg_stat_user_tables_idx_scan{table="incidents"}
pg_stat_user_tables_n_tup_ins{table="incidents"}
pg_stat_user_tables_n_tup_upd{table="incidents"}

# Query performance
pg_stat_statements_mean_exec_time{query="SELECT * FROM incidents WHERE..."}
pg_stat_statements_calls{query="SELECT * FROM incidents WHERE..."}

# Replication (if applicable)
pg_stat_replication_pg_current_wal_lsn_bytes
pg_stat_replication_sent_lsn
pg_stat_replication_replay_lag
```

#### System Metrics

```yaml
# Node Exporter metrics

# CPU
node_cpu_seconds_total{mode="idle"}
node_load1
node_load5
node_load15

# Memory
node_memory_MemTotal_bytes
node_memory_MemAvailable_bytes
node_memory_SwapTotal_bytes
node_memory_SwapFree_bytes

# Disk
node_filesystem_avail_bytes{mountpoint="/"}
node_filesystem_size_bytes{mountpoint="/"}
node_disk_io_time_seconds_total{device="sda"}

# Network
node_network_receive_bytes_total{device="eth0"}
node_network_transmit_bytes_total{device="eth0"}
node_network_receive_errs_total{device="eth0"}
```

### Custom Python Instrumentation

```python
# src/worldenergydata/modules/marine_safety/monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge, Summary
from functools import wraps
import time

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

incidents_processed = Counter(
    'incidents_processed_total',
    'Total incidents processed',
    ['source', 'status']
)

scraper_duration = Histogram(
    'scraper_duration_seconds',
    'Scraper execution duration',
    ['source'],
    buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600]
)

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type', 'table'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

data_quality_score = Gauge(
    'data_quality_score',
    'Data quality score per source',
    ['source']
)

# Decorator for timing functions
def track_time(metric, labels=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            labels_dict = labels or {}
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                metric.labels(**labels_dict).observe(duration)
        return wrapper
    return decorator

# Usage example
@track_time(scraper_duration, {'source': 'uscg'})
def scrape_uscg_data():
    """Scrape USCG data with automatic timing"""
    pass

# API request tracking
def track_request(method, endpoint):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            status = '500'
            try:
                result = func(*args, **kwargs)
                status = '200'
                return result
            except Exception as e:
                status = '500'
                raise
            finally:
                duration = time.time() - start
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
                http_request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
        return wrapper
    return decorator
```

---

## Dashboards

### 1. **Operational Health Dashboard**

**Purpose**: Real-time system health overview
**Audience**: Operations team, on-call engineers
**Refresh**: 10 seconds

#### Panels

```yaml
Dashboard: Marine Safety - Operational Health
Rows:
  - name: "System Overview"
    panels:
      - title: "System Status"
        type: "stat"
        query: "up{job='marine-safety'}"
        thresholds:
          - value: 0
            color: "red"
          - value: 1
            color: "green"

      - title: "API Response Time (p95)"
        type: "graph"
        query: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
          )
        unit: "seconds"
        thresholds:
          - value: 0.5
            color: "green"
          - value: 1.0
            color: "yellow"
          - value: 2.0
            color: "red"

      - title: "Error Rate"
        type: "graph"
        query: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) /
          sum(rate(http_requests_total[5m])) * 100
        unit: "percent"
        thresholds:
          - value: 1
            color: "green"
          - value: 5
            color: "yellow"
          - value: 10
            color: "red"

      - title: "Request Rate"
        type: "graph"
        query: "sum(rate(http_requests_total[5m]))"
        unit: "reqps"

  - name: "Database Health"
    panels:
      - title: "Active Connections"
        type: "graph"
        query: "pg_stat_database_numbackends{database='marine_safety'}"
        max: 100

      - title: "Query Duration (p99)"
        type: "graph"
        query: |
          histogram_quantile(0.99,
            sum(rate(db_query_duration_seconds_bucket[5m])) by (le, query_type)
          )
        unit: "seconds"

      - title: "Slow Queries (>1s)"
        type: "stat"
        query: |
          sum(rate(db_query_duration_seconds_bucket{le="+Inf",query_time=">1"}[5m]))
        thresholds:
          - value: 0
            color: "green"
          - value: 1
            color: "yellow"
          - value: 10
            color: "red"

      - title: "Connection Pool Usage"
        type: "gauge"
        query: |
          db_connection_pool_active{pool="main"} /
          (db_connection_pool_active{pool="main"} + db_connection_pool_idle{pool="main"}) * 100
        unit: "percent"

  - name: "System Resources"
    panels:
      - title: "CPU Usage"
        type: "graph"
        query: "100 - (avg(rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)"
        unit: "percent"

      - title: "Memory Usage"
        type: "graph"
        query: |
          (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
        unit: "percent"

      - title: "Disk Usage"
        type: "graph"
        query: |
          (1 - (node_filesystem_avail_bytes{mountpoint='/'} /
           node_filesystem_size_bytes{mountpoint='/'})) * 100
        unit: "percent"

      - title: "Network I/O"
        type: "graph"
        queries:
          - name: "RX"
            query: "rate(node_network_receive_bytes_total{device='eth0'}[5m])"
          - name: "TX"
            query: "rate(node_network_transmit_bytes_total{device='eth0'}[5m])"
        unit: "Bps"
```

### 2. **Data Collection Dashboard**

**Purpose**: Monitor scraper performance and data quality
**Audience**: Data engineering team
**Refresh**: 30 seconds

#### Grafana JSON Configuration

```json
{
  "dashboard": {
    "title": "Marine Safety - Data Collection",
    "refresh": "30s",
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "Scraper Success Rate (24h)",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(scraper_runs_total{status='success'}[24h])) / sum(rate(scraper_runs_total[24h])) * 100",
            "legendFormat": "Success Rate"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 90, "color": "yellow"},
                {"value": 95, "color": "green"}
              ]
            }
          }
        },
        "gridPos": {"x": 0, "y": 0, "w": 4, "h": 4}
      },
      {
        "id": 2,
        "title": "Incidents Collected (by Source)",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(scraper_incidents_collected[5m])) by (source)",
            "legendFormat": "{{source}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short"
          }
        },
        "gridPos": {"x": 4, "y": 0, "w": 8, "h": 4}
      },
      {
        "id": 3,
        "title": "Scraper Duration (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(scraper_duration_seconds_bucket[5m])) by (le, source))",
            "legendFormat": "{{source}} p95"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 300, "color": "yellow"},
                {"value": 600, "color": "red"}
              ]
            }
          }
        },
        "gridPos": {"x": 12, "y": 0, "w": 8, "h": 4}
      },
      {
        "id": 4,
        "title": "Data Quality Score by Source",
        "type": "gauge",
        "targets": [
          {
            "expr": "data_quality_score",
            "legendFormat": "{{source}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 1,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 0.7, "color": "yellow"},
                {"value": 0.85, "color": "green"}
              ]
            }
          }
        },
        "gridPos": {"x": 0, "y": 4, "w": 12, "h": 6}
      },
      {
        "id": 5,
        "title": "Scraper Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(scraper_errors_total[5m])) by (source, error_type)",
            "legendFormat": "{{source}} - {{error_type}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "ops"
          }
        },
        "gridPos": {"x": 12, "y": 4, "w": 8, "h": 6}
      },
      {
        "id": 6,
        "title": "Duplicate Detection Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(scraper_duplicates_detected[1h])) / sum(rate(scraper_incidents_collected[1h])) * 100",
            "legendFormat": "Duplicate %"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 5, "color": "yellow"},
                {"value": 10, "color": "red"}
              ]
            }
          }
        },
        "gridPos": {"x": 0, "y": 10, "w": 4, "h": 4}
      },
      {
        "id": 7,
        "title": "Validation Failures",
        "type": "table",
        "targets": [
          {
            "expr": "topk(10, sum(rate(scraper_validation_failures[1h])) by (source, field))",
            "format": "table",
            "instant": true
          }
        ],
        "gridPos": {"x": 4, "y": 10, "w": 16, "h": 8}
      }
    ]
  }
}
```

### 3. **Business Metrics Dashboard**

**Purpose**: Track key business indicators and data insights
**Audience**: Management, analysts, stakeholders
**Refresh**: 5 minutes

```yaml
Dashboard: Marine Safety - Business Metrics
Rows:
  - name: "Database Statistics"
    panels:
      - title: "Total Incidents in Database"
        type: "stat"
        query: "incidents_database_total"
        format: "number"

      - title: "Incidents by Type (30d)"
        type: "pie"
        query: |
          sum(increase(incidents_database_total[30d])) by (type)

      - title: "Incidents by Severity (30d)"
        type: "bar"
        query: |
          sum(increase(incidents_database_total[30d])) by (severity)

      - title: "Incidents Over Time"
        type: "graph"
        query: |
          sum(rate(incidents_database_total[1d]))
        unit: "incidents/day"

  - name: "Data Coverage"
    panels:
      - title: "Records by Source"
        type: "bar"
        query: |
          sum(incidents_database_total) by (source)

      - title: "Historical Coverage"
        type: "graph"
        query: |
          count(incidents{incident_date >= "1990-01-01"})
        groupBy: "year(incident_date)"

      - title: "Geographic Coverage"
        type: "worldmap"
        query: |
          count(incidents) by (country_code)

  - name: "Data Freshness"
    panels:
      - title: "Latest Update by Source"
        type: "table"
        query: |
          max(scraper_last_run_timestamp) by (source)
        format: "time_since"

      - title: "Records Added (24h)"
        type: "stat"
        query: |
          sum(increase(incidents_database_total[24h]))

      - title: "Data Update Frequency"
        type: "graph"
        query: |
          rate(incidents_database_total[1h])
```

---

## Alert Definitions

### Alert Rule Files (Prometheus Format)

#### `/etc/prometheus/rules/marine_safety_critical.yml`

```yaml
groups:
  - name: marine_safety_critical_alerts
    interval: 30s
    rules:
      # API availability
      - alert: APIServerDown
        expr: up{job="marine-safety-api"} == 0
        for: 1m
        labels:
          severity: critical
          component: api
          team: platform
        annotations:
          summary: "Marine Safety API server is down"
          description: "API server {{ $labels.instance }} has been down for more than 1 minute."
          runbook_url: "https://wiki.example.com/runbooks/api-server-down"
          dashboard_url: "https://grafana.example.com/d/marine-safety-ops"

      # Database availability
      - alert: DatabaseDown
        expr: up{job="postgresql-exporter"} == 0
        for: 1m
        labels:
          severity: critical
          component: database
          team: platform
        annotations:
          summary: "PostgreSQL database is down"
          description: "Database {{ $labels.instance }} is unreachable."
          runbook_url: "https://wiki.example.com/runbooks/database-down"

      # High error rate
      - alert: HighErrorRate
        expr: |
          (sum(rate(http_requests_total{status=~"5.."}[5m])) /
           sum(rate(http_requests_total[5m]))) > 0.05
        for: 5m
        labels:
          severity: critical
          component: api
          team: platform
        annotations:
          summary: "High API error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} over last 5 minutes."
          runbook_url: "https://wiki.example.com/runbooks/high-error-rate"

      # Database connection pool exhaustion
      - alert: DatabaseConnectionPoolExhausted
        expr: |
          (db_connection_pool_active{pool="main"} /
           (db_connection_pool_active{pool="main"} + db_connection_pool_idle{pool="main"})) > 0.9
        for: 5m
        labels:
          severity: critical
          component: database
          team: platform
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Connection pool usage at {{ $value | humanizePercentage }}."
          runbook_url: "https://wiki.example.com/runbooks/connection-pool-exhausted"

      # Disk space critical
      - alert: DiskSpaceCritical
        expr: |
          (node_filesystem_avail_bytes{mountpoint="/"} /
           node_filesystem_size_bytes{mountpoint="/"}) < 0.1
        for: 5m
        labels:
          severity: critical
          component: infrastructure
          team: platform
        annotations:
          summary: "Disk space critically low"
          description: "Only {{ $value | humanizePercentage }} disk space remaining on {{ $labels.instance }}."
          runbook_url: "https://wiki.example.com/runbooks/disk-space-low"

      # Memory exhaustion
      - alert: MemoryExhausted
        expr: |
          (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) < 0.05
        for: 2m
        labels:
          severity: critical
          component: infrastructure
          team: platform
        annotations:
          summary: "Memory exhaustion imminent"
          description: "Only {{ $value | humanizePercentage }} memory available on {{ $labels.instance }}."
          runbook_url: "https://wiki.example.com/runbooks/memory-exhaustion"
```

#### `/etc/prometheus/rules/marine_safety_high.yml`

```yaml
groups:
  - name: marine_safety_high_priority_alerts
    interval: 1m
    rules:
      # Slow API responses
      - alert: SlowAPIResponses
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
          ) > 2.0
        for: 10m
        labels:
          severity: high
          component: api
          team: platform
        annotations:
          summary: "API responses are slow"
          description: "p95 response time for {{ $labels.endpoint }} is {{ $value }}s."
          dashboard_url: "https://grafana.example.com/d/marine-safety-ops"

      # Scraper failures
      - alert: ScraperConsecutiveFailures
        expr: |
          sum(increase(scraper_runs_total{status="failure"}[1h])) by (source) > 3
        for: 5m
        labels:
          severity: high
          component: scraper
          team: data-engineering
        annotations:
          summary: "Scraper experiencing consecutive failures"
          description: "{{ $labels.source }} scraper has failed {{ $value }} times in the last hour."
          runbook_url: "https://wiki.example.com/runbooks/scraper-failures"

      # Low data quality
      - alert: LowDataQuality
        expr: data_quality_score < 0.70
        for: 30m
        labels:
          severity: high
          component: scraper
          team: data-engineering
        annotations:
          summary: "Data quality score below threshold"
          description: "{{ $labels.source }} data quality is {{ $value }} (threshold: 0.70)."
          runbook_url: "https://wiki.example.com/runbooks/data-quality-low"

      # High duplicate rate
      - alert: HighDuplicateRate
        expr: |
          (sum(rate(scraper_duplicates_detected[1h])) by (source) /
           sum(rate(scraper_incidents_collected[1h])) by (source)) > 0.10
        for: 30m
        labels:
          severity: high
          component: scraper
          team: data-engineering
        annotations:
          summary: "High duplicate detection rate"
          description: "{{ $labels.source }} duplicate rate is {{ $value | humanizePercentage }}."

      # Database replication lag (if applicable)
      - alert: DatabaseReplicationLag
        expr: pg_stat_replication_replay_lag > 60
        for: 5m
        labels:
          severity: high
          component: database
          team: platform
        annotations:
          summary: "Database replication lag detected"
          description: "Replication lag is {{ $value }}s on {{ $labels.instance }}."
          runbook_url: "https://wiki.example.com/runbooks/replication-lag"

      # Long-running queries
      - alert: LongRunningQueries
        expr: |
          sum(pg_stat_activity_max_tx_duration{state="active"}) by (instance) > 300
        for: 5m
        labels:
          severity: high
          component: database
          team: platform
        annotations:
          summary: "Long-running database queries detected"
          description: "Query running for {{ $value }}s on {{ $labels.instance }}."
          runbook_url: "https://wiki.example.com/runbooks/long-running-queries"
```

#### `/etc/prometheus/rules/marine_safety_medium.yml`

```yaml
groups:
  - name: marine_safety_medium_priority_alerts
    interval: 5m
    rules:
      # Increased error rate (warning level)
      - alert: IncreasedErrorRate
        expr: |
          (sum(rate(http_requests_total{status=~"5.."}[15m])) /
           sum(rate(http_requests_total[15m]))) > 0.01
        for: 15m
        labels:
          severity: medium
          component: api
          team: platform
        annotations:
          summary: "Elevated API error rate"
          description: "Error rate is {{ $value | humanizePercentage }}."

      # Scraper taking longer than usual
      - alert: ScraperSlowPerformance
        expr: |
          histogram_quantile(0.95,
            sum(rate(scraper_duration_seconds_bucket[1h])) by (le, source)
          ) > (
            avg_over_time(
              histogram_quantile(0.95,
                sum(rate(scraper_duration_seconds_bucket[1h])) by (le, source)
              )[7d:1h]
            ) * 2
          )
        for: 30m
        labels:
          severity: medium
          component: scraper
          team: data-engineering
        annotations:
          summary: "Scraper performance degraded"
          description: "{{ $labels.source }} is taking 2x longer than usual: {{ $value }}s."

      # High cache miss rate
      - alert: HighCacheMissRate
        expr: |
          (sum(rate(cache_misses_total[5m])) /
           (sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m])))) > 0.5
        for: 30m
        labels:
          severity: medium
          component: cache
          team: platform
        annotations:
          summary: "High cache miss rate"
          description: "Cache miss rate is {{ $value | humanizePercentage }}."

      # Worker queue backlog
      - alert: WorkerQueueBacklog
        expr: celery_queue_length{queue="scraping"} > 100
        for: 30m
        labels:
          severity: medium
          component: worker
          team: data-engineering
        annotations:
          summary: "Worker queue backlog detected"
          description: "{{ $labels.queue }} has {{ $value }} pending tasks."

      # Disk space warning
      - alert: DiskSpaceWarning
        expr: |
          (node_filesystem_avail_bytes{mountpoint="/"} /
           node_filesystem_size_bytes{mountpoint="/"}) < 0.2
        for: 30m
        labels:
          severity: medium
          component: infrastructure
          team: platform
        annotations:
          summary: "Disk space running low"
          description: "{{ $value | humanizePercentage }} disk space remaining on {{ $labels.instance }}."

      # CPU usage elevated
      - alert: HighCPUUsage
        expr: |
          100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance) * 100) > 80
        for: 30m
        labels:
          severity: medium
          component: infrastructure
          team: platform
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}% on {{ $labels.instance }}."
```

#### `/etc/prometheus/rules/marine_safety_low.yml`

```yaml
groups:
  - name: marine_safety_low_priority_alerts
    interval: 10m
    rules:
      # Data update lag
      - alert: DataUpdateLag
        expr: |
          (time() - max(scraper_last_run_timestamp) by (source)) > 86400
        for: 1h
        labels:
          severity: low
          component: scraper
          team: data-engineering
        annotations:
          summary: "Data source not updated recently"
          description: "{{ $labels.source }} hasn't been updated in {{ $value | humanizeDuration }}."

      # Validation failure rate increased
      - alert: IncreasedValidationFailures
        expr: |
          sum(rate(scraper_validation_failures[1h])) by (source) >
          avg_over_time(sum(rate(scraper_validation_failures[1h])) by (source)[7d:1h]) * 2
        for: 2h
        labels:
          severity: low
          component: scraper
          team: data-engineering
        annotations:
          summary: "Validation failures increased"
          description: "{{ $labels.source }} validation failures are 2x higher than usual."

      # Memory usage elevated
      - alert: ElevatedMemoryUsage
        expr: |
          (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) < 0.2
        for: 1h
        labels:
          severity: low
          component: infrastructure
          team: platform
        annotations:
          summary: "Memory usage elevated"
          description: "Only {{ $value | humanizePercentage }} memory available on {{ $labels.instance }}."

      # API request rate anomaly
      - alert: APIRequestRateAnomaly
        expr: |
          abs(
            sum(rate(http_requests_total[1h])) -
            avg_over_time(sum(rate(http_requests_total[1h]))[7d:1h])
          ) / avg_over_time(sum(rate(http_requests_total[1h]))[7d:1h]) > 0.5
        for: 2h
        labels:
          severity: low
          component: api
          team: platform
        annotations:
          summary: "API request rate anomaly detected"
          description: "Request rate deviates 50% from 7-day average."

      # Certificate expiry warning
      - alert: TLSCertificateExpiringSoon
        expr: |
          (ssl_certificate_expiry_timestamp - time()) / 86400 < 30
        for: 24h
        labels:
          severity: low
          component: infrastructure
          team: platform
        annotations:
          summary: "TLS certificate expiring soon"
          description: "Certificate for {{ $labels.domain }} expires in {{ $value }} days."
```

---

## Alert Routing

### Alertmanager Configuration

#### `/etc/alertmanager/alertmanager.yml`

```yaml
global:
  # External service URLs
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
  pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'

  # Global defaults
  resolve_timeout: 5m

# Alert routing tree
route:
  # Default receiver for unmatched alerts
  receiver: 'default-receiver'

  # Group alerts by these labels
  group_by: ['alertname', 'cluster', 'service']

  # Wait before sending initial notification (allows grouping)
  group_wait: 30s

  # Wait before sending update about new alerts in the group
  group_interval: 5m

  # Wait before re-sending an alert notification
  repeat_interval: 4h

  # Child routes (evaluated in order)
  routes:
    # Critical alerts -> PagerDuty + Slack
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      continue: true
      group_wait: 10s
      repeat_interval: 1h

    - match:
        severity: critical
      receiver: 'slack-critical'
      continue: false

    # High priority -> Slack + Email
    - match:
        severity: high
      receiver: 'slack-high'
      continue: true
      repeat_interval: 2h

    - match:
        severity: high
      receiver: 'email-ops'
      continue: false

    # Medium priority -> Slack only
    - match:
        severity: medium
      receiver: 'slack-medium'
      repeat_interval: 4h

    # Low priority -> Email only
    - match:
        severity: low
      receiver: 'email-ops'
      repeat_interval: 12h

    # Team-specific routing
    - match:
        team: data-engineering
      receiver: 'slack-data-engineering'
      repeat_interval: 4h

    - match:
        team: platform
      receiver: 'slack-platform'
      repeat_interval: 4h

# Inhibition rules (suppress alerts)
inhibit_rules:
  # Suppress warnings if critical alert fires
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'medium'
    equal: ['alertname', 'instance']

  # Suppress high if critical fires
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'high'
    equal: ['alertname', 'instance']

  # Suppress derivative alerts when root cause is known
  - source_match:
      alertname: 'DatabaseDown'
    target_match_re:
      alertname: '(SlowAPIResponses|HighErrorRate)'

  - source_match:
      alertname: 'APIServerDown'
    target_match_re:
      alertname: '.*'
    equal: ['instance']

# Receiver definitions
receivers:
  # Default catch-all
  - name: 'default-receiver'
    email_configs:
      - to: 'ops-team@example.com'
        send_resolved: true

  # PagerDuty for critical alerts
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
        severity: 'critical'
        description: '{{ .GroupLabels.alertname }}: {{ .Annotations.summary }}'
        details:
          firing: '{{ template "pagerduty.default.instances" .Alerts.Firing }}'
          num_firing: '{{ .Alerts.Firing | len }}'
          num_resolved: '{{ .Alerts.Resolved | len }}'
          resolved: '{{ template "pagerduty.default.instances" .Alerts.Resolved }}'
        client: 'Marine Safety Monitoring'
        client_url: '{{ template "pagerduty.default.clientURL" . }}'

  # Slack channels
  - name: 'slack-critical'
    slack_configs:
      - channel: '#alerts-critical'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          *Alert:* {{ .Annotations.summary }}
          *Description:* {{ .Annotations.description }}
          *Severity:* {{ .Labels.severity }}
          *Component:* {{ .Labels.component }}
          *Runbook:* {{ .Annotations.runbook_url }}
          *Dashboard:* {{ .Annotations.dashboard_url }}
          {{ end }}
        color: 'danger'
        send_resolved: true

  - name: 'slack-high'
    slack_configs:
      - channel: '#alerts-high'
        title: '⚠️ HIGH: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}{{ end }}'
        color: 'warning'
        send_resolved: true

  - name: 'slack-medium'
    slack_configs:
      - channel: '#alerts-medium'
        title: '⚡ MEDIUM: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
        color: '#439FE0'
        send_resolved: true

  - name: 'slack-data-engineering'
    slack_configs:
      - channel: '#team-data-engineering'
        title: '📊 Data Engineering Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}{{ end }}'

  - name: 'slack-platform'
    slack_configs:
      - channel: '#team-platform'
        title: '🏗️ Platform Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}{{ end }}'

  # Email receivers
  - name: 'email-ops'
    email_configs:
      - to: 'ops-team@example.com'
        from: 'alertmanager@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alertmanager@example.com'
        auth_identity: 'alertmanager@example.com'
        auth_password: 'YOUR_SMTP_PASSWORD'
        headers:
          Subject: '[{{ .Status | toUpper }}] {{ .GroupLabels.alertname }} - Marine Safety'
        html: |
          <h2>Marine Safety Incidents Database Alert</h2>
          {{ range .Alerts }}
          <h3>{{ .Annotations.summary }}</h3>
          <p><strong>Description:</strong> {{ .Annotations.description }}</p>
          <p><strong>Severity:</strong> {{ .Labels.severity }}</p>
          <p><strong>Component:</strong> {{ .Labels.component }}</p>
          <p><strong>Time:</strong> {{ .StartsAt }}</p>
          {{ if .Annotations.runbook_url }}
          <p><a href="{{ .Annotations.runbook_url }}">Runbook</a></p>
          {{ end }}
          {{ if .Annotations.dashboard_url }}
          <p><a href="{{ .Annotations.dashboard_url }}">Dashboard</a></p>
          {{ end }}
          {{ end }}
        send_resolved: true
```

### PagerDuty Integration Details

#### Service Configuration

```yaml
# PagerDuty Service Setup
Service Name: Marine Safety - Production
Integration Type: Prometheus
Escalation Policy: On-Call Engineering
Incident Urgency: High for critical, Low for high severity

# Escalation Policy
Level 1: On-call engineer (immediately)
Level 2: Engineering manager (after 15 minutes)
Level 3: Director of Engineering (after 30 minutes)

# Service Dependencies
- Marine Safety API
- PostgreSQL Database
- Redis Cache
- Worker Queues
```

#### Custom Event Transformer

```python
# Custom PagerDuty event enrichment
# src/worldenergydata/modules/marine_safety/monitoring/pagerduty_enrich.py

import requests
from typing import Dict, Any

def enrich_pagerduty_event(alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich PagerDuty events with additional context
    """
    event = {
        "routing_key": os.getenv("PAGERDUTY_ROUTING_KEY"),
        "event_action": "trigger",
        "payload": {
            "summary": alert["annotations"]["summary"],
            "severity": alert["labels"]["severity"],
            "source": alert["labels"]["instance"],
            "component": alert["labels"]["component"],
            "group": alert["labels"]["alertname"],
            "class": alert["labels"]["team"],
            "custom_details": {
                "description": alert["annotations"]["description"],
                "runbook": alert["annotations"].get("runbook_url", "N/A"),
                "dashboard": alert["annotations"].get("dashboard_url", "N/A"),
                "labels": alert["labels"],
                "firing_alerts": len(alert.get("alerts", [])),
                "environment": "production"
            }
        },
        "links": [
            {
                "href": alert["annotations"].get("dashboard_url", ""),
                "text": "View Dashboard"
            },
            {
                "href": alert["annotations"].get("runbook_url", ""),
                "text": "View Runbook"
            }
        ]
    }

    return event

def send_to_pagerduty(alert: Dict[str, Any]):
    """Send enriched event to PagerDuty"""
    event = enrich_pagerduty_event(alert)

    response = requests.post(
        "https://events.pagerduty.com/v2/enqueue",
        json=event,
        headers={"Content-Type": "application/json"}
    )

    return response.json()
```

---

## Health Checks

### API Health Check Endpoint

```python
# src/worldenergydata/modules/marine_safety/api/health.py

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from redis import Redis
from typing import Dict, Any
import time

router = APIRouter()

def check_database(db: Session) -> Dict[str, Any]:
    """Check database connectivity and performance"""
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        latency = (time.time() - start) * 1000  # ms

        # Check connection pool
        pool = db.bind.pool
        pool_stats = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "overflow": pool.overflow(),
            "checked_out": pool.checkedout()
        }

        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "pool": pool_stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def check_redis(redis_client: Redis) -> Dict[str, Any]:
    """Check Redis connectivity and performance"""
    try:
        start = time.time()
        redis_client.ping()
        latency = (time.time() - start) * 1000

        info = redis_client.info()

        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "memory_used_mb": round(info['used_memory'] / 1024 / 1024, 2),
            "connected_clients": info['connected_clients']
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def check_external_services() -> Dict[str, Any]:
    """Check external service availability"""
    services = {
        "uscg": "https://www.dco.uscg.mil",
        "ntsb": "https://data.ntsb.gov",
        "bts": "https://www.bts.gov"
    }

    results = {}
    for name, url in services.items():
        try:
            start = time.time()
            response = requests.head(url, timeout=5)
            latency = (time.time() - start) * 1000

            results[name] = {
                "status": "healthy" if response.status_code < 500 else "degraded",
                "status_code": response.status_code,
                "latency_ms": round(latency, 2)
            }
        except Exception as e:
            results[name] = {
                "status": "unhealthy",
                "error": str(e)
            }

    return results

@router.get("/health")
async def health_check(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Dict[str, Any]:
    """
    Lightweight health check endpoint
    Returns 200 if service is healthy
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(
    response: Response,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Dict[str, Any]:
    """
    Detailed health check including all dependencies
    Returns 200 if all healthy, 503 if any unhealthy
    """
    checks = {
        "api": {"status": "healthy"},
        "database": check_database(db),
        "redis": check_redis(redis),
        "external_services": check_external_services()
    }

    # Determine overall status
    all_healthy = all(
        check.get("status") == "healthy"
        for component_checks in checks.values()
        for check in (
            [component_checks] if isinstance(component_checks, dict)
            else component_checks.values()
        )
    )

    overall_status = "healthy" if all_healthy else "degraded"

    if not all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": overall_status,
        "timestamp": time.time(),
        "version": "1.0.0",
        "checks": checks
    }

@router.get("/health/ready")
async def readiness_check(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Kubernetes readiness probe
    Checks if service is ready to accept traffic
    """
    try:
        db.execute(text("SELECT 1"))
        return {"ready": True}
    except:
        return {"ready": False}

@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes liveness probe
    Checks if service is alive (doesn't check dependencies)
    """
    return {"alive": True}
```

### Kubernetes Health Check Configuration

```yaml
# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: marine-safety-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: marine-safety-api:latest
        ports:
        - containerPort: 8000

        # Liveness probe - restart if fails
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        # Readiness probe - remove from service if fails
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3

        # Startup probe - allow slow startup
        startupProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 0
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30  # 5 minutes to start
```

### External Monitoring (Uptime Robot)

```yaml
# Uptime Robot Configuration

Monitors:
  - name: "Marine Safety API - Incidents Endpoint"
    type: HTTP(s)
    url: "https://api.marinesafety.example.com/api/v1/incidents"
    interval: 5 minutes
    alert_type: ["email", "pagerduty"]
    expected_status: 200

  - name: "Marine Safety API - Health Check"
    type: HTTP(s)
    url: "https://api.marinesafety.example.com/health"
    interval: 1 minute
    alert_type: ["pagerduty"]
    expected_status: 200

  - name: "Marine Safety Dashboard"
    type: HTTP(s)
    url: "https://dashboard.marinesafety.example.com"
    interval: 5 minutes
    alert_type: ["email"]
    expected_status: 200
    keyword_check: "Marine Safety Incidents"
```

---

## Log Aggregation

### ELK Stack Configuration

#### Filebeat Configuration

```yaml
# /etc/filebeat/filebeat.yml

filebeat.inputs:
  # Application logs
  - type: log
    enabled: true
    paths:
      - /var/log/marine-safety/api/*.log
      - /var/log/marine-safety/scrapers/*.log
      - /var/log/marine-safety/workers/*.log
    fields:
      service: marine-safety
      environment: production
    fields_under_root: true
    multiline:
      pattern: '^\d{4}-\d{2}-\d{2}'
      negate: true
      match: after
    json:
      keys_under_root: true
      add_error_key: true

  # Nginx access logs
  - type: log
    enabled: true
    paths:
      - /var/log/nginx/access.log
    fields:
      service: nginx
      log_type: access

  # Nginx error logs
  - type: log
    enabled: true
    paths:
      - /var/log/nginx/error.log
    fields:
      service: nginx
      log_type: error

  # PostgreSQL logs
  - type: log
    enabled: true
    paths:
      - /var/log/postgresql/postgresql-*.log
    fields:
      service: postgresql
      log_type: database

# Processors
processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_cloud_metadata: ~
  - add_docker_metadata: ~
  - add_kubernetes_metadata: ~
  - drop_fields:
      fields: ["agent.ephemeral_id", "agent.id"]
  - decode_json_fields:
      fields: ["message"]
      target: "json"
      overwrite_keys: true

# Output to Logstash
output.logstash:
  hosts: ["logstash:5044"]
  loadbalance: true
  worker: 2

# Output to Elasticsearch (alternative)
# output.elasticsearch:
#   hosts: ["elasticsearch:9200"]
#   index: "marine-safety-%{+yyyy.MM.dd}"
```

#### Logstash Configuration

```ruby
# /etc/logstash/conf.d/marine-safety.conf

input {
  beats {
    port => 5044
  }
}

filter {
  # Parse JSON logs
  if [service] == "marine-safety" {
    json {
      source => "message"
      target => "parsed"
    }

    # Extract structured fields
    mutate {
      add_field => {
        "log_level" => "%{[parsed][level]}"
        "logger" => "%{[parsed][logger]}"
        "request_id" => "%{[parsed][request_id]}"
      }
    }

    # Parse timestamp
    date {
      match => ["timestamp", "ISO8601"]
      target => "@timestamp"
    }
  }

  # Parse Nginx access logs
  if [log_type] == "access" {
    grok {
      match => {
        "message" => '%{IPORHOST:remote_addr} - %{DATA:remote_user} \[%{HTTPDATE:time_local}\] "%{WORD:request_method} %{DATA:request_path} HTTP/%{NUMBER:http_version}" %{INT:status} %{INT:body_bytes_sent} "%{DATA:http_referer}" "%{DATA:http_user_agent}"'
      }
    }

    mutate {
      convert => {
        "status" => "integer"
        "body_bytes_sent" => "integer"
      }
    }

    geoip {
      source => "remote_addr"
      target => "geoip"
    }
  }

  # Enrich with GeoIP
  if [remote_addr] {
    geoip {
      source => "remote_addr"
      target => "geoip"
    }
  }

  # Add tags for error logs
  if [log_level] == "ERROR" {
    mutate {
      add_tag => ["error"]
    }
  }

  if [log_level] == "CRITICAL" {
    mutate {
      add_tag => ["critical"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "marine-safety-%{+YYYY.MM.dd}"
    document_type => "_doc"
    template_name => "marine-safety"
    template => "/etc/logstash/templates/marine-safety.json"
    template_overwrite => true
  }

  # Send critical errors to separate index for alerting
  if "critical" in [tags] {
    elasticsearch {
      hosts => ["elasticsearch:9200"]
      index => "marine-safety-critical-%{+YYYY.MM.dd}"
    }
  }
}
```

#### Elasticsearch Index Template

```json
{
  "index_patterns": ["marine-safety-*"],
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "index.lifecycle.name": "marine-safety-ilm-policy",
    "index.lifecycle.rollover_alias": "marine-safety"
  },
  "mappings": {
    "properties": {
      "@timestamp": {"type": "date"},
      "service": {"type": "keyword"},
      "environment": {"type": "keyword"},
      "log_level": {"type": "keyword"},
      "logger": {"type": "keyword"},
      "request_id": {"type": "keyword"},
      "message": {"type": "text"},
      "source": {"type": "keyword"},
      "incident_id": {"type": "keyword"},
      "user_id": {"type": "keyword"},
      "endpoint": {"type": "keyword"},
      "method": {"type": "keyword"},
      "status_code": {"type": "integer"},
      "duration_ms": {"type": "float"},
      "error": {
        "properties": {
          "type": {"type": "keyword"},
          "message": {"type": "text"},
          "stack_trace": {"type": "text"}
        }
      },
      "geoip": {
        "properties": {
          "location": {"type": "geo_point"},
          "city_name": {"type": "keyword"},
          "country_code2": {"type": "keyword"}
        }
      }
    }
  }
}
```

#### Index Lifecycle Management (ILM) Policy

```json
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50GB",
            "max_age": "7d"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": {
            "number_of_shards": 1
          },
          "forcemerge": {
            "max_num_segments": 1
          },
          "set_priority": {
            "priority": 50
          }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "freeze": {},
          "set_priority": {
            "priority": 0
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

### Log Retention Policy

```yaml
Retention Rules:
  Hot Tier (ES):
    - Duration: 7 days
    - Performance: High (SSD)
    - Full-text search enabled

  Warm Tier (ES):
    - Duration: 7-30 days
    - Performance: Medium
    - Compressed, read-only

  Cold Tier (ES):
    - Duration: 30-90 days
    - Performance: Low (HDD)
    - Frozen, searchable snapshots

  Archive (S3):
    - Duration: 90 days - 7 years
    - Performance: Very low
    - Compressed, infrequent access

  Delete:
    - After 7 years (compliance requirement)
```

### Kibana Dashboard Configuration

```yaml
# Kibana Saved Searches and Visualizations

Dashboards:
  - name: "Marine Safety - Operations"
    visualizations:
      - "Error Rate by Service"
      - "Request Volume by Endpoint"
      - "P95 Latency by Endpoint"
      - "Geographic Distribution of Requests"
      - "Top Errors"

  - name: "Marine Safety - Scraper Logs"
    visualizations:
      - "Scraper Runs by Source"
      - "Scraper Errors"
      - "Data Quality Issues"
      - "Collection Rate Timeline"

  - name: "Marine Safety - Security"
    visualizations:
      - "Failed Authentication Attempts"
      - "Unusual Access Patterns"
      - "API Rate Limit Hits"
      - "Suspicious IP Addresses"

Saved Searches:
  - name: "Critical Errors"
    query: 'log_level:"CRITICAL"'
    time_range: "Last 24 hours"

  - name: "API 5xx Errors"
    query: 'service:"marine-safety" AND status_code >= 500'
    time_range: "Last 1 hour"

  - name: "Slow Queries"
    query: 'duration_ms > 1000'
    time_range: "Last 1 hour"
```

---

## Distributed Tracing

### OpenTelemetry Configuration

#### Python Instrumentation

```python
# src/worldenergydata/modules/marine_safety/monitoring/tracing.py

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

def setup_tracing(app):
    """
    Configure OpenTelemetry tracing for the application
    """
    # Create resource
    resource = Resource(attributes={
        SERVICE_NAME: "marine-safety-api",
        SERVICE_VERSION: "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production")
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Configure OTLP exporter (sends to OpenTelemetry Collector)
    otlp_exporter = OTLPSpanExporter(
        endpoint="otel-collector:4317",
        insecure=True
    )

    # Add batch span processor
    provider.add_span_processor(
        BatchSpanProcessor(otlp_exporter)
    )

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    # Auto-instrument frameworks
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()
    RequestsInstrumentor().instrument()

    return trace.get_tracer(__name__)

# Manual instrumentation example
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("scrape_uscg_data")
def scrape_uscg_data():
    """Scrape USCG data with distributed tracing"""
    span = trace.get_current_span()
    span.set_attribute("source", "uscg")

    try:
        # Fetch data
        with tracer.start_as_current_span("fetch_uscg_reports"):
            reports = fetch_reports()
            span.set_attribute("reports_count", len(reports))

        # Process data
        with tracer.start_as_current_span("process_reports"):
            processed = process_reports(reports)
            span.set_attribute("processed_count", len(processed))

        # Save to database
        with tracer.start_as_current_span("save_to_database"):
            save_reports(processed)

        span.set_attribute("status", "success")
        return processed

    except Exception as e:
        span.set_attribute("error", True)
        span.set_attribute("error.type", type(e).__name__)
        span.set_attribute("error.message", str(e))
        span.record_exception(e)
        raise
```

#### OpenTelemetry Collector Configuration

```yaml
# /etc/otel-collector/config.yaml

receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024

  memory_limiter:
    check_interval: 1s
    limit_mib: 512

  attributes:
    actions:
      - key: environment
        value: production
        action: insert

  resource:
    attributes:
      - key: service.namespace
        value: marine-safety
        action: insert

  # Tail sampling - keep interesting traces
  tail_sampling:
    decision_wait: 10s
    policies:
      # Always sample errors
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]

      # Always sample slow requests
      - name: slow-requests
        type: latency
        latency:
          threshold_ms: 1000

      # Sample 10% of normal traffic
      - name: normal-traffic
        type: probabilistic
        probabilistic:
          sampling_percentage: 10

exporters:
  # Export to Jaeger
  jaeger:
    endpoint: jaeger-collector:14250
    tls:
      insecure: true

  # Export to Prometheus (metrics from spans)
  prometheus:
    endpoint: "0.0.0.0:8889"
    namespace: otel
    const_labels:
      service: marine-safety

  # Export to logging (debugging)
  logging:
    loglevel: info

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, attributes, resource, tail_sampling]
      exporters: [jaeger, logging]

    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch, attributes, resource]
      exporters: [prometheus]
```

#### Jaeger Query Configuration

```yaml
# docker-compose.yml excerpt

services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    environment:
      - COLLECTOR_ZIPKIN_HTTP_PORT=9411
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
    ports:
      - "5775:5775/udp"     # accept zipkin.thrift over compact thrift protocol
      - "6831:6831/udp"     # accept jaeger.thrift over compact thrift protocol
      - "6832:6832/udp"     # accept jaeger.thrift over binary thrift protocol
      - "5778:5778"         # serve configs
      - "16686:16686"       # serve frontend
      - "14268:14268"       # accept jaeger.thrift directly from clients
      - "14250:14250"       # accept model.proto
      - "9411:9411"         # Zipkin compatible endpoint
```

### Trace Analysis Queries

```yaml
# Common Jaeger queries for troubleshooting

Queries:
  - name: "Find slow API requests"
    query: "service=marine-safety-api AND duration>1s"

  - name: "Find failed scraper runs"
    query: "service=marine-safety-scraper AND error=true"

  - name: "Database query performance"
    query: "operation=db.query AND duration>500ms"

  - name: "External API calls"
    query: "span.kind=client AND http.url=~'.*uscg.mil.*'"

  - name: "Trace full request flow"
    query: "traceID={trace_id}"
```

---

## Performance Monitoring

### Application Performance Monitoring (APM)

#### Sentry Integration

```python
# src/worldenergydata/modules/marine_safety/monitoring/sentry_config.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

def initialize_sentry():
    """Initialize Sentry APM"""
    sentry_sdk.init(
        dsn="https://your-dsn@sentry.io/project-id",
        environment=os.getenv("ENVIRONMENT", "production"),
        release=f"marine-safety@{os.getenv('VERSION', '1.0.0')}",

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=0.1,  # 10% of transactions

        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        profiles_sample_rate=0.1,

        # Integrations
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration()
        ],

        # Before send callback for filtering
        before_send=before_send_filter,

        # Tag all events
        default_integrations=True,
        send_default_pii=False,

        # Performance monitoring
        enable_tracing=True,
    )

def before_send_filter(event, hint):
    """Filter events before sending to Sentry"""
    # Don't send health check errors
    if "health" in event.get("request", {}).get("url", ""):
        return None

    # Add custom context
    event.setdefault("tags", {})
    event["tags"]["service"] = "marine-safety"
    event["tags"]["module"] = "api"

    return event
```

### Query Performance Analysis

```python
# src/worldenergydata/modules/marine_safety/monitoring/query_analyzer.py

from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

logger = logging.getLogger(__name__)

# Track slow queries
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop(-1)

    # Log slow queries
    if total_time > 1.0:  # 1 second threshold
        logger.warning(
            f"Slow query detected",
            extra={
                "duration": total_time,
                "statement": statement,
                "parameters": parameters
            }
        )

    # Track in Prometheus
    db_query_duration.labels(
        query_type=classify_query(statement),
        table=extract_table(statement)
    ).observe(total_time)

def classify_query(statement: str) -> str:
    """Classify query type"""
    statement_upper = statement.upper()
    if statement_upper.startswith("SELECT"):
        return "select"
    elif statement_upper.startswith("INSERT"):
        return "insert"
    elif statement_upper.startswith("UPDATE"):
        return "update"
    elif statement_upper.startswith("DELETE"):
        return "delete"
    else:
        return "other"

def extract_table(statement: str) -> str:
    """Extract primary table from query"""
    # Simple regex-based extraction
    import re
    match = re.search(r'FROM\s+(\w+)', statement, re.IGNORECASE)
    if match:
        return match.group(1)
    return "unknown"
```

### Performance Profiling

```python
# src/worldenergydata/modules/marine_safety/monitoring/profiler.py

import cProfile
import pstats
import io
from functools import wraps
from typing import Callable

def profile_function(output_file: str = None):
    """Decorator to profile a function"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                profiler.disable()

                # Print stats
                s = io.StringIO()
                stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
                stats.print_stats(20)  # Top 20 functions

                print(f"\n{'='*80}")
                print(f"Profile for {func.__name__}")
                print(f"{'='*80}")
                print(s.getvalue())

                # Save to file if specified
                if output_file:
                    stats.dump_stats(output_file)

        return wrapper
    return decorator

# Usage
@profile_function(output_file="/tmp/scraper_profile.prof")
def scrape_all_sources():
    """Profile scraper performance"""
    pass
```

---

## SLO/SLA Tracking

### Service Level Objectives (SLOs)

```yaml
# SLO Definitions

API Availability:
  Target: 99.9%
  Measurement: Successful responses / Total responses
  Window: 30 days
  Error Budget: 0.1% (43.2 minutes/month)

API Latency (p95):
  Target: < 500ms
  Measurement: 95th percentile response time
  Window: 7 days
  Error Budget: 5% of requests can exceed target

API Latency (p99):
  Target: < 2s
  Measurement: 99th percentile response time
  Window: 7 days
  Error Budget: 1% of requests can exceed target

Database Availability:
  Target: 99.95%
  Measurement: Database uptime
  Window: 30 days
  Error Budget: 0.05% (21.6 minutes/month)

Scraper Success Rate:
  Target: 95%
  Measurement: Successful scraper runs / Total runs
  Window: 7 days
  Error Budget: 5% failure rate

Data Freshness:
  Target: < 24 hours
  Measurement: Time since last successful scrape
  Window: Continuous
  Error Budget: 1 source can be stale at a time
```

### SLO Tracking Prometheus Queries

```yaml
# Prometheus recording rules for SLO tracking
# /etc/prometheus/rules/slo_recording_rules.yml

groups:
  - name: slo_recording_rules
    interval: 30s
    rules:
      # API Availability - Success Rate
      - record: slo:api:availability:ratio_rate5m
        expr: |
          sum(rate(http_requests_total{status=~"2..|3.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))

      # API Availability - 30 day window
      - record: slo:api:availability:ratio_rate30d
        expr: |
          sum(rate(http_requests_total{status=~"2..|3.."}[30d]))
          /
          sum(rate(http_requests_total[30d]))

      # API Latency - p95
      - record: slo:api:latency:p95
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          )

      # API Latency - p99
      - record: slo:api:latency:p99
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          )

      # Scraper Success Rate
      - record: slo:scraper:success_rate:ratio_rate7d
        expr: |
          sum(rate(scraper_runs_total{status="success"}[7d]))
          /
          sum(rate(scraper_runs_total[7d]))

      # Error Budget Consumption
      - record: slo:api:error_budget_remaining
        expr: |
          1 - (
            (1 - slo:api:availability:ratio_rate30d) /
            (1 - 0.999)  # Target availability
          )
```

### SLO Dashboard (Grafana)

```json
{
  "dashboard": {
    "title": "Marine Safety - SLO Dashboard",
    "panels": [
      {
        "id": 1,
        "title": "API Availability SLO (99.9%)",
        "type": "gauge",
        "targets": [
          {
            "expr": "slo:api:availability:ratio_rate30d * 100"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 99,
            "max": 100,
            "thresholds": {
              "steps": [
                {"value": 99, "color": "red"},
                {"value": 99.9, "color": "green"}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "Error Budget Remaining",
        "type": "stat",
        "targets": [
          {
            "expr": "slo:api:error_budget_remaining * 100"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 25, "color": "yellow"},
                {"value": 50, "color": "green"}
              ]
            }
          }
        }
      },
      {
        "id": 3,
        "title": "API Latency p95 vs SLO (500ms)",
        "type": "graph",
        "targets": [
          {
            "expr": "slo:api:latency:p95",
            "legendFormat": "Actual p95"
          },
          {
            "expr": "vector(0.5)",
            "legendFormat": "SLO Target"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s"
          }
        }
      },
      {
        "id": 4,
        "title": "Scraper Success Rate vs SLO (95%)",
        "type": "graph",
        "targets": [
          {
            "expr": "slo:scraper:success_rate:ratio_rate7d * 100",
            "legendFormat": "Success Rate"
          },
          {
            "expr": "vector(95)",
            "legendFormat": "SLO Target"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent"
          }
        }
      },
      {
        "id": 5,
        "title": "SLO Compliance Summary (30d)",
        "type": "table",
        "targets": [
          {
            "expr": "slo:api:availability:ratio_rate30d * 100",
            "format": "table",
            "instant": true
          }
        ]
      }
    ]
  }
}
```

### SLO Alerting

```yaml
# /etc/prometheus/rules/slo_alerts.yml

groups:
  - name: slo_alerts
    interval: 1m
    rules:
      # Alert when error budget is being consumed rapidly
      - alert: ErrorBudgetBurnRateFast
        expr: |
          (
            1 - slo:api:availability:ratio_rate5m
          ) > (
            (1 - 0.999) * 14.4  # 14.4x burn rate = budget gone in 2 days
          )
        for: 5m
        labels:
          severity: critical
          slo: availability
        annotations:
          summary: "Fast error budget burn rate"
          description: "At current rate, error budget will be exhausted in 2 days."

      - alert: ErrorBudgetBurnRateSlow
        expr: |
          (
            1 - slo:api:availability:ratio_rate5m
          ) > (
            (1 - 0.999) * 1  # 1x burn rate = budget gone in 30 days
          )
        for: 1h
        labels:
          severity: high
          slo: availability
        annotations:
          summary: "Elevated error budget consumption"
          description: "Error budget being consumed at or above target rate."

      # Alert when SLO is breached
      - alert: SLOViolation_Availability
        expr: slo:api:availability:ratio_rate30d < 0.999
        for: 5m
        labels:
          severity: critical
          slo: availability
        annotations:
          summary: "API Availability SLO violated"
          description: "30-day availability is {{ $value | humanizePercentage }}, below 99.9% target."

      - alert: SLOViolation_Latency_p95
        expr: slo:api:latency:p95 > 0.5
        for: 15m
        labels:
          severity: high
          slo: latency
        annotations:
          summary: "API Latency p95 SLO violated"
          description: "p95 latency is {{ $value }}s, exceeding 500ms target."

      - alert: SLOViolation_ScraperSuccess
        expr: slo:scraper:success_rate:ratio_rate7d < 0.95
        for: 1h
        labels:
          severity: high
          slo: scraper-success
        annotations:
          summary: "Scraper Success Rate SLO violated"
          description: "7-day success rate is {{ $value | humanizePercentage }}, below 95% target."
```

---

## Implementation Roadmap

### Phase 1: Core Monitoring (Week 1-2)

**Objectives:**
- Set up Prometheus and Grafana
- Implement basic metrics collection
- Create operational health dashboard
- Configure critical alerts

**Tasks:**
- [ ] Deploy Prometheus server
- [ ] Deploy Grafana
- [ ] Configure Node Exporter on all servers
- [ ] Instrument API with custom metrics
- [ ] Create "Operational Health" dashboard
- [ ] Set up Alertmanager
- [ ] Configure critical alert rules
- [ ] Test PagerDuty integration
- [ ] Set up Slack notifications

**Deliverables:**
- Prometheus collecting system and application metrics
- Grafana dashboard showing key metrics
- Critical alerts routing to PagerDuty
- Team notifications in Slack

### Phase 2: Log Aggregation (Week 3)

**Objectives:**
- Deploy ELK Stack
- Centralize all logs
- Create log dashboards

**Tasks:**
- [ ] Deploy Elasticsearch cluster
- [ ] Deploy Logstash
- [ ] Deploy Kibana
- [ ] Configure Filebeat on all servers
- [ ] Create Logstash pipelines
- [ ] Define Elasticsearch index templates
- [ ] Set up ILM policies
- [ ] Create Kibana dashboards
- [ ] Configure log retention

**Deliverables:**
- All logs centralized in Elasticsearch
- Kibana dashboards for log analysis
- Log retention automated

### Phase 3: Distributed Tracing (Week 4)

**Objectives:**
- Implement OpenTelemetry
- Deploy Jaeger
- Instrument application code

**Tasks:**
- [ ] Deploy OpenTelemetry Collector
- [ ] Deploy Jaeger backend
- [ ] Instrument FastAPI application
- [ ] Instrument database queries
- [ ] Instrument external API calls
- [ ] Instrument scraper workflows
- [ ] Configure trace sampling
- [ ] Create trace analysis queries

**Deliverables:**
- End-to-end request tracing
- Performance bottleneck identification
- Trace visualization in Jaeger UI

### Phase 4: Advanced Monitoring (Week 5)

**Objectives:**
- Set up APM (Sentry)
- Implement SLO tracking
- Create business metrics dashboards

**Tasks:**
- [ ] Set up Sentry account
- [ ] Instrument error tracking
- [ ] Configure performance monitoring
- [ ] Define SLOs
- [ ] Create SLO tracking queries
- [ ] Build SLO dashboard
- [ ] Create data collection dashboard
- [ ] Create business metrics dashboard
- [ ] Implement query performance analysis

**Deliverables:**
- Error tracking with Sentry
- SLO compliance tracking
- Comprehensive dashboards

### Phase 5: Health Checks & External Monitoring (Week 6)

**Objectives:**
- Implement health check endpoints
- Set up external monitoring
- Configure synthetic monitoring

**Tasks:**
- [ ] Create API health check endpoints
- [ ] Implement dependency health checks
- [ ] Configure Kubernetes probes
- [ ] Set up Uptime Robot monitors
- [ ] Create synthetic test scripts
- [ ] Configure external alerting
- [ ] Test failover scenarios

**Deliverables:**
- Health check system
- External uptime monitoring
- Synthetic monitoring

### Phase 6: Documentation & Training (Week 7)

**Objectives:**
- Document monitoring system
- Create runbooks
- Train team

**Tasks:**
- [ ] Write monitoring system documentation
- [ ] Create runbooks for common alerts
- [ ] Document troubleshooting procedures
- [ ] Create dashboard user guides
- [ ] Conduct team training sessions
- [ ] Create on-call handbook

**Deliverables:**
- Complete monitoring documentation
- Runbooks for all critical alerts
- Trained operations team

### Phase 7: Optimization & Tuning (Week 8)

**Objectives:**
- Optimize alert thresholds
- Reduce false positives
- Improve dashboard performance

**Tasks:**
- [ ] Analyze alert history
- [ ] Tune alert thresholds
- [ ] Optimize Prometheus queries
- [ ] Add query caching
- [ ] Review and consolidate dashboards
- [ ] Implement alert inhibition rules
- [ ] Set up alert testing framework

**Deliverables:**
- Optimized alert rules
- High-performance dashboards
- Reduced alert fatigue

---

## Configuration Examples

### Complete Docker Compose Stack

```yaml
# docker-compose.monitoring.yml

version: '3.8'

services:
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/prometheus/rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - monitoring
    restart: unless-stopped

  # Alertmanager
  alertmanager:
    image: prom/alertmanager:latest
    volumes:
      - ./monitoring/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    networks:
      - monitoring
    restart: unless-stopped

  # Grafana
  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_ROOT_URL=https://grafana.example.com
      - GF_SMTP_ENABLED=true
      - GF_SMTP_HOST=smtp.example.com:587
      - GF_SMTP_USER=grafana@example.com
      - GF_SMTP_PASSWORD=${SMTP_PASSWORD}
    ports:
      - "3000:3000"
    networks:
      - monitoring
    restart: unless-stopped

  # Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    networks:
      - monitoring
    restart: unless-stopped

  # PostgreSQL Exporter
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    environment:
      - DATA_SOURCE_NAME=postgresql://user:password@postgres:5432/marine_safety?sslmode=disable
    ports:
      - "9187:9187"
    networks:
      - monitoring
    restart: unless-stopped

  # Redis Exporter
  redis-exporter:
    image: oliver006/redis_exporter:latest
    environment:
      - REDIS_ADDR=redis:6379
    ports:
      - "9121:9121"
    networks:
      - monitoring
    restart: unless-stopped

  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - monitoring
    restart: unless-stopped

  # Logstash
  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./monitoring/logstash/pipeline:/usr/share/logstash/pipeline
      - ./monitoring/logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml
    ports:
      - "5044:5044"
      - "9600:9600"
    networks:
      - monitoring
    depends_on:
      - elasticsearch
    restart: unless-stopped

  # Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    networks:
      - monitoring
    depends_on:
      - elasticsearch
    restart: unless-stopped

  # Filebeat
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    user: root
    volumes:
      - ./monitoring/filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command: filebeat -e -strict.perms=false
    networks:
      - monitoring
    depends_on:
      - logstash
    restart: unless-stopped

  # OpenTelemetry Collector
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    volumes:
      - ./monitoring/otel/config.yaml:/etc/otel-collector-config.yaml
    command: --config=/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
      - "8889:8889"   # Prometheus exporter
    networks:
      - monitoring
    restart: unless-stopped

  # Jaeger
  jaeger:
    image: jaegertracing/all-in-one:latest
    environment:
      - COLLECTOR_ZIPKIN_HTTP_PORT=9411
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    networks:
      - monitoring
    depends_on:
      - elasticsearch
    restart: unless-stopped

volumes:
  prometheus_data:
  alertmanager_data:
  grafana_data:
  elasticsearch_data:

networks:
  monitoring:
    driver: bridge
```

### Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'marine-safety-production'
    environment: 'production'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# Load rules
rule_files:
  - '/etc/prometheus/rules/*.yml'

# Scrape configurations
scrape_configs:
  # Marine Safety API
  - job_name: 'marine-safety-api'
    static_configs:
      - targets:
          - 'api-server:9090'
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '([^:]+)(?::\d+)?'
        replacement: '${1}'

  # PostgreSQL
  - job_name: 'postgresql'
    static_configs:
      - targets:
          - 'postgres-exporter:9187'

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets:
          - 'redis-exporter:9121'

  # Node Exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets:
          - 'node-exporter:9100'

  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets:
          - 'localhost:9090'

  # Alertmanager
  - job_name: 'alertmanager'
    static_configs:
      - targets:
          - 'alertmanager:9093'

  # OpenTelemetry Collector metrics
  - job_name: 'otel-collector'
    static_configs:
      - targets:
          - 'otel-collector:8889'
```

---

## Appendix

### A. Alert Severity Matrix

| Severity | Response Time | Escalation | Examples |
|----------|--------------|------------|----------|
| **Critical** | Immediate | PagerDuty → On-call | API down, Database down, Memory exhausted |
| **High** | 15 minutes | Slack → Email | High error rate, Slow responses, Scraper failures |
| **Medium** | 1 hour | Slack | Elevated error rate, Cache misses, Queue backlog |
| **Low** | 4 hours | Email | Data lag, Validation failures, Certificate expiry |

### B. Runbook Template

```markdown
# Runbook: [Alert Name]

## Alert Description
[Brief description of what this alert means]

## Severity
[Critical/High/Medium/Low]

## Impact
[What is affected when this alert fires]

## Diagnosis Steps
1. Check [dashboard/logs]
2. Verify [component] status
3. Review [metrics]

## Resolution Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Escalation
If not resolved within [timeframe], escalate to [team/person]

## Related Alerts
- [Related alert 1]
- [Related alert 2]

## Postmortem
[Link to postmortem template if applicable]
```

### C. Metrics Naming Conventions

```yaml
# Prometheus metrics naming best practices

Format: <namespace>_<subsystem>_<name>_<unit>

Examples:
  - http_requests_total          # Counter
  - http_request_duration_seconds # Histogram
  - database_connections_active   # Gauge
  - scraper_success_ratio        # Gauge (0-1)

Labels:
  - Keep cardinality low (<100 unique values)
  - Use consistent label names across metrics
  - Avoid high-cardinality labels (user_id, trace_id)

Reserved Labels:
  - job (scrape job name)
  - instance (target instance)
  - __name__ (metric name)
```

### D. Dashboard Design Best Practices

```yaml
Dashboard Guidelines:
  - One dashboard per audience (ops, dev, business)
  - Group related panels in rows
  - Use consistent time ranges
  - Include SLO targets as threshold lines
  - Add annotations for deployments
  - Use templates for repeated queries
  - Set appropriate refresh rates
  - Add panel descriptions
  - Link to runbooks in panel titles
```

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-03 | System Architecture Designer | Initial comprehensive specification |

---

**Approvals**

- [ ] Technical Review
- [ ] Operations Review
- [ ] Security Review
- [ ] Implementation Approval

---

**Next Steps**

1. Review and approve this specification
2. Provision infrastructure resources
3. Begin Phase 1 implementation
4. Set up development environment
5. Configure test alerts and dashboards

---

**Complete File Path**: `/mnt/github/workspace-hub/worldenergydata/specs/modules/analysis/marine/monitoring-alerting.md`
