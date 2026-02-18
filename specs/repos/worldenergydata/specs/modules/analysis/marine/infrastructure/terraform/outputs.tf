# Marine Safety Incidents Database - Terraform Outputs
# Purpose: Export important resource information for use by other tools and teams

# ============================================================================
# Network Outputs
# ============================================================================

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "nat_gateway_ips" {
  description = "Elastic IPs of NAT Gateways"
  value       = var.enable_nat_gateway ? aws_eip.nat[*].public_ip : []
}

# ============================================================================
# RDS Database Outputs
# ============================================================================

output "database_endpoint" {
  description = "RDS PostgreSQL endpoint for database connections"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_address" {
  description = "RDS PostgreSQL hostname"
  value       = aws_db_instance.main.address
  sensitive   = true
}

output "database_port" {
  description = "RDS PostgreSQL port"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "Name of the PostgreSQL database"
  value       = aws_db_instance.main.db_name
}

output "database_username" {
  description = "Master username for PostgreSQL"
  value       = aws_db_instance.main.username
  sensitive   = true
}

output "database_password_secret_arn" {
  description = "ARN of Secrets Manager secret containing database password"
  value       = aws_secretsmanager_secret.db_password.arn
}

output "database_arn" {
  description = "ARN of the RDS instance"
  value       = aws_db_instance.main.arn
}

# ============================================================================
# ElastiCache Redis Outputs
# ============================================================================

output "redis_primary_endpoint" {
  description = "Primary endpoint for Redis cluster"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
  sensitive   = true
}

output "redis_reader_endpoint" {
  description = "Reader endpoint for Redis cluster"
  value       = aws_elasticache_replication_group.main.reader_endpoint_address
  sensitive   = true
}

output "redis_port" {
  description = "Redis port"
  value       = 6379
}

output "redis_auth_token_secret_arn" {
  description = "ARN of Secrets Manager secret containing Redis auth token"
  value       = aws_secretsmanager_secret.redis_auth_token.arn
}

output "redis_arn" {
  description = "ARN of the Redis replication group"
  value       = aws_elasticache_replication_group.main.arn
}

# ============================================================================
# S3 Bucket Outputs
# ============================================================================

output "s3_raw_data_bucket" {
  description = "Name of S3 bucket for raw data ingestion"
  value       = aws_s3_bucket.raw_data.id
}

output "s3_raw_data_bucket_arn" {
  description = "ARN of S3 bucket for raw data"
  value       = aws_s3_bucket.raw_data.arn
}

output "s3_backups_bucket" {
  description = "Name of S3 bucket for database backups"
  value       = aws_s3_bucket.backups.id
}

output "s3_backups_bucket_arn" {
  description = "ARN of S3 bucket for backups"
  value       = aws_s3_bucket.backups.arn
}

output "s3_exports_bucket" {
  description = "Name of S3 bucket for data exports"
  value       = aws_s3_bucket.exports.id
}

output "s3_exports_bucket_arn" {
  description = "ARN of S3 bucket for exports"
  value       = aws_s3_bucket.exports.arn
}

output "s3_kms_key_arn" {
  description = "ARN of KMS key used for S3 encryption"
  value       = aws_kms_key.s3.arn
}

# ============================================================================
# ECS Cluster Outputs
# ============================================================================

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.api.name
}

output "ecs_task_definition_arn" {
  description = "ARN of the ECS task definition"
  value       = aws_ecs_task_definition.api.arn
}

output "ecs_task_execution_role_arn" {
  description = "ARN of ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_role_arn" {
  description = "ARN of ECS task role"
  value       = aws_iam_role.ecs_task.arn
}

# ============================================================================
# ECR Repository Outputs
# ============================================================================

output "ecr_repository_url" {
  description = "URL of the ECR repository for API images"
  value       = aws_ecr_repository.api.repository_url
}

output "ecr_repository_arn" {
  description = "ARN of the ECR repository"
  value       = aws_ecr_repository.api.arn
}

output "ecr_repository_name" {
  description = "Name of the ECR repository"
  value       = aws_ecr_repository.api.name
}

# ============================================================================
# Load Balancer Outputs
# ============================================================================

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

output "alb_target_group_arn" {
  description = "ARN of the ALB target group"
  value       = aws_lb_target_group.api.arn
}

output "alb_security_group_id" {
  description = "Security group ID for the ALB"
  value       = aws_security_group.alb.id
}

# ============================================================================
# CloudFront Outputs
# ============================================================================

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.main.id
}

output "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.main.arn
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.main.domain_name
}

output "cloudfront_hosted_zone_id" {
  description = "Route53 zone ID for CloudFront distribution"
  value       = aws_cloudfront_distribution.main.hosted_zone_id
}

# ============================================================================
# Security Group Outputs
# ============================================================================

output "ecs_security_group_id" {
  description = "Security group ID for ECS tasks"
  value       = aws_security_group.ecs_tasks.id
}

