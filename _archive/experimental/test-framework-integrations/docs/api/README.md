# API Documentation

Complete API reference for Test Framework Integrations with examples, authentication, and usage patterns.

## 📚 API Overview

The Test Framework Integrations API provides programmatic access to:
- **Framework Management**: Detect, switch, and configure test frameworks
- **Test Execution**: Run tests with coverage and profiling
- **Baseline Tracking**: Save, load, and compare test baselines
- **Coverage Reporting**: Generate and manage coverage reports
- **Performance Analysis**: Profile tests and analyze bottlenecks

## 🔗 API Endpoints

### Base URLs
- **Local Development**: `http://localhost:3000/api/v1`
- **Production**: `https://api.test-integrations.com/v1`

### Authentication
- **API Key**: Include `X-API-Key` header
- **Bearer Token**: Include `Authorization: Bearer <token>` header

## 📋 Quick Reference

### Frameworks
- `GET /frameworks` - List detected frameworks
- `POST /frameworks/{framework}/switch` - Switch active framework

### Tests
- `GET /tests/discover` - Discover test files
- `POST /tests/run` - Run tests
- `POST /tests/run/all-frameworks` - Run across all frameworks
- `POST /tests/stop` - Stop running tests

### Baselines
- `GET /baselines` - List saved baselines
- `POST /baselines` - Save new baseline
- `GET /baselines/{label}` - Get specific baseline
- `POST /baselines/{label}/compare` - Compare with baseline

### Coverage
- `GET /coverage/reports` - List coverage reports
- `POST /coverage/reports` - Generate coverage report

### Profiling
- `GET /profiling/metrics` - Get current metrics
- `GET /profiling/bottlenecks` - Analyze bottlenecks

## 🚀 Getting Started

### 1. Initialize API Client

```javascript
const axios = require('axios');

const apiClient = axios.create({
  baseURL: 'http://localhost:3000/api/v1',
  headers: {
    'X-API-Key': 'your-api-key',
    'Content-Type': 'application/json'
  }
});
```

### 2. Detect Frameworks

```javascript
async function detectFrameworks() {
  try {
    const response = await apiClient.get('/frameworks');
    console.log('Detected frameworks:', response.data.frameworks);
    return response.data.frameworks;
  } catch (error) {
    console.error('Failed to detect frameworks:', error.response.data);
  }
}
```

### 3. Run Tests

```javascript
async function runTests() {
  try {
    const response = await apiClient.post('/tests/run', {
      coverage: true,
      profiling: true,
      verbose: true
    });

    console.log('Test Results:');
    console.log(`Tests: ${response.data.summary.passed}/${response.data.summary.total}`);
    console.log(`Coverage: ${response.data.coverage?.total.toFixed(2)}%`);

    return response.data;
  } catch (error) {
    console.error('Test execution failed:', error.response.data);
  }
}
```

### 4. Save Baseline

```javascript
async function saveBaseline(results, label = 'latest') {
  try {
    const response = await apiClient.post('/baselines', {
      label,
      results
    });

    console.log(`Baseline saved: ${response.data.label}`);
    return response.data;
  } catch (error) {
    console.error('Failed to save baseline:', error.response.data);
  }
}
```

## 📖 Detailed Examples

### Complete Test Workflow

```javascript
const TestFrameworkAPI = require('./test-framework-api');

class TestRunner {
  constructor(apiKey) {
    this.api = new TestFrameworkAPI(apiKey);
  }

  async runCompleteWorkflow() {
    try {
      // 1. Detect available frameworks
      const frameworks = await this.api.getFrameworks();
      console.log(`Found ${frameworks.length} frameworks`);

      // 2. Switch to preferred framework
      if (frameworks.find(f => f.name === 'jest')) {
        await this.api.switchFramework('jest');
      }

      // 3. Discover test files
      const testFiles = await this.api.discoverTests();
      console.log(`Discovered ${testFiles.count} test files`);

      // 4. Run tests with full features
      const results = await this.api.runTests({
        coverage: true,
        profiling: true,
        baseline: 'v1.0.0'
      });

      // 5. Analyze results
      await this.analyzeResults(results);

      // 6. Save new baseline if successful
      if (results.summary.success) {
        await this.api.saveBaseline(results, 'latest');
      }

      return results;

    } catch (error) {
      console.error('Workflow failed:', error);
      throw error;
    }
  }

  async analyzeResults(results) {
    // Check for regressions
    if (results.baseline?.performance.slower.length > 0) {
      console.log('⚠️ Performance regressions detected:');
      results.baseline.performance.slower.forEach(test => {
        console.log(`  ${test.name}: +${test.regression}ms`);
      });
    }

    // Check coverage thresholds
    if (results.coverage?.total < 80) {
      console.log(`⚠️ Coverage below threshold: ${results.coverage.total}%`);
    }

    // Analyze bottlenecks
    const bottlenecks = await this.api.analyzeBottlenecks();
    if (bottlenecks.slowTests.length > 0) {
      console.log('🐌 Slowest tests:');
      bottlenecks.slowTests.slice(0, 3).forEach((test, i) => {
        console.log(`  ${i + 1}. ${test.name}: ${test.duration}ms`);
      });
    }
  }
}

// Usage
const runner = new TestRunner(process.env.API_KEY);
runner.runCompleteWorkflow().catch(console.error);
```

