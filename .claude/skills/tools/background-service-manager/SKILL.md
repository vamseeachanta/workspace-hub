---
name: background-service-manager
description: Create and manage long-running background processes with start/stop/status controls, logging, and monitoring. Use for batch processing jobs, data pipelines, continuous services, or any long-running tasks.
---

# Background Service Manager Skill

## Overview

This skill creates service management scripts for long-running background processes. Includes start/stop controls, PID management, log rotation, status monitoring, and graceful shutdown handling.

## When to Use

- Running long batch processing jobs (extraction, embedding, ETL)
- Managing continuous data pipelines
- Background workers for queues or scheduled tasks
- Any process that needs to run for hours/days
- Services requiring monitoring and restart capabilities

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Service Manager Script              │
├─────────────────────────────────────────────────┤
│  start    │  stop    │  status  │  restart     │
└─────┬─────┴────┬─────┴────┬─────┴──────┬───────┘
      │          │          │            │
      ▼          ▼          ▼            ▼
┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────────┐
│ PID File │ │  Kill  │ │ Check  │ │ Stop + Start │
│ + nohup  │ │Process │ │  PID   │ │              │
└──────────┘ └────────┘ └────────┘ └──────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│           Log Files                   │
│  /tmp/service.log  /tmp/service.pid  │
└──────────────────────────────────────┘
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
SERVICE_CMD="python3 ${SCRIPT_DIR}/worker.py"

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "Already running (PID: $(cat $PID_FILE))"
        return 1
    fi

    echo "Starting ${SERVICE_NAME}..."
    nohup $SERVICE_CMD >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Started (PID: $!)"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Not running (no PID file)"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping ${SERVICE_NAME} (PID: $PID)..."
        kill "$PID"

        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done

        # Force kill if still running
        if kill -0 "$PID" 2>/dev/null; then
            echo "Force killing..."
            kill -9 "$PID"
        fi

        rm -f "$PID_FILE"
        echo "Stopped"
    else
        echo "Process not running, cleaning up PID file"
        rm -f "$PID_FILE"
    fi
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Running (PID: $PID)"

            # Show resource usage
            ps -p "$PID" -o pid,pcpu,pmem,etime,cmd --no-headers 2>/dev/null
            return 0
        else
            echo "Not running (stale PID file)"
            return 1
        fi
    else
        echo "Not running"
        return 1
    fi
}

restart() {
    stop
    sleep 2
    start
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "No log file found: $LOG_FILE"
    fi
}

case "$1" in
    start)   start ;;
    stop)    stop ;;
    status)  status ;;
    restart) restart ;;
    logs)    logs ;;
    *)
        echo "Usage: $0 {start|stop|status|restart|logs}"
        exit 1
        ;;
esac
```

### Multi-Service Manager

```bash
#!/bin/bash
# services.sh - Manage multiple services

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Define services
declare -A SERVICES=(
    ["extract"]="python3 ${SCRIPT_DIR}/extract.py"
    ["embed"]="python3 ${SCRIPT_DIR}/embed.py"
    ["api"]="python3 ${SCRIPT_DIR}/api.py"
)

get_pid_file() {
    echo "/tmp/${1}.pid"
}

get_log_file() {
    echo "/tmp/${1}.log"
}

start_service() {
    local name="$1"
    local cmd="${SERVICES[$name]}"
    local pid_file=$(get_pid_file "$name")
    local log_file=$(get_log_file "$name")

    if [ -z "$cmd" ]; then
        echo "Unknown service: $name"
        return 1
    fi

    if [ -f "$pid_file" ] && kill -0 $(cat "$pid_file") 2>/dev/null; then
        echo "$name: Already running"
        return 1
    fi

    echo "Starting $name..."
    nohup $cmd >> "$log_file" 2>&1 &
    echo $! > "$pid_file"
    echo "$name: Started (PID: $!)"
}

stop_service() {
    local name="$1"
    local pid_file=$(get_pid_file "$name")

    if [ ! -f "$pid_file" ]; then
        echo "$name: Not running"
        return 1
    fi

    local pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        rm -f "$pid_file"
        echo "$name: Stopped"
    else
        rm -f "$pid_file"
        echo "$name: Already stopped (cleaned PID file)"
    fi
}

status_all() {
    echo "Service Status:"
    echo "─────────────────────────────────"
    for name in "${!SERVICES[@]}"; do
        local pid_file=$(get_pid_file "$name")
        if [ -f "$pid_file" ] && kill -0 $(cat "$pid_file") 2>/dev/null; then
            printf "  %-12s  ● Running (PID: %s)\n" "$name" "$(cat $pid_file)"
        else
            printf "  %-12s  ○ Stopped\n" "$name"
        fi
    done
}

