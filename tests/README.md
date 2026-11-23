# Comprehensive Test Suite for Baseline System

This directory contains a comprehensive test suite designed to achieve >90% code coverage and ensure the reliability of the baseline comparison system. The test suite includes multiple testing strategies and advanced testing techniques.

## Test Architecture

### 📁 Directory Structure

```
tests/
├── jest.config.js              # Jest configuration
├── playwright.config.js        # Playwright E2E configuration
├── stryker.conf.js             # Mutation testing configuration
├── setup.js                    # Global test setup
├── unit/                       # Unit tests (>90% coverage target)
│   ├── baseline-manager.test.js
│   ├── metrics-collector.test.js
│   ├── comparison-engine.test.js
│   ├── rule-engine.test.js
│   └── report-generator.test.js
├── integration/                # Integration tests
│   ├── framework-adapters.test.js
│   ├── cicd-integration.test.js
│   ├── database-operations.test.js
│   └── api-endpoints.test.js
├── e2e/                       # End-to-end tests
│   ├── complete-workflows.test.js
│   ├── dashboard-interactions.test.js
│   ├── alert-system.test.js
│   └── report-generation.test.js
├── performance/               # Performance & load tests
│   ├── load-testing.test.js
│   ├── concurrent-execution.test.js
│   ├── memory-usage.test.js
│   └── database-performance.test.js
├── property-based/            # Property-based testing
│   └── baseline-properties.test.js
├── fixtures/                  # Test data & mocks
│   ├── baseline-data.js
│   └── mock-factories.js
├── coverage/                  # Coverage verification
│   └── coverage-verification.test.js
├── mutation/                  # Mutation testing utilities
│   └── mutation-helpers.js
└── scripts/                   # Test runners & utilities
    ├── run-all-tests.js
    └── analyze-results.js
```

## 🧪 Test Categories

### 1. Unit Tests (Core Coverage)
- **BaselineManager**: Creation, validation, CRUD operations
- **MetricsCollector**: Jest, Pytest, Mocha, Playwright adapters
- **ComparisonEngine**: Metric comparison, change calculation, status determination
- **RuleEngine**: Threshold evaluation, anomaly detection, risk assessment
- **ReportGenerator**: HTML, PDF, JSON report generation

**Coverage Target**: >95% for critical components

### 2. Integration Tests
- **Framework Adapters**: Real test framework integration
- **CI/CD Integration**: GitHub, GitLab, Jenkins, CircleCI
- **Database Operations**: Transaction handling, connection pooling
- **API Endpoints**: REST API validation and error handling

### 3. End-to-End Tests
- **Complete Workflows**: Full baseline creation → comparison → reporting
- **Dashboard Interactions**: User interface testing with Playwright
- **Alert System**: Notification and escalation flows
- **Report Generation**: Multi-format report creation and delivery

### 4. Performance Tests
- **Load Testing**: High-volume baseline creation and comparison
- **Concurrent Execution**: Multi-threaded operations
- **Memory Usage**: Memory leak detection and optimization
- **Database Performance**: Query optimization and connection limits

### 5. Property-Based Testing
- **Mathematical Properties**: Metric calculations, change computations
- **Data Integrity**: Serialization, validation boundaries
- **Edge Cases**: Division by zero, extreme values, null handling

### 6. Mutation Testing
- **Code Quality**: Tests that actually test behavior changes
- **Test Effectiveness**: Mutation score >90% target
- **Weakness Detection**: Areas needing better test coverage

## 🚀 Running Tests

### Quick Commands
```bash
# Run all tests (comprehensive)
npm test

# Run specific test types
npm run test:unit
npm run test:integration
npm run test:e2e
npm run test:performance
npm run test:property
npm run test:mutation

# Development workflows
npm run test:quick        # Unit + Integration only
npm run test:watch        # Watch mode for development
npm run test:ci           # CI/CD optimized (skip slow tests)
npm run test:parallel     # Parallel execution

# Coverage & Analysis
npm run test:coverage     # Generate coverage report
npm run test:analyze      # Analyze test results
npm run coverage:open     # Open coverage report
npm run mutation:open     # Open mutation report
```

### Advanced Options
```bash
# Debug tests
npm run test:debug

# Skip slow tests
npm run test:ci

# Mutation testing (critical paths only)
npm run test:mutation-quick

# Serve reports
npm run reports:serve
```

## 📊 Quality Metrics

### Coverage Thresholds
- **Lines**: ≥90%
- **Branches**: ≥90%
- **Functions**: ≥90%
- **Statements**: ≥90%

### Mutation Testing
- **Mutation Score**: ≥90%
- **Critical Components**: ≥95%
- **Adapter Components**: ≥85%

