---
name: airflow-1-basic-dag-structure
description: 'Sub-skill of airflow: 1. Basic DAG Structure.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Basic DAG Structure

## 1. Basic DAG Structure


```python
# dags/basic_dag.py
"""
Basic DAG demonstrating core Airflow concepts.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

# Default arguments for all tasks
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['alerts@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
    'execution_timeout': timedelta(hours=2),
}

# DAG definition
with DAG(
    dag_id='basic_etl_pipeline',
    default_args=default_args,
    description='Basic ETL pipeline demonstrating core patterns',
    schedule_interval='0 6 * * *',  # Daily at 6 AM
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['etl', 'production'],
    doc_md="""
