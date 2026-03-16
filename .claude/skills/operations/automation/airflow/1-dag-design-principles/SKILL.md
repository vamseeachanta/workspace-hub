---
name: airflow-1-dag-design-principles
description: 'Sub-skill of airflow: 1. DAG Design Principles (+3).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. DAG Design Principles (+3)

## 1. DAG Design Principles

```python
# Use meaningful DAG and task IDs
dag_id='sales_daily_etl_pipeline'  # Good
dag_id='dag1'  # Bad

# Set appropriate concurrency limits
max_active_runs=1  # For data pipelines with dependencies
max_active_tasks_per_dag=16  # Limit resource usage

# Use tags for organization
tags=['production', 'etl', 'sales']

# Always set catchup=False unless backfill needed
catchup=False

# Use execution_timeout to prevent stuck tasks
execution_timeout=timedelta(hours=2)
```


## 2. Task Best Practices

```python
# Keep tasks atomic and idempotent
def process_partition(partition_date: str):
    """Idempotent: can be safely re-run."""
    # Delete existing data for this partition
    delete_partition(partition_date)
    # Process and insert new data
    insert_data(partition_date)

# Use retries with exponential backoff
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
}

# Avoid heavy processing in sensors
# Bad: sensor does complex computation
# Good: sensor checks simple condition, processing in separate task
```


## 3. Configuration Management

```python
# Use Variables for configuration, not hardcoded values
batch_size = Variable.get('batch_size', default_var=1000)

# Use Connections for credentials
conn = BaseHook.get_connection('my_database')

# Environment-specific configuration
env = Variable.get('environment')
config = Variable.get(f'config_{env}', deserialize_json=True)
```


## 4. Testing DAGs

```python
# tests/test_dags.py
import pytest
from airflow.models import DagBag

def test_dag_loads():
    """Test that DAGs load without errors."""
    dagbag = DagBag()
    assert len(dagbag.import_errors) == 0

def test_dag_structure():
    """Test DAG has expected structure."""
    dagbag = DagBag()
    dag = dagbag.get_dag('my_pipeline')

    assert dag is not None
    assert len(dag.tasks) == 5
    assert dag.schedule_interval == '@daily'
```
