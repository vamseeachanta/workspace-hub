# Marine Safety Incidents Database - Terraform Variables
# Purpose: Define configurable parameters for infrastructure deployment

# ============================================================================
# General Configuration
# ============================================================================

variable "environment" {
  description = "Environment name (e.g., development, staging, production)"
  type        = string
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "availability_zones" {
  description = "List of availability zones for multi-AZ deployment"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# ============================================================================
# Network Configuration
# ============================================================================

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnet internet access"
  type        = bool
  default     = true
}

# ============================================================================
# RDS PostgreSQL Configuration
# ============================================================================

variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15.4"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
  validation {
    condition     = can(regex("^db\\.", var.db_instance_class))
    error_message = "Instance class must start with 'db.'"
  }
}

variable "db_allocated_storage" {
  description = "Initial allocated storage for RDS in GB"
  type        = number
  default     = 100
  validation {
    condition     = var.db_allocated_storage >= 20 && var.db_allocated_storage <= 65536
    error_message = "Allocated storage must be between 20 and 65536 GB."
  }
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS autoscaling in GB"
  type        = number
  default     = 500
  validation {
    condition     = var.db_max_allocated_storage >= var.db_allocated_storage
    error_message = "Max allocated storage must be greater than or equal to allocated storage."
  }
}

variable "database_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "marine_safety"
  validation {
    condition     = can(regex("^[a-z][a-z0-9_]*$", var.database_name))
    error_message = "Database name must start with a letter and contain only lowercase letters, numbers, and underscores."
  }
}

variable "database_username" {
  description = "Master username for PostgreSQL database"
  type        = string
  default     = "postgres"
  sensitive   = true
  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.database_username))
    error_message = "Database username must start with a letter and contain only alphanumeric characters and underscores."
  }
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = true
}

variable "db_backup_retention_days" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 7
  validation {
    condition     = var.db_backup_retention_days >= 1 && var.db_backup_retention_days <= 35
    error_message = "Backup retention must be between 1 and 35 days."
  }
}

# ============================================================================
# ElastiCache Redis Configuration
# ============================================================================

variable "redis_version" {
  description = "Redis version"
  type        = string
  default     = "7.0"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.medium"
  validation {
    condition     = can(regex("^cache\\.", var.redis_node_type))
    error_message = "Node type must start with 'cache.'"
  }
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes in the Redis cluster"
  type        = number
  default     = 2
  validation {
    condition     = var.redis_num_cache_nodes >= 1 && var.redis_num_cache_nodes <= 6
    error_message = "Number of cache nodes must be between 1 and 6."
  }
}

variable "redis_snapshot_retention_limit" {
  description = "Number of days to retain Redis snapshots"
  type        = number
  default     = 5
  validation {
    condition     = var.redis_snapshot_retention_limit >= 0 && var.redis_snapshot_retention_limit <= 35
    error_message = "Snapshot retention must be between 0 and 35 days."
  }
}

# ============================================================================
# S3 Configuration
# ============================================================================

variable "backup_retention_days" {
  description = "Number of days to retain S3 backups before deletion"
  type        = number
  default     = 90
  validation {
    condition     = var.backup_retention_days >= 1
    error_message = "Backup retention must be at least 1 day."
  }
}

# ============================================================================
# ECS Fargate Configuration
# ============================================================================

variable "ecs_task_cpu" {
  description = "CPU units for ECS task (1024 = 1 vCPU)"
  type        = string
  default     = "1024"
  validation {
    condition     = contains(["256", "512", "1024", "2048", "4096"], var.ecs_task_cpu)
    error_message = "CPU must be one of: 256, 512, 1024, 2048, 4096."
  }
}

variable "ecs_task_memory" {
  description = "Memory for ECS task in MB"
  type        = string
  default     = "2048"
  validation {
    condition     = contains(["512", "1024", "2048", "3072", "4096", "5120", "6144", "7168", "8192"], var.ecs_task_memory)
    error_message = "Memory must be a valid value for the selected CPU."
  }
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8000
  validation {
    condition     = var.container_port > 0 && var.container_port < 65536
    error_message = "Container port must be between 1 and 65535."
  }
}

variable "api_image_tag" {
  description = "Docker image tag for the API"
  type        = string
  default     = "latest"
}

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 2
  validation {
    condition     = var.ecs_desired_count >= 1
    error_message = "Desired count must be at least 1."
  }
}

variable "ecs_min_count" {
  description = "Minimum number of ECS tasks for auto-scaling"
  type        = number
  default     = 2
  validation {
    condition     = var.ecs_min_count >= 1
    error_message = "Minimum count must be at least 1."
  }
}

variable "ecs_max_count" {
  description = "Maximum number of ECS tasks for auto-scaling"
  type        = number
  default     = 10
  validation {
    condition     = var.ecs_max_count >= var.ecs_min_count
    error_message = "Maximum count must be greater than or equal to minimum count."
  }
}

# ============================================================================
# SSL/TLS Configuration
# ============================================================================

variable "acm_certificate_arn" {
  description = "ARN of ACM certificate for HTTPS (must be in us-east-1 for CloudFront)"
  type        = string
  default     = ""
}

# ============================================================================
# CloudFront Configuration
# ============================================================================

variable "cloudfront_price_class" {
  description = "CloudFront price class (PriceClass_All, PriceClass_200, PriceClass_100)"
  type        = string
  default     = "PriceClass_100"
  validation {
    condition     = contains(["PriceClass_All", "PriceClass_200", "PriceClass_100"], var.cloudfront_price_class)
    error_message = "Price class must be PriceClass_All, PriceClass_200, or PriceClass_100."
  }
}

# ============================================================================
# Monitoring and Alerting
# ============================================================================

variable "enable_enhanced_monitoring" {
  description = "Enable enhanced monitoring for RDS and ElastiCache"
  type        = bool
  default     = true
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarms"
  type        = string
  default     = ""
  validation {
    condition     = var.alarm_email == "" || can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alarm_email))
    error_message = "Must be a valid email address or empty string."
  }
}

# ============================================================================
# Tags
# ============================================================================

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# ============================================================================
# Feature Flags
# ============================================================================

variable "enable_deletion_protection" {
  description = "Enable deletion protection on critical resources"
  type        = bool
  default     = true
}

variable "enable_backup_encryption" {
  description = "Enable encryption for all backups"
  type        = bool
  default     = true
}

variable "enable_access_logs" {
  description = "Enable access logging for ALB and CloudFront"
  type        = bool
  default     = true
}
