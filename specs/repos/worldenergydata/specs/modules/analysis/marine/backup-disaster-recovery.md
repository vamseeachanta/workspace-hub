# Backup & Disaster Recovery Specification
## Marine Safety Incidents Database

**Version:** 1.0
**Last Updated:** 2025-10-03
**Owner:** Data Operations Team
**Status:** Production-Ready

---

## 1. Executive Summary

This document defines the comprehensive backup and disaster recovery strategy for the Marine Safety Incidents Database. It ensures data integrity, availability, and recoverability in accordance with industry best practices and regulatory requirements.

### Key Objectives
- **RTO (Recovery Time Objective):** 4 hours for critical systems
- **RPO (Recovery Point Objective):** 15 minutes for transactional data
- **Availability Target:** 99.9% uptime
- **Data Retention:** 7 years for compliance

---

## 2. Backup Strategy

### 2.1 Backup Types & Schedules

#### Full Backups
- **Frequency:** Weekly (Sunday 02:00 UTC)
- **Scope:** Complete database dump, all schemas, indexes, and metadata
- **Method:** PostgreSQL `pg_dump` with custom format
- **Estimated Duration:** 2-4 hours
- **Storage:** Primary + Off-site + Cloud

```bash
# Full backup command
pg_dump -h localhost -U marine_admin -d marine_incidents \
  --format=custom \
  --file=/backups/full/marine_incidents_$(date +%Y%m%d_%H%M%S).dump \
  --verbose \
  --compress=9
```

#### Incremental Backups
- **Frequency:** Every 4 hours
- **Scope:** Changed data since last incremental
- **Method:** WAL (Write-Ahead Logging) archiving
- **Estimated Duration:** 5-15 minutes
- **Storage:** Primary + Cloud replication

```bash
# WAL archiving configuration in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /backups/wal/%f && cp %p /backups/wal/%f'
archive_timeout = 3600  # Force segment switch every hour
```

#### Differential Backups
- **Frequency:** Daily (01:00 UTC)
- **Scope:** All changes since last full backup
- **Method:** PostgreSQL logical replication + snapshot
- **Estimated Duration:** 30-60 minutes
- **Storage:** Primary + Off-site

```sql
-- Differential backup using logical replication
SELECT pg_create_logical_replication_slot('marine_backup_slot', 'test_decoding');

-- Export differential changes
pg_recvlogical -d marine_incidents \
  --slot marine_backup_slot \
  --start \
  -f /backups/differential/marine_diff_$(date +%Y%m%d).sql
```

#### Transaction Log Backups
- **Frequency:** Continuous (real-time)
- **Scope:** All transaction logs (WAL files)
- **Method:** Continuous archiving to S3
- **RPO:** 15 minutes maximum data loss

---

## 3. RTO/RPO Targets

### 3.1 Service Level Objectives

| **Component** | **RTO** | **RPO** | **Priority** | **Notes** |
|---------------|---------|---------|--------------|-----------|
| Production Database | 4 hours | 15 minutes | Critical | Automated failover available |
| API Services | 2 hours | 30 minutes | High | Stateless, quick recovery |
| Analytics Pipeline | 24 hours | 1 hour | Medium | Batch processing tolerant |
| File Storage (S3) | 1 hour | 5 minutes | High | Cross-region replication |
| Configuration Files | 1 hour | 1 day | Low | Version controlled in Git |
| Monitoring Systems | 2 hours | 1 hour | High | Required for recovery validation |

### 3.2 Disaster Recovery Tiers

#### Tier 1: Critical (RTO ≤ 4 hours)
- Production database
- Authentication services
- File storage systems
- Core API endpoints

#### Tier 2: High Priority (RTO ≤ 24 hours)
- Analytics databases
- Reporting systems
- Secondary APIs
- ETL pipelines

#### Tier 3: Standard (RTO ≤ 72 hours)
- Historical archives
- Development databases
- Testing environments
- Documentation systems

---

## 4. Backup Types & Components

### 4.1 Database Backups

#### PostgreSQL Database
```bash
#!/bin/bash
# /scripts/backup/database_backup.sh

BACKUP_DIR="/backups/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="marine_incidents"

# Full schema backup
pg_dump -h localhost -U marine_admin -d $DB_NAME \
  --schema-only \
  --file=$BACKUP_DIR/schema_$TIMESTAMP.sql

# Full data backup (custom format for parallel restore)
pg_dump -h localhost -U marine_admin -d $DB_NAME \
  --format=custom \
  --blobs \
  --encoding=UTF8 \
  --file=$BACKUP_DIR/full_$TIMESTAMP.dump \
  --jobs=4 \
  --verbose

# Individual table backups (critical tables)
for table in incidents vessels inspections citations; do
  pg_dump -h localhost -U marine_admin -d $DB_NAME \
    --table=$table \
    --format=custom \
    --file=$BACKUP_DIR/table_${table}_$TIMESTAMP.dump
done

# Compress and encrypt
tar -czf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz $BACKUP_DIR/*_$TIMESTAMP.*
openssl enc -aes-256-cbc -salt -in $BACKUP_DIR/backup_$TIMESTAMP.tar.gz \
  -out $BACKUP_DIR/backup_$TIMESTAMP.tar.gz.enc \
  -pass file:/etc/backup/encryption.key

# Upload to S3
aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.tar.gz.enc \
  s3://marine-backups/database/$(date +%Y/%m/%d)/ \
  --storage-class STANDARD_IA \
  --server-side-encryption AES256

# Cleanup local files older than 7 days
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete
```

#### Metadata & Configurations
```bash
# Backup database roles and permissions
pg_dumpall -h localhost -U postgres --roles-only \
  --file=/backups/config/roles_$(date +%Y%m%d).sql

# Backup database globals
pg_dumpall -h localhost -U postgres --globals-only \
  --file=/backups/config/globals_$(date +%Y%m%d).sql

# Backup PostgreSQL configuration
cp /etc/postgresql/14/main/postgresql.conf \
  /backups/config/postgresql_$(date +%Y%m%d).conf
cp /etc/postgresql/14/main/pg_hba.conf \
  /backups/config/pg_hba_$(date +%Y%m%d).conf
```

### 4.2 Raw Data Files

#### Source CSV/XML Files
```bash
#!/bin/bash
# /scripts/backup/raw_data_backup.sh

RAW_DATA_DIR="/data/marine/raw"
BACKUP_DIR="/backups/raw_data"
TIMESTAMP=$(date +%Y%m%d)

# Incremental backup using rsync
rsync -avz --delete \
  --backup --backup-dir=$BACKUP_DIR/incremental_$TIMESTAMP \
  $RAW_DATA_DIR/ \
  $BACKUP_DIR/current/

# Create dated snapshot
tar -czf $BACKUP_DIR/snapshot_$TIMESTAMP.tar.gz \
  -C $BACKUP_DIR current/

# Upload to S3 with lifecycle policy
aws s3 cp $BACKUP_DIR/snapshot_$TIMESTAMP.tar.gz \
  s3://marine-backups/raw-data/$(date +%Y/%m/)/ \
  --storage-class GLACIER_IR \
  --metadata "backup-type=raw-data,timestamp=$TIMESTAMP"
```

### 4.3 Application Code & Configurations

#### Git Repository Backup
```bash
#!/bin/bash
# /scripts/backup/code_backup.sh

REPO_DIR="/var/www/marine-incidents"
BACKUP_DIR="/backups/code"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create bundle of all branches
cd $REPO_DIR
git bundle create $BACKUP_DIR/marine_repo_$TIMESTAMP.bundle --all

# Backup configuration files
tar -czf $BACKUP_DIR/config_$TIMESTAMP.tar.gz \
  /etc/nginx/sites-available/marine-incidents.conf \
  /etc/systemd/system/marine-api.service \
  /var/www/marine-incidents/.env.production

# Upload to S3
aws s3 sync $BACKUP_DIR s3://marine-backups/code/$(date +%Y/%m/)/ \
  --exclude "*.tmp" \
  --storage-class STANDARD_IA
```

### 4.4 Monitoring & Logs

```bash
#!/bin/bash
# /scripts/backup/logs_backup.sh

LOG_DIR="/var/log/marine-incidents"
BACKUP_DIR="/backups/logs"
TIMESTAMP=$(date +%Y%m%d)

# Compress and archive logs older than 7 days
find $LOG_DIR -name "*.log" -mtime +7 -exec gzip {} \;

# Move to backup directory
find $LOG_DIR -name "*.log.gz" -mtime +7 \
  -exec mv {} $BACKUP_DIR/$(date +%Y/%m/)/ \;

# Upload to S3 with 90-day retention
aws s3 sync $BACKUP_DIR s3://marine-backups/logs/ \
  --storage-class GLACIER \
  --exclude "*" --include "*.log.gz"
```