start_all() {
    for name in "${!SERVICES[@]}"; do
        start_service "$name"
    done
}

stop_all() {
    for name in "${!SERVICES[@]}"; do
        stop_service "$name"
    done
}

case "$1" in
    start)
        if [ -n "$2" ]; then
            start_service "$2"
        else
            start_all
        fi
        ;;
    stop)
        if [ -n "$2" ]; then
            stop_service "$2"
        else
            stop_all
        fi
        ;;
    status)  status_all ;;
    restart)
        stop_all
        sleep 2
        start_all
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart} [service_name]"
        echo ""
        echo "Available services:"
        for name in "${!SERVICES[@]}"; do
            echo "  - $name"
        done
        ;;
esac
```

### Status Dashboard Script

```bash
#!/bin/bash
# status.sh - Rich status display

DB_PATH="${1:-./database.db}"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

print_header() {
    echo -e "${BLUE}${BOLD}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}${BOLD}       SERVICE STATUS DASHBOARD${NC}"
    echo -e "${BLUE}${BOLD}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

print_section() {
    echo -e "${CYAN}${BOLD}$1${NC}"
}

check_process() {
    local name="$1"
    local pid_file="/tmp/${name}.pid"

    if [ -f "$pid_file" ] && kill -0 $(cat "$pid_file") 2>/dev/null; then
        echo -e "   ${name}:  ${GREEN}●${NC} Running (PID: $(cat $pid_file))"
    else
        echo -e "   ${name}:  ${YELLOW}○${NC} Not running"
    fi
}

get_db_stats() {
    if [ -f "$DB_PATH" ]; then
        local total=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM documents" 2>/dev/null || echo "0")
        local extracted=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM documents WHERE extracted=1" 2>/dev/null || echo "0")
        local chunks=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM chunks" 2>/dev/null || echo "0")

        echo -e "   Total Documents:  ${BOLD}${total}${NC}"
        echo -e "   Extracted:        ${BOLD}${extracted}${NC}"
        echo -e "   Total Chunks:     ${BOLD}${chunks}${NC}"
    else
        echo -e "   ${YELLOW}Database not found${NC}"
    fi
}

show_recent_logs() {
    local log_file="$1"
    local lines="${2:-3}"

    if [ -f "$log_file" ]; then
        echo "   $(tail -1 "$log_file" | cut -c1-60)..."
    else
        echo "   No logs available"
    fi
}

# Main display
print_header

echo -e "${CYAN}${BOLD}📊 Database Statistics${NC}"
get_db_stats
echo ""

echo -e "${CYAN}${BOLD}⚙️  Background Processes${NC}"
check_process "extract"
check_process "embed"
check_process "api"
echo ""

echo -e "${CYAN}${BOLD}📈 Recent Activity${NC}"
echo -n "   Last extract: "
show_recent_logs "/tmp/extract.log"
echo -n "   Last embed:   "
show_recent_logs "/tmp/embed.log"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
```

### Python Service Wrapper

```python
#!/usr/bin/env python3
"""Python service with graceful shutdown."""

import signal
import sys
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GracefulShutdown:
    """Handle graceful shutdown on SIGTERM/SIGINT."""

    def __init__(self):
        self.shutdown_requested = False
        signal.signal(signal.SIGTERM, self._handler)
        signal.signal(signal.SIGINT, self._handler)

    def _handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown_requested = True

    @property
    def should_continue(self):
        return not self.shutdown_requested


def main():
    shutdown = GracefulShutdown()
    logger.info("Service started")

    try:
        while shutdown.should_continue:
            # Your main processing loop
            do_work()

            # Check for shutdown between iterations
            if shutdown.shutdown_requested:
                break

            time.sleep(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        cleanup()
        logger.info("Service stopped")


def do_work():
    """Main work function - customize this."""
    pass


def cleanup():
    """Cleanup on shutdown - customize this."""
    pass


if __name__ == '__main__':
    main()
```

## Best Practices

1. **Always use PID files** - Track running processes reliably
2. **Implement graceful shutdown** - Handle SIGTERM properly
3. **Log to files** - Use `/tmp/` or dedicated log directory
4. **Check before start** - Prevent duplicate instances
5. **Clean stale PIDs** - Remove orphaned PID files
6. **Add status monitoring** - Show resource usage
7. **Support restart** - Stop + start in one command
8. **Environment variables** - Configure via env, not hardcoded

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

- `pdf-text-extractor` - Long-running extraction job
- `semantic-search-setup` - Embedding generation service
- `knowledge-base-builder` - Background indexing

---

## Version History

- **1.0.0** (2024-10-15): Initial release with service manager scripts, multi-service support, status dashboard, Python wrapper, graceful shutdown handling
