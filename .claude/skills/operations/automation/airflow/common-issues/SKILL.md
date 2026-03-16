---
name: airflow-common-issues
description: 'Sub-skill of airflow: Common Issues (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


**Issue: DAG not appearing in UI**
```bash
# Check for import errors
airflow dags list-import-errors

# Validate DAG file
python dags/my_dag.py

# Check scheduler logs
docker logs airflow-scheduler-1 | grep -i error
```

**Issue: Tasks stuck in queued state**
```bash
# Check worker status
airflow celery status

# Verify executor configuration
airflow config get-value core executor

# Check for resource constraints
kubectl top pods -n airflow
```

**Issue: XCom size limits**
```python
# Use external storage for large data
def store_large_result(**context):
    # Store in S3 instead of XCom
    s3_hook.load_string(large_data, key='results/data.json', bucket='my-bucket')
    return 's3://my-bucket/results/data.json'  # Return reference only
```

**Issue: Scheduler performance**
```yaml
# Tune scheduler settings
AIRFLOW__SCHEDULER__PARSING_PROCESSES: 4
AIRFLOW__SCHEDULER__MIN_FILE_PROCESS_INTERVAL: 30
AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL: 60
```


## Debugging Tips


```python
# Add detailed logging
import logging
logger = logging.getLogger(__name__)

def my_task(**context):
    logger.info(f"Starting task with context: {context}")
    # ... task logic
    logger.debug(f"Intermediate result: {result}")
```

```bash
# Test specific task
airflow tasks test my_dag my_task 2026-01-15

# Clear task state for re-run
airflow tasks clear my_dag -t my_task -s 2026-01-15 -e 2026-01-15

# Trigger DAG run
airflow dags trigger my_dag --conf '{"key": "value"}'
```