output "rds_security_group_id" {
  description = "Security group ID for RDS"
  value       = aws_security_group.rds.id
}

output "redis_security_group_id" {
  description = "Security group ID for Redis"
  value       = aws_security_group.redis.id
}

# ============================================================================
# KMS Key Outputs
# ============================================================================

output "rds_kms_key_arn" {
  description = "ARN of KMS key for RDS encryption"
  value       = aws_kms_key.rds.arn
}

output "redis_kms_key_arn" {
  description = "ARN of KMS key for Redis encryption"
  value       = aws_kms_key.redis.arn
}

output "ecr_kms_key_arn" {
  description = "ARN of KMS key for ECR encryption"
  value       = aws_kms_key.ecr.arn
}

# ============================================================================
# CloudWatch Outputs
# ============================================================================

output "ecs_log_group_name" {
  description = "Name of CloudWatch log group for ECS"
  value       = aws_cloudwatch_log_group.ecs.name
}

output "redis_log_group_name" {
  description = "Name of CloudWatch log group for Redis"
  value       = aws_cloudwatch_log_group.redis.name
}

# ============================================================================
# Connection Information (for application configuration)
# ============================================================================

output "api_url" {
  description = "Public URL for the API (via CloudFront)"
  value       = "https://${aws_cloudfront_distribution.main.domain_name}"
}

output "environment_variables" {
  description = "Environment variables for application deployment"
  value = {
    ENVIRONMENT          = var.environment
    AWS_REGION          = var.aws_region
    DATABASE_HOST       = aws_db_instance.main.address
    DATABASE_PORT       = "5432"
    DATABASE_NAME       = var.database_name
    REDIS_HOST          = aws_elasticache_replication_group.main.primary_endpoint_address
    REDIS_PORT          = "6379"
    S3_RAW_DATA_BUCKET  = aws_s3_bucket.raw_data.id
    S3_BACKUPS_BUCKET   = aws_s3_bucket.backups.id
    S3_EXPORTS_BUCKET   = aws_s3_bucket.exports.id
    CDN_DOMAIN          = aws_cloudfront_distribution.main.domain_name
  }
  sensitive = true
}

# ============================================================================
# Secret ARNs (for ECS task definitions)
# ============================================================================

output "secrets_arns" {
  description = "ARNs of secrets for use in ECS task definitions"
  value = {
    database_password  = aws_secretsmanager_secret.db_password.arn
    redis_auth_token   = aws_secretsmanager_secret.redis_auth_token.arn
  }
  sensitive = true
}

# ============================================================================
# Auto-scaling Outputs
# ============================================================================

output "autoscaling_target_id" {
  description = "ID of the autoscaling target"
  value       = aws_appautoscaling_target.ecs.id
}

output "autoscaling_cpu_policy_name" {
  description = "Name of CPU-based autoscaling policy"
  value       = aws_appautoscaling_policy.ecs_cpu.name
}

output "autoscaling_memory_policy_name" {
  description = "Name of memory-based autoscaling policy"
  value       = aws_appautoscaling_policy.ecs_memory.name
}

# ============================================================================
# Cost Tracking Outputs
# ============================================================================

output "resource_tags" {
  description = "Common tags applied to all resources"
  value = {
    Project     = "MarineSafetyIncidents"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ============================================================================
# Quick Reference Guide
# ============================================================================

output "deployment_guide" {
  description = "Quick reference for deploying and managing the infrastructure"
  value = <<-EOT
    Marine Safety Incidents Database - Deployment Guide
    ====================================================

    API Endpoint: https://${aws_cloudfront_distribution.main.domain_name}

    Database:
      - Endpoint: ${aws_db_instance.main.endpoint}
      - Name: ${var.database_name}
      - Password: Stored in AWS Secrets Manager (${aws_secretsmanager_secret.db_password.name})

    Redis Cache:
      - Endpoint: ${aws_elasticache_replication_group.main.primary_endpoint_address}:6379
      - Auth Token: Stored in AWS Secrets Manager (${aws_secretsmanager_secret.redis_auth_token.name})

    S3 Buckets:
      - Raw Data: ${aws_s3_bucket.raw_data.id}
      - Backups: ${aws_s3_bucket.backups.id}
      - Exports: ${aws_s3_bucket.exports.id}

    Container Registry:
      - ECR: ${aws_ecr_repository.api.repository_url}

    ECS Cluster:
      - Cluster: ${aws_ecs_cluster.main.name}
      - Service: ${aws_ecs_service.api.name}

    Monitoring:
      - ECS Logs: /ecs/marine-safety-${var.environment}
      - Redis Logs: /aws/elasticache/marine-safety-${var.environment}

    To deploy a new version:
      1. Build and tag image: docker build -t ${aws_ecr_repository.api.repository_url}:latest .
      2. Push to ECR: docker push ${aws_ecr_repository.api.repository_url}:latest
      3. Update ECS service: aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.api.name} --force-new-deployment
  EOT
}
