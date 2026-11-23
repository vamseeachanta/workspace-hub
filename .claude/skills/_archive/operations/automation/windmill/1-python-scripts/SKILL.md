---
name: windmill-1-python-scripts
description: 'Sub-skill of windmill: 1. Python Scripts.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Python Scripts

## 1. Python Scripts


```python
# scripts/data_processing/fetch_and_transform.py
"""
Fetch data from API and transform for analysis.
Auto-generates UI with input fields for all parameters.
"""

import wmill
from datetime import datetime, timedelta
import requests
import pandas as pd


def main(
    api_endpoint: str,
    date_range_days: int = 7,
    include_metadata: bool = True,
    output_format: str = "json",  # Dropdown: json, csv, parquet
    filters: dict = None,
):
    """
    Fetch and transform data from external API.

    Args:
        api_endpoint: The API endpoint URL to fetch data from
        date_range_days: Number of days of data to fetch (default: 7)
        include_metadata: Whether to include metadata in response
        output_format: Output format - json, csv, or parquet
        filters: Optional filters to apply to the data

    Returns:
        Transformed data in specified format
    """
    # Get API credentials from Windmill resources
    api_credentials = wmill.get_resource("u/admin/api_credentials")

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=date_range_days)

    # Fetch data
    headers = {
        "Authorization": f"Bearer {api_credentials['api_key']}",
        "Content-Type": "application/json"
    }

    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }

    if filters:
        params.update(filters)

    response = requests.get(
        f"{api_endpoint}/data",
        headers=headers,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()

    # Transform with pandas
    df = pd.DataFrame(data["records"])

    # Apply transformations
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date
        df["hour"] = df["timestamp"].dt.hour

    if "value" in df.columns:
        df["value_normalized"] = (df["value"] - df["value"].min()) / (
            df["value"].max() - df["value"].min()
        )

    # Generate summary statistics
    summary = {
        "total_records": len(df),
        "date_range": {
            "start": str(start_date.date()),
            "end": str(end_date.date())
        },
        "statistics": df.describe().to_dict() if not df.empty else {}
    }

    # Format output
    if output_format == "json":
        result = df.to_dict(orient="records")
    elif output_format == "csv":
        result = df.to_csv(index=False)
    else:
        # For parquet, return as dict (Windmill handles serialization)
        result = df.to_dict(orient="records")

    if include_metadata:
        return {
            "data": result,
            "metadata": summary,
            "format": output_format,
            "generated_at": datetime.now().isoformat()
        }

    return result
```

```python
# scripts/integrations/sync_crm_to_database.py
"""
Sync CRM contacts to internal database with deduplication.
"""

import wmill
from typing import Optional
import psycopg2
from psycopg2.extras import execute_values


def main(
    crm_list_id: str,
    batch_size: int = 100,
    dry_run: bool = False,
    update_existing: bool = True,
):
    """
    Sync CRM contacts to PostgreSQL database.

    Args:
        crm_list_id: The CRM list ID to sync
        batch_size: Number of records per batch
        dry_run: If True, don't actually write to database
        update_existing: If True, update existing records

    Returns:
        Sync statistics
    """
    # Get resources
    crm_api = wmill.get_resource("u/admin/crm_api")
    db_conn = wmill.get_resource("u/admin/postgres_warehouse")

    # Fetch contacts from CRM
    import requests
    contacts = []
    page = 1

    while True:
        response = requests.get(
            f"{crm_api['base_url']}/lists/{crm_list_id}/contacts",
            headers={"Authorization": f"Bearer {crm_api['api_key']}"},
            params={"page": page, "per_page": batch_size}
        )
        response.raise_for_status()
        data = response.json()

        contacts.extend(data["contacts"])

        if not data.get("has_more"):
            break
        page += 1

    print(f"Fetched {len(contacts)} contacts from CRM")

    if dry_run:
        return {
            "mode": "dry_run",
            "contacts_fetched": len(contacts),
            "sample": contacts[:5]
        }

    # Connect to database
    conn = psycopg2.connect(
        host=db_conn["host"],
        port=db_conn["port"],
        database=db_conn["database"],
        user=db_conn["user"],
        password=db_conn["password"]
    )

    stats = {"inserted": 0, "updated": 0, "skipped": 0, "errors": []}

    try:
        with conn.cursor() as cur:
            for contact in contacts:

*Content truncated — see parent skill for full reference.*
