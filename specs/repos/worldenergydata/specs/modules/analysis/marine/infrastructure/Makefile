# Marine Safety Incidents Database - Makefile
# Purpose: Simplify common development and deployment tasks
# Usage: make [target]

.PHONY: help build test deploy clean

# Default shell
SHELL := /bin/bash

# Environment variables
ENV ?= development
AWS_REGION ?= us-east-1
ECR_REGISTRY ?= $(shell aws sts get-caller-identity --query Account --output text).dkr.ecr.$(AWS_REGION).amazonaws.com
IMAGE_NAME ?= marine-safety-api
IMAGE_TAG ?= latest

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ Help

help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(BLUE)Usage:$(NC)\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

dev-up: ## Start local development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Development environment started$(NC)"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "pgAdmin: http://localhost:5050"

dev-down: ## Stop local development environment
	@echo "$(BLUE)Stopping development environment...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Development environment stopped$(NC)"

dev-restart: dev-down dev-up ## Restart local development environment

dev-logs: ## View development logs
	docker-compose logs -f api

dev-shell: ## Open shell in API container
	docker-compose exec api /bin/bash

dev-db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d marine_safety

dev-redis-shell: ## Open Redis CLI
	docker-compose exec redis redis-cli -a redis_dev_password_change_in_production

dev-clean: ## Clean development environment (removes volumes)
	@echo "$(RED)⚠️  This will delete all local data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "$(GREEN)✓ Development environment cleaned$(NC)"; \
	fi

##@ Testing

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	docker-compose exec api pytest tests/ -v
	@echo "$(GREEN)✓ Tests completed$(NC)"

test-unit: ## Run unit tests only
	docker-compose exec api pytest tests/unit/ -v

test-integration: ## Run integration tests only
	docker-compose exec api pytest tests/integration/ -v

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	docker-compose exec api pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

test-watch: ## Run tests in watch mode
	docker-compose exec api pytest-watch tests/

lint: ## Run code linting
	@echo "$(BLUE)Running linters...$(NC)"
	docker-compose exec api black --check app/ tests/
	docker-compose exec api flake8 app/ tests/
	docker-compose exec api mypy app/
	@echo "$(GREEN)✓ Linting completed$(NC)"

format: ## Format code with Black
	@echo "$(BLUE)Formatting code...$(NC)"
	docker-compose exec api black app/ tests/
	docker-compose exec api isort app/ tests/
	@echo "$(GREEN)✓ Code formatted$(NC)"

##@ Database

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	docker-compose exec api alembic upgrade head
	@echo "$(GREEN)✓ Migrations completed$(NC)"

db-migrate-create: ## Create new migration
	@read -p "Migration description: " desc; \
	docker-compose exec api alembic revision --autogenerate -m "$$desc"

db-rollback: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	docker-compose exec api alembic downgrade -1
	@echo "$(GREEN)✓ Rollback completed$(NC)"

db-reset: ## Reset database (drop and recreate)
	@echo "$(RED)⚠️  This will delete all database data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS marine_safety;"; \
		docker-compose exec postgres psql -U postgres -c "CREATE DATABASE marine_safety;"; \
		docker-compose exec api alembic upgrade head; \
		echo "$(GREEN)✓ Database reset$(NC)"; \
	fi

db-backup: ## Create database backup
	@echo "$(BLUE)Creating database backup...$(NC)"
	@mkdir -p backups
	docker-compose exec -T postgres pg_dump -U postgres marine_safety > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup created$(NC)"

