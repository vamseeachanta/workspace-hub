# Baseline Storage System Design

## Storage Architecture Overview

The baseline storage system uses a hybrid approach combining Git-based versioning with database storage for optimal performance and auditability.

## Storage Components

### 1. Git-Based Baseline Repository

#### Repository Structure
```
baselines/
├── .baseline-config.json           # Global configuration
├── schemas/
│   ├── v1.0.0/
│   │   └── baseline-schema.json    # Schema version 1.0.0
│   └── v2.0.0/
│       └── baseline-schema.json    # Schema version 2.0.0
├── branches/
│   ├── main/
│   │   ├── environments/
│   │   │   ├── production/
│   │   │   │   ├── current-baseline.json
│   │   │   │   └── history/
│   │   │   │       ├── 2024-01-01-baseline.json
│   │   │   │       └── 2024-01-02-baseline.json
│   │   │   ├── staging/
│   │   │   └── development/
│   │   └── projects/
│   │       ├── frontend/
│   │       ├── backend/
│   │       └── mobile/
│   ├── feature-branches/
│   │   ├── feature-auth/
│   │   └── feature-payment/
│   └── release-branches/
│       ├── v1.0.0/
│       └── v1.1.0/
└── templates/
    ├── jest-baseline-template.json
    ├── mocha-baseline-template.json
    └── pytest-baseline-template.json
```

#### Baseline File Schema (v2.0.0)
```json
{
  "$schema": "https://tbts.example.com/schemas/v2.0.0/baseline-schema.json",
  "metadata": {
    "version": "2.0.0",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "ci-system",
    "branch": "main",
    "environment": "production",
    "project": "backend-api",
    "commit_hash": "abc123def456",
    "build_number": "1234",
    "tags": ["stable", "release-candidate"]
  },
  "test_frameworks": {
    "jest": {
      "version": "29.5.0",
      "config_hash": "md5hash123"
    },
    "pytest": {
      "version": "7.3.0",
      "config_hash": "md5hash456"
    }
  },
  "metrics": {
    "execution": {
      "total_tests": 1250,
      "passed_tests": 1248,
      "failed_tests": 2,
      "skipped_tests": 0,
      "pass_rate_percentage": 99.84,
      "total_execution_time_ms": 45000,
      "average_test_duration_ms": 36,
      "slowest_test": {
        "name": "integration.test.js - API stress test",
        "duration_ms": 5000,
        "file_path": "tests/integration/api.test.js"
      },
      "fastest_test": {
        "name": "unit.test.js - utility function",
        "duration_ms": 1,
        "file_path": "tests/unit/utils.test.js"
      }
    },
    "coverage": {
      "overall": {
        "line_coverage": 87.5,
        "branch_coverage": 82.1,
        "function_coverage": 94.2,
        "statement_coverage": 86.8
      },
      "by_directory": {
        "src/controllers": {
          "line_coverage": 95.2,
          "branch_coverage": 89.1,
          "function_coverage": 98.5,
          "statement_coverage": 94.8
        },
        "src/services": {
          "line_coverage": 78.3,
          "branch_coverage": 72.4,
          "function_coverage": 85.6,
          "statement_coverage": 77.9
        }
      },
      "uncovered_lines": [
        {
          "file": "src/services/payment.js",
          "lines": [45, 46, 78, 92]
        }
      ]
    },
    "performance": {
      "memory_usage": {
        "peak_memory_mb": 512,
        "average_memory_mb": 256,
        "memory_leak_detected": false
      },
      "cpu_usage": {
        "peak_cpu_percentage": 85,
        "average_cpu_percentage": 45
      },
      "benchmarks": {
        "api_response_time_ms": {
          "p50": 120,
          "p95": 250,
          "p99": 500,
          "max": 1200
        },
        "database_query_time_ms": {
          "p50": 15,
          "p95": 45,
          "p99": 80,
          "max": 150
        }
      }
    },
    "quality": {
      "flaky_tests": [
        {
          "name": "user-auth.test.js - login timeout",
          "file_path": "tests/integration/auth.test.js",
          "failure_rate": 0.05,
          "last_failure": "2024-01-01T10:30:00Z"
        }
      ],
      "new_tests": [
        {
          "name": "payment validation test",
          "file_path": "tests/unit/payment.test.js",
          "added_in_commit": "def456abc789"
        }
      ],
      "deleted_tests": [],
      "test_stability_score": 0.98,
      "code_complexity": {
        "cyclomatic_complexity": 3.2,
        "maintainability_index": 78.5
      }
    }
  },
  "thresholds": {
    "execution": {
      "pass_rate_min_percentage": 95.0,
      "execution_time_max_ms": 60000,
      "individual_test_max_ms": 10000
    },
    "coverage": {
      "line_coverage_min": 80.0,
      "branch_coverage_min": 75.0,
      "function_coverage_min": 90.0,
      "statement_coverage_min": 80.0
    },
    "performance": {
      "memory_usage_max_mb": 1024,
      "api_response_time_p95_max_ms": 300,
      "database_query_time_p95_max_ms": 50
    },
    "quality": {
      "flaky_test_rate_max": 0.02,
      "stability_score_min": 0.95
    }
  },
  "comparison_results": {
    "previous_baseline": "2023-12-31T23:59:59Z",
    "changes": {
      "pass_rate_delta": 0.16,
      "coverage_delta": 2.1,
      "performance_delta": -5.2,
      "new_tests_count": 5,
      "removed_tests_count": 1
    },
    "regression_detected": false,
    "improvement_detected": true
  }
}
```

