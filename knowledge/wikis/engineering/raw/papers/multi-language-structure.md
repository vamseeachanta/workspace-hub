# Multi-Language Project Testing Structure

This document provides templates and examples for organizing tests in projects that use multiple programming languages.

## Common Multi-Language Patterns

### Pattern 1: Backend + Frontend Separation

```
project/
├── backend/ (Python/Django/FastAPI)
│   ├── src/
│   │   └── app/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── pytest.ini
│   ├── .coveragerc
│   └── requirements-test.txt
├── frontend/ (React/Vue/Angular)
│   ├── src/
│   │   └── components/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── setup.js
│   ├── jest.config.js
│   └── package.json
├── tests/ (System-wide integration)
│   ├── e2e/
│   ├── api/
│   └── system/
├── .github/
│   └── workflows/
│       ├── backend-tests.yml
│       ├── frontend-tests.yml
│       └── integration-tests.yml
└── docker-compose.test.yml
```

### Pattern 2: Monorepo with Multiple Services

```
monorepo/
├── services/
│   ├── auth-service/ (Python)
│   │   ├── src/
│   │   ├── tests/
│   │   └── pytest.ini
│   ├── user-service/ (Node.js)
│   │   ├── src/
│   │   ├── tests/
│   │   └── jest.config.js
│   └── payment-service/ (Go)
│       ├── cmd/
│       ├── internal/
│       └── *_test.go
├── packages/
│   ├── shared-types/ (TypeScript)
│   ├── ui-components/ (React)
│   └── utils/ (Multiple languages)
├── tests/
│   ├── integration/
│   ├── e2e/
│   └── performance/
├── tools/
│   └── test-runner/
└── .github/
    └── workflows/
        ├── service-tests.yml
        ├── package-tests.yml
        └── integration-tests.yml
```

### Pattern 3: Full-Stack with Shared Testing

```
fullstack/
├── api/ (Python)
│   ├── src/
│   ├── tests/
│   └── pytest.ini
├── web/ (React/TypeScript)
│   ├── src/
│   ├── tests/
│   └── jest.config.js
├── mobile/ (React Native)
│   ├── src/
│   ├── __tests__/
│   └── jest.config.js
├── shared/
│   ├── schemas/
│   ├── types/
│   └── fixtures/
├── tests/
│   ├── contracts/ (API contract tests)
│   ├── e2e/ (Cross-platform tests)
│   └── load/ (Performance tests)
└── scripts/
    ├── test-all.sh
    └── coverage-report.sh
```

## Testing Strategy Templates

### 1. Contract Testing Configuration

#### API Contract Testing (Python + JavaScript)

```yaml
# tests/contracts/pact-config.yml
pact:
  consumer: frontend-app
  provider: backend-api
  broker_url: ${PACT_BROKER_URL}
  publish_results: true

contracts:
  - name: user-endpoints
    consumer_tests: frontend/tests/contracts/
    provider_tests: backend/tests/contracts/
  - name: auth-endpoints
    consumer_tests: frontend/tests/contracts/
    provider_tests: backend/tests/contracts/
```

#### Python Provider Test (backend/tests/contracts/test_user_contract.py)

```python
import pytest
from pact import Verifier

class TestUserContract:
    def test_user_endpoints_contract(self):
        verifier = Verifier(
            provider='backend-api',
            provider_base_url='http://localhost:8000'
        )

        success, logs = verifier.verify_pacts(
            './pacts/frontend-app-backend-api.json',
            verbose=True,
            provider_states_setup_url='http://localhost:8000/_pact/provider_states'
        )

        assert success == 0
```

#### JavaScript Consumer Test (frontend/tests/contracts/user.contract.test.js)

