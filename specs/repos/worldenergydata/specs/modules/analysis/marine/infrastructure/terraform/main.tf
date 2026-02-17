# Marine Safety Incidents Database - Terraform Infrastructure
# Provider: AWS
# Purpose: Production-ready infrastructure for marine safety data processing and API

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # State management - configure backend for team collaboration
  backend "s3" {
    bucket         = "marine-safety-terraform-state"
    key            = "marine-incidents/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "MarineSafetyIncidents"
      Environment = var.environment
      ManagedBy   = "Terraform"
      CostCenter  = "DataAnalysis"
    }
  }
}

# ============================================================================
# VPC and Network Configuration
# ============================================================================

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "marine-safety-vpc-${var.environment}"
  }
}

# Internet Gateway for public subnets
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "marine-safety-igw-${var.environment}"
  }
}

# Public subnets for load balancers (multi-AZ)
resource "aws_subnet" "public" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "marine-safety-public-${var.availability_zones[count.index]}"
    Type = "Public"
  }
}

# Private subnets for application and database (multi-AZ)
resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "marine-safety-private-${var.availability_zones[count.index]}"
    Type = "Private"
  }
}

# NAT Gateways for private subnet internet access (one per AZ for HA)
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? length(var.availability_zones) : 0
  domain = "vpc"

  tags = {
    Name = "marine-safety-nat-eip-${var.availability_zones[count.index]}"
  }
}

resource "aws_nat_gateway" "main" {
  count         = var.enable_nat_gateway ? length(var.availability_zones) : 0
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name = "marine-safety-nat-${var.availability_zones[count.index]}"
  }

  depends_on = [aws_internet_gateway.main]
}

# Route table for public subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "marine-safety-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Route tables for private subnets (one per AZ)
resource "aws_route_table" "private" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.main[count.index].id
    }
  }

  tags = {
    Name = "marine-safety-private-rt-${var.availability_zones[count.index]}"
  }
}

resource "aws_route_table_association" "private" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# ============================================================================
# Security Groups
# ============================================================================

# Security group for Application Load Balancer
resource "aws_security_group" "alb" {
  name_prefix = "marine-safety-alb-"
  description = "Security group for Marine Safety ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP from internet (redirect to HTTPS)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "marine-safety-alb-sg"
  }
}

# Security group for ECS tasks
resource "aws_security_group" "ecs_tasks" {
  name_prefix = "marine-safety-ecs-"
  description = "Security group for Marine Safety ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTP from ALB"
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "marine-safety-ecs-sg"
  }
}

# Security group for RDS PostgreSQL
resource "aws_security_group" "rds" {
  name_prefix = "marine-safety-rds-"
  description = "Security group for Marine Safety RDS"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from ECS tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "marine-safety-rds-sg"
  }
}

# Security group for ElastiCache Redis
resource "aws_security_group" "redis" {
  name_prefix = "marine-safety-redis-"
  description = "Security group for Marine Safety Redis"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Redis from ECS tasks"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "marine-safety-redis-sg"
  }
}

# ============================================================================
# RDS PostgreSQL Database (Multi-AZ, Encrypted)
# ============================================================================

# DB subnet group for multi-AZ deployment
resource "aws_db_subnet_group" "main" {
  name       = "marine-safety-db-subnet-${var.environment}"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "marine-safety-db-subnet-group"
  }
}

# Random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store database password in Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name_prefix = "marine-safety-db-password-"
  description = "PostgreSQL database password for Marine Safety Incidents"

  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_password.result
}

# RDS PostgreSQL instance
resource "aws_db_instance" "main" {
  identifier     = "marine-safety-db-${var.environment}"
  engine         = "postgres"
  engine_version = var.postgres_version

  # Instance configuration
  instance_class        = var.db_instance_class
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  # Database configuration
  db_name  = var.database_name
  username = var.database_username
  password = random_password.db_password.result
  port     = 5432

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  # High availability and backup
  multi_az               = var.db_multi_az
  backup_retention_period = var.db_backup_retention_days
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  # Backup to S3
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  # Performance Insights
  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn
  performance_insights_retention_period = 7

  # Deletion protection
  deletion_protection = var.environment == "production" ? true : false
  skip_final_snapshot = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "marine-safety-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  # Parameter group for performance tuning
  parameter_group_name = aws_db_parameter_group.main.name

  tags = {
    Name = "marine-safety-db"
  }
}

