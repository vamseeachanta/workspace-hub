# API Specification

This is the API specification for the spec detailed in @specs/modules/analysis/well-data-verification/spec.md

> Created: 2025-01-13
> Version: 1.0.0
> Module: Analysis

## API Overview

The Well Data Verification API provides RESTful endpoints for data validation, quality checking, and verification workflow management.

### Base URL
```
/api/v1/verification
```

### Authentication
- Bearer token authentication required for all endpoints
- Tokens expire after 24 hours
- Role-based access control enforced

### Response Format
All responses follow JSON:API specification with consistent structure:
```json
{
    "data": {},
    "meta": {
        "timestamp": "2025-01-13T10:30:00Z",
        "version": "1.0.0"
    },
    "errors": []
}
```

## Endpoints

### 1. Verification Sessions

#### POST /sessions
**Purpose:** Create a new verification session
**Parameters:**
```json
{
    "wells": ["W-001", "W-002"],
    "rules": ["production_volume", "completeness"],
    "date_range": {
        "start": "2024-01-01",
        "end": "2024-12-31"
    }
}
```
**Response:**
```json
{
    "session_id": "uuid-12345",
    "status": "initialized",
    "created_at": "2025-01-13T10:30:00Z"
}
```
**Errors:** 400 (Invalid parameters), 401 (Unauthorized)

#### GET /sessions/{session_id}
**Purpose:** Get verification session status
**Response:**
```json
{
    "session_id": "uuid-12345",
    "status": "in_progress",
    "progress": 45,
    "current_step": "validating_production",
    "wells_processed": 150,
    "wells_total": 300
}
```
**Errors:** 404 (Session not found), 401 (Unauthorized)

#### PUT /sessions/{session_id}/pause
**Purpose:** Pause verification session
**Response:**
```json
{
    "session_id": "uuid-12345",
    "status": "paused",
    "checkpoint": "step_3_of_7"
}
```
**Errors:** 404 (Session not found), 409 (Cannot pause)

#### PUT /sessions/{session_id}/resume
**Purpose:** Resume paused session
**Response:**
```json
{
    "session_id": "uuid-12345",
    "status": "in_progress",
    "resumed_from": "step_3_of_7"
}
```
**Errors:** 404 (Session not found), 409 (Not paused)

### 2. Validation Rules

#### GET /rules
**Purpose:** List available validation rules
**Response:**
```json
{
    "rules": [
        {
            "id": "production_volume",
            "name": "Production Volume Validation",
            "description": "Validates oil and gas production volumes",
            "configurable": true
        },
        {
            "id": "completeness",
            "name": "Data Completeness Check",
            "description": "Checks for missing required fields",
            "configurable": false
        }
    ]
}
```
**Errors:** 401 (Unauthorized)

#### GET /rules/{rule_id}
**Purpose:** Get rule details and configuration
**Response:**
```json
{
    "id": "production_volume",
    "configuration": {
        "oil_min": 0,
        "oil_max": 100000,
        "gas_min": 0,
        "gas_max": 1000000,
        "units": "bbl/day"
    }
}
```
**Errors:** 404 (Rule not found)

#### POST /rules/custom
**Purpose:** Create custom validation rule
**Parameters:**
```json
{
    "name": "Custom Price Check",
    "expression": "oil_price > 0 AND oil_price < 200",
    "error_message": "Oil price out of expected range"
}
```
**Response:**
```json
{
    "rule_id": "custom_001",
    "status": "created"
}
```
**Errors:** 400 (Invalid rule), 403 (Insufficient permissions)

### 3. Data Quality

#### POST /quality/check
**Purpose:** Run quality check on specific wells
**Parameters:**
```json
{
    "wells": ["W-001", "W-002"],
    "checks": ["anomaly", "completeness", "consistency"]
}
```
**Response:**
```json
{
    "quality_score": 85.5,
    "issues": [
        {
            "well_id": "W-001",
            "type": "anomaly",
            "severity": "warning",
            "description": "Production spike detected",
            "date": "2024-06-15"
        }
    ]
}
```
**Errors:** 400 (Invalid parameters)