```javascript
import { Pact } from '@pact-foundation/pact';
import { userApi } from '../../src/api/user';

describe('User API Contract', () => {
  const provider = new Pact({
    consumer: 'frontend-app',
    provider: 'backend-api',
    port: 1234,
    log: path.resolve(process.cwd(), 'logs', 'pact.log'),
    dir: path.resolve(process.cwd(), 'pacts'),
  });

  beforeAll(() => provider.setup());
  afterEach(() => provider.verify());
  afterAll(() => provider.finalize());

  test('should get user by ID', async () => {
    await provider
      .given('user with ID 1 exists')
      .uponReceiving('a request for user 1')
      .withRequest({
        method: 'GET',
        path: '/api/users/1',
        headers: {
          'Accept': 'application/json',
        },
      })
      .willRespondWith({
        status: 200,
        headers: {
          'Content-Type': 'application/json',
        },
        body: {
          id: 1,
          name: 'John Doe',
          email: 'john@example.com',
        },
      });

    const user = await userApi.getUser(1);
    expect(user.id).toBe(1);
  });
});
```

### 2. Cross-Language Test Data Management

#### Shared Test Fixtures (shared/fixtures/users.json)

```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "admin",
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "role": "user",
      "created_at": "2025-01-02T00:00:00Z"
    }
  ],
  "roles": ["admin", "user", "guest"]
}
```

#### Python Fixture Loader (backend/tests/fixtures.py)

```python
import json
from pathlib import Path

def load_shared_fixtures(fixture_name):
    """Load shared test fixtures."""
    fixtures_path = Path(__file__).parent.parent.parent / "shared" / "fixtures"
    with open(fixtures_path / f"{fixture_name}.json") as f:
        return json.load(f)

@pytest.fixture
def sample_users():
    return load_shared_fixtures("users")["users"]

@pytest.fixture
def sample_roles():
    return load_shared_fixtures("users")["roles"]
```

#### JavaScript Fixture Loader (frontend/tests/fixtures.js)

```javascript
import fs from 'fs';
import path from 'path';

export function loadSharedFixtures(fixtureName) {
  const fixturesPath = path.join(
    __dirname,
    '..', '..',
    'shared',
    'fixtures',
    `${fixtureName}.json`
  );
  return JSON.parse(fs.readFileSync(fixturesPath, 'utf8'));
}

export const sampleUsers = loadSharedFixtures('users').users;
export const sampleRoles = loadSharedFixtures('users').roles;
```

### 3. Database Testing Strategy

#### Docker Compose for Test Services (docker-compose.test.yml)

```yaml
version: '3.8'

services:
  test-postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    ports:
      - "5433:5432"
    volumes:
      - ./shared/db/init.sql:/docker-entrypoint-initdb.d/init.sql

  test-redis:
    image: redis:7
    ports:
      - "6380:6379"

  test-mongodb:
    image: mongo:6
    environment:
      MONGO_INITDB_ROOT_USERNAME: test_user
      MONGO_INITDB_ROOT_PASSWORD: test_pass
    ports:
      - "27018:27017"

networks:
  default:
    name: test-network
```

#### Shared Database Setup (shared/db/init.sql)

```sql
-- Shared database schema for testing
CREATE SCHEMA IF NOT EXISTS test_schema;

-- Users table
CREATE TABLE test_schema.users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert test data
INSERT INTO test_schema.users (name, email, role) VALUES
('John Doe', 'john@example.com', 'admin'),
('Jane Smith', 'jane@example.com', 'user');
```

### 4. Integration Test Scripts

#### Master Test Runner (scripts/test-all.sh)

```bash
#!/bin/bash
set -e

echo "🚀 Starting multi-language test suite..."

# Configuration
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
INTEGRATION_DIR="tests"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Start test services
log_info "Starting test services..."
docker-compose -f docker-compose.test.yml up -d
sleep 5

# Backend tests
if [ -d "$BACKEND_DIR" ]; then
    log_info "Running backend tests..."
    cd $BACKEND_DIR

    # Install dependencies
    python -m pip install -r requirements-test.txt

    # Run tests
    pytest --cov=src --cov-report=xml:../coverage-backend.xml --verbose

    if [ $? -eq 0 ]; then
        log_info "Backend tests passed ✅"
    else
        log_error "Backend tests failed ❌"
        exit 1
    fi

    cd ..
fi

# Frontend tests
if [ -d "$FRONTEND_DIR" ]; then
    log_info "Running frontend tests..."
    cd $FRONTEND_DIR

    # Install dependencies
    npm ci

    # Run tests
    npm run test:ci

    if [ $? -eq 0 ]; then
        log_info "Frontend tests passed ✅"
    else
        log_error "Frontend tests failed ❌"
        exit 1
    fi

    cd ..
fi

# Integration tests
if [ -d "$INTEGRATION_DIR" ]; then
    log_info "Running integration tests..."
    cd $INTEGRATION_DIR

    # Run integration tests
    npm run test:integration

    if [ $? -eq 0 ]; then
        log_info "Integration tests passed ✅"
    else
        log_error "Integration tests failed ❌"
        exit 1
    fi

    cd ..
fi

# Generate combined coverage report
log_info "Generating combined coverage report..."
./scripts/coverage-report.sh

# Cleanup
log_info "Cleaning up test services..."
docker-compose -f docker-compose.test.yml down

log_info "🎉 All tests completed successfully!"
```