---

## 5. Storage Locations

### 5.1 Storage Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Primary Data Center                      │
├─────────────────────────────────────────────────────────────┤
│  Production DB (NVMe SSD)                                    │
│  ├── Hot Backups: /backups/hot/ (24 hours retention)        │
│  └── Local Staging: /backups/staging/ (7 days retention)    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├──────────────┐
                            ▼              ▼
┌──────────────────────────────┐  ┌──────────────────────────┐
│   Off-Site Data Center       │  │   Cloud Storage (AWS)    │
├──────────────────────────────┤  ├──────────────────────────┤
│  NAS Storage                 │  │  S3 Standard-IA          │
│  - Daily backups (30 days)   │  │  - US-East-1 (Primary)   │
│  - Weekly backups (90 days)  │  │  - US-West-2 (Replica)   │
│  - 10 Gbps fiber connection  │  │  - Versioning enabled    │
└──────────────────────────────┘  └──────────────────────────┘
                                              │
                                              ▼
                                  ┌──────────────────────────┐
                                  │  S3 Glacier Deep Archive  │
                                  ├──────────────────────────┤
                                  │  - Monthly archives       │
                                  │  - 7-year retention       │
                                  │  - Compliance tier        │
                                  └──────────────────────────┘
```

### 5.2 Storage Configuration

#### On-Site Primary Storage
```yaml
# Storage Configuration
primary_storage:
  location: /backups
  filesystem: XFS
  raid_level: RAID-10
  capacity: 20 TB
  usage_alert: 80%
  partitions:
    - hot: 500 GB (NVMe)
    - daily: 5 TB (SSD)
    - weekly: 10 TB (HDD)
    - staging: 2 TB (SSD)
```

#### Off-Site Secondary Storage
```yaml
offsite_storage:
  location: DR Site - 50 miles from primary
  connection: Dedicated 10 Gbps fiber
  replication_mode: Asynchronous
  sync_frequency: Every 4 hours
  capacity: 50 TB
  encryption: AES-256-GCM at rest
```

#### Cloud Storage (AWS S3)
```yaml
s3_configuration:
  primary_region: us-east-1
  replica_region: us-west-2

  buckets:
    - name: marine-backups-prod
      storage_class: STANDARD_IA
      versioning: enabled
      mfa_delete: enabled
      encryption: SSE-S3 (AES-256)

    - name: marine-backups-archive
      storage_class: GLACIER_DEEP_ARCHIVE
      versioning: enabled
      lifecycle_policy: transition_to_glacier
      encryption: SSE-KMS

  cross_region_replication:
    enabled: true
    destination: us-west-2
    rule: replicate_all_encrypted
```

### 5.3 AWS S3 Lifecycle Policies

```json
{
  "Rules": [
    {
      "Id": "TransitionDatabaseBackups",
      "Status": "Enabled",
      "Prefix": "database/",
      "Transitions": [
        {
          "Days": 7,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 30,
          "StorageClass": "GLACIER_IR"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ],
      "Expiration": {
        "Days": 2555
      }
    },
    {
      "Id": "TransitionRawData",
      "Status": "Enabled",
      "Prefix": "raw-data/",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER_IR"
        },
        {
          "Days": 180,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 2555
      }
    },
    {
      "Id": "TransitionLogs",
      "Status": "Enabled",
      "Prefix": "logs/",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    },
    {
      "Id": "CleanupIncompleteUploads",
      "Status": "Enabled",
      "AbortIncompleteMultipartUpload": {
        "DaysAfterInitiation": 7
      }
    }
  ]
}
```

---

## 6. Retention Policies

### 6.1 Retention Schedule

| **Backup Type** | **Daily** | **Weekly** | **Monthly** | **Yearly** | **Total Retention** |
|-----------------|-----------|------------|-------------|------------|---------------------|
| Full Database   | 7 days    | 4 weeks    | 12 months   | 7 years    | 7 years             |
| Incremental     | 7 days    | 4 weeks    | -           | -          | 30 days             |
| Differential    | 7 days    | 4 weeks    | 3 months    | -          | 90 days             |
| Transaction Logs| 30 days   | -          | -           | -          | 30 days             |
| Raw Data Files  | 30 days   | -          | 12 months   | 7 years    | 7 years             |
| Application Code| 30 days   | 12 weeks   | 24 months   | 7 years    | 7 years             |
| Configuration   | 90 days   | 52 weeks   | 36 months   | 7 years    | 7 years             |
| System Logs     | 90 days   | -          | -           | -          | 90 days             |

### 6.2 Retention Implementation

```sql
-- Automated retention cleanup procedure
CREATE OR REPLACE FUNCTION cleanup_expired_backups()
RETURNS void AS $$
DECLARE
  backup_record RECORD;
BEGIN
  -- Log retention enforcement
  DELETE FROM backup_catalog
  WHERE backup_type = 'daily'
    AND backup_date < CURRENT_DATE - INTERVAL '7 days';

  DELETE FROM backup_catalog
  WHERE backup_type = 'weekly'
    AND backup_date < CURRENT_DATE - INTERVAL '4 weeks';

  DELETE FROM backup_catalog
  WHERE backup_type = 'monthly'
    AND backup_date < CURRENT_DATE - INTERVAL '12 months';

  -- Keep yearly backups for 7 years
  DELETE FROM backup_catalog
  WHERE backup_type = 'yearly'
    AND backup_date < CURRENT_DATE - INTERVAL '7 years';

  -- Log cleanup action
  INSERT INTO backup_audit_log (action, timestamp, details)
  VALUES ('retention_cleanup', NOW(),
          'Automated retention policy enforcement executed');
END;
$$ LANGUAGE plpgsql;

-- Schedule daily execution
SELECT cron.schedule('backup-retention-cleanup', '0 3 * * *',
                      'SELECT cleanup_expired_backups()');
```

### 6.3 Legal & Compliance Requirements

```yaml
compliance_requirements:
  regulatory_frameworks:
    - GDPR: 7 years for incident data
    - CCPA: 24 months minimum
    - SOC 2: 1 year audit trail
    - HIPAA: Not applicable

  data_classification:
    - PII: 7 years retention, encrypted
    - Financial: 7 years retention, audit trail
    - Operational: 3 years retention
    - Logs: 90 days minimum

  deletion_policy:
    - Right to erasure: 30-day process
    - Data minimization: Quarterly review
    - Anonymization: After 7 years for research
```

---

## 7. Encryption

### 7.1 Encryption Standards

#### At Rest Encryption
```bash
# Database encryption (Transparent Data Encryption)
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/postgresql.crt'
ssl_key_file = '/etc/ssl/private/postgresql.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'

# Encrypt tablespace
CREATE TABLESPACE encrypted_space
  LOCATION '/var/lib/postgresql/encrypted'
  WITH (encryption_key_id = 'marine_master_key');

# Backup encryption using GPG
pg_dump -h localhost -d marine_incidents | \
  gzip | \
  gpg --encrypt --recipient backup@marine-safety.gov \
      --output /backups/encrypted/backup_$(date +%Y%m%d).dump.gz.gpg
```

#### In Transit Encryption
```nginx
# Nginx SSL configuration for backup uploads
server {
    listen 443 ssl http2;
    server_name backups.marine-safety.gov;

    ssl_certificate /etc/ssl/certs/backup_server.crt;
    ssl_certificate_key /etc/ssl/private/backup_server.key;

    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;

    location /upload/ {
        client_max_body_size 10G;
        proxy_pass http://backup_storage_backend;
    }
}
```

### 7.2 Key Management

```yaml
encryption_keys:
  master_key:
    type: AWS KMS
    key_id: arn:aws:kms:us-east-1:123456789012:key/master-backup-key
    rotation_period: 365 days

  data_encryption_keys:
    - purpose: Database backups
      algorithm: AES-256-GCM
      key_length: 256 bits
      storage: AWS Secrets Manager
      rotation: 90 days

    - purpose: File encryption
      algorithm: AES-256-CBC
      key_length: 256 bits
      storage: HashiCorp Vault
      rotation: 90 days

  access_control:
    - role: backup_admin
      permissions: [encrypt, decrypt, rotate]
    - role: restore_operator
      permissions: [decrypt]
    - role: audit_reviewer
      permissions: [view_metadata]