#### GET /quality/metrics
**Purpose:** Get quality metrics for dataset
**Parameters:**
- `start_date`: ISO date string
- `end_date`: ISO date string
- `field`: Optional field filter
**Response:**
```json
{
    "completeness": 98.5,
    "accuracy": 95.2,
    "consistency": 97.8,
    "timeliness": 99.1,
    "overall_score": 97.7
}
```
**Errors:** 400 (Invalid date range)

### 4. Cross-Reference

#### POST /crossref/excel
**Purpose:** Cross-reference with Excel benchmark
**Parameters:**
```json
{
    "excel_file_id": "file_12345",
    "wells": ["W-001", "W-002"],
    "tolerance": 0.01
}
```
**Response:**
```json
{
    "matches": 95,
    "discrepancies": [
        {
            "well_id": "W-001",
            "field": "oil_production",
            "database_value": 1000,
            "excel_value": 1050,
            "difference": 50
        }
    ]
}
```
**Errors:** 404 (File not found), 400 (Invalid format)

### 5. Reports

#### POST /reports/generate
**Purpose:** Generate verification report
**Parameters:**
```json
{
    "session_id": "uuid-12345",
    "format": "pdf",
    "include": ["summary", "details", "charts"]
}
```
**Response:**
```json
{
    "report_id": "report_789",
    "status": "generating",
    "estimated_time": 30
}
```
**Errors:** 404 (Session not found), 400 (Invalid format)

#### GET /reports/{report_id}
**Purpose:** Download generated report
**Response:** Binary file (PDF or Excel)
**Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="verification_report.pdf"
```
**Errors:** 404 (Report not found), 202 (Still generating)

### 6. Audit Trail

#### GET /audit/activities
**Purpose:** Get audit trail activities
**Parameters:**
- `session_id`: Optional session filter
- `user_id`: Optional user filter
- `start_date`: ISO date string
- `end_date`: ISO date string
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 100)
**Response:**
```json
{
    "activities": [
        {
            "id": "activity_001",
            "timestamp": "2025-01-13T10:30:00Z",
            "user": "john.doe",
            "action": "validation_started",
            "details": {
                "wells_count": 150,
                "rules_applied": ["production_volume"]
            }
        }
    ],
    "pagination": {
        "page": 1,
        "total_pages": 5,
        "total_items": 450
    }
}
```
**Errors:** 403 (Insufficient permissions)

## WebSocket API

### Real-time Updates
```javascript
// WebSocket endpoint
ws://api/v1/verification/ws

// Subscribe to session updates
{
    "action": "subscribe",
    "session_id": "uuid-12345"
}

// Receive updates
{
    "type": "progress",
    "session_id": "uuid-12345",
    "progress": 75,
    "wells_processed": 225
}
```

## Error Codes

| Code | Description |
|------|-------------|
| VER_001 | Invalid well identifier |
| VER_002 | Validation rule not found |
| VER_003 | Session already exists |
| VER_004 | Cannot modify active session |
| VER_005 | Insufficient permissions |
| VER_006 | Data quality check failed |
| VER_007 | Excel file format invalid |
| VER_008 | Report generation failed |

## Rate Limiting

- 1000 requests per hour per API key
- 100 concurrent sessions per account
- 10 report generations per hour

## SDK Examples

### Python
```python
from worldenergydata.verification import VerificationClient

client = VerificationClient(api_key="your_key")

# Start verification
session = client.create_session(
    wells=["W-001", "W-002"],
    rules=["production_volume"]
)

# Check progress
status = client.get_session_status(session.id)
print(f"Progress: {status.progress}%")

# Generate report
report = client.generate_report(
    session_id=session.id,
    format="pdf"
)
```

### JavaScript
```javascript
const client = new VerificationClient({
    apiKey: 'your_key'
});

// Start verification
const session = await client.createSession({
    wells: ['W-001', 'W-002'],
    rules: ['production_volume']
});

// Subscribe to updates
client.subscribe(session.id, (update) => {
    console.log(`Progress: ${update.progress}%`);
});
```