### Multi-Framework Testing

```javascript
async function compareFrameworks() {
  const api = new TestFrameworkAPI(process.env.API_KEY);

  try {
    // Run tests across all frameworks
    const multiResults = await api.runAllFrameworks({
      coverage: true,
      parallel: false // Sequential for comparison
    });

    // Compare results
    const comparison = {};
    for (const [framework, results] of Object.entries(multiResults.results)) {
      comparison[framework] = {
        duration: results.summary.duration,
        coverage: results.coverage?.total || 0,
        memoryUsage: results.profiling?.memory.peak.heapUsed || 0
      };
    }

    // Generate comparison report
    console.log('Framework Comparison:');
    console.table(comparison);

    // Find fastest framework
    const fastest = Object.entries(comparison)
      .sort((a, b) => a[1].duration - b[1].duration)[0];
    console.log(`Fastest framework: ${fastest[0]} (${fastest[1].duration}ms)`);

    return comparison;

  } catch (error) {
    console.error('Multi-framework testing failed:', error);
  }
}
```

### Real-time Monitoring

```javascript
async function monitorTestExecution() {
  const api = new TestFrameworkAPI(process.env.API_KEY);

  try {
    // Start test execution
    const testPromise = api.runTests({
      profiling: true,
      verbose: false
    });

    // Monitor performance in real-time
    const monitorInterval = setInterval(async () => {
      try {
        const metrics = await api.getCurrentMetrics();

        console.log('Real-time Metrics:');
        console.log(`Memory: ${(metrics.memory.process.heapUsed / 1024 / 1024).toFixed(2)}MB`);
        console.log(`CPU: ${metrics.cpu.usage.toFixed(1)}%`);
        console.log(`Uptime: ${(metrics.uptime).toFixed(1)}s`);
        console.log('---');

      } catch (error) {
        console.log('Monitoring temporarily unavailable');
      }
    }, 2000);

    // Wait for tests to complete
    const results = await testPromise;
    clearInterval(monitorInterval);

    console.log('Test execution completed');
    return results;

  } catch (error) {
    console.error('Monitoring failed:', error);
  }
}
```

### Coverage Management

```javascript
class CoverageManager {
  constructor(api) {
    this.api = api;
  }

  async generateComprehensiveReports(coverage) {
    const formats = ['json', 'html', 'lcov', 'text'];
    const reports = [];

    for (const format of formats) {
      try {
        const report = await this.api.generateCoverageReport({
          name: `coverage-${format}`,
          format: [format],
          coverage
        });

        reports.push(report);
        console.log(`Generated ${format} report: ${report.paths[format]}`);

      } catch (error) {
        console.error(`Failed to generate ${format} report:`, error);
      }
    }

    return reports;
  }

  async trackCoverageTrends() {
    try {
      const reports = await this.api.getCoverageReports();

      // Sort by timestamp
      reports.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

      // Calculate trends
      const trends = [];
      for (let i = 1; i < reports.length; i++) {
        const current = reports[i].summary.total;
        const previous = reports[i - 1].summary.total;
        const change = current - previous;

        trends.push({
          date: reports[i].timestamp,
          coverage: current,
          change: change,
          trend: change > 0 ? '📈' : change < 0 ? '📉' : '➡️'
        });
      }

      console.log('Coverage Trends:');
      trends.slice(-10).forEach(trend => {
        console.log(`${trend.date}: ${trend.coverage.toFixed(2)}% ${trend.trend} ${trend.change.toFixed(2)}%`);
      });

      return trends;

    } catch (error) {
      console.error('Failed to track coverage trends:', error);
    }
  }
}
```

