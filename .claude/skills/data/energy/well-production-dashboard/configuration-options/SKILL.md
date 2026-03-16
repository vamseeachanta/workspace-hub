---
name: well-production-dashboard-configuration-options
description: 'Sub-skill of well-production-dashboard: Configuration Options.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Configuration Options

## Configuration Options


| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `title` | string | "Well Production Dashboard" | Dashboard title |
| `enable_verification` | bool | True | Enable data verification |
| `enable_real_time` | bool | False | Real-time updates |
| `cache_ttl` | int | 300 | Cache lifetime (seconds) |
| `quality_threshold` | float | 0.8 | Minimum quality score |
| `websocket_port` | int | 8765 | WebSocket port |
| `api_port` | int | 5000 | REST API port |
| `auth_enabled` | bool | True | Enable authentication |
| `export_formats` | list | ['pdf', 'excel'] | Available exports |