### Performance Benchmarks
- **Baseline Creation**: <1s per baseline
- **Comparison**: <5s for large datasets
- **Report Generation**: <10s for comprehensive reports
- **Memory Usage**: <200MB sustained load

## 🛠️ Test Utilities

### Mock Factories
```javascript
const MockFactory = require('./fixtures/mock-factories');

// Generate realistic test data
const baseline = MockFactory.createBaseline();
const metrics = MockFactory.createMetrics();
const comparison = MockFactory.createComparison();
```

### Property-Based Testing
```javascript
const fc = require('fast-check');

// Test mathematical properties
fc.assert(
  fc.property(fc.float(), fc.float(), (a, b) => {
    const change = calculateChange(a, b);
    expect(change.absolute).toBe(b - a);
  })
);
```

### Performance Testing
```javascript
// Memory usage monitoring
const startMemory = process.memoryUsage().heapUsed;
await performOperation();
const endMemory = process.memoryUsage().heapUsed;
expect(endMemory - startMemory).toBeLessThan(maxMemoryIncrease);
```

## 🔍 Mutation Testing Analysis

The mutation testing setup identifies weak spots in the test suite:

### Common Mutation Survivors
1. **Error Handling**: Exception paths not tested
2. **Boundary Conditions**: Edge case validations missing
3. **Arithmetic Operations**: Calculation verification incomplete
4. **Logical Operators**: Boolean logic branches untested

### Improvement Strategies
1. **Add Negative Test Cases**: Test error conditions explicitly
2. **Boundary Testing**: Test edge values and limits
3. **Calculation Verification**: Assert exact mathematical results
4. **Branch Coverage**: Ensure all conditional paths tested

## 📈 Continuous Integration

### GitHub Actions Integration
```yaml
- name: Run Tests
  run: npm run test:ci

- name: Upload Coverage
  uses: codecov/codecov-action@v3

- name: Mutation Testing
  run: npm run test:mutation
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

### Test Reporting
- **JSON Reports**: Machine-readable results in `reports/`
- **HTML Reports**: Human-readable dashboards
- **Coverage Reports**: Line-by-line coverage analysis
- **Mutation Reports**: Test quality assessment

## 🐛 Debugging Failed Tests

### Common Issues
1. **Async Operations**: Use proper async/await patterns
2. **Mock Cleanup**: Reset mocks between tests
3. **Test Isolation**: Each test should be independent
4. **Resource Cleanup**: Close database connections, clear timers

### Debug Commands
```bash
# Run single test file
npx jest tests/unit/baseline-manager.test.js

# Debug with breakpoints
npm run test:debug

# Verbose output
npx jest --verbose

# Watch specific files
npx jest --watch baseline-manager
```

## 📝 Writing New Tests

### Unit Test Template
```javascript
describe('ComponentName', () => {
  let component;
  let mockDependency;

  beforeEach(() => {
    mockDependency = createMockDependency();
    component = new ComponentName({ dependency: mockDependency });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('methodName', () => {
    it('should handle normal case', () => {
      // Arrange
      const input = validInput;

      // Act
      const result = component.methodName(input);

      // Assert
      expect(result).toEqual(expectedOutput);
    });

    it('should handle edge case', () => {
      // Test boundary conditions
    });

    it('should handle error case', () => {
      // Test error handling
    });
  });
});
```

### Integration Test Pattern
```javascript
describe('Component Integration', () => {
  let testEnvironment;

  beforeAll(async () => {
    testEnvironment = await setupTestEnvironment();
  });

  afterAll(async () => {
    await cleanupTestEnvironment(testEnvironment);
  });

  it('should integrate components correctly', async () => {
    // Test real component interactions
  });
});
```

## 📚 Best Practices

### Test Organization
1. **One Assertion Per Test**: Focus on single behavior
2. **Descriptive Names**: Explain what and why
3. **Arrange-Act-Assert**: Clear test structure
4. **Test Data Builders**: Use factories for complex data
5. **Mock External Dependencies**: Keep tests isolated

### Performance Considerations
1. **Parallel Execution**: Use `--runInBand` for integration tests
2. **Memory Management**: Clean up resources after tests
3. **Test Data Size**: Use minimal realistic datasets
4. **Timeout Configuration**: Set appropriate timeouts

### Coverage Goals
1. **Prioritize Critical Paths**: Focus on core business logic
2. **Edge Case Testing**: Test boundary conditions
3. **Error Path Coverage**: Test exception handling
4. **Integration Points**: Test component interactions

---

This comprehensive test suite ensures reliability, maintainability, and confidence in the baseline comparison system. The multi-layered approach catches issues at different levels while maintaining fast feedback loops for developers.