# DB parameter group for PostgreSQL optimization
resource "aws_db_parameter_group" "main" {
  name_prefix = "marine-safety-postgres-"
  family      = "postgres15"
  description = "Custom parameter group for Marine Safety PostgreSQL"

  # Optimize for analytical workloads
  parameter {
    name  = "shared_buffers"
    value = "{DBInstanceClassMemory/4096}"  # 25% of instance memory
  }

  parameter {
    name  = "work_mem"
    value = "16384"  # 16MB for sorting operations
  }

  parameter {
    name  = "maintenance_work_mem"
    value = "524288"  # 512MB for maintenance operations
  }

  parameter {
    name  = "effective_cache_size"
    value = "{DBInstanceClassMemory/2048}"  # 50% of instance memory
  }

  parameter {
    name  = "max_connections"
    value = "200"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"  # Log queries slower than 1 second
  }

  tags = {
    Name = "marine-safety-db-params"
  }
}

# KMS key for RDS encryption
resource "aws_kms_key" "rds" {
  description             = "KMS key for Marine Safety RDS encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = {
    Name = "marine-safety-rds-key"
  }
}

resource "aws_kms_alias" "rds" {
  name          = "alias/marine-safety-rds-${var.environment}"
  target_key_id = aws_kms_key.rds.key_id
}

# ============================================================================
# ElastiCache Redis (for caching and session management)
# ============================================================================

# Redis subnet group
resource "aws_elasticache_subnet_group" "main" {
  name       = "marine-safety-redis-subnet-${var.environment}"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "marine-safety-redis-subnet-group"
  }
}

# Redis replication group (cluster mode disabled for simplicity)
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "marine-safety-${var.environment}"
  replication_group_description = "Redis cache for Marine Safety Incidents API"

  engine               = "redis"
  engine_version       = var.redis_version
  node_type            = var.redis_node_type
  num_cache_clusters   = var.redis_num_cache_nodes
  port                 = 6379

  # Network configuration
  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  # High availability
  automatic_failover_enabled = var.redis_num_cache_nodes > 1
  multi_az_enabled           = var.redis_num_cache_nodes > 1

  # Encryption
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token_enabled         = true
  auth_token                 = random_password.redis_auth_token.result
  kms_key_id                 = aws_kms_key.redis.arn

  # Backup
  snapshot_retention_limit = var.redis_snapshot_retention_limit
  snapshot_window          = "03:00-05:00"

  # Maintenance
  maintenance_window = "sun:05:00-sun:07:00"

  # Parameter group
  parameter_group_name = aws_elasticache_parameter_group.main.name

  # Logging
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "slow-log"
  }

  tags = {
    Name = "marine-safety-redis"
  }
}

# Random auth token for Redis
resource "random_password" "redis_auth_token" {
  length  = 32
  special = false
}

# Store Redis auth token in Secrets Manager
resource "aws_secretsmanager_secret" "redis_auth_token" {
  name_prefix = "marine-safety-redis-token-"
  description = "Redis auth token for Marine Safety Incidents"

  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "redis_auth_token" {
  secret_id     = aws_secretsmanager_secret.redis_auth_token.id
  secret_string = random_password.redis_auth_token.result
}

# KMS key for Redis encryption
resource "aws_kms_key" "redis" {
  description             = "KMS key for Marine Safety Redis encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = {
    Name = "marine-safety-redis-key"
  }
}

resource "aws_kms_alias" "redis" {
  name          = "alias/marine-safety-redis-${var.environment}"
  target_key_id = aws_kms_key.redis.key_id
}

# Redis parameter group
resource "aws_elasticache_parameter_group" "main" {
  name_prefix = "marine-safety-redis-"
  family      = "redis7"
  description = "Custom parameter group for Marine Safety Redis"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "timeout"
    value = "300"
  }

  tags = {
    Name = "marine-safety-redis-params"
  }
}

# CloudWatch log group for Redis
resource "aws_cloudwatch_log_group" "redis" {
  name              = "/aws/elasticache/marine-safety-${var.environment}"
  retention_in_days = 7

  tags = {
    Name = "marine-safety-redis-logs"
  }
}

# ============================================================================
# S3 Buckets (Raw Data, Backups, Exports)
# ============================================================================

# KMS key for S3 encryption
resource "aws_kms_key" "s3" {
  description             = "KMS key for Marine Safety S3 buckets"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = {
    Name = "marine-safety-s3-key"
  }
}

resource "aws_kms_alias" "s3" {
  name          = "alias/marine-safety-s3-${var.environment}"
  target_key_id = aws_kms_key.s3.key_id
}

