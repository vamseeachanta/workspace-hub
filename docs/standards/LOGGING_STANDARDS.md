# Logging Standards

> **Version:** 1.0.0
> **Last Updated:** 2025-10-22
> **Status:** Mandatory for all workspace-hub repositories

## Overview

This document defines mandatory logging standards for all 26 repositories in workspace-hub. Consistent logging enables debugging, monitoring, performance analysis, and operational visibility across all modules.

## Logging Levels

### Standard Levels (All Repositories)

All modules MUST support these five logging levels:

| Level | Value | Purpose | When to Use |
|-------|-------|---------|-------------|
| **DEBUG** | 10 | Detailed diagnostic information | Development, troubleshooting, variable inspection |
| **INFO** | 20 | General informational messages | Normal operations, milestones, confirmations |
| **WARNING** | 30 | Warning messages for potential issues | Deprecated features, recoverable errors, anomalies |
| **ERROR** | 40 | Error messages for serious problems | Failed operations, exceptions, data corruption |
| **CRITICAL** | 50 | Critical messages for system failures | System crashes, data loss, security breaches |

### Level Usage Guidelines

**DEBUG:**
```python
logger.debug("Function called with args: %s", args)
logger.debug("Processing item %d of %d", current, total)
logger.debug("Variable state: x=%s, y=%s", x, y)
```

**INFO:**
```python
logger.info("Starting data processing pipeline")
logger.info("Successfully processed %d records", count)
logger.info("Configuration loaded from %s", config_path)
```

**WARNING:**
```python
logger.warning("Deprecated function called: %s", func_name)
logger.warning("Retry attempt %d of %d", attempt, max_retries)
logger.warning("Missing optional parameter: %s", param_name)
```

**ERROR:**
```python
logger.error("Failed to connect to database: %s", error)
logger.error("Invalid input data: %s", validation_error)
logger.error("File not found: %s", file_path)
```

**CRITICAL:**
```python
logger.critical("System shutdown due to critical error: %s", error)
logger.critical("Data corruption detected in %s", data_source)
logger.critical("Security breach attempt from %s", ip_address)
```

## Log Format Standards

### Standard Format Template

All log messages MUST follow this format:

```
%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s
```

**Example Output:**
```
2025-10-22 14:23:45,123 - data_processor - INFO - [processor.py:45] - Processing started with 1000 records
2025-10-22 14:23:46,234 - data_processor - WARNING - [validator.py:89] - Missing field 'email' in record 42
2025-10-22 14:23:47,345 - data_processor - ERROR - [writer.py:112] - Failed to write to output file: Permission denied
```

### Format Components

| Component | Description | Example |
|-----------|-------------|---------|
| `%(asctime)s` | Timestamp with milliseconds | `2025-10-22 14:23:45,123` |
| `%(name)s` | Logger name (module/class) | `data_processor` |
| `%(levelname)s` | Log level | `INFO`, `ERROR` |
| `%(filename)s` | Source file name | `processor.py` |
| `%(lineno)d` | Line number | `45` |
| `%(message)s` | Log message | `Processing started` |

### Additional Optional Fields

For specific use cases, add these fields:

```python
# With function name
"%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s"

# With process/thread ID
"%(asctime)s - %(name)s - %(levelname)s - [PID:%(process)d TID:%(thread)d] - %(message)s"

# With correlation ID (for distributed systems)
"%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s"
```

## Configuration

### Python Logging Configuration

**Basic Setup (logging_config.py):**
```python
import logging
import sys
from pathlib import Path

def setup_logging(
    level: str = "INFO",
    log_file: Path = None,
    format_string: str = None
):
    """
    Setup logging configuration for module.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for file logging
        format_string: Optional custom format string
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )

    # Create formatter
    formatter = logging.Formatter(
        format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger

# Usage
logger = setup_logging(
    level="DEBUG",
    log_file=Path("logs/app.log")
)
```

**YAML Configuration:**
```yaml
# logging_config.yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    datefmt: "%Y-%m-%d %H:%M:%S"

  detailed:
    format: "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s"
    datefmt: "%Y-%m-%d %H:%M:%S"

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/app.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

  error_file:
    class: logging.FileHandler
    level: ERROR
    formatter: detailed
    filename: logs/errors.log

loggers:
  data_processor:
    level: DEBUG
    handlers: [console, file]
    propagate: false

  api_client:
    level: INFO
    handlers: [console, file]
    propagate: false

root:
  level: INFO
  handlers: [console, file, error_file]
```

**Load YAML Configuration:**
```python
import logging.config
import yaml
from pathlib import Path

def load_logging_config(config_path: Path):
    """Load logging configuration from YAML file."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)

# Usage
load_logging_config(Path("config/logging_config.yaml"))
logger = logging.getLogger(__name__)
```