```

### 7.3 Encryption Scripts

```bash
#!/bin/bash
# /scripts/encryption/encrypt_backup.sh

BACKUP_FILE=$1
ENCRYPTION_KEY_ID="marine_master_key"
OUTPUT_FILE="${BACKUP_FILE}.enc"

# Retrieve encryption key from AWS Secrets Manager
ENCRYPTION_KEY=$(aws secretsmanager get-secret-value \
  --secret-id $ENCRYPTION_KEY_ID \
  --query SecretString \
  --output text)

# Encrypt using OpenSSL
openssl enc -aes-256-gcm \
  -salt \
  -in "$BACKUP_FILE" \
  -out "$OUTPUT_FILE" \
  -pass pass:"$ENCRYPTION_KEY" \
  -pbkdf2

# Generate checksum for integrity
sha256sum "$OUTPUT_FILE" > "${OUTPUT_FILE}.sha256"

# Sign the backup
gpg --detach-sign --armor "$OUTPUT_FILE"

# Cleanup plaintext
shred -uvz -n 3 "$BACKUP_FILE"

echo "Backup encrypted: $OUTPUT_FILE"
```

---

## 8. Recovery Procedures

### 8.1 Database Recovery - Full Restore

```bash
#!/bin/bash
# /scripts/recovery/full_database_restore.sh

BACKUP_FILE=$1
TARGET_DB="marine_incidents"

echo "=== Full Database Restore ==="
echo "Backup file: $BACKUP_FILE"
echo "Target database: $TARGET_DB"
echo "Start time: $(date)"

# Step 1: Stop application services
systemctl stop marine-api
systemctl stop marine-etl

