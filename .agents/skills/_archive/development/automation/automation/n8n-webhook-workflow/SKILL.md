---
name: automation-n8n-webhook-workflow
description: 'Sub-skill of automation: n8n Webhook Workflow (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# n8n Webhook Workflow (+3)

## n8n Webhook Workflow


```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "incoming-data",
        "httpMethod": "POST"
      }

*See sub-skills for full details.*

## Airflow DAG Definition


```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

*See sub-skills for full details.*

## GitHub Actions Workflow


```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:

*See sub-skills for full details.*

## Windmill Script Workflow


```typescript
// windmill script with auto-generated UI
export async function main(
  database_url: string,
  table_name: string,
  limit: number = 100
): Promise<Record<string, any>[]> {
  const client = new Client(database_url);

  const result = await client.query(

*See sub-skills for full details.*