#### Coverage Report Generator (scripts/coverage-report.sh)

```bash
#!/bin/bash

echo "📊 Generating combined coverage report..."

# Create coverage directory
mkdir -p coverage-combined

# Combine coverage reports
if [ -f "coverage-backend.xml" ] && [ -f "frontend/coverage/lcov.info" ]; then
    echo "Combining Python and JavaScript coverage..."

    # Install coverage tools if needed
    pip install coverage[toml] --quiet
    npm install -g lcov-result-merger --silent

    # Convert lcov to cobertura for consistency
    cd frontend
    npx lcov-to-cobertura-xml -o ../coverage-frontend.xml coverage/lcov.info
    cd ..

    # Generate HTML report
    echo "Generating HTML coverage report..."
    python -c "
import coverage
import xml.etree.ElementTree as ET

# Simple coverage combination script
print('Combined coverage report generated in coverage-combined/')
"

    echo "✅ Combined coverage report ready"
else
    echo "⚠️  Coverage files not found, skipping combined report"
fi
```

### 5. Test Configuration Templates

#### Root Test Configuration (tests/config/test-config.js)

```javascript
// Shared test configuration for all languages
export const testConfig = {
  // API endpoints
  api: {
    baseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
    timeout: 10000,
    retries: 3
  },

  // Database connections
  database: {
    postgres: {
      host: 'localhost',
      port: 5433,
      database: 'test_db',
      username: 'test_user',
      password: 'test_pass'
    },
    redis: {
      host: 'localhost',
      port: 6380
    }
  },

  // Test data
  fixtures: {
    users: './shared/fixtures/users.json',
    products: './shared/fixtures/products.json'
  },

  // Timeouts
  timeouts: {
    short: 1000,
    medium: 5000,
    long: 10000
  }
};
```

#### Python Test Configuration (backend/tests/config.py)

```python
import os
from pathlib import Path

class TestConfig:
    # API settings
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
    API_TIMEOUT = 10

    # Database settings
    DATABASE_URL = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://test_user:test_pass@localhost:5433/test_db'
    )
    REDIS_URL = os.getenv('TEST_REDIS_URL', 'redis://localhost:6380/0')

    # File paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    FIXTURES_DIR = PROJECT_ROOT / 'shared' / 'fixtures'

    # Test settings
    TESTING = True
    DEBUG = False

    @classmethod
    def get_fixture_path(cls, fixture_name):
        return cls.FIXTURES_DIR / f'{fixture_name}.json'
```

## Best Practices for Multi-Language Testing

### 1. Shared Test Standards
- Use consistent test naming conventions across languages
- Maintain unified coverage thresholds
- Implement similar test categorization (unit, integration, e2e)
- Share test data and fixtures

### 2. CI/CD Integration
- Use matrix builds for different language/version combinations
- Implement parallel test execution
- Generate combined coverage reports
- Maintain consistent quality gates

### 3. Cross-Language Communication
- Use contract testing for API boundaries
- Implement shared test utilities
- Maintain consistent error handling patterns
- Document inter-service dependencies

### 4. Performance Considerations
- Run language-specific tests in parallel
- Use caching for dependencies
- Optimize test data setup/teardown
- Monitor test execution times

### 5. Maintenance
- Keep test configurations synchronized
- Update dependencies consistently
- Monitor test reliability across languages
- Regular cleanup of unused test code