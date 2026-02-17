# Marine Safety Incidents Database - Infrastructure Documentation

Complete Infrastructure as Code (IaC) for deploying and managing the Marine Safety Incidents Database on AWS.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Local Development](#local-development)
6. [Deployment](#deployment)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Monitoring](#monitoring)
9. [Maintenance](#maintenance)
10. [Troubleshooting](#troubleshooting)

## Overview

This infrastructure includes:

- **AWS RDS PostgreSQL**: Multi-AZ, encrypted database with automated backups
- **ElastiCache Redis**: High-availability caching layer
- **ECS Fargate**: Serverless container orchestration
- **Application Load Balancer**: Auto-scaling HTTPS load balancer
- **CloudFront CDN**: Global content delivery network
- **S3 Buckets**: Raw data, backups, and exports storage
- **Complete networking**: VPC, subnets, NAT gateways, security groups
- **GitHub Actions**: Automated CI/CD pipeline

## Architecture

```
Internet
   │
   ▼
CloudFront CDN
   │
   ├──────────────────┐
   │                  │
   ▼                  ▼
Application LB    S3 (Exports)
   │
   ▼
ECS Fargate Cluster
   │
   ├─────────┬──────────┐
   │         │          │
   ▼         ▼          ▼
RDS (Multi-AZ)  Redis   S3 (Raw Data/Backups)
```

### AWS Resources Created

- **Network**: VPC, 6 subnets (3 public, 3 private), NAT gateways, route tables
- **Compute**: ECS cluster, Fargate tasks, auto-scaling policies
- **Database**: RDS PostgreSQL 15.4 (Multi-AZ, encrypted)
- **Cache**: ElastiCache Redis 7.0 (Multi-AZ, encrypted)
- **Storage**: 4 S3 buckets (raw data, backups, exports, ALB logs)
- **CDN**: CloudFront distribution with custom domain support
- **Security**: KMS keys, security groups, IAM roles, Secrets Manager
- **Monitoring**: CloudWatch logs, Performance Insights, Container Insights

## Prerequisites

### Required Tools

```bash
# AWS CLI
aws --version  # >= 2.0

# Terraform
terraform --version  # >= 1.0

# Docker
docker --version  # >= 20.0

# Docker Compose
docker-compose --version  # >= 2.0
```

### AWS Credentials

```bash
# Configure AWS credentials
aws configure

# Or use environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

### Required AWS Services

- ECR (Elastic Container Registry)
- ECS (Elastic Container Service)
- RDS (Relational Database Service)
- ElastiCache
- S3
- CloudFront
- Secrets Manager
- KMS (Key Management Service)

## Quick Start

### 1. Local Development Setup

```bash
# Clone repository
git clone <repository-url>
cd infrastructure/

# Start local development stack
docker-compose up -d

# Verify services are running
docker-compose ps

# Access services:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - pgAdmin: http://localhost:5050
# - Redis Commander: http://localhost:8081
# - MinIO Console: http://localhost:9001
```

### 2. Initialize Terraform

```bash
cd terraform/

# Initialize Terraform
terraform init

# Create terraform.tfvars from example
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
vim terraform.tfvars
```

### 3. Deploy Infrastructure

```bash
# Validate configuration
terraform validate

# Plan deployment
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan

# Save outputs
terraform output > ../terraform-outputs.txt
```

## Local Development

### Starting the Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Remove all data (WARNING: destructive)
docker-compose down -v
```

### Running Tests

```bash
# Run all tests
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec api pytest tests/test_incidents.py -v
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d marine_safety

# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Rollback migration
docker-compose exec api alembic downgrade -1
```

### Redis Operations

```bash
# Access Redis CLI
docker-compose exec redis redis-cli -a redis_dev_password_change_in_production

# Flush all cache
docker-compose exec redis redis-cli -a redis_dev_password_change_in_production FLUSHALL
```

## Deployment

### Building and Pushing Docker Image

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t marine-safety-api:latest .

# Tag for ECR
docker tag marine-safety-api:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/marine-safety-api-production:latest

# Push to ECR
docker push \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/marine-safety-api-production:latest
```

### Deploying to ECS

```bash
# Update ECS service with new image
aws ecs update-service \
  --cluster marine-safety-cluster-production \
  --service marine-safety-api-production \
  --force-new-deployment

# Wait for deployment to complete
aws ecs wait services-stable \
  --cluster marine-safety-cluster-production \
  --services marine-safety-api-production
```

### Manual Deployment Steps

1. **Build Docker image** with version tag
2. **Push to ECR** repository
3. **Run database migrations** (if needed)
4. **Update ECS task definition** with new image
5. **Deploy to ECS** with force new deployment
6. **Monitor deployment** in CloudWatch
7. **Run smoke tests** to verify deployment
8. **Invalidate CloudFront cache** (if needed)

## CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline automatically:

1. **Lints code** (Black, Flake8, MyPy, Bandit)
2. **Runs tests** with PostgreSQL and Redis services
3. **Builds Docker image** and pushes to ECR
4. **Scans for vulnerabilities** with Trivy
5. **Runs database migrations** on target environment
6. **Deploys to ECS** with zero-downtime
7. **Runs smoke tests** to verify deployment
8. **Rolls back** automatically on failure

### Triggering Deployment

```bash
# Push to main branch for production
git push origin main

# Push to staging branch for staging
git push origin staging

# Manual deployment via GitHub UI
# Go to Actions > Marine Safety CI/CD Pipeline > Run workflow
```

### Required GitHub Secrets

Configure these secrets in your GitHub repository:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_ACCOUNT_ID
DB_USER
DB_HOST
CLOUDFRONT_DISTRIBUTION_ID
SLACK_WEBHOOK (optional)
```

## Monitoring

### CloudWatch Dashboards

Access CloudWatch dashboards for:

- **ECS Metrics**: CPU, memory, task count
- **RDS Metrics**: Connections, IOPS, storage
- **Redis Metrics**: Cache hit rate, memory usage
- **ALB Metrics**: Request count, latency, errors

### Logs

```bash
# View ECS logs
aws logs tail /ecs/marine-safety-production --follow

# View Redis logs
aws logs tail /aws/elasticache/marine-safety-production --follow

# Query logs with Logs Insights
aws logs start-query \
  --log-group-name /ecs/marine-safety-production \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/'
```

### Alarms

Pre-configured CloudWatch alarms:

- High CPU utilization (>80%)
- High memory utilization (>90%)
- Database connection errors
- Redis connection errors
- API response time (>2s)
- 5xx error rate (>5%)

## Maintenance

### Database Backups

```bash
# Manual backup
aws rds create-db-snapshot \
  --db-instance-identifier marine-safety-db-production \
  --db-snapshot-identifier marine-safety-manual-backup-$(date +%Y%m%d)

# List backups
aws rds describe-db-snapshots \
  --db-instance-identifier marine-safety-db-production

# Restore from backup
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier marine-safety-db-restored \
  --db-snapshot-identifier <snapshot-id>
```

### Scaling ECS Service

```bash
# Scale up
aws ecs update-service \
  --cluster marine-safety-cluster-production \
  --service marine-safety-api-production \
  --desired-count 5

# Scale down
aws ecs update-service \
  --cluster marine-safety-cluster-production \
  --service marine-safety-api-production \
  --desired-count 2
```

### Database Maintenance

```bash
# Performance Insights
# View in AWS Console: RDS > marine-safety-db-production > Performance Insights

# Analyze slow queries
docker-compose exec postgres psql -U postgres -d marine_safety -c \
  "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Vacuum database
docker-compose exec postgres psql -U postgres -d marine_safety -c "VACUUM ANALYZE;"
```

## Troubleshooting

### Common Issues

#### 1. ECS Task Fails to Start

```bash
# Check task logs
aws ecs describe-tasks \
  --cluster marine-safety-cluster-production \
  --tasks <task-id>

# View CloudWatch logs
aws logs tail /ecs/marine-safety-production --follow

# Common causes:
# - Incorrect environment variables
# - Database connection failure
# - Secrets Manager permissions
# - Image not found in ECR
```

#### 2. Database Connection Issues

```bash
# Test database connectivity
docker-compose exec api python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:password@postgres:5432/marine_safety')
conn = engine.connect()
print('Connected successfully')
"

# Check security group rules
aws ec2 describe-security-groups \
  --group-ids <security-group-id>
```

#### 3. Redis Connection Issues

```bash
# Test Redis connectivity
docker-compose exec api python -c "
import redis
r = redis.Redis(host='redis', port=6379, password='password', decode_responses=True)
r.ping()
print('Connected to Redis')
"

# Check Redis cluster status
aws elasticache describe-replication-groups \
  --replication-group-id marine-safety-production
```

#### 4. High API Latency

```bash
# Check ECS CPU/Memory metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=marine-safety-api-production \
  --start-time $(date -u -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date -u --iso-8601=seconds) \
  --period 300 \
  --statistics Average

# Check database performance
# AWS Console: RDS > Performance Insights

# Check Redis hit rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name CacheHitRate \
  --dimensions Name=CacheClusterId,Value=marine-safety-production-001 \
  --start-time $(date -u -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date -u --iso-8601=seconds) \
  --period 300 \
  --statistics Average
```

### Getting Help

- Check CloudWatch Logs for detailed error messages
- Review ECS task events for deployment issues
- Verify security group rules and network ACLs
- Check IAM permissions for ECS task roles
- Review Terraform state for infrastructure drift

## Cost Optimization

### Estimated Monthly Costs (Production)

| Service | Configuration | Est. Cost/Month |
|---------|--------------|----------------|
| RDS PostgreSQL | db.r6g.large Multi-AZ | $400 |
| ElastiCache Redis | cache.r6g.large x2 | $320 |
| ECS Fargate | 2 vCPU, 4GB x 2 tasks | $150 |
| ALB | Application Load Balancer | $25 |
| NAT Gateway | 3 AZs | $100 |
| S3 | 100GB storage | $5 |
| CloudFront | 1TB transfer | $85 |
| Data Transfer | Various | $50 |
| **Total** | | **~$1,135/month** |

### Cost Saving Tips

1. Use `db.t3` instances for development/staging
2. Disable NAT Gateway in development (`enable_nat_gateway = false`)
3. Use single-AZ for non-production (`db_multi_az = false`)
4. Implement S3 lifecycle policies for old data
5. Use reserved instances for predictable workloads
6. Enable CloudFront query string caching

## Security Best Practices

- ✅ All data encrypted at rest (RDS, Redis, S3)
- ✅ All data encrypted in transit (TLS 1.2+)
- ✅ Secrets stored in AWS Secrets Manager
- ✅ Least privilege IAM policies
- ✅ Multi-AZ for high availability
- ✅ Automated backups enabled
- ✅ Security group rules follow principle of least privilege
- ✅ Container image scanning with Trivy
- ✅ No hard-coded credentials

## License

[Your License Here]

## Support

For issues or questions:
- Create an issue in GitHub repository
- Contact data team at data-team@example.com
- Check internal documentation wiki