db-restore: ## Restore database from backup
	@echo "$(BLUE)Available backups:$(NC)"
	@ls -1 backups/*.sql 2>/dev/null || echo "No backups found"
	@read -p "Enter backup filename: " backup; \
	if [ -f "backups/$$backup" ]; then \
		docker-compose exec -T postgres psql -U postgres marine_safety < "backups/$$backup"; \
		echo "$(GREEN)✓ Database restored$(NC)"; \
	else \
		echo "$(RED)✗ Backup file not found$(NC)"; \
	fi

##@ Docker

build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "$(GREEN)✓ Image built: $(IMAGE_NAME):$(IMAGE_TAG)$(NC)"

build-dev: ## Build development Docker image
	@echo "$(BLUE)Building development Docker image...$(NC)"
	docker build --target development -t $(IMAGE_NAME):dev .
	@echo "$(GREEN)✓ Development image built$(NC)"

push: ## Push Docker image to ECR
	@echo "$(BLUE)Pushing to ECR...$(NC)"
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REGISTRY)
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(ECR_REGISTRY)/$(IMAGE_NAME)-$(ENV):$(IMAGE_TAG)
	docker push $(ECR_REGISTRY)/$(IMAGE_NAME)-$(ENV):$(IMAGE_TAG)
	@echo "$(GREEN)✓ Image pushed to ECR$(NC)"

scan: ## Scan Docker image for vulnerabilities
	@echo "$(BLUE)Scanning image for vulnerabilities...$(NC)"
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy image $(IMAGE_NAME):$(IMAGE_TAG)

##@ Terraform

tf-init: ## Initialize Terraform
	@echo "$(BLUE)Initializing Terraform...$(NC)"
	cd terraform && terraform init
	@echo "$(GREEN)✓ Terraform initialized$(NC)"

tf-plan: ## Run Terraform plan
	@echo "$(BLUE)Running Terraform plan...$(NC)"
	cd terraform && terraform plan -var-file=terraform.tfvars -out=tfplan
	@echo "$(GREEN)✓ Plan saved to terraform/tfplan$(NC)"

tf-apply: ## Apply Terraform changes
	@echo "$(YELLOW)Applying Terraform changes...$(NC)"
	@read -p "Environment (development/staging/production): " env; \
	cd terraform && terraform apply -var="environment=$$env" -auto-approve
	@echo "$(GREEN)✓ Infrastructure deployed$(NC)"

tf-destroy: ## Destroy Terraform infrastructure
	@echo "$(RED)⚠️  This will destroy all infrastructure!$(NC)"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		cd terraform && terraform destroy -auto-approve; \
		echo "$(GREEN)✓ Infrastructure destroyed$(NC)"; \
	fi

tf-output: ## Show Terraform outputs
	cd terraform && terraform output

tf-validate: ## Validate Terraform configuration
	@echo "$(BLUE)Validating Terraform...$(NC)"
	cd terraform && terraform validate
	@echo "$(GREEN)✓ Terraform configuration valid$(NC)"

tf-fmt: ## Format Terraform files
	cd terraform && terraform fmt -recursive

##@ Deployment

deploy: build push ## Build, push, and deploy to ECS
	@echo "$(BLUE)Deploying to ECS...$(NC)"
	aws ecs update-service \
		--cluster marine-safety-cluster-$(ENV) \
		--service marine-safety-api-$(ENV) \
		--force-new-deployment \
		--region $(AWS_REGION)
	@echo "$(GREEN)✓ Deployment initiated$(NC)"
	@echo "Monitor deployment: aws ecs wait services-stable --cluster marine-safety-cluster-$(ENV) --services marine-safety-api-$(ENV)"

deploy-wait: deploy ## Deploy and wait for service stability
	@echo "$(BLUE)Waiting for deployment to stabilize...$(NC)"
	aws ecs wait services-stable \
		--cluster marine-safety-cluster-$(ENV) \
		--services marine-safety-api-$(ENV) \
		--region $(AWS_REGION)
	@echo "$(GREEN)✓ Deployment completed successfully$(NC)"

rollback: ## Rollback ECS service to previous version
	@echo "$(YELLOW)Rolling back deployment...$(NC)"
	@PREV_TASK=$$(aws ecs list-task-definitions \
		--family-prefix marine-safety-api-$(ENV) \
		--sort DESC \
		--max-items 2 \
		--query 'taskDefinitionArns[1]' \
		--output text); \
	aws ecs update-service \
		--cluster marine-safety-cluster-$(ENV) \
		--service marine-safety-api-$(ENV) \
		--task-definition $$PREV_TASK \
		--force-new-deployment \
		--region $(AWS_REGION)
	@echo "$(GREEN)✓ Rollback initiated$(NC)"

invalidate-cdn: ## Invalidate CloudFront cache
	@echo "$(BLUE)Invalidating CloudFront cache...$(NC)"
	@DISTRIBUTION_ID=$$(aws cloudfront list-distributions \
		--query "DistributionList.Items[?Comment=='Marine Safety Incidents CDN'].Id" \
		--output text); \
	aws cloudfront create-invalidation \
		--distribution-id $$DISTRIBUTION_ID \
		--paths "/*"
	@echo "$(GREEN)✓ Cache invalidation initiated$(NC)"

##@ Monitoring

logs: ## View ECS logs
	@echo "$(BLUE)Fetching ECS logs...$(NC)"
	aws logs tail /ecs/marine-safety-$(ENV) --follow --region $(AWS_REGION)

logs-errors: ## View error logs only
	aws logs tail /ecs/marine-safety-$(ENV) --follow --filter-pattern "ERROR" --region $(AWS_REGION)

status: ## Check service status
	@echo "$(BLUE)Checking service status...$(NC)"
	@aws ecs describe-services \
		--cluster marine-safety-cluster-$(ENV) \
		--services marine-safety-api-$(ENV) \
		--query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}' \
		--output table

metrics: ## Show CloudWatch metrics
	@echo "$(BLUE)Fetching metrics (last 1 hour)...$(NC)"
	@aws cloudwatch get-metric-statistics \
		--namespace AWS/ECS \
		--metric-name CPUUtilization \
		--dimensions Name=ServiceName,Value=marine-safety-api-$(ENV) \
		--start-time $$(date -u -d '1 hour ago' --iso-8601=seconds) \
		--end-time $$(date -u --iso-8601=seconds) \
		--period 300 \
		--statistics Average \
		--query 'Datapoints[*].{Time:Timestamp,CPU:Average}' \
		--output table

##@ Utilities

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage coverage.xml
	@echo "$(GREEN)✓ Cleaned$(NC)"

install: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

version: ## Show version information
	@echo "$(BLUE)Version Information:$(NC)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"
	@echo "AWS CLI: $$(aws --version)"
	@echo "Terraform: $$(cd terraform && terraform version | head -n 1)"
	@echo "Python: $$(python --version)"

check-deps: ## Check required dependencies
	@echo "$(BLUE)Checking dependencies...$(NC)"
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)✗ Docker not installed$(NC)"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "$(RED)✗ Docker Compose not installed$(NC)"; exit 1; }
	@command -v aws >/dev/null 2>&1 || { echo "$(RED)✗ AWS CLI not installed$(NC)"; exit 1; }
	@command -v terraform >/dev/null 2>&1 || { echo "$(RED)✗ Terraform not installed$(NC)"; exit 1; }
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

setup: check-deps install ## Initial setup
	@echo "$(BLUE)Setting up project...$(NC)"
	@mkdir -p backups logs data
	@if [ ! -f terraform/terraform.tfvars ]; then \
		cp terraform/terraform.tfvars.example terraform/terraform.tfvars; \
		echo "$(YELLOW)⚠️  Edit terraform/terraform.tfvars with your values$(NC)"; \
	fi
	@if [ ! -f .env ]; then \
		echo "Creating .env file..."; \
		touch .env; \
		echo "$(YELLOW)⚠️  Configure .env with your environment variables$(NC)"; \
	fi
	@echo "$(GREEN)✓ Setup complete$(NC)"

.DEFAULT_GOAL := help