## 🔐 Authentication

### API Key Authentication

```javascript
// Set API key in headers
const config = {
  headers: {
    'X-API-Key': 'your-api-key-here'
  }
};

const response = await axios.get('/frameworks', config);
```

### JWT Token Authentication

```javascript
// Set Bearer token
const config = {
  headers: {
    'Authorization': 'Bearer your-jwt-token-here'
  }
};

const response = await axios.post('/tests/run', data, config);
```

### Environment Configuration

```bash
# .env
API_KEY=your-api-key
API_BASE_URL=https://api.test-integrations.com/v1
API_TIMEOUT=30000
```

```javascript
// API client with environment config
const apiClient = axios.create({
  baseURL: process.env.API_BASE_URL,
  timeout: process.env.API_TIMEOUT,
  headers: {
    'X-API-Key': process.env.API_KEY
  }
});
```

## 📊 Response Formats

### Success Response Format

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "timestamp": "2023-06-15T10:30:00Z"
}
```

### Error Response Format

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    // Additional error details
  },
  "timestamp": "2023-06-15T10:30:00Z"
}
```

## 📈 Rate Limiting

- **Rate Limit**: 100 requests per minute per API key
- **Headers**:
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when rate limit resets

## 🔧 SDKs and Libraries

### Official JavaScript SDK

```bash
npm install @test-framework-integrations/sdk
```

```javascript
const { TestFrameworkClient } = require('@test-framework-integrations/sdk');

const client = new TestFrameworkClient({
  apiKey: process.env.API_KEY,
  baseURL: 'https://api.test-integrations.com/v1'
});

// High-level methods
const results = await client.runTests({ coverage: true });
await client.saveBaseline(results, 'v1.0.0');
```

### Python SDK

```bash
pip install test-framework-integrations-python
```

```python
from test_framework_integrations import TestFrameworkClient

client = TestFrameworkClient(api_key=os.getenv('API_KEY'))

# Run tests
results = client.run_tests(coverage=True, profiling=True)
print(f"Tests: {results['summary']['passed']}/{results['summary']['total']}")

# Save baseline
client.save_baseline(results, label='v1.0.0')
```

## 🐛 Error Handling

### Common Error Codes

- `INVALID_PARAMETERS` - Invalid request parameters
- `FRAMEWORK_NOT_FOUND` - Requested framework not detected
- `TEST_EXECUTION_FAILED` - Test execution failed
- `BASELINE_NOT_FOUND` - Baseline label not found
- `COVERAGE_COLLECTION_FAILED` - Coverage collection failed
- `PROFILING_ERROR` - Performance profiling error
- `RATE_LIMIT_EXCEEDED` - Rate limit exceeded
- `AUTHENTICATION_FAILED` - Invalid API key or token
- `INTERNAL_ERROR` - Internal server error

### Error Handling Patterns

```javascript
async function handleApiErrors(apiCall) {
  try {
    return await apiCall();
  } catch (error) {
    const { response } = error;

    if (response?.status === 429) {
      console.log('Rate limit exceeded, retrying in 60 seconds...');
      await new Promise(resolve => setTimeout(resolve, 60000));
      return apiCall(); // Retry once
    }

    if (response?.status === 401) {
      throw new Error('Authentication failed. Check your API key.');
    }

    if (response?.status >= 500) {
      console.error('Server error:', response.data);
      throw new Error('Server error. Please try again later.');
    }

    // Client error
    console.error('API error:', response?.data || error.message);
    throw error;
  }
}
```

## 📚 Additional Resources

- **[OpenAPI Specification](./openapi.yaml)** - Complete API specification
- **[GraphQL Schema](./graphql-schema.md)** - GraphQL queries and mutations
- **[WebSocket Events](./websocket-events.md)** - Real-time event subscriptions
- **[Postman Collection](./postman-collection.json)** - API testing collection
- **[SDK Documentation](./sdks/)** - Language-specific SDK docs

## 🔗 External Links

- [REST API Best Practices](https://restfulapi.net/)
- [OpenAPI Specification](https://spec.openapis.org/oas/v3.0.0)
- [JSON Schema](https://json-schema.org/)
- [HTTP Status Codes](https://httpstatuses.com/)