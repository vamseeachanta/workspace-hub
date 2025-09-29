# README Testing Section Template

Copy and customize this testing section for your project's README.md file.

---

## 🧪 Testing

This project maintains comprehensive test coverage with automated testing at multiple levels.

### Test Coverage

[![Coverage Status](https://codecov.io/gh/yourusername/yourproject/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/yourproject)

- **Current Coverage**: 85%+ across all modules
- **Target Coverage**: 90%+ for critical paths
- **Minimum Threshold**: 80% (CI/CD enforced)

### Test Structure

```
tests/
├── unit/          # Fast, isolated unit tests
├── integration/   # Component interaction tests
├── e2e/          # End-to-end system tests
├── fixtures/     # Shared test data
└── conftest.py   # Test configuration (Python projects)
```

### Running Tests

#### Quick Start

```bash
# Run all tests
npm test                    # Node.js projects
pytest                      # Python projects

# Run with coverage
npm run test:coverage       # Node.js projects
pytest --cov=src           # Python projects
```

#### Development Workflow

```bash
# Watch mode for development
npm run test:watch          # Node.js projects
pytest-watch               # Python projects (requires pytest-watch)

# Run specific test types
npm run test:unit           # Unit tests only
npm run test:integration    # Integration tests only
npm run test:e2e           # End-to-end tests only

# Python equivalents
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest -m e2e              # End-to-end tests only
```

#### Advanced Testing

```bash
# Run tests in parallel
npm run test:parallel       # Jest with --maxWorkers
pytest -n auto             # pytest-xdist

# Debug mode
npm run test:debug          # Node.js debugging
pytest --pdb               # Python debugging

# Performance testing
npm run test:performance    # Performance benchmarks
pytest --benchmark          # Python benchmarks (pytest-benchmark)
```

### Test Categories

#### Unit Tests
- ✅ **Fast**: < 100ms per test
- ✅ **Isolated**: No external dependencies
- ✅ **Focused**: Single function/method testing

#### Integration Tests
- ✅ **Component interaction**: API endpoints, database operations
- ✅ **Service integration**: External service mocking
- ✅ **Medium speed**: < 5 seconds per test

#### End-to-End Tests
- ✅ **Full user workflows**: Complete feature testing
- ✅ **Browser automation**: UI interaction testing
- ✅ **Slower execution**: < 30 seconds per test

### Test Requirements

#### Prerequisites

**Node.js Projects:**
```bash
npm install  # Installs test dependencies from package.json
```

**Python Projects:**
```bash
pip install -r requirements-test.txt
# or
uv pip install -r requirements-test.txt
```

#### Environment Setup

1. **Environment Variables**
   ```bash
   # Copy test environment template
   cp .env.test.example .env.test

   # Set required test variables
   export TESTING=true
   export DATABASE_URL=sqlite:///:memory:
   ```

2. **Test Database** (if applicable)
   ```bash
   # Start test services
   docker-compose -f docker-compose.test.yml up -d

   # Run migrations
   npm run db:migrate:test     # Node.js
   alembic upgrade head        # Python with Alembic
   ```

### CI/CD Integration

Tests run automatically on:
- ✅ **Push to main/develop**
- ✅ **Pull requests**
- ✅ **Scheduled runs** (weekly)

#### GitHub Actions

[![Tests](https://github.com/yourusername/yourproject/workflows/Tests/badge.svg)](https://github.com/yourusername/yourproject/actions)

```yaml
# .github/workflows/tests.yml
- Runs on multiple OS (Ubuntu, Windows, macOS)
- Tests multiple language versions
- Enforces coverage thresholds
- Publishes test results
```

#### Quality Gates

All PRs must pass:
- ✅ **80%+ code coverage**
- ✅ **All tests passing**
- ✅ **No security vulnerabilities**
- ✅ **Linting checks**

### Writing Tests

#### Best Practices

1. **Naming Convention**
   ```javascript
   // Good
   describe('UserService', () => {
     test('should create user with valid data', () => {});
     test('should throw error for invalid email', () => {});
   });
   ```

   ```python
   # Good
   class TestUserService:
       def test_should_create_user_with_valid_data(self):
           pass

       def test_should_raise_error_for_invalid_email(self):
           pass
   ```

2. **Test Structure** (Arrange-Act-Assert)
   ```javascript
   test('should calculate total with tax', () => {
     // Arrange
     const items = [{ price: 100 }, { price: 200 }];
     const taxRate = 0.1;

     // Act
     const total = calculateTotal(items, taxRate);

     // Assert
     expect(total).toBe(330);
   });
   ```

3. **Mock External Dependencies**
   ```javascript
   // Mock API calls
   jest.mock('../api/userApi');

   // Mock database
   jest.mock('../db/connection');
   ```

   ```python
   # Mock external services
   @patch('src.services.email_service.send_email')
   def test_user_registration_sends_email(self, mock_send_email):
       # Test implementation
       pass
   ```

#### Test Data Management

**Use Factories for Complex Objects**

```javascript
// tests/factories/userFactory.js
export const createUser = (overrides = {}) => ({
  id: 1,
  name: 'Test User',
  email: 'test@example.com',
  role: 'user',
  ...overrides
});
```

```python
# tests/factories.py
import factory
from src.models import User

class UserFactory(factory.Factory):
    class Meta:
        model = User

    name = factory.Faker('name')
    email = factory.Faker('email')
    role = 'user'
```

### Performance Testing

#### Load Testing

```bash
# API load testing
npm run test:load           # Artillery or similar
k6 run tests/load/api.js    # K6 load testing

# Python load testing
locust -f tests/load/api.py # Locust load testing
```

#### Benchmarking

```bash
# JavaScript performance
npm run test:benchmark      # Jest benchmark tests

# Python performance
pytest --benchmark          # pytest-benchmark
```

### Testing Tools

#### Core Testing Frameworks
- **JavaScript**: Jest, Mocha, Vitest
- **Python**: pytest, unittest
- **E2E**: Playwright, Cypress, Selenium

#### Additional Tools
- **Mocking**: Jest mocks, Python mock/unittest.mock
- **API Testing**: Supertest, requests-mock
- **Database**: In-memory SQLite, Test containers
- **Coverage**: Jest coverage, coverage.py
- **Load Testing**: Artillery, K6, Locust

### Troubleshooting

#### Common Issues

**Tests Fail Locally But Pass in CI**
```bash
# Check environment differences
npm run test:ci             # Run with CI settings
pytest --verbose            # Run with verbose output
```

**Slow Test Performance**
```bash
# Identify slow tests
jest --detectOpenHandles    # Find memory leaks
pytest --durations=10       # Show slowest tests
```

**Coverage Issues**
```bash
# Debug coverage
jest --coverage --verbose   # Detailed coverage
pytest --cov-report=html    # HTML coverage report
```

#### Getting Help

1. **Check test logs**: Look for detailed error messages
2. **Run tests in isolation**: Test individual files
3. **Review test environment**: Verify setup and dependencies
4. **Check CI logs**: Compare local vs CI execution

### Contributing

#### Test Requirements for PRs

- ✅ **Add tests for new features**
- ✅ **Update tests for changed functionality**
- ✅ **Maintain or improve coverage**
- ✅ **All tests must pass**

#### Test Review Checklist

- [ ] Tests cover happy path and edge cases
- [ ] Tests are focused and well-named
- [ ] Mocks are used appropriately
- [ ] Test data is realistic
- [ ] Tests run quickly and reliably

---

## 📊 Test Reports

### Latest Test Results

| Test Type | Status | Coverage | Duration |
|-----------|--------|----------|----------|
| Unit Tests | ✅ Passing | 95% | 2.3s |
| Integration Tests | ✅ Passing | 87% | 15.2s |
| E2E Tests | ✅ Passing | 78% | 1m 34s |

### Coverage by Module

| Module | Coverage | Status |
|--------|----------|--------|
| Core Services | 96% | ✅ |
| API Endpoints | 89% | ✅ |
| Database Models | 94% | ✅ |
| Utilities | 85% | ✅ |
| UI Components | 82% | ✅ |

*Last updated: [Auto-generated by CI/CD]*

---

*For more detailed testing documentation, see [TESTING.md](./TESTING.md)*