### JavaScript/TypeScript Logging

**Using winston:**
```javascript
// logger.js
const winston = require('winston');
const path = require('path');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss.SSS'
    }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.printf(({ timestamp, level, message, label, ...meta }) => {
      const metaStr = Object.keys(meta).length ? JSON.stringify(meta) : '';
      return `${timestamp} - ${label || 'app'} - ${level.toUpperCase()} - ${message} ${metaStr}`;
    })
  ),
  defaultMeta: { service: 'app-name' },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 10485760, // 10MB
      maxFiles: 5
    }),
    new winston.transports.File({
      filename: 'logs/combined.log',
      maxsize: 10485760,
      maxFiles: 5
    })
  ]
});

module.exports = logger;

// Usage
const logger = require('./logger');
logger.info('Application started');
logger.error('Failed to connect to database', { error: err.message });
```

### Bash Script Logging

**Using functions:**
```bash
#!/bin/bash

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log file
LOG_FILE="${LOG_FILE:-logs/script.log}"
mkdir -p "$(dirname "$LOG_FILE")"

# Logging functions
log_debug() {
    local message="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] DEBUG - $message" >> "$LOG_FILE"
}

log_info() {
    local message="$1"
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO${NC} - $message"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO - $message" >> "$LOG_FILE"
}

log_warning() {
    local message="$1"
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING${NC} - $message"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING - $message" >> "$LOG_FILE"
}

log_error() {
    local message="$1"
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR${NC} - $message" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR - $message" >> "$LOG_FILE"
}

log_critical() {
    local message="$1"
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] CRITICAL${NC} - $message" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] CRITICAL - $message" >> "$LOG_FILE"
}

# Usage
log_info "Script started"
log_warning "Configuration file not found, using defaults"
log_error "Failed to connect to server"
```

## Log File Management

### File Organization

```
repository/
├── logs/
│   ├── app.log          # General application logs
│   ├── error.log        # Error and critical logs only
│   ├── performance.log  # Performance metrics
│   ├── audit.log        # Audit trail for security events
│   └── archive/         # Archived/rotated logs
│       ├── app.log.1
│       ├── app.log.2
│       └── ...
```

### Rotation Configuration

**Python (using RotatingFileHandler):**
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
```

**System logrotate (/etc/logrotate.d/app):**
```
/path/to/repo/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 user group
}
```

### Log Retention Policy

| Log Type | Retention Period | Rotation |
|----------|-----------------|----------|
| Application logs | 7 days | Daily |
| Error logs | 30 days | Weekly |
| Performance logs | 14 days | Daily |
| Audit logs | 90 days | Monthly |
| Debug logs | 3 days | Daily |

## Structured Logging

### JSON Logging (for machine parsing)

**Python:**
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'user_id'):
            log_obj["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_obj["request_id"] = record.request_id

        return json.dumps(log_obj)

# Setup JSON logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger()
logger.addHandler(handler)

# Usage with extra fields
logger.info("User logged in", extra={"user_id": 12345, "request_id": "abc-123"})
```

**Output:**
```json
{
  "timestamp": "2025-10-22T14:23:45.123456",
  "level": "INFO",
  "logger": "auth_service",
  "message": "User logged in",
  "module": "auth",
  "function": "login",
  "line": 45,
  "user_id": 12345,
  "request_id": "abc-123"
}
```

## Performance Logging

### Execution Time Tracking

**Python Decorator:**
```python
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def log_execution_time(func):
    """Decorator to log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.debug("Starting %s", func.__name__)

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                "Function %s completed in %.3f seconds",
                func.__name__,
                execution_time
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Function %s failed after %.3f seconds: %s",
                func.__name__,
                execution_time,
                str(e)
            )
            raise

    return wrapper

# Usage
@log_execution_time
def process_data(data):
    # Processing logic
    return processed_data
```

### Resource Usage Logging

```python
import logging
import psutil
import os

logger = logging.getLogger(__name__)

def log_resource_usage():
    """Log current resource usage."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    cpu_percent = process.cpu_percent(interval=1)

    logger.info(
        "Resource usage - Memory: %.2f MB, CPU: %.1f%%",
        memory_info.rss / 1024 / 1024,
        cpu_percent
    )

# Call periodically or at key points
log_resource_usage()
```

## Context and Correlation

### Request ID Tracking

**Python (using contextvars):**
```python
import logging
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar('request_id', default='')

class RequestIDFilter(logging.Filter):
    """Add request ID to log records."""

    def filter(self, record):
        record.request_id = request_id_var.get('')
        return True

# Setup
handler = logging.StreamHandler()
handler.addFilter(RequestIDFilter())
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s"
)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)

# Usage
def handle_request(request):
    # Generate and set request ID
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)

    logger.info("Processing request")
    # All subsequent logs will include request_id
```

