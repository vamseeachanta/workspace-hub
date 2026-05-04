---
name: background-service-manager
description: Create and manage long-running background processes with start/stop/status
  controls, logging, and monitoring. Use for batch processing jobs, data pipelines,
  continuous services, or any long-running tasks.
type: reference
version: 2.0.0
category: operations
last_updated: 2026-01-02
related_skills:
- semantic-search-setup
- knowledge-base-builder
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Background Service Manager

## Overview

This skill creates service management scripts for long-running background processes. Includes start/stop controls, PID management, log rotation, status monitoring, and graceful shutdown handling.

## Quick Start

1. **Create service script** - Copy the basic template below
2. **Customize command** - Set `SERVICE_CMD` to your process
3. **Make executable** - `chmod +x service.sh`
4. **Start service** - `./service.sh start`
5. **Monitor** - `./service.sh status` or `./service.sh logs`

```bash
#!/bin/bash
# Quick service wrapper
SERVICE_NAME="myservice"
PID_FILE="/tmp/${SERVICE_NAME}.pid"
LOG_FILE="/tmp/${SERVICE_NAME}.log"
SERVICE_CMD="python3 ./worker.py"

case "$1" in
    start)
        nohup $SERVICE_CMD >> "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "Started (PID: $!)"
        ;;
    stop)
        [ -f "$PID_FILE" ] && kill $(cat "$PID_FILE") && rm "$PID_FILE"
        ;;
    status)
        [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null && echo "Running" || echo "Stopped"
        ;;
    *) echo "Usage: $0 {start|stop|status}" ;;
esac
```

## When to Use

- Running long batch processing jobs (extraction, embedding, ETL)
- Managing continuous data pipelines
- Background workers for queues or scheduled tasks
- Any process that needs to run for hours/days
- Services requiring monitoring and restart capabilities

## Architecture

```
+-------------------------------------------------+
|              Service Manager Script              |
+-------------------------------------------------+
|  start    |  stop    |  status  |  restart     |
+-----+-----+----+-----+----+-----+------+-------+
      |          |          |            |
      v          v          v            v
+----------+ +--------+ +--------+ +--------------+
| PID File | |  Kill  | | Check  | | Stop + Start |
| + nohup  | |Process | |  PID   | |              |
+----------+ +--------+ +--------+ +--------------+
      |
      v
+--------------------------------------+
|           Log Files                   |
|  /tmp/service.log  /tmp/service.pid  |
+--------------------------------------+
```

## Implementation

### Basic Service Script

```bash
#!/bin/bash
# service.sh - Generic service manager

SERVICE_NAME="myservice"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="/tmp/${SERVICE_NAME}.pid"
LOG_FILE="/tmp/${SERVICE_NAME}.log"

# Command to run (customize this)

*See sub-skills for full details.*
### Multi-Service Manager

```bash
#!/bin/bash
# services.sh - Manage multiple services

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Define services
declare -A SERVICES=(
    ["extract"]="python3 ${SCRIPT_DIR}/extract.py"
    ["embed"]="python3 ${SCRIPT_DIR}/embed.py"

*See sub-skills for full details.*
### Status Dashboard Script

```bash
#!/bin/bash
# status.sh - Rich status display

DB_PATH="${1:-./database.db}"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'

*See sub-skills for full details.*
### Python Service Wrapper

```python
#!/usr/bin/env python3
"""Python service with graceful shutdown."""

import signal
import sys
import time
import logging

logging.basicConfig(

*See sub-skills for full details.*

## Example Usage

```bash
# Single service
./service.sh start
./service.sh status
./service.sh logs
./service.sh stop

# Multiple services
./services.sh start           # Start all
./services.sh start extract   # Start specific
./services.sh status          # Show all status
./services.sh stop            # Stop all

# Status dashboard
./status.sh
```

## Related Skills

- [pdf/text-extractor](../../document-handling/pdf/text-extractor/SKILL.md) - Long-running extraction job
- [semantic-search-setup](../../document-handling/semantic-search-setup/SKILL.md) - Embedding generation service
- [knowledge-base-builder](../../document-handling/knowledge-base-builder/SKILL.md) - Background indexing

---

## Version History

- **2.0.0** (2026-01-02): Upgraded to v2 template - added Quick Start, Execution Checklist, Error Handling, Metrics sections; enhanced frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with service manager scripts, multi-service support, status dashboard, Python wrapper, graceful shutdown handling

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)