# S3 bucket for raw data ingestion
resource "aws_s3_bucket" "raw_data" {
  bucket = "marine-safety-raw-data-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "marine-safety-raw-data"
    DataClass   = "Sensitive"
  }
}

resource "aws_s3_bucket_versioning" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    id     = "archive-old-data"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER_IR"
    }

    transition {
      days          = 180
      storage_class = "DEEP_ARCHIVE"
    }
  }
}

# S3 bucket for database backups
resource "aws_s3_bucket" "backups" {
  bucket = "marine-safety-backups-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name      = "marine-safety-backups"
    DataClass = "Critical"
  }
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "retain-backups"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "GLACIER_IR"
    }

    expiration {
      days = var.backup_retention_days
    }
  }
}

# S3 bucket for data exports
resource "aws_s3_bucket" "exports" {
  bucket = "marine-safety-exports-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name      = "marine-safety-exports"
    DataClass = "Public"
  }
}

resource "aws_s3_bucket_versioning" "exports" {
  bucket = aws_s3_bucket.exports.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "exports" {
  bucket = aws_s3_bucket.exports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "exports" {
  bucket = aws_s3_bucket.exports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_cors_configuration" "exports" {
  bucket = aws_s3_bucket.exports.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    max_age_seconds = 3000
  }
}

# ============================================================================
# ECS Fargate Cluster and Service
# ============================================================================

# ECS cluster
resource "aws_ecs_cluster" "main" {
  name = "marine-safety-cluster-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "marine-safety-cluster"
  }
}

# CloudWatch log group for ECS
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/marine-safety-${var.environment}"
  retention_in_days = 7

  tags = {
    Name = "marine-safety-ecs-logs"
  }
}

# IAM role for ECS task execution
resource "aws_iam_role" "ecs_task_execution" {
  name_prefix = "marine-safety-ecs-exec-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "marine-safety-ecs-execution-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional policy for Secrets Manager access
resource "aws_iam_role_policy" "ecs_secrets" {
  name_prefix = "marine-safety-ecs-secrets-"
  role        = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.db_password.arn,
          aws_secretsmanager_secret.redis_auth_token.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = [
          aws_kms_key.rds.arn,
          aws_kms_key.redis.arn
        ]
      }
    ]
  })
}

# IAM role for ECS task (application permissions)
resource "aws_iam_role" "ecs_task" {
  name_prefix = "marine-safety-ecs-task-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "marine-safety-ecs-task-role"
  }
}

# S3 access policy for task
resource "aws_iam_role_policy" "ecs_s3_access" {
  name_prefix = "marine-safety-s3-access-"
  role        = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.raw_data.arn,
          "${aws_s3_bucket.raw_data.arn}/*",
          aws_s3_bucket.exports.arn,
          "${aws_s3_bucket.exports.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ]
        Resource = [aws_kms_key.s3.arn]
      }
    ]
  })
}

# ECS task definition
resource "aws_ecs_task_definition" "api" {
  family                   = "marine-safety-api-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory

  execution_role_arn = aws_iam_role.ecs_task_execution.arn
  task_role_arn      = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "marine-safety-api"
    image = "${aws_ecr_repository.api.repository_url}:${var.api_image_tag}"

    portMappings = [{
      containerPort = var.container_port
      protocol      = "tcp"
    }]

    environment = [
      {
        name  = "ENVIRONMENT"
        value = var.environment
      },
      {
        name  = "AWS_REGION"
        value = var.aws_region
      },
      {
        name  = "DATABASE_HOST"
        value = aws_db_instance.main.address
      },
      {
        name  = "DATABASE_PORT"
        value = "5432"
      },
      {
        name  = "DATABASE_NAME"
        value = var.database_name
      },
      {
        name  = "DATABASE_USER"
        value = var.database_username
      },
      {
        name  = "REDIS_HOST"
        value = aws_elasticache_replication_group.main.primary_endpoint_address
      },
      {
        name  = "REDIS_PORT"
        value = "6379"
      },
      {
        name  = "S3_RAW_DATA_BUCKET"
        value = aws_s3_bucket.raw_data.id
      },
      {
        name  = "S3_EXPORTS_BUCKET"
        value = aws_s3_bucket.exports.id
      }
    ]

    secrets = [
      {
        name      = "DATABASE_PASSWORD"
        valueFrom = aws_secretsmanager_secret.db_password.arn
      },
      {
        name      = "REDIS_AUTH_TOKEN"
        valueFrom = aws_secretsmanager_secret.redis_auth_token.arn
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "api"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])

  tags = {
    Name = "marine-safety-api-task"
  }
}

