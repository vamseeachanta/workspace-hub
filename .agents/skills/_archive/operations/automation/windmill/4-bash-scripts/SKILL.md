---
name: windmill-4-bash-scripts
description: 'Sub-skill of windmill: 4. Bash Scripts.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 4. Bash Scripts

## 4. Bash Scripts


```bash
#!/bin/bash
# scripts/devops/deploy_service.sh
# Deploy a service with health checks and rollback capability.

# Windmill automatically provides these as environment variables
# SERVICE_NAME, VERSION, ENVIRONMENT, DRY_RUN

set -euo pipefail

# Get secrets from Windmill resources
DEPLOY_KEY=$(curl -s -H "Authorization: Bearer $WM_TOKEN" \
  "$BASE_INTERNAL_URL/api/w/$WM_WORKSPACE/resources/get/u/admin/deploy_key" | jq -r '.value.key')

AWS_REGION=$(curl -s -H "Authorization: Bearer $WM_TOKEN" \
  "$BASE_INTERNAL_URL/api/w/$WM_WORKSPACE/resources/get/u/admin/aws_config" | jq -r '.value.region')

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

deploy_service() {
  local service=$1
  local version=$2
  local env=$3

  log "Deploying $service version $version to $env"

  # Update ECS service
  if [[ "$DRY_RUN" == "true" ]]; then
    log "[DRY RUN] Would update ECS service $service to $version"
    return 0
  fi

  aws ecs update-service \
    --cluster "${env}-cluster" \
    --service "$service" \
    --force-new-deployment \
    --region "$AWS_REGION"

  log "Deployment initiated"
}

wait_for_healthy() {
  local service=$1
  local env=$2
  local max_wait=300
  local interval=10
  local elapsed=0

  log "Waiting for $service to become healthy..."

  while [[ $elapsed -lt $max_wait ]]; do
    local running_count=$(aws ecs describe-services \
      --cluster "${env}-cluster" \
      --services "$service" \
      --region "$AWS_REGION" \
      --query 'services[0].runningCount' \
      --output text)

    local desired_count=$(aws ecs describe-services \
      --cluster "${env}-cluster" \
      --services "$service" \
      --region "$AWS_REGION" \
      --query 'services[0].desiredCount' \
      --output text)

    if [[ "$running_count" == "$desired_count" ]]; then
      log "Service healthy: $running_count/$desired_count tasks running"
      return 0
    fi

    log "Waiting... ($running_count/$desired_count tasks running)"
    sleep $interval
    elapsed=$((elapsed + interval))
  done

  log "ERROR: Service did not become healthy within ${max_wait}s"
  return 1
}

rollback() {
  local service=$1
  local env=$2

  log "Rolling back $service in $env"

  # Get previous task definition
  local prev_task_def=$(aws ecs describe-services \
    --cluster "${env}-cluster" \
    --services "$service" \
    --region "$AWS_REGION" \
    --query 'services[0].deployments[1].taskDefinition' \
    --output text)

  if [[ -z "$prev_task_def" || "$prev_task_def" == "None" ]]; then
    log "ERROR: No previous task definition found for rollback"
    return 1
  fi

  aws ecs update-service \
    --cluster "${env}-cluster" \
    --service "$service" \
    --task-definition "$prev_task_def" \
    --region "$AWS_REGION"

  log "Rollback initiated to $prev_task_def"
}

# Main execution
main() {
  log "=== Deployment Started ==="
  log "Service: $SERVICE_NAME"
  log "Version: $VERSION"
  log "Environment: $ENVIRONMENT"
  log "Dry Run: $DRY_RUN"

  # Deploy
  if ! deploy_service "$SERVICE_NAME" "$VERSION" "$ENVIRONMENT"; then
    log "ERROR: Deployment failed"
    exit 1
  fi

  # Wait for health (skip in dry run)
  if [[ "$DRY_RUN" != "true" ]]; then
    if ! wait_for_healthy "$SERVICE_NAME" "$ENVIRONMENT"; then
      log "Deployment failed health check, initiating rollback"
      rollback "$SERVICE_NAME" "$ENVIRONMENT"
      exit 1
    fi
  fi

  log "=== Deployment Completed Successfully ==="

  # Output result as JSON for Windmill
  cat <<EOF
{
  "status": "success",
  "service": "$SERVICE_NAME",
  "version": "$VERSION",
  "environment": "$ENVIRONMENT",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
}

main
```