### 2. Database Storage Layer

#### PostgreSQL Schema
```sql
-- Baseline metadata table
CREATE TABLE baselines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version VARCHAR(10) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    branch VARCHAR(255) NOT NULL,
    environment VARCHAR(100) NOT NULL,
    project VARCHAR(255) NOT NULL,
    commit_hash VARCHAR(40) NOT NULL,
    build_number VARCHAR(50),
    file_path TEXT NOT NULL,
    git_repository VARCHAR(500) NOT NULL,
    tags TEXT[],
    created_by VARCHAR(255),
    INDEX idx_branch_env_project (branch, environment, project),
    INDEX idx_created_at (created_at),
    INDEX idx_commit_hash (commit_hash)
);

-- Test execution metrics
CREATE TABLE test_execution_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_id UUID REFERENCES baselines(id) ON DELETE CASCADE,
    total_tests INTEGER NOT NULL,
    passed_tests INTEGER NOT NULL,
    failed_tests INTEGER NOT NULL,
    skipped_tests INTEGER DEFAULT 0,
    pass_rate_percentage DECIMAL(5,2) NOT NULL,
    total_execution_time_ms BIGINT NOT NULL,
    average_test_duration_ms DECIMAL(10,2),
    peak_memory_mb INTEGER,
    average_memory_mb INTEGER,
    peak_cpu_percentage INTEGER,
    average_cpu_percentage INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Coverage metrics
CREATE TABLE coverage_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_id UUID REFERENCES baselines(id) ON DELETE CASCADE,
    line_coverage DECIMAL(5,2) NOT NULL,
    branch_coverage DECIMAL(5,2) NOT NULL,
    function_coverage DECIMAL(5,2) NOT NULL,
    statement_coverage DECIMAL(5,2) NOT NULL,
    directory VARCHAR(500),
    file_path VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_baseline_directory (baseline_id, directory)
);

-- Performance benchmarks
CREATE TABLE performance_benchmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_id UUID REFERENCES baselines(id) ON DELETE CASCADE,
    benchmark_name VARCHAR(255) NOT NULL,
    metric_type VARCHAR(100) NOT NULL, -- 'response_time', 'query_time', etc.
    p50_value DECIMAL(10,2),
    p95_value DECIMAL(10,2),
    p99_value DECIMAL(10,2),
    max_value DECIMAL(10,2),
    min_value DECIMAL(10,2),
    unit VARCHAR(20) NOT NULL, -- 'ms', 'mb', 'percentage'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_baseline_benchmark (baseline_id, benchmark_name)
);

-- Test quality metrics
CREATE TABLE test_quality_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_id UUID REFERENCES baselines(id) ON DELETE CASCADE,
    test_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    is_flaky BOOLEAN DEFAULT FALSE,
    failure_rate DECIMAL(5,4),
    stability_score DECIMAL(5,4),
    last_failure TIMESTAMP WITH TIME ZONE,
    test_type VARCHAR(50), -- 'unit', 'integration', 'e2e'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_baseline_test (baseline_id, test_name),
    INDEX idx_flaky_tests (baseline_id, is_flaky)
);

-- Threshold configurations
CREATE TABLE threshold_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_id UUID REFERENCES baselines(id) ON DELETE CASCADE,
    metric_category VARCHAR(100) NOT NULL, -- 'execution', 'coverage', 'performance', 'quality'
    metric_name VARCHAR(255) NOT NULL,
    threshold_type VARCHAR(50) NOT NULL, -- 'min', 'max', 'range'
    threshold_value DECIMAL(10,2) NOT NULL,
    is_blocking BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_baseline_thresholds (baseline_id, metric_category)
);

-- Comparison results
CREATE TABLE baseline_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    current_baseline_id UUID REFERENCES baselines(id) ON DELETE CASCADE,
    previous_baseline_id UUID REFERENCES baselines(id) ON DELETE CASCADE,
    comparison_type VARCHAR(100) NOT NULL, -- 'temporal', 'branch', 'environment'
    regression_detected BOOLEAN DEFAULT FALSE,
    improvement_detected BOOLEAN DEFAULT FALSE,
    overall_score DECIMAL(5,2),
    comparison_summary JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_current_baseline (current_baseline_id),
    INDEX idx_regression_detected (regression_detected)
);

-- Historical trends (aggregated data for performance)
CREATE TABLE historical_trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project VARCHAR(255) NOT NULL,
    branch VARCHAR(255) NOT NULL,
    environment VARCHAR(100) NOT NULL,
    date_bucket DATE NOT NULL, -- Daily aggregation
    avg_pass_rate DECIMAL(5,2),
    avg_line_coverage DECIMAL(5,2),
    avg_execution_time_ms BIGINT,
    trend_direction VARCHAR(20), -- 'improving', 'degrading', 'stable'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project, branch, environment, date_bucket),
    INDEX idx_project_trends (project, branch, environment, date_bucket)
);
```

