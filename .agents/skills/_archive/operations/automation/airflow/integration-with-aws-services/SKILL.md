---
name: airflow-integration-with-aws-services
description: 'Sub-skill of airflow: Integration with AWS Services.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Integration with AWS Services

## Integration with AWS Services


```python
# dags/aws_integration.py
"""
DAG integrating with AWS services.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.athena import AthenaOperator

default_args = {
    'owner': 'data-team',
    'retries': 2,
}

with DAG(
    dag_id='aws_integration_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['aws', 'integration'],
) as dag:

    # Upload to S3
    upload_to_s3 = LocalFilesystemToS3Operator(
        task_id='upload_to_s3',
        filename='/data/output/{{ ds }}/data.parquet',
        dest_key='raw/{{ ds }}/data.parquet',
        dest_bucket='my-data-lake',
        aws_conn_id='aws_default',
        replace=True,
    )

    # Run Glue ETL job
    run_glue_job = GlueJobOperator(
        task_id='run_glue_etl',
        job_name='my-etl-job',
        script_args={
            '--input_path': 's3://my-data-lake/raw/{{ ds }}/',
            '--output_path': 's3://my-data-lake/processed/{{ ds }}/',
        },
        aws_conn_id='aws_default',
        wait_for_completion=True,
    )

    # Query with Athena
    run_athena_query = AthenaOperator(
        task_id='run_athena_analysis',
        query="""
            SELECT date, COUNT(*) as count, SUM(value) as total
            FROM processed_data
            WHERE partition_date = '{{ ds }}'
            GROUP BY date
        """,
        database='analytics',
        output_location='s3://my-data-lake/athena-results/',
        aws_conn_id='aws_default',
    )

    # Load to Redshift
    load_to_redshift = S3ToRedshiftOperator(
        task_id='load_to_redshift',
        schema='public',
        table='fact_daily_metrics',
        s3_bucket='my-data-lake',
        s3_key='processed/{{ ds }}/',
        redshift_conn_id='redshift_warehouse',
        aws_conn_id='aws_default',
        copy_options=['FORMAT AS PARQUET'],
    )

    upload_to_s3 >> run_glue_job >> run_athena_query >> load_to_redshift
```
