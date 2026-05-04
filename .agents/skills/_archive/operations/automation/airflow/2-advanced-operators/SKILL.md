---
name: airflow-2-advanced-operators
description: 'Sub-skill of airflow: 2. Advanced Operators (+6).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 2. Advanced Operators (+6)

## 2. Advanced Operators


```python
# dags/advanced_operators.py
"""
DAG demonstrating advanced operator patterns.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

*See sub-skills for full details.*

## 3. Sensors for Event-Driven Workflows


```python
# dags/sensor_patterns.py
"""
DAG demonstrating sensor patterns for event-driven workflows.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor

*See sub-skills for full details.*

## 4. Hooks for External System Integration


```python
# dags/hooks_demo.py
"""
DAG demonstrating hook patterns for external system integration.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

*See sub-skills for full details.*

## 5. XCom for Task Communication


```python
# dags/xcom_patterns.py
"""
DAG demonstrating XCom patterns for inter-task communication.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import XCom


*See sub-skills for full details.*

## 6. Variables and Connections


```python
# dags/config_management.py
"""
DAG demonstrating Variables and Connections for configuration.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.hooks.base import BaseHook

*See sub-skills for full details.*

## 7. Error Handling and Callbacks


```python
# dags/error_handling.py
"""
DAG demonstrating error handling and callback patterns.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule

*See sub-skills for full details.*

## 8. Docker and Kubernetes Deployment


```yaml
# docker-compose.yml - Production-ready Airflow deployment
version: '3.8'

x-airflow-common:
  &airflow-common
  image: apache/airflow:2.8.1
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor

*See sub-skills for full details.*