### 3. Redis Caching Layer

#### Cache Structure
```json
{
  "cache_keys": {
    "current_baseline": "baseline:current:{project}:{branch}:{environment}",
    "comparison_result": "comparison:{baseline_id}:{previous_baseline_id}",
    "trend_data": "trends:{project}:{branch}:{timeframe}",
    "threshold_config": "thresholds:{project}:{branch}:{environment}",
    "test_metrics": "metrics:{baseline_id}:{metric_type}"
  },
  "ttl_policies": {
    "current_baseline": 3600,
    "comparison_result": 7200,
    "trend_data": 1800,
    "threshold_config": 86400,
    "test_metrics": 3600
  }
}
```

#### Cache Invalidation Strategy
```javascript
// Cache invalidation triggers
const cacheInvalidationTriggers = {
  newBaseline: ['current_baseline', 'trend_data'],
  thresholdUpdate: ['threshold_config'],
  comparisonComplete: ['comparison_result'],
  configChange: ['threshold_config', 'current_baseline']
};

// Cache warming strategy
const cacheWarmingJobs = {
  dailyTrends: '0 1 * * *',      // Daily at 1 AM
  weeklyBaselines: '0 2 * * 0',   // Weekly on Sunday at 2 AM
  monthlyArchives: '0 3 1 * *'    // Monthly on 1st at 3 AM
};
```

### 4. Storage Access Patterns

#### Read Patterns
```javascript
// High-frequency reads
const readPatterns = {
  currentBaseline: {
    frequency: 'very_high',
    caching: 'redis_primary',
    fallback: 'database'
  },
  comparisonResults: {
    frequency: 'high',
    caching: 'redis_secondary',
    fallback: 'database'
  },
  historicalTrends: {
    frequency: 'medium',
    caching: 'redis_aggregated',
    fallback: 'database_aggregated'
  },
  detailedMetrics: {
    frequency: 'low',
    caching: 'none',
    source: 'git_repository'
  }
};
```

#### Write Patterns
```javascript
// Write strategies
const writePatterns = {
  newBaseline: {
    strategy: 'dual_write',
    primary: 'git_repository',
    secondary: 'database',
    cache_invalidation: true
  },
  metricUpdates: {
    strategy: 'database_first',
    cache_refresh: 'lazy'
  },
  configChanges: {
    strategy: 'git_first',
    database_sync: 'immediate',
    cache_invalidation: true
  }
};
```

### 5. Data Retention and Archival

#### Retention Policies
```json
{
  "retention_policies": {
    "git_repository": {
      "current_baselines": "indefinite",
      "historical_baselines": "2_years",
      "archived_branches": "6_months"
    },
    "database": {
      "detailed_metrics": "6_months",
      "aggregated_trends": "2_years",
      "comparison_results": "1_year"
    },
    "redis_cache": {
      "current_data": "1_hour",
      "aggregated_data": "24_hours",
      "configuration": "7_days"
    }
  },
  "archival_strategy": {
    "trigger": "storage_threshold_80_percent",
    "compression": "gzip",
    "destination": "s3_cold_storage",
    "retrieval_sla": "4_hours"
  }
}
```

#### Archive Process
```javascript
const archivalProcess = {
  identification: {
    criteria: 'age > retention_period',
    exceptions: ['tagged_releases', 'milestone_baselines']
  },
  preparation: {
    compression: 'gzip',
    integrity_check: 'sha256',
    metadata_extraction: true
  },
  storage: {
    destination: 's3_glacier',
    encryption: 'aws_kms',
    redundancy: 'cross_region'
  },
  cleanup: {
    database_cleanup: true,
    cache_invalidation: true,
    git_tag_preservation: true
  }
};
```

### 6. Backup and Recovery

#### Backup Strategy
```yaml
backup_strategy:
  git_repository:
    frequency: continuous
    method: git_mirror
    destinations:
      - github_primary
      - gitlab_backup
      - local_mirror

  database:
    frequency: hourly
    method: pg_dump
    compression: true
    encryption: true
    retention: 30_days

  redis:
    frequency: daily
    method: rdb_snapshot
    compression: true
    retention: 7_days

recovery_procedures:
  git_repository:
    rto: 5_minutes
    rpo: 0_seconds
    procedure: git_clone_from_mirror

  database:
    rto: 15_minutes
    rpo: 1_hour
    procedure: pg_restore_from_backup

  redis:
    rto: 5_minutes
    rpo: 24_hours
    procedure: rdb_restore
```

This storage system provides comprehensive versioning, efficient querying, robust caching, and reliable data retention while maintaining the flexibility to scale across different environments and projects.