# Step 2: Download backup from S3 if needed
if [[ $BACKUP_FILE == s3://* ]]; then
  LOCAL_BACKUP="/tmp/$(basename $BACKUP_FILE)"
  aws s3 cp "$BACKUP_FILE" "$LOCAL_BACKUP"
  BACKUP_FILE=$LOCAL_BACKUP
fi

# Step 3: Decrypt backup
if [[ $BACKUP_FILE == *.enc ]]; then
  DECRYPTED_FILE="${BACKUP_FILE%.enc}"
  openssl enc -aes-256-gcm -d \
    -in "$BACKUP_FILE" \
    -out "$DECRYPTED_FILE" \
    -pass file:/etc/backup/encryption.key
  BACKUP_FILE=$DECRYPTED_FILE
fi

# Step 4: Verify backup integrity
if [[ -f "${BACKUP_FILE}.sha256" ]]; then
  sha256sum -c "${BACKUP_FILE}.sha256" || {
    echo "ERROR: Backup integrity check failed!"
    exit 1
  }
fi

# Step 5: Create new database or drop existing
psql -U postgres -c "DROP DATABASE IF EXISTS ${TARGET_DB}_restore;"
psql -U postgres -c "CREATE DATABASE ${TARGET_DB}_restore;"

# Step 6: Restore database
pg_restore -h localhost -U marine_admin \
  -d ${TARGET_DB}_restore \
  --format=custom \
  --jobs=4 \
  --verbose \
  --no-owner \
  --no-privileges \
  "$BACKUP_FILE"

# Step 7: Verify restoration
psql -d ${TARGET_DB}_restore -U marine_admin -c "
  SELECT
    schemaname,
    COUNT(*) as table_count
  FROM pg_tables
  WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  GROUP BY schemaname;
"

# Step 8: Apply any pending migrations
cd /var/www/marine-incidents
python manage.py migrate --database=${TARGET_DB}_restore

# Step 9: Validate data integrity
psql -d ${TARGET_DB}_restore -U marine_admin -c "
  SELECT
    'incidents' as table_name, COUNT(*) as row_count FROM incidents
  UNION ALL
  SELECT 'vessels', COUNT(*) FROM vessels
  UNION ALL
  SELECT 'inspections', COUNT(*) FROM inspections;
"

# Step 10: Swap databases (if validation passes)
echo "Ready to swap databases. Continue? (yes/no)"
read -r response
if [[ $response == "yes" ]]; then
  psql -U postgres -c "
    ALTER DATABASE ${TARGET_DB} RENAME TO ${TARGET_DB}_old;
    ALTER DATABASE ${TARGET_DB}_restore RENAME TO ${TARGET_DB};
  "
  echo "Database restored successfully!"
else
  echo "Restore cancelled. Restored database kept as ${TARGET_DB}_restore"
  exit 0
fi

# Step 11: Restart services
systemctl start marine-api
systemctl start marine-etl

# Step 12: Verify application connectivity
sleep 10
curl -f http://localhost:8000/health || {
  echo "WARNING: Application health check failed!"
  systemctl status marine-api
}

echo "=== Restore Complete ==="
echo "End time: $(date)"
```

### 8.2 Point-in-Time Recovery (PITR)

```bash
#!/bin/bash
# /scripts/recovery/point_in_time_restore.sh

TARGET_TIMESTAMP=$1  # Format: 2025-10-03 14:30:00
BASE_BACKUP=$2
WAL_ARCHIVE_DIR="/backups/wal"

echo "=== Point-in-Time Recovery ==="
echo "Target timestamp: $TARGET_TIMESTAMP"
echo "Base backup: $BASE_BACKUP"

# Step 1: Stop PostgreSQL
systemctl stop postgresql

# Step 2: Backup current data directory
mv /var/lib/postgresql/14/main /var/lib/postgresql/14/main_backup_$(date +%Y%m%d_%H%M%S)

# Step 3: Extract base backup
mkdir -p /var/lib/postgresql/14/main
tar -xzf "$BASE_BACKUP" -C /var/lib/postgresql/14/main

# Step 4: Create recovery.conf
cat > /var/lib/postgresql/14/main/recovery.conf <<EOF
restore_command = 'cp $WAL_ARCHIVE_DIR/%f %p'
recovery_target_time = '$TARGET_TIMESTAMP'
recovery_target_action = 'promote'
EOF

# Step 5: Set permissions
chown -R postgres:postgres /var/lib/postgresql/14/main
chmod 700 /var/lib/postgresql/14/main

# Step 6: Start PostgreSQL in recovery mode
systemctl start postgresql

# Step 7: Monitor recovery
echo "Monitoring recovery progress..."
while true; do
  RECOVERY_STATUS=$(psql -U postgres -t -c "SELECT pg_is_in_recovery();")
  if [[ $RECOVERY_STATUS == *"f"* ]]; then
    echo "Recovery complete! Database promoted to primary."
    break
  fi
  echo "Still recovering... ($(date))"
  sleep 10
done

# Step 8: Verify target timestamp
psql -U postgres -d marine_incidents -c "
  SELECT
    'Latest incident timestamp' as metric,
    MAX(incident_date) as value
  FROM incidents;
"

echo "=== PITR Complete ==="
```

### 8.3 Table-Level Recovery

```bash
#!/bin/bash
# /scripts/recovery/table_restore.sh

TABLE_NAME=$1
BACKUP_FILE=$2
TARGET_DB="marine_incidents"

echo "=== Table-Level Restore ==="
echo "Table: $TABLE_NAME"
echo "Backup: $BACKUP_FILE"

# Step 1: Extract specific table
pg_restore -h localhost -U marine_admin \
  -d ${TARGET_DB} \
  --table=$TABLE_NAME \
  --data-only \
  --format=custom \
  "$BACKUP_FILE"

# Step 2: Rebuild indexes
psql -d $TARGET_DB -U marine_admin -c "
  REINDEX TABLE $TABLE_NAME;
"

# Step 3: Update statistics
psql -d $TARGET_DB -U marine_admin -c "
  ANALYZE $TABLE_NAME;
"

# Step 4: Verify row count
psql -d $TARGET_DB -U marine_admin -c "
  SELECT
    '$TABLE_NAME' as table_name,
    COUNT(*) as row_count,
    pg_size_pretty(pg_total_relation_size('$TABLE_NAME')) as size
  FROM $TABLE_NAME;
"

echo "=== Table Restore Complete ==="
```

### 8.4 Recovery Validation Checklist

```sql
-- /scripts/recovery/validation_checks.sql

-- 1. Check database connectivity
SELECT version();

-- 2. Verify table counts
SELECT
  schemaname,
  tablename,
  n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY schemaname, tablename;

-- 3. Check data integrity constraints
SELECT
  conrelid::regclass AS table_name,
  conname AS constraint_name,
  contype AS constraint_type
FROM pg_constraint
WHERE connamespace = 'public'::regnamespace;

-- 4. Verify foreign key relationships
SELECT
  tc.table_name,
  kcu.column_name,
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';

-- 5. Check index health
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 6. Verify sequence values
SELECT
  sequence_schema,
  sequence_name,
  last_value
FROM information_schema.sequences;

-- 7. Check for orphaned records
SELECT
  'incidents without vessels' as issue,
  COUNT(*) as count
FROM incidents i
LEFT JOIN vessels v ON i.vessel_id = v.id
WHERE v.id IS NULL;

-- 8. Validate date ranges
SELECT
  'incidents' as table_name,
  MIN(incident_date) as earliest_date,
  MAX(incident_date) as latest_date,
  COUNT(*) as total_records
FROM incidents;
```

---

## 9. Disaster Scenarios & Response

### 9.1 Scenario 1: Data Corruption

**Detection:**
- Application errors on data retrieval
- Constraint violations in logs
- Checksum mismatches

**Response Procedure:**
```bash
#!/bin/bash
# /scripts/recovery/corruption_recovery.sh

# 1. Identify corrupted tables
psql -d marine_incidents -c "
  SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
  FROM pg_tables
  WHERE schemaname = 'public';
" > /tmp/table_list.txt

# 2. Check for corruption
for table in $(cat /tmp/table_list.txt | awk '{print $1}' | tail -n +3); do
  echo "Checking $table..."
  psql -d marine_incidents -c "
    SELECT * FROM $table LIMIT 1;
  " > /dev/null 2>&1 || echo "CORRUPTION DETECTED: $table"
done

# 3. Restore from most recent clean backup
# Use table-level restore for affected tables only
./table_restore.sh <corrupted_table> <last_known_good_backup>

# 4. Verify integrity
psql -d marine_incidents -c "
  SELECT COUNT(*) FROM <corrupted_table>;
"
```

**Recovery Time:** 2-4 hours
**Data Loss:** Up to last backup (max 4 hours with incremental)

---

### 9.2 Scenario 2: Accidental Deletion

**Detection:**
- User reports missing data
- Audit logs show DELETE operations
- Sudden drop in table row counts

**Response Procedure:**
```bash
#!/bin/bash
# /scripts/recovery/undelete_recovery.sh

DELETED_TIME=$1  # When deletion occurred
TABLE_NAME=$2

# 1. Identify backup before deletion
BACKUP_DATE=$(date -d "$DELETED_TIME - 1 hour" +%Y%m%d_%H%M%S)
BACKUP_FILE=$(ls /backups/database/*${BACKUP_DATE}*.dump | head -1)

# 2. Restore to temporary database
createdb marine_incidents_temp
pg_restore -d marine_incidents_temp "$BACKUP_FILE"

# 3. Export deleted records
psql -d marine_incidents_temp -c "
  COPY (
    SELECT * FROM $TABLE_NAME
    WHERE id NOT IN (SELECT id FROM marine_incidents.$TABLE_NAME)
  ) TO '/tmp/deleted_records.csv' CSV HEADER;
"

# 4. Re-import deleted records
psql -d marine_incidents -c "
  COPY $TABLE_NAME FROM '/tmp/deleted_records.csv' CSV HEADER;
"

# 5. Cleanup
dropdb marine_incidents_temp
rm /tmp/deleted_records.csv

echo "Deleted records restored!"
```

**Recovery Time:** 1-2 hours
**Data Loss:** None if caught within backup retention period

---

### 9.3 Scenario 3: Complete System Loss

**Detection:**
- Server hardware failure
- Data center outage
- Catastrophic infrastructure failure

**Response Procedure:**
```bash
#!/bin/bash
# /scripts/recovery/disaster_recovery_full.sh

# 1. Provision new infrastructure
terraform apply -var-file="dr-config.tfvars"

# 2. Restore OS and application stack
ansible-playbook -i dr-inventory.yml restore-infrastructure.yml

# 3. Download latest backups from S3
aws s3 sync s3://marine-backups/database/latest/ /backups/restore/

# 4. Restore database (full + transaction logs)
pg_restore -d marine_incidents /backups/restore/full_latest.dump

# 5. Apply WAL logs for PITR
for wal_file in /backups/restore/wal/*; do
  pg_waldump $wal_file
done

# 6. Restore file storage
aws s3 sync s3://marine-raw-data/ /data/marine/raw/

# 7. Restart all services
systemctl start postgresql
systemctl start marine-api
systemctl start marine-etl
systemctl start nginx

# 8. Update DNS records
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://dns-failover.json

# 9. Verify application
curl -f https://marine-safety.gov/health

echo "Disaster recovery complete!"
```

**Recovery Time:** 4-8 hours
**Data Loss:** Up to 15 minutes (RPO)

---

### 9.4 Scenario 4: Ransomware Attack

**Detection:**
- Encrypted files with ransom note
- Unusual file system activity
- Unauthorized access logs

**Response Procedure:**
```bash
#!/bin/bash
# /scripts/recovery/ransomware_recovery.sh

# 1. IMMEDIATELY isolate infected systems
iptables -A INPUT -j DROP
iptables -A OUTPUT -j DROP

# 2. Preserve evidence
dd if=/dev/sda of=/mnt/forensics/disk_image_$(date +%Y%m%d).img bs=4M

# 3. Identify infection timeline
journalctl --since "2025-10-01" | grep -i "encrypt\|ransom\|suspicious"

# 4. Retrieve clean backup BEFORE infection
CLEAN_BACKUP_DATE=$(date -d "2025-09-30" +%Y%m%d)
aws s3 cp s3://marine-backups/database/$CLEAN_BACKUP_DATE/ /backups/clean/

# 5. Wipe and rebuild compromised systems
ansible-playbook -i production-inventory.yml wipe-and-rebuild.yml

# 6. Restore from clean backup
pg_restore -d marine_incidents /backups/clean/full_${CLEAN_BACKUP_DATE}.dump

# 7. Restore file storage from immutable S3 version
aws s3api list-object-versions \
  --bucket marine-raw-data \
  --prefix "" \
  --query "Versions[?IsLatest==\`false\`]" \
  > /tmp/clean_versions.json

# Restore clean versions
python restore_clean_versions.py /tmp/clean_versions.json

# 8. Enhance security posture
./implement_security_hardening.sh

# 9. Monitor for reinfection
./deploy_enhanced_monitoring.sh

echo "Ransomware recovery complete. Manual data loss assessment required."
```

**Recovery Time:** 8-24 hours
**Data Loss:** Data between last clean backup and infection (potentially hours/days)

---

## 10. Testing Schedule

### 10.1 Monthly Restore Tests

```yaml
monthly_restore_test:
  schedule: First Sunday of each month, 02:00 UTC
  duration: 4 hours
  scope: Full database restore to isolated environment

  test_procedure:
    - step_1: Select random full backup from previous month
    - step_2: Provision test environment (Docker or VM)
    - step_3: Execute full restore procedure
    - step_4: Run validation queries
    - step_5: Measure restoration time
    - step_6: Document results and anomalies
    - step_7: Cleanup test environment

  success_criteria:
    - restoration_time: < 4 hours
    - data_integrity: 100% validation passed
    - application_functionality: All APIs respond correctly
    - documentation_accuracy: Procedures match actual steps

  documentation:
    - test_report: /docs/backup-tests/monthly-restore-YYYY-MM.md
    - metrics_log: /logs/backup-tests/restore-metrics.csv
```

```bash
#!/bin/bash
# /scripts/testing/monthly_restore_test.sh

TEST_DATE=$(date +%Y-%m-%d)
TEST_LOG="/logs/backup-tests/restore_test_$TEST_DATE.log"

exec > >(tee -a "$TEST_LOG") 2>&1

echo "=== Monthly Restore Test ==="
echo "Date: $TEST_DATE"
echo "Tester: $(whoami)"

# Select random backup
BACKUP_FILES=($(ls /backups/database/full_*.dump))
RANDOM_BACKUP=${BACKUP_FILES[$RANDOM % ${#BACKUP_FILES[@]}]}

echo "Selected backup: $RANDOM_BACKUP"

# Provision test environment
docker run -d --name postgres_test \
  -e POSTGRES_PASSWORD=test123 \
  -p 5433:5432 \
  postgres:14

sleep 10

# Restore backup
START_TIME=$(date +%s)
docker exec postgres_test createdb -U postgres marine_test
docker cp "$RANDOM_BACKUP" postgres_test:/tmp/backup.dump
docker exec postgres_test pg_restore \
  -U postgres -d marine_test /tmp/backup.dump
END_TIME=$(date +%s)

RESTORE_DURATION=$((END_TIME - START_TIME))
echo "Restore duration: ${RESTORE_DURATION}s"

# Validation checks
docker exec postgres_test psql -U postgres -d marine_test -c "
  SELECT
    'incidents' as table_name,
    COUNT(*) as row_count
  FROM incidents;
"

# Cleanup
docker stop postgres_test
docker rm postgres_test

echo "=== Test Complete ==="
echo "Results logged to: $TEST_LOG"

# Send notification
mail -s "Monthly Restore Test Complete" \
  backup-team@marine-safety.gov < "$TEST_LOG"
```

### 10.2 Quarterly Disaster Recovery Drills

```yaml
quarterly_dr_drill:
  schedule: Last Saturday of March, June, September, December
  duration: 8 hours (full business day simulation)
  participants:
    - Database administrators
    - DevOps engineers
    - Application developers
    - IT management
    - Security team

  drill_scenarios:
    Q1: Complete data center failure
    Q2: Ransomware attack
    Q3: Regional AWS outage
    Q4: Insider threat / malicious deletion

  drill_procedure:
    - preparation:
        - Notify all participants 2 weeks in advance
        - Prepare test environment
        - Document expected outcomes

    - execution:
        - Simulate disaster scenario
        - Execute recovery procedures
        - Document all actions and timestamps
        - Measure RTO/RPO achievement

    - debrief:
        - Review timeline and decisions
        - Identify gaps in procedures
        - Update runbooks
        - Assign action items

  success_metrics:
    - rto_achievement: Within 4 hours
    - rpo_achievement: < 15 minutes data loss
    - procedure_accuracy: < 5 deviations from documented procedures
    - team_coordination: Effective communication throughout
```

```bash
#!/bin/bash
# /scripts/testing/dr_drill.sh

DRILL_TYPE=$1  # "datacenter-failure", "ransomware", "aws-outage", "insider-threat"
DRILL_DATE=$(date +%Y-%m-%d)
DRILL_LOG="/logs/dr-drills/drill_${DRILL_TYPE}_${DRILL_DATE}.log"

exec > >(tee -a "$DRILL_LOG") 2>&1

echo "=== Disaster Recovery Drill ==="
echo "Type: $DRILL_TYPE"
echo "Date: $DRILL_DATE"
echo "Start time: $(date)"

# Record start time for RTO measurement
START_TIME=$(date +%s)

case $DRILL_TYPE in
  "datacenter-failure")
    # Simulate complete infrastructure loss
    echo "Simulating datacenter failure..."

    # Step 1: Provision DR infrastructure
    terraform apply -var-file="dr-config.tfvars" -auto-approve

    # Step 2: Restore from S3 backups
    aws s3 sync s3://marine-backups/database/latest/ /backups/restore/

    # Step 3: Full database restore
    ./full_database_restore.sh /backups/restore/full_latest.dump

    # Step 4: Verify application
    curl -f https://dr.marine-safety.gov/health
    ;;

  "ransomware")
    echo "Simulating ransomware attack..."

    # Step 1: Identify clean backup
    CLEAN_BACKUP_DATE=$(date -d "7 days ago" +%Y%m%d)

    # Step 2: Restore from clean backup
    ./ransomware_recovery.sh $CLEAN_BACKUP_DATE

    # Step 3: Apply security hardening
    ./implement_security_hardening.sh
    ;;

  "aws-outage")
    echo "Simulating AWS regional outage..."

    # Step 1: Failover to secondary region
    aws route53 change-resource-record-sets \
      --hosted-zone-id Z1234567890ABC \
      --change-batch file://dns-failover-us-west.json

    # Step 2: Verify replication status
    aws s3api get-bucket-replication \
      --bucket marine-backups-prod
    ;;

  "insider-threat")
    echo "Simulating insider threat / malicious deletion..."

    # Step 1: Simulate deletion
    psql -d marine_incidents -c "DELETE FROM incidents WHERE RANDOM() < 0.1;"

    # Step 2: Detect and recover
    ./undelete_recovery.sh "1 hour ago" "incidents"
    ;;
esac

# Record end time and calculate RTO
END_TIME=$(date +%s)
RTO_ACTUAL=$((END_TIME - START_TIME))
RTO_MINUTES=$((RTO_ACTUAL / 60))

echo "=== Drill Complete ==="
echo "End time: $(date)"
echo "RTO Actual: ${RTO_MINUTES} minutes"
echo "RTO Target: 240 minutes"

if [ $RTO_MINUTES -le 240 ]; then
  echo "✓ RTO ACHIEVED"
else
  echo "✗ RTO MISSED"
fi

# Generate drill report
python generate_drill_report.py \
  --drill-type "$DRILL_TYPE" \
  --drill-date "$DRILL_DATE" \
  --rto-actual "$RTO_MINUTES" \
  --log-file "$DRILL_LOG"

echo "Drill report: /docs/dr-drills/report_${DRILL_TYPE}_${DRILL_DATE}.pdf"
```

### 10.3 Weekly Backup Integrity Checks

```bash
#!/bin/bash
# /scripts/testing/weekly_integrity_check.sh
# Schedule: Every Monday 03:00 UTC

INTEGRITY_LOG="/logs/backup-tests/integrity_$(date +%Y%m%d).log"

exec > >(tee -a "$INTEGRITY_LOG") 2>&1

echo "=== Weekly Backup Integrity Check ==="
echo "Date: $(date)"

# Check last 7 days of backups
for i in {0..6}; do
  CHECK_DATE=$(date -d "$i days ago" +%Y%m%d)
  BACKUP_FILES=$(ls /backups/database/*${CHECK_DATE}*.dump 2>/dev/null)

  if [ -z "$BACKUP_FILES" ]; then
    echo "✗ MISSING backup for $CHECK_DATE"
    continue
  fi

  for BACKUP_FILE in $BACKUP_FILES; do
    echo "Checking: $BACKUP_FILE"

    # Verify checksum
    if [ -f "${BACKUP_FILE}.sha256" ]; then
      sha256sum -c "${BACKUP_FILE}.sha256" > /dev/null 2>&1
      if [ $? -eq 0 ]; then
        echo "  ✓ Checksum valid"
      else
        echo "  ✗ CHECKSUM MISMATCH"
      fi
    else
      echo "  ⚠ No checksum file"
    fi

    # Check file size (should be > 100MB)
    FILE_SIZE=$(stat -c%s "$BACKUP_FILE")
    if [ $FILE_SIZE -gt 104857600 ]; then
      echo "  ✓ Size OK: $(numfmt --to=iec-i --suffix=B $FILE_SIZE)"
    else
      echo "  ✗ SUSPICIOUS SIZE: $(numfmt --to=iec-i --suffix=B $FILE_SIZE)"
    fi

    # Test backup header (quick validation)
    pg_restore --list "$BACKUP_FILE" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
      echo "  ✓ Structure valid"
    else
      echo "  ✗ CORRUPTED BACKUP"
    fi
  done
done

# Check S3 backup replication
echo ""
echo "=== S3 Replication Status ==="
aws s3api get-bucket-replication \
  --bucket marine-backups-prod \
  --query 'ReplicationConfiguration.Rules[].Status'

# Check disk space
echo ""
echo "=== Storage Capacity ==="
df -h /backups

# Summary
echo ""
echo "=== Integrity Check Complete ==="
echo "Full log: $INTEGRITY_LOG"

# Alert on failures
FAILURES=$(grep -c "✗" "$INTEGRITY_LOG")
if [ $FAILURES -gt 0 ]; then
  mail -s "ALERT: Backup Integrity Failures Detected" \
    backup-team@marine-safety.gov < "$INTEGRITY_LOG"
fi
```

---

## 11. Monitoring & Alerting

### 11.1 Backup Monitoring Dashboard

```yaml
monitoring_metrics:
  backup_health:
    - metric: backup_success_rate
      threshold: 95%
      alert_level: warning

    - metric: backup_duration
      threshold: 4 hours
      alert_level: warning

    - metric: backup_size_anomaly
      threshold: ±20% from average
      alert_level: info

    - metric: backup_age
      threshold: 25 hours (daily should be < 24h)
      alert_level: critical

  storage_health:
    - metric: disk_space_usage
      threshold: 80%
      alert_level: warning

    - metric: s3_replication_lag
      threshold: 1 hour
      alert_level: warning

    - metric: failed_uploads
      threshold: 0
      alert_level: critical

  restore_readiness:
    - metric: last_restore_test
      threshold: 30 days
      alert_level: warning

    - metric: integrity_check_failures
      threshold: 0
      alert_level: critical

    - metric: encryption_key_expiry
      threshold: 30 days
      alert_level: warning
```

### 11.2 Prometheus Metrics

```yaml
# /etc/prometheus/backup-exporter.yml

scrape_configs:
  - job_name: 'backup_metrics'
    static_configs:
      - targets: ['localhost:9100']

    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'backup_.*'
        action: keep

# Custom metrics exported by backup scripts
metrics:
  - name: backup_last_success_timestamp
    type: gauge
    help: Unix timestamp of last successful backup

  - name: backup_duration_seconds
    type: histogram
    help: Time taken to complete backup
    buckets: [300, 600, 1800, 3600, 7200, 14400]

  - name: backup_size_bytes
    type: gauge
    help: Size of backup file in bytes

  - name: backup_failures_total
    type: counter
    help: Total number of backup failures

  - name: restore_test_success
    type: gauge
    help: 1 if last restore test passed, 0 otherwise

  - name: backup_integrity_check_failures
    type: counter
    help: Number of integrity check failures
```

```python
# /scripts/monitoring/backup_exporter.py

from prometheus_client import start_http_server, Gauge, Histogram, Counter
import time
import subprocess
import json

# Define metrics
backup_last_success = Gauge('backup_last_success_timestamp',
                             'Unix timestamp of last successful backup',
                             ['backup_type'])

backup_duration = Histogram('backup_duration_seconds',
                            'Time taken to complete backup',
                            ['backup_type'],
                            buckets=[300, 600, 1800, 3600, 7200, 14400])

backup_size = Gauge('backup_size_bytes',
                    'Size of backup file in bytes',
                    ['backup_type'])

backup_failures = Counter('backup_failures_total',
                          'Total number of backup failures',
                          ['backup_type'])

def collect_backup_metrics():
    """Collect metrics from backup catalog database"""
    query = """
        SELECT
            backup_type,
            EXTRACT(EPOCH FROM MAX(backup_timestamp)) as last_success,
            AVG(EXTRACT(EPOCH FROM (end_time - start_time))) as avg_duration,
            AVG(backup_size_bytes) as avg_size
        FROM backup_catalog
        WHERE status = 'success'
        GROUP BY backup_type;
    """

    result = subprocess.run(
        ['psql', '-d', 'marine_incidents', '-t', '-A', '-c', query],
        capture_output=True, text=True
    )

    for line in result.stdout.strip().split('\n'):
        backup_type, last_success, avg_duration, avg_size = line.split('|')

        backup_last_success.labels(backup_type=backup_type).set(float(last_success))
        backup_duration.labels(backup_type=backup_type).observe(float(avg_duration))
        backup_size.labels(backup_type=backup_type).set(float(avg_size))

if __name__ == '__main__':
    # Start Prometheus metrics server
    start_http_server(9100)

    # Collect metrics every 60 seconds
    while True:
        collect_backup_metrics()
        time.sleep(60)
```

### 11.3 Alert Rules

```yaml
# /etc/prometheus/alerts/backup-alerts.yml

groups:
  - name: backup_alerts
    interval: 5m
    rules:
      - alert: BackupMissing
        expr: (time() - backup_last_success_timestamp) > 86400
        for: 1h
        labels:
          severity: critical
          team: dba
        annotations:
          summary: "Backup missing for {{ $labels.backup_type }}"
          description: "No successful backup for {{ $labels.backup_type }} in last 24 hours"

      - alert: BackupDurationHigh
        expr: backup_duration_seconds > 14400
        for: 10m
        labels:
          severity: warning
          team: dba
        annotations:
          summary: "Backup taking too long"
          description: "{{ $labels.backup_type }} backup exceeded 4 hours"

      - alert: BackupSizeAnomaly
        expr: |
          abs(backup_size_bytes - avg_over_time(backup_size_bytes[7d])) /
          avg_over_time(backup_size_bytes[7d]) > 0.2
        for: 30m
        labels:
          severity: warning
          team: dba
        annotations:
          summary: "Backup size anomaly detected"
          description: "{{ $labels.backup_type }} size deviated >20% from 7-day average"

      - alert: BackupStorageFull
        expr: (node_filesystem_avail_bytes{mountpoint="/backups"} /
               node_filesystem_size_bytes{mountpoint="/backups"}) < 0.2
        for: 15m
        labels:
          severity: critical
          team: ops
        annotations:
          summary: "Backup storage critically low"
          description: "Less than 20% space available on /backups"

      - alert: RestoreTestOverdue
        expr: (time() - restore_test_last_success_timestamp) > 2592000
        for: 1d
        labels:
          severity: warning
          team: dba
        annotations:
          summary: "Restore test overdue"
          description: "No successful restore test in last 30 days"

      - alert: IntegrityCheckFailed
        expr: increase(backup_integrity_check_failures[1h]) > 0
        for: 5m
        labels:
          severity: critical
          team: dba
        annotations:
          summary: "Backup integrity check failed"
          description: "{{ $value }} integrity check failures in last hour"
```

### 11.4 Notification Channels

```yaml
# /etc/alertmanager/config.yml

route:
  receiver: 'default'
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10m
  repeat_interval: 12h

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true

    - match:
        severity: warning
      receiver: 'slack'

    - match:
        team: dba
      receiver: 'dba-team'

receivers:
  - name: 'default'
    email_configs:
      - to: 'ops@marine-safety.gov'
        from: 'alerts@marine-safety.gov'
        smarthost: 'smtp.marine-safety.gov:587'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<PAGERDUTY_SERVICE_KEY>'
        description: '{{ .GroupLabels.alertname }}'

  - name: 'slack'
    slack_configs:
      - api_url: '<SLACK_WEBHOOK_URL>'
        channel: '#backup-alerts'
        title: 'Backup Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'dba-team'
    email_configs:
      - to: 'dba-team@marine-safety.gov'
        from: 'alerts@marine-safety.gov'
    slack_configs:
      - api_url: '<SLACK_WEBHOOK_URL>'
        channel: '#dba-team'
```

---

## 12. Automation Scripts

### 12.1 Master Backup Orchestration Script

```bash
#!/bin/bash
# /scripts/automation/master_backup.sh
# Master orchestration script for all backup operations

set -e
set -o pipefail

# Configuration
BACKUP_ROOT="/backups"
LOG_DIR="/var/log/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/master_backup_${TIMESTAMP}.log"

# Logging function
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handler
error_handler() {
  log "ERROR: Backup failed at line $1"
  # Send alert
  mail -s "CRITICAL: Backup Failure" \
    backup-team@marine-safety.gov <<< "Backup failed. Check log: $LOG_FILE"
  exit 1
}

trap 'error_handler $LINENO' ERR

# Main execution
log "=== Starting Master Backup Orchestration ==="

# Step 1: Pre-backup validation
log "Step 1: Pre-backup validation"
./pre_backup_checks.sh || exit 1

# Step 2: Database backup
log "Step 2: Database backup"
./database_backup.sh

# Step 3: Raw data backup
log "Step 3: Raw data backup"
./raw_data_backup.sh

# Step 4: Configuration backup
log "Step 4: Configuration backup"
./config_backup.sh

# Step 5: Log backup
log "Step 5: Log backup"
./logs_backup.sh

# Step 6: Encrypt all backups
log "Step 6: Encrypting backups"
for file in ${BACKUP_ROOT}/staging/${TIMESTAMP}/*; do
  ./encrypt_backup.sh "$file"
done

# Step 7: Upload to S3
log "Step 7: Uploading to S3"
aws s3 sync ${BACKUP_ROOT}/staging/${TIMESTAMP}/ \
  s3://marine-backups/$(date +%Y/%m/%d)/ \
  --storage-class STANDARD_IA \
  --metadata "timestamp=${TIMESTAMP},backup-type=automated"

# Step 8: Replicate to off-site
log "Step 8: Replicating to off-site storage"
rsync -avz --delete \
  ${BACKUP_ROOT}/staging/${TIMESTAMP}/ \
  backup-server:/backups/marine/$(date +%Y/%m/%d)/

# Step 9: Update backup catalog
log "Step 9: Updating backup catalog"
psql -d marine_incidents -c "
  INSERT INTO backup_catalog (
    backup_timestamp, backup_type, backup_size_bytes,
    status, s3_location
  ) VALUES (
    '${TIMESTAMP}', 'full',
    $(du -sb ${BACKUP_ROOT}/staging/${TIMESTAMP} | cut -f1),
    'success',
    's3://marine-backups/$(date +%Y/%m/%d)/'
  );
"

# Step 10: Cleanup old backups
log "Step 10: Cleanup old backups"
./cleanup_old_backups.sh

# Step 11: Post-backup validation
log "Step 11: Post-backup validation"
./post_backup_validation.sh

# Step 12: Send success notification
log "=== Backup Orchestration Complete ==="
mail -s "SUCCESS: Backup Complete" \
  backup-team@marine-safety.gov < "$LOG_FILE"

# Export metrics to Prometheus
curl -X POST http://localhost:9091/metrics/job/backup_master \
  --data-binary @- <<EOF
backup_last_success_timestamp $(date +%s)
backup_duration_seconds $SECONDS
backup_size_bytes $(du -sb ${BACKUP_ROOT}/staging/${TIMESTAMP} | cut -f1)
EOF
```

### 12.2 Automated Restore Script

```bash
#!/bin/bash
# /scripts/automation/automated_restore.sh
# Automated restore with minimal manual intervention

set -e

# Configuration
RESTORE_TARGET_DB="marine_incidents"
BACKUP_SOURCE=$1  # "s3", "local", "offsite"
RESTORE_TIMESTAMP=$2  # Optional: specific backup timestamp

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "=== Starting Automated Restore ==="
log "Source: $BACKUP_SOURCE"
log "Target DB: $RESTORE_TARGET_DB"

# Step 1: Identify backup to restore
case $BACKUP_SOURCE in
  "s3")
    if [ -z "$RESTORE_TIMESTAMP" ]; then
      # Find latest backup
      BACKUP_KEY=$(aws s3 ls s3://marine-backups/database/ \
        --recursive | sort | tail -1 | awk '{print $4}')
    else
      BACKUP_KEY="database/${RESTORE_TIMESTAMP}/full_${RESTORE_TIMESTAMP}.dump.enc"
    fi

    log "Identified backup: s3://marine-backups/$BACKUP_KEY"

    # Download backup
    LOCAL_BACKUP="/tmp/restore_$(basename $BACKUP_KEY)"
    aws s3 cp "s3://marine-backups/$BACKUP_KEY" "$LOCAL_BACKUP"
    ;;

  "local")
    LOCAL_BACKUP=$(ls -t /backups/database/full_*.dump.enc | head -1)
    log "Using local backup: $LOCAL_BACKUP"
    ;;

  "offsite")
    log "Retrieving from off-site storage..."
    LATEST_OFFSITE=$(ssh backup-server "ls -t /backups/marine/database/full_*.dump.enc | head -1")
    LOCAL_BACKUP="/tmp/restore_$(basename $LATEST_OFFSITE)"
    scp backup-server:$LATEST_OFFSITE "$LOCAL_BACKUP"
    ;;
esac

# Step 2: Decrypt backup
log "Decrypting backup..."
DECRYPTED_BACKUP="${LOCAL_BACKUP%.enc}"
./decrypt_backup.sh "$LOCAL_BACKUP" "$DECRYPTED_BACKUP"

# Step 3: Verify integrity
log "Verifying backup integrity..."
if [ -f "${LOCAL_BACKUP}.sha256" ]; then
  sha256sum -c "${LOCAL_BACKUP}.sha256" || {
    log "ERROR: Integrity check failed!"
    exit 1
  }
fi

# Step 4: Stop dependent services
log "Stopping dependent services..."
systemctl stop marine-api
systemctl stop marine-etl

# Step 5: Create restore point
log "Creating restore point..."
RESTORE_POINT_DB="${RESTORE_TARGET_DB}_pre_restore_$(date +%Y%m%d_%H%M%S)"
psql -U postgres -c "
  CREATE DATABASE $RESTORE_POINT_DB WITH TEMPLATE $RESTORE_TARGET_DB;
"

# Step 6: Drop and recreate target database
log "Recreating target database..."
psql -U postgres -c "DROP DATABASE IF EXISTS ${RESTORE_TARGET_DB};"
psql -U postgres -c "CREATE DATABASE ${RESTORE_TARGET_DB};"

# Step 7: Restore database
log "Restoring database..."
pg_restore -h localhost -U marine_admin \
  -d $RESTORE_TARGET_DB \
  --format=custom \
  --jobs=4 \
  --verbose \
  --no-owner \
  --no-privileges \
  "$DECRYPTED_BACKUP"

# Step 8: Validate restore
log "Validating restore..."
VALIDATION_RESULT=$(psql -d $RESTORE_TARGET_DB -t -c "
  SELECT COUNT(*) FROM incidents;
")

if [ $VALIDATION_RESULT -gt 0 ]; then
  log "✓ Validation passed: $VALIDATION_RESULT incidents found"
else
  log "✗ Validation failed: No data in incidents table"

  # Rollback to restore point
  log "Rolling back to restore point..."
  psql -U postgres -c "DROP DATABASE $RESTORE_TARGET_DB;"
  psql -U postgres -c "ALTER DATABASE $RESTORE_POINT_DB RENAME TO $RESTORE_TARGET_DB;"

  exit 1
fi

# Step 9: Restart services
log "Restarting services..."
systemctl start marine-api
systemctl start marine-etl

# Step 10: Verify application health
sleep 10
curl -f http://localhost:8000/health || {
  log "WARNING: Application health check failed"
}

# Step 11: Cleanup
log "Cleaning up temporary files..."
rm -f "$LOCAL_BACKUP" "$DECRYPTED_BACKUP"

log "=== Automated Restore Complete ==="
log "Restore point database: $RESTORE_POINT_DB (keep for 7 days)"
```

### 12.3 Backup Catalog Management

```sql
-- /scripts/automation/backup_catalog_schema.sql

CREATE TABLE IF NOT EXISTS backup_catalog (
  id SERIAL PRIMARY KEY,
  backup_timestamp TIMESTAMP NOT NULL,
  backup_type VARCHAR(50) NOT NULL, -- 'full', 'incremental', 'differential'
  backup_size_bytes BIGINT,
  status VARCHAR(20) NOT NULL, -- 'success', 'failed', 'in_progress'
  start_time TIMESTAMP DEFAULT NOW(),
  end_time TIMESTAMP,
  s3_location TEXT,
  local_location TEXT,
  offsite_location TEXT,
  checksum_sha256 VARCHAR(64),
  encryption_key_id VARCHAR(100),
  retention_expiry_date DATE,
  notes TEXT,
  created_by VARCHAR(100) DEFAULT CURRENT_USER
);

CREATE INDEX idx_backup_timestamp ON backup_catalog(backup_timestamp DESC);
CREATE INDEX idx_backup_status ON backup_catalog(status);
CREATE INDEX idx_retention_expiry ON backup_catalog(retention_expiry_date);

-- Backup audit log
CREATE TABLE IF NOT EXISTS backup_audit_log (
  id SERIAL PRIMARY KEY,
  action VARCHAR(50) NOT NULL, -- 'backup_start', 'backup_complete', 'restore_start', etc.
  timestamp TIMESTAMP DEFAULT NOW(),
  backup_id INTEGER REFERENCES backup_catalog(id),
  details JSONB,
  performed_by VARCHAR(100) DEFAULT CURRENT_USER
);

-- Restore history
CREATE TABLE IF NOT EXISTS restore_history (
  id SERIAL PRIMARY KEY,
  restore_timestamp TIMESTAMP DEFAULT NOW(),
  backup_id INTEGER REFERENCES backup_catalog(id),
  restore_type VARCHAR(50), -- 'full', 'pitr', 'table-level'
  target_database VARCHAR(100),
  restore_duration_seconds INTEGER,
  status VARCHAR(20),
  validated BOOLEAN DEFAULT FALSE,
  performed_by VARCHAR(100) DEFAULT CURRENT_USER,
  notes TEXT
);

-- Views for monitoring
CREATE OR REPLACE VIEW backup_health_summary AS
SELECT
  backup_type,
  COUNT(*) as total_backups,
  SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_backups,
  ROUND(AVG(EXTRACT(EPOCH FROM (end_time - start_time)))) as avg_duration_seconds,
  pg_size_pretty(AVG(backup_size_bytes)::BIGINT) as avg_backup_size,
  MAX(backup_timestamp) as last_backup_time
FROM backup_catalog
WHERE backup_timestamp > NOW() - INTERVAL '30 days'
GROUP BY backup_type;

-- Function to calculate next retention expiry
CREATE OR REPLACE FUNCTION calculate_retention_expiry(
  p_backup_type VARCHAR,
  p_backup_timestamp TIMESTAMP
)
RETURNS DATE AS $$
BEGIN
  RETURN CASE p_backup_type
    WHEN 'daily' THEN (p_backup_timestamp + INTERVAL '7 days')::DATE
    WHEN 'weekly' THEN (p_backup_timestamp + INTERVAL '4 weeks')::DATE
    WHEN 'monthly' THEN (p_backup_timestamp + INTERVAL '12 months')::DATE
    WHEN 'yearly' THEN (p_backup_timestamp + INTERVAL '7 years')::DATE
    ELSE (p_backup_timestamp + INTERVAL '30 days')::DATE
  END;
END;
$$ LANGUAGE plpgsql;
```

---

## 13. Compliance & Documentation

### 13.1 Backup Compliance Checklist

```yaml
compliance_requirements:
  - requirement: Daily backups executed
    frequency: Daily
    verification: Check backup_catalog table
    responsible: DBA Team

  - requirement: Weekly full backup verification
    frequency: Weekly
    verification: Execute restore test
    responsible: DBA Team

  - requirement: Monthly restore drill
    frequency: Monthly
    verification: Document restore test results
    responsible: Operations Team

  - requirement: Quarterly disaster recovery test
    frequency: Quarterly
    verification: Complete DR drill with documentation
    responsible: IT Management

  - requirement: Backup encryption verified
    frequency: Monthly
    verification: Audit encryption keys and methods
    responsible: Security Team

  - requirement: Off-site backup replication
    frequency: Daily
    verification: Verify replication status
    responsible: Operations Team

  - requirement: Retention policy enforcement
    frequency: Daily
    verification: Automated cleanup logs
    responsible: DBA Team

  - requirement: Access control audit
    frequency: Quarterly
    verification: Review backup access permissions
    responsible: Security Team
```

### 13.2 Annual DR Audit Report Template

```markdown
# Disaster Recovery Audit Report
## Marine Safety Incidents Database

**Reporting Period:** [YYYY-01-01] to [YYYY-12-31]
**Report Date:** [YYYY-01-15]
**Auditor:** [Name, Title]

---

## Executive Summary

[2-3 paragraph summary of DR posture, key findings, and recommendations]

---

## Backup Statistics

| **Metric** | **Target** | **Actual** | **Status** |
|------------|------------|------------|------------|
| Backup Success Rate | 99% | [XX]% | ✓/✗ |
| Average RTO | 4 hours | [XX] hours | ✓/✗ |
| Average RPO | 15 minutes | [XX] minutes | ✓/✗ |
| Monthly Restore Tests | 12 | [XX] | ✓/✗ |
| Quarterly DR Drills | 4 | [XX] | ✓/✗ |

---

## Backup Completeness

- Total Backups Executed: [XXXX]
- Successful Backups: [XXXX] ([XX]%)
- Failed Backups: [XX]
- Average Backup Size: [XX] GB
- Total Data Protected: [XX] TB

---

## Restore Tests Performed

| **Date** | **Type** | **Duration** | **Data Loss** | **Status** |
|----------|----------|--------------|---------------|------------|
| [YYYY-MM-DD] | Full Restore | [XX] hours | [XX] minutes | Pass/Fail |
| [YYYY-MM-DD] | PITR | [XX] hours | [XX] minutes | Pass/Fail |
| [YYYY-MM-DD] | Table-Level | [XX] minutes | None | Pass/Fail |

---

## Disaster Recovery Drills

### Q1 Drill: [Scenario]
- **Date:** [YYYY-MM-DD]
- **Participants:** [Names/Roles]
- **RTO Achieved:** [XX] hours
- **RPO Achieved:** [XX] minutes
- **Findings:** [Summary of findings]
- **Action Items:** [List of action items]

[Repeat for Q2, Q3, Q4]

---

## Compliance Status

- ✓ GDPR Data Retention: Compliant
- ✓ Encryption Standards: AES-256 enforced
- ✓ Access Controls: Reviewed and updated
- ✓ Off-site Replication: Active and verified

---

## Findings and Recommendations

### Critical Findings
1. [Finding 1]
   - **Impact:** [Description]
   - **Recommendation:** [Action to take]
   - **Priority:** High
   - **Due Date:** [YYYY-MM-DD]

### Medium Findings
[List medium-priority findings]

### Low Findings
[List low-priority findings]

---

## Action Items

| **Item** | **Owner** | **Due Date** | **Status** |
|----------|-----------|--------------|------------|
| [Action 1] | [Name] | [YYYY-MM-DD] | Open/Closed |
| [Action 2] | [Name] | [YYYY-MM-DD] | Open/Closed |

---

## Conclusion

[Summary paragraph with overall assessment]

---

**Approved By:**
[Name, Title, Date]

**Distribution:**
- IT Management
- DBA Team
- Security Team
- Compliance Officer
```

---

## 14. Emergency Contact Information

```yaml
emergency_contacts:
  primary_dba:
    name: "John Smith"
    role: "Senior Database Administrator"
    phone: "+1-555-0101"
    email: "john.smith@marine-safety.gov"
    backup_contact: "Jane Doe"

  backup_dba:
    name: "Jane Doe"
    role: "Database Administrator"
    phone: "+1-555-0102"
    email: "jane.doe@marine-safety.gov"

  it_manager:
    name: "Robert Johnson"
    role: "IT Operations Manager"
    phone: "+1-555-0103"
    email: "robert.johnson@marine-safety.gov"

  security_team:
    name: "Security Operations Center"
    phone: "+1-555-0199"
    email: "security@marine-safety.gov"
    availability: "24/7"

  cloud_provider_support:
    aws_support: "+1-866-947-6782"
    support_plan: "Enterprise"
    account_id: "123456789012"

  vendor_support:
    postgresql_support: "support@postgresql.org"
    backup_software: "support@backupsoftware.com"
```

---

## 15. Revision History

| **Version** | **Date** | **Author** | **Changes** |
|-------------|----------|------------|-------------|
| 1.0 | 2025-10-03 | System Architecture Designer | Initial comprehensive specification |

---

## Appendix A: Backup Commands Quick Reference

```bash
# Full database backup
pg_dump -h localhost -U marine_admin -d marine_incidents \
  --format=custom --file=backup.dump --compress=9

# Table-specific backup
pg_dump -h localhost -U marine_admin -d marine_incidents \
  --table=incidents --format=custom --file=incidents.dump

# Schema-only backup
pg_dump -h localhost -U marine_admin -d marine_incidents \
  --schema-only --file=schema.sql

# Full database restore
pg_restore -h localhost -U marine_admin -d marine_incidents \
  --format=custom --jobs=4 backup.dump

# PITR restore
# (See Section 8.2 for complete procedure)

# List backup contents
pg_restore --list backup.dump

# WAL archiving status
SELECT * FROM pg_stat_archiver;

# Check replication lag
SELECT
  client_addr,
  state,
  sync_state,
  pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS pending_bytes
FROM pg_stat_replication;
```

---

## Appendix B: Disaster Recovery Decision Tree

```
Disaster Detected
│
├─ Data Corruption?
│  ├─ Isolated table → Table-level restore (Section 8.3)
│  └─ Multiple tables → Full restore (Section 8.1)
│
├─ Accidental Deletion?
│  ├─ Recent (< 4 hours) → Point-in-time recovery (Section 8.2)
│  └─ Older → Undelete from backup (Section 9.2)
│
├─ Complete System Loss?
│  ├─ Hardware failure → Restore to new hardware (Section 9.3)
│  └─ Data center outage → Failover to DR site (Section 9.3)
│
└─ Security Incident?
   ├─ Ransomware → Clean backup restore (Section 9.4)
   └─ Data breach → Forensics + restore from clean backup
```

---

## Appendix C: Glossary

- **RTO (Recovery Time Objective):** Maximum acceptable time to restore service after a disaster
- **RPO (Recovery Point Objective):** Maximum acceptable amount of data loss measured in time
- **WAL (Write-Ahead Logging):** PostgreSQL transaction log for point-in-time recovery
- **PITR (Point-in-Time Recovery):** Restore database to a specific moment in time
- **Full Backup:** Complete copy of all database objects
- **Incremental Backup:** Only data changed since last incremental backup
- **Differential Backup:** All data changed since last full backup
- **Cold Backup:** Backup taken while database is offline
- **Hot Backup:** Backup taken while database is online and operational

---

**END OF DOCUMENT**