## Error Logging Best Practices

### Exception Logging

**DO:**
```python
try:
    result = process_data(data)
except ValueError as e:
    logger.error("Invalid data format: %s", e, exc_info=True)
    raise
except IOError as e:
    logger.error("File operation failed: %s", e, exc_info=True)
    raise
```

**DON'T:**
```python
# ❌ Bad: Loses stack trace
try:
    result = process_data(data)
except Exception as e:
    logger.error(str(e))

# ❌ Bad: Too generic
try:
    result = process_data(data)
except Exception:
    logger.error("Something went wrong")
```

### Security-Sensitive Information

**NEVER log:**
- Passwords or API keys
- Credit card numbers
- Social security numbers
- Personal health information
- Session tokens

**Sanitize before logging:**
```python
def sanitize_for_logging(data: dict) -> dict:
    """Remove sensitive fields before logging."""
    sensitive_fields = ['password', 'api_key', 'token', 'ssn']
    sanitized = data.copy()

    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = '***REDACTED***'

    return sanitized

# Usage
logger.info("User data: %s", sanitize_for_logging(user_data))
```

## Module-Specific Loggers

### Logger Naming Convention

```python
# Use __name__ for automatic naming
logger = logging.getLogger(__name__)

# Results in hierarchical names:
# - data_processor
# - data_processor.validator
# - data_processor.writer
```

### Configure Per-Module Levels

```yaml
loggers:
  data_processor:
    level: DEBUG  # Verbose for debugging

  api_client:
    level: WARNING  # Only important messages

  performance_monitor:
    level: INFO  # Standard logging
```

## Testing and Development

### Development Logging

```python
import logging
import sys

def setup_dev_logging():
    """Setup logging for development with enhanced output."""
    logging.basicConfig(
        level=logging.DEBUG,
        format=(
            "\n%(asctime)s\n"
            "%(levelname)s in %(name)s [%(filename)s:%(lineno)d]\n"
            "%(message)s\n" + "-" * 80
        ),
        stream=sys.stdout
    )

# Use in development
if os.getenv('ENVIRONMENT') == 'development':
    setup_dev_logging()
```

### Test Logging

**Capture logs in tests:**
```python
import logging
import pytest

def test_logging(caplog):
    """Test that function logs expected messages."""
    caplog.set_level(logging.INFO)

    result = process_data([1, 2, 3])

    assert "Processing started" in caplog.text
    assert "Processing completed" in caplog.text
    assert caplog.records[0].levelname == "INFO"
```

## Monitoring and Alerting

### Log Aggregation

**Tools:**
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog**
- **CloudWatch** (AWS)
- **Loki** (Grafana)

**Configuration Example (Filebeat):**
```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /path/to/logs/*.log
  fields:
    environment: production
    application: workspace-hub

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "workspace-hub-%{+yyyy.MM.dd}"
```

### Alerting Rules

**Example (Prometheus AlertManager):**
```yaml
groups:
- name: application_logs
  rules:
  - alert: HighErrorRate
    expr: rate(log_messages{level="ERROR"}[5m]) > 10
    for: 5m
    annotations:
      summary: "High error rate detected"
      description: "Error log rate exceeds 10 per minute"

  - alert: CriticalError
    expr: log_messages{level="CRITICAL"} > 0
    for: 1m
    annotations:
      summary: "Critical error detected"
      description: "Critical error logged, immediate action required"
```

## Repository Integration

### Required Files

Each repository must include:

1. **logging_config.yaml** - Logging configuration
2. **logs/.gitignore** - Prevent logs from being committed
   ```
   # Ignore log files but keep directory
   *.log
   *.log.*
   !.gitkeep
   ```
3. **logs/.gitkeep** - Keep logs directory in git

### Integration with YAML Configuration

**Module YAML:**
```yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
  handlers:
    console:
      enabled: true
      level: INFO
    file:
      enabled: true
      path: "logs/module_name.log"
      level: DEBUG
      max_bytes: 10485760  # 10MB
      backup_count: 5
    error_file:
      enabled: true
      path: "logs/errors.log"
      level: ERROR
```

## Compliance Checklist

- [ ] All five logging levels implemented (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- [ ] Standard log format used with timestamps, module name, level, file, line
- [ ] Log files organized in `logs/` directory
- [ ] Log rotation configured (10MB max, 5 backups)
- [ ] Sensitive information sanitized before logging
- [ ] Module-specific loggers used (`__name__`)
- [ ] Performance logging for long-running operations
- [ ] Exception logging with stack traces (`exc_info=True`)
- [ ] Log configuration loaded from YAML
- [ ] Integration with module YAML configuration
- [ ] logs/.gitignore configured
- [ ] Development vs production logging differentiated

---

**Compliance:** This document is mandatory for all workspace-hub repositories. Non-compliance will block PR merges.
