#!/bin/bash

# ABOUTME: Development workflow for web application repositories
# ABOUTME: Orchestrates user_prompt.md → YAML config → pseudocode → TDD → deployment

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
USER_PROMPT="$REPO_ROOT/.agent-os/user_prompt.md"
USER_PROMPT_CHANGELOG="$REPO_ROOT/.agent-os/user_prompt_changelog.md"
CONFIG_DIR="$REPO_ROOT/config"
PSEUDOCODE_DIR="$REPO_ROOT/.agent-os/pseudocode"
SCRIPTS_DIR="$REPO_ROOT/scripts"
SPECS_DIR="$REPO_ROOT/.agent-os/specs"

# Parse arguments
FEATURE_NAME="$1"
AUTO_MODE=false

if [ -z "$FEATURE_NAME" ]; then
    echo "Usage: $0 <feature-name> [--auto]"
    echo ""
    echo "Example: $0 user-authentication"
    echo ""
    echo "Options:"
    echo "  --auto    Skip approval prompts (use with caution)"
    exit 1
fi

if [ "$2" = "--auto" ]; then
    AUTO_MODE=true
fi

# Utility function to wait for approval
wait_for_approval() {
    local message="$1"

    if [ "$AUTO_MODE" = true ]; then
        echo -e "${YELLOW}[AUTO MODE] $message${NC}"
        return 0
    fi

    echo ""
    echo -e "${YELLOW}$message${NC}"
    echo -e "${YELLOW}Press ENTER to continue, or Ctrl+C to abort...${NC}"
    read
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Web App Workflow: $FEATURE_NAME${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Phase 1: Read user prompt
echo -e "${BLUE}Phase 1: User Requirements${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ ! -f "$USER_PROMPT" ]; then
    echo -e "${RED}✗ $USER_PROMPT not found${NC}"
    echo ""
    echo -e "${YELLOW}Please create user_prompt.md with your requirements.${NC}"
    echo -e "${YELLOW}Location: $USER_PROMPT${NC}"
    exit 1
fi

echo -e "${GREEN}✓ User prompt found: $USER_PROMPT${NC}"
echo ""

# Create changelog if it doesn't exist
if [ ! -f "$USER_PROMPT_CHANGELOG" ]; then
    cat > "$USER_PROMPT_CHANGELOG" << 'EOF'
# User Prompt Changelog

> **Purpose:** Track all changes and updates to requirements
> **Original:** `.agent-os/user_prompt.md` (immutable)

## Changelog Entries

EOF
    echo -e "${GREEN}✓ Created changelog: $USER_PROMPT_CHANGELOG${NC}"
fi

# Phase 2: Generate YAML configuration
echo -e "${BLUE}Phase 2: YAML Configuration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

SPEC_DIR="$SPECS_DIR/$FEATURE_NAME"
CONFIG_FILE="$SPEC_DIR/config.yaml"

# Create spec directory
mkdir -p "$SPEC_DIR"

echo -e "${YELLOW}Generating YAML configuration...${NC}"
echo ""

cat > "$CONFIG_FILE" << EOF
module:
  name: $FEATURE_NAME
  version: "1.0.0"
  description: "Web application feature: $FEATURE_NAME"
  type: web_app

execution:
  memory_limit_mb: 2048
  timeout_seconds: 300
  max_retries: 2
  environment: "development"

api:
  endpoints:
    - path: "/api/$FEATURE_NAME"
      method: "GET"
      auth_required: true
      rate_limit: 100

    - path: "/api/$FEATURE_NAME"
      method: "POST"
      auth_required: true
      rate_limit: 50

    - path: "/api/$FEATURE_NAME/{id}"
      method: "PUT"
      auth_required: true
      rate_limit: 50

    - path: "/api/$FEATURE_NAME/{id}"
      method: "DELETE"
      auth_required: true
      rate_limit: 20

database:
  tables:
    - name: "${FEATURE_NAME}_table"
      columns:
        - name: id
          type: integer
          primary_key: true
          auto_increment: true

        - name: user_id
          type: integer
          foreign_key: users.id
          nullable: false

        - name: created_at
          type: timestamp
          default: "CURRENT_TIMESTAMP"

        - name: updated_at
          type: timestamp
          default: "CURRENT_TIMESTAMP"
          on_update: "CURRENT_TIMESTAMP"

      indexes:
        - columns: [user_id]
          type: btree

frontend:
  components:
    - name: "${FEATURE_NAME}Component"
      type: "react"
      props:
        - name: data
          type: array
          required: true

        - name: onSubmit
          type: function
          required: true

  routes:
    - path: "/$FEATURE_NAME"
      component: "${FEATURE_NAME}Page"
      auth_required: true

testing:
  unit_tests:
    - "test_${FEATURE_NAME}_api"
    - "test_${FEATURE_NAME}_model"
    - "test_${FEATURE_NAME}_service"

  integration_tests:
    - "test_${FEATURE_NAME}_workflow"
    - "test_${FEATURE_NAME}_api_integration"

  e2e_tests:
    - "test_${FEATURE_NAME}_user_flow"

  coverage_target: 85

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
  handlers:
    console:
      enabled: true
      level: INFO
    file:
      enabled: true
      path: "logs/${FEATURE_NAME}.log"
      level: DEBUG
      max_bytes: 10485760
      backup_count: 5

security:
  authentication: true
  authorization: true
  input_validation: true
  xss_protection: true
  csrf_protection: true
  rate_limiting: true

performance:
  cache:
    enabled: true
    ttl_seconds: 300

  optimization:
    lazy_loading: true
    code_splitting: true
    image_optimization: true

error_handling:
  strategy: fail_fast
  on_error:
    - log_error
    - rollback_transaction
    - notify_monitoring

deployment:
  strategy: "blue_green"
  health_check: "/health"
  readiness_probe: "/ready"
EOF

echo -e "${GREEN}✓ YAML configuration created: $CONFIG_FILE${NC}"
echo ""

# Validate YAML
if [ -f "$REPO_ROOT/modules/automation/validate_yaml.py" ]; then
    echo -e "${YELLOW}Validating YAML configuration...${NC}"
    if python "$REPO_ROOT/modules/automation/validate_yaml.py" "$CONFIG_FILE"; then
        echo -e "${GREEN}✓ YAML validation passed${NC}"
    else
        echo -e "${RED}✗ YAML validation failed${NC}"
        exit 1
    fi
    echo ""
fi

wait_for_approval "Review YAML configuration and approve to continue"

# Phase 3: Initialize approval tracker
echo -e "${BLUE}Phase 3: Approval Tracking${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ -f "$REPO_ROOT/modules/automation/approval_tracker.py" ]; then
    python "$REPO_ROOT/modules/automation/approval_tracker.py" \
        --spec "$FEATURE_NAME" \
        --workspace "$REPO_ROOT" \
        create

    echo ""
fi

# Phase 4: Generate pseudocode
echo -e "${BLUE}Phase 4: Pseudocode Generation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

PSEUDOCODE_FILE="$SPEC_DIR/pseudocode_v1.0.md"

echo -e "${YELLOW}Generating pseudocode from YAML configuration...${NC}"
echo ""

cat > "$PSEUDOCODE_FILE" << 'PSEUDOEOF'
# Pseudocode Specification - Web Application Feature

## Architecture Overview

```
ARCHITECTURE three_tier_web_app
  LAYER presentation:
    - React frontend components
    - Route handling
    - State management

  LAYER application:
    - API endpoints
    - Business logic
    - Authentication/Authorization

  LAYER data:
    - Database models
    - Data access layer
    - Caching layer
END ARCHITECTURE
```

## API Endpoints

### GET /api/feature

```
ENDPOINT GET "/api/feature"
  REQUIRES authentication
  RATE_LIMIT 100 requests_per_minute

  FUNCTION handle_get_request(request)
    # 1. Authenticate user
    user = AUTHENTICATE(request.headers.authorization)
    IF user IS NULL THEN
      RETURN HTTP 401 Unauthorized
    END IF

    # 2. Check authorization
    IF NOT AUTHORIZED(user, "read_feature") THEN
      RETURN HTTP 403 Forbidden
    END IF

    # 3. Get user's data
    data = DATABASE.query(
      "SELECT * FROM feature_table WHERE user_id = ?",
      user.id
    )

    # 4. Return response
    RETURN HTTP 200 {
      "data": data,
      "count": data.length
    }
  END FUNCTION
END ENDPOINT
```

### POST /api/feature

```
ENDPOINT POST "/api/feature"
  REQUIRES authentication
  RATE_LIMIT 50 requests_per_minute

  FUNCTION handle_post_request(request)
    # 1. Authenticate
    user = AUTHENTICATE(request.headers.authorization)
    IF user IS NULL THEN
      RETURN HTTP 401 Unauthorized
    END IF

    # 2. Validate input
    input_data = request.body
    validation_result = VALIDATE_INPUT(input_data)

    IF validation_result.has_errors THEN
      RETURN HTTP 400 {
        "errors": validation_result.errors
      }
    END IF

    # 3. Sanitize input (XSS protection)
    sanitized_data = SANITIZE_FOR_XSS(input_data)

    # 4. Begin transaction
    BEGIN_TRANSACTION

    TRY
      # 5. Create database record
      new_record = DATABASE.insert(
        "feature_table",
        {
          user_id: user.id,
          data: sanitized_data,
          created_at: NOW(),
          updated_at: NOW()
        }
      )

      # 6. Invalidate cache
      CACHE.invalidate("user_" + user.id + "_features")

      # 7. Commit transaction
      COMMIT_TRANSACTION

      # 8. Log success
      LOG INFO "Created feature record {new_record.id} for user {user.id}"

      # 9. Return response
      RETURN HTTP 201 {
        "id": new_record.id,
        "data": new_record
      }

    CATCH error
      # Rollback on error
      ROLLBACK_TRANSACTION
      LOG ERROR "Failed to create feature: {error}"

      # Notify monitoring
      NOTIFY_MONITORING("feature_creation_failed", {
        user_id: user.id,
        error: error.message
      })

      RETURN HTTP 500 {
        "error": "Internal server error"
      }
    END TRY
  END FUNCTION
END ENDPOINT
```

## Frontend Components

### React Component

```
COMPONENT FeatureComponent
  PROPS:
    - data: Array<FeatureData>
    - onSubmit: Function
    - loading: Boolean

  STATE:
    - formData: Object
    - errors: Object
    - submitting: Boolean

  FUNCTION handleInputChange(event)
    field = event.target.name
    value = event.target.value

    # Update form data
    SET_STATE formData[field] = value

    # Clear field error if exists
    IF errors[field] EXISTS THEN
      SET_STATE errors[field] = NULL
    END IF
  END FUNCTION

  FUNCTION validateForm()
    validation_errors = {}

    # Validate required fields
    IF formData.name IS EMPTY THEN
      validation_errors.name = "Name is required"
    END IF

    # Validate field formats
    IF formData.email AND NOT IS_VALID_EMAIL(formData.email) THEN
      validation_errors.email = "Invalid email format"
    END IF

    RETURN validation_errors
  END FUNCTION

  ASYNC FUNCTION handleSubmit(event)
    PREVENT_DEFAULT(event)

    # Validate
    validation_errors = validateForm()

    IF validation_errors IS NOT EMPTY THEN
      SET_STATE errors = validation_errors
      RETURN
    END IF

    # Submit
    SET_STATE submitting = TRUE

    TRY
      result = AWAIT onSubmit(formData)
      SET_STATE formData = {}  # Clear form
      SHOW_SUCCESS_MESSAGE("Feature created successfully")

    CATCH error
      LOG ERROR "Submission failed: {error}"
      SHOW_ERROR_MESSAGE("Failed to create feature")

    FINALLY
      SET_STATE submitting = FALSE
    END TRY
  END FUNCTION

  RENDER
    <form onSubmit={handleSubmit}>
      <input
        name="name"
        value={formData.name}
        onChange={handleInputChange}
        disabled={submitting}
      />
      {errors.name && <span class="error">{errors.name}</span>}

      <button type="submit" disabled={submitting}>
        {submitting ? "Submitting..." : "Submit"}
      </button>
    </form>

    <div class="data-list">
      {loading ? (
        <LoadingSpinner />
      ) : (
        data.map(item => <FeatureItem key={item.id} data={item} />)
      )}
    </div>
  END RENDER
END COMPONENT
```

## Database Operations

```
FUNCTION create_feature_record(user_id, data)
  # Prepare SQL
  sql = "INSERT INTO feature_table (user_id, data, created_at, updated_at) VALUES (?, ?, ?, ?)"
  params = [user_id, data, NOW(), NOW()]

  # Execute
  result = DATABASE.execute(sql, params)

  # Return inserted record
  RETURN DATABASE.get_by_id("feature_table", result.last_insert_id)
END FUNCTION

FUNCTION update_feature_record(id, data)
  # Check record exists
  record = DATABASE.get_by_id("feature_table", id)
  IF record IS NULL THEN
    RAISE RecordNotFoundError
  END IF

  # Update
  sql = "UPDATE feature_table SET data = ?, updated_at = ? WHERE id = ?"
  params = [data, NOW(), id]

  DATABASE.execute(sql, params)

  # Return updated record
  RETURN DATABASE.get_by_id("feature_table", id)
END FUNCTION

FUNCTION delete_feature_record(id, user_id)
  # Verify ownership
  record = DATABASE.get_by_id("feature_table", id)
  IF record IS NULL THEN
    RAISE RecordNotFoundError
  END IF

  IF record.user_id != user_id THEN
    RAISE UnauthorizedError
  END IF

  # Delete
  sql = "DELETE FROM feature_table WHERE id = ? AND user_id = ?"
  params = [id, user_id]

  DATABASE.execute(sql, params)
END FUNCTION
```

## Security Functions

```
FUNCTION validate_and_sanitize_input(data)
  # XSS protection
  FOR EACH field IN data
    data[field] = ESCAPE_HTML(data[field])
    data[field] = STRIP_SCRIPT_TAGS(data[field])
  END FOR

  # SQL injection protection (use parameterized queries)
  # Handled by database layer

  # Length limits
  FOR EACH field IN data
    IF LENGTH(data[field]) > MAX_FIELD_LENGTH THEN
      RAISE ValidationError("Field too long: {field}")
    END IF
  END FOR

  RETURN data
END FUNCTION

FUNCTION check_rate_limit(user_id, endpoint)
  key = "rate_limit_" + user_id + "_" + endpoint
  count = CACHE.get(key) OR 0

  IF count >= RATE_LIMIT_THRESHOLD THEN
    RAISE RateLimitExceededError
  END IF

  CACHE.increment(key)
  CACHE.expire(key, 60)  # 60 seconds window
END FUNCTION
```

## Testing Requirements

```
TESTS REQUIRED:
  API Tests:
    - test_get_feature_authenticated()
    - test_get_feature_unauthenticated()
    - test_get_feature_unauthorized()
    - test_post_feature_valid_data()
    - test_post_feature_invalid_data()
    - test_post_feature_xss_attack()
    - test_update_feature()
    - test_delete_feature()
    - test_rate_limiting()

  Component Tests:
    - test_component_renders()
    - test_form_validation()
    - test_form_submission()
    - test_error_display()
    - test_loading_state()

  Integration Tests:
    - test_end_to_end_create_workflow()
    - test_authentication_flow()
    - test_database_transactions()

  Performance Tests:
    - test_api_response_time()  # < 200ms
    - test_concurrent_requests()
    - test_cache_effectiveness()

  Security Tests:
    - test_xss_prevention()
    - test_csrf_protection()
    - test_sql_injection_prevention()
    - test_authentication_bypass_attempts()

  Target Coverage: 85%+
END TESTS
```
PSEUDOEOF

echo -e "${GREEN}✓ Pseudocode generated: $PSEUDOCODE_FILE${NC}"
echo ""

wait_for_approval "Review pseudocode and approve to continue"

# Submit for approval
if [ -f "$REPO_ROOT/modules/automation/approval_tracker.py" ]; then
    echo -e "${YELLOW}Recording approval...${NC}"
    python "$REPO_ROOT/modules/automation/approval_tracker.py" \
        --spec "$FEATURE_NAME" \
        --workspace "$REPO_ROOT" \
        submit \
        --phase pseudocode \
        --version "1.0" \
        --approver "$USER" \
        --status APPROVED \
        --changes "Initial pseudocode specification" \
        --comments "Pseudocode includes API endpoints, React components, database operations, and security measures"
    echo ""
fi

# Phase 5: TDD Implementation Guidance
echo -e "${BLUE}Phase 5: TDD Implementation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}Implementation Instructions:${NC}"
echo ""
echo -e "${BLUE}1. Create test directory structure:${NC}"
echo -e "   ${YELLOW}mkdir -p tests/{api,components,integration,e2e}${NC}"
echo ""
echo -e "${BLUE}2. Create backend structure:${NC}"
echo -e "   ${YELLOW}mkdir -p server/{routes,models,controllers,middleware}${NC}"
echo ""
echo -e "${BLUE}3. Create frontend structure:${NC}"
echo -e "   ${YELLOW}mkdir -p client/src/{components,pages,services,utils}${NC}"
echo ""
echo -e "${BLUE}4. Write API tests FIRST:${NC}"
echo -e "   ${YELLOW}vim tests/api/test_${FEATURE_NAME}_api.test.js${NC}"
echo ""
echo -e "${BLUE}5. Write component tests:${NC}"
echo -e "   ${YELLOW}vim tests/components/${FEATURE_NAME}Component.test.jsx${NC}"
echo ""
echo -e "${BLUE}6. Run tests (should fail):${NC}"
echo -e "   ${YELLOW}npm test${NC}"
echo ""
echo -e "${BLUE}7. Implement backend API:${NC}"
echo -e "   ${YELLOW}vim server/routes/${FEATURE_NAME}.js${NC}"
echo -e "   ${YELLOW}vim server/models/${FEATURE_NAME}.js${NC}"
echo ""
echo -e "${BLUE}8. Implement frontend components:${NC}"
echo -e "   ${YELLOW}vim client/src/components/${FEATURE_NAME}Component.jsx${NC}"
echo ""
echo -e "${BLUE}9. Run tests (should pass):${NC}"
echo -e "   ${YELLOW}npm test -- --coverage${NC}"
echo ""
echo -e "${BLUE}10. Verify 85%+ coverage:${NC}"
echo -e "   ${YELLOW}npm test -- --coverage --coverageThreshold=85${NC}"
echo ""

wait_for_approval "Press ENTER when implementation is complete..."

# Phase 6: Create execution/deployment scripts
echo -e "${BLUE}Phase 6: Deployment Scripts${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Development server script
DEV_SCRIPT="$SCRIPTS_DIR/dev_${FEATURE_NAME}.sh"
cat > "$DEV_SCRIPT" << 'DEVEOF'
#!/bin/bash

# ABOUTME: Development server for feature testing
# ABOUTME: Runs frontend and backend in development mode

set -e

echo "Starting development servers..."

# Start backend
cd server && npm run dev &
BACKEND_PID=$!

# Start frontend
cd client && npm start &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Development servers running:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID" INT
wait
DEVEOF

chmod +x "$DEV_SCRIPT"
echo -e "${GREEN}✓ Development script created: $DEV_SCRIPT${NC}"

# Production build script
BUILD_SCRIPT="$SCRIPTS_DIR/build_${FEATURE_NAME}.sh"
cat > "$BUILD_SCRIPT" << 'BUILDEOF'
#!/bin/bash

# ABOUTME: Production build script
# ABOUTME: Builds optimized frontend and backend

set -e

echo "Building for production..."

# Build frontend
echo "Building frontend..."
cd client && npm run build
cd ..

# Build backend (if using TypeScript)
if [ -f "server/tsconfig.json" ]; then
    echo "Building backend..."
    cd server && npm run build
    cd ..
fi

echo ""
echo "Build completed successfully!"
echo "  Frontend: client/build/"
echo "  Backend: server/dist/"
BUILDEOF

chmod +x "$BUILD_SCRIPT"
echo -e "${GREEN}✓ Build script created: $BUILD_SCRIPT${NC}"
echo ""

# Final summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Workflow Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${GREEN}✓ All phases completed successfully${NC}"
echo ""

echo -e "${BLUE}Created Files:${NC}"
echo -e "  • User Prompt: ${YELLOW}$USER_PROMPT${NC}"
echo -e "  • Changelog: ${YELLOW}$USER_PROMPT_CHANGELOG${NC}"
echo -e "  • YAML Config: ${YELLOW}$CONFIG_FILE${NC}"
echo -e "  • Pseudocode: ${YELLOW}$PSEUDOCODE_FILE${NC}"
echo -e "  • Dev Script: ${YELLOW}$DEV_SCRIPT${NC}"
echo -e "  • Build Script: ${YELLOW}$BUILD_SCRIPT${NC}"
if [ -f "$SPEC_DIR/approval_log.md" ]; then
    echo -e "  • Approval Log: ${YELLOW}$SPEC_DIR/approval_log.md${NC}"
fi
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Verify tests: ${YELLOW}npm test -- --coverage${NC}"
echo -e "  2. Start development: ${YELLOW}$DEV_SCRIPT${NC}"
echo -e "  3. Build for production: ${YELLOW}$BUILD_SCRIPT${NC}"
echo ""

echo -e "${GREEN}Web app workflow completed! 🚀${NC}"