# ECR repository for API images
resource "aws_ecr_repository" "api" {
  name                 = "marine-safety-api-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.ecr.arn
  }

  tags = {
    Name = "marine-safety-api-ecr"
  }
}

# ECR lifecycle policy
resource "aws_ecr_lifecycle_policy" "api" {
  repository = aws_ecr_repository.api.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = {
        type = "expire"
      }
    }]
  })
}

# KMS key for ECR encryption
resource "aws_kms_key" "ecr" {
  description             = "KMS key for Marine Safety ECR encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = {
    Name = "marine-safety-ecr-key"
  }
}

resource "aws_kms_alias" "ecr" {
  name          = "alias/marine-safety-ecr-${var.environment}"
  target_key_id = aws_kms_key.ecr.key_id
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "marine-safety-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = var.environment == "production"
  enable_http2              = true
  enable_cross_zone_load_balancing = true

  access_logs {
    bucket  = aws_s3_bucket.alb_logs.id
    enabled = true
  }

  tags = {
    Name = "marine-safety-alb"
  }
}

# S3 bucket for ALB logs
resource "aws_s3_bucket" "alb_logs" {
  bucket = "marine-safety-alb-logs-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "marine-safety-alb-logs"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    id     = "delete-old-logs"
    status = "Enabled"

    expiration {
      days = 30
    }
  }
}

resource "aws_s3_bucket_public_access_block" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ALB bucket policy for access logs
resource "aws_s3_bucket_policy" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        AWS = data.aws_elb_service_account.main.arn
      }
      Action   = "s3:PutObject"
      Resource = "${aws_s3_bucket.alb_logs.arn}/*"
    }]
  })
}

# ALB target group
resource "aws_lb_target_group" "api" {
  name        = "marine-safety-api-${var.environment}"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = {
    Name = "marine-safety-api-tg"
  }
}

# ALB listener (HTTPS)
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

# ALB listener (HTTP - redirect to HTTPS)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# ECS service
resource "aws_ecs_service" "api" {
  name            = "marine-safety-api-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "marine-safety-api"
    container_port   = var.container_port
  }

  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  enable_execute_command = var.environment != "production"

  tags = {
    Name = "marine-safety-api-service"
  }

  depends_on = [
    aws_lb_listener.https,
    aws_lb_listener.http
  ]
}

# Auto Scaling for ECS service
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = var.ecs_max_count
  min_capacity       = var.ecs_min_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto Scaling policy - CPU based
resource "aws_appautoscaling_policy" "ecs_cpu" {
  name               = "marine-safety-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Auto Scaling policy - Memory based
resource "aws_appautoscaling_policy" "ecs_memory" {
  name               = "marine-safety-memory-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 80.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# ============================================================================
# CloudFront CDN for API and Static Assets
# ============================================================================

# CloudFront Origin Access Identity for S3
resource "aws_cloudfront_origin_access_identity" "exports" {
  comment = "Marine Safety Exports OAI"
}

# Update S3 bucket policy to allow CloudFront
resource "aws_s3_bucket_policy" "exports" {
  bucket = aws_s3_bucket.exports.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        AWS = aws_cloudfront_origin_access_identity.exports.iam_arn
      }
      Action   = "s3:GetObject"
      Resource = "${aws_s3_bucket.exports.arn}/*"
    }]
  })
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "main" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Marine Safety Incidents CDN"
  default_root_object = "index.html"
  price_class         = var.cloudfront_price_class

  # ALB origin (API)
  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "alb"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # S3 origin (exports)
  origin {
    domain_name = aws_s3_bucket.exports.bucket_regional_domain_name
    origin_id   = "s3-exports"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.exports.cloudfront_access_identity_path
    }
  }

  # Default cache behavior (API)
  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD", "OPTIONS"]
    target_origin_id       = "alb"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = true
      headers      = ["Host", "Authorization"]

      cookies {
        forward = "all"
      }
    }

    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  # Cache behavior for exports
  ordered_cache_behavior {
    path_pattern           = "/exports/*"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD", "OPTIONS"]
    target_origin_id       = "s3-exports"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.acm_certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  tags = {
    Name = "marine-safety-cdn"
  }
}

# ============================================================================
# Data Sources
# ============================================================================

data "aws_caller_identity" "current" {}

data "aws_elb_service_account" "main" {}
