# WebSocket Events Documentation

Real-time event streaming for Test Framework Integrations via WebSocket connections.

## 📚 Overview

The WebSocket API provides real-time updates for:
- **Test Execution**: Live test progress and results
- **Performance Monitoring**: Real-time performance metrics
- **Coverage Tracking**: Live coverage updates
- **System Health**: System status monitoring
- **Framework Events**: Framework state changes

## 🔗 Connection

### WebSocket Endpoint
```
ws://localhost:3000/ws
wss://api.test-integrations.com/ws
```

### Authentication
```javascript
// Connect with API key
const ws = new WebSocket('ws://localhost:3000/ws?apiKey=your-api-key');

// Or with JWT token
const ws = new WebSocket('ws://localhost:3000/ws?token=your-jwt-token');
```

### Connection Lifecycle

```javascript
const ws = new WebSocket('ws://localhost:3000/ws?apiKey=your-api-key');

ws.onopen = function(event) {
  console.log('Connected to Test Framework Integrations WebSocket');

  // Subscribe to events
  ws.send(JSON.stringify({
    type: 'subscribe',
    events: ['test.progress', 'performance.metrics']
  }));
};

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received event:', data);
};

ws.onclose = function(event) {
  console.log('WebSocket connection closed:', event.code, event.reason);
};

ws.onerror = function(error) {
  console.error('WebSocket error:', error);
};
```

## 📡 Event Types

### Test Events

#### test.started
Fired when test execution begins.

```json
{
  "type": "test.started",
  "timestamp": "2023-06-15T10:30:00Z",
  "data": {
    "framework": "jest",
    "totalTests": 45,
    "testFiles": ["src/utils.test.js", "src/components/Button.test.js"],
    "options": {
      "coverage": true,
      "profiling": true
    }
  }
}
```

#### test.progress
Fired during test execution with progress updates.

```json
{
  "type": "test.progress",
  "timestamp": "2023-06-15T10:30:15Z",
  "data": {
    "framework": "jest",
    "testName": "should calculate total correctly",
    "suite": "utils",
    "status": "running",
    "progress": 0.45,
    "completed": 20,
    "total": 45,
    "duration": 15000
  }
}
```

#### test.result
Fired when individual test completes.

```json
{
  "type": "test.result",
  "timestamp": "2023-06-15T10:30:16Z",
  "data": {
    "framework": "jest",
    "testName": "should calculate total correctly",
    "suite": "utils",
    "status": "passed",
    "duration": 1200,
    "file": "src/utils.test.js",
    "line": 45,
    "assertions": 3
  }
}
```

#### test.completed
Fired when all tests complete.

```json
{
  "type": "test.completed",
  "timestamp": "2023-06-15T10:31:00Z",
  "data": {
    "framework": "jest",
    "summary": {
      "total": 45,
      "passed": 43,
      "failed": 2,
      "skipped": 0,
      "duration": 30000,
      "success": false
    },
    "coverage": {
      "total": 87.3,
      "statements": 89.1,
      "branches": 84.2,
      "functions": 91.5,
      "lines": 87.8
    }
  }
}
```

#### test.failed
Fired when test execution fails.

```json
{
  "type": "test.failed",
  "timestamp": "2023-06-15T10:30:45Z",
  "data": {
    "framework": "jest",
    "testName": "should handle edge cases",
    "suite": "utils",
    "status": "failed",
    "duration": 850,
    "error": {
      "message": "Expected 'undefined' to equal 'null'",
      "stack": "Error: Expected 'undefined' to equal 'null'\n    at Object.<anonymous> (src/utils.test.js:67:23)",
      "type": "AssertionError"
    },
    "file": "src/utils.test.js",
    "line": 67
  }
}
```

#### test.output
Fired for test output (stdout/stderr).

```json
{
  "type": "test.output",
  "timestamp": "2023-06-15T10:30:20Z",
  "data": {
    "framework": "jest",
    "testName": "should log debug information",
    "suite": "api",
    "output": "Debug: Processing user data...",
    "outputType": "stdout",
    "stream": "log"
  }
}
```

### Performance Events

#### performance.metrics
Real-time performance metrics during test execution.

```json
{
  "type": "performance.metrics",
  "timestamp": "2023-06-15T10:30:25Z",
  "data": {
    "memory": {
      "heapUsed": 45.6,
      "heapTotal": 67.2,
      "external": 8.1,
      "rss": 89.3
    },
    "cpu": {
      "usage": 78.5,
      "load": [1.2, 1.5, 1.8]
    },
    "uptime": 125.7,
    "gc": {
      "recentEvents": 3,
      "totalTime": 45.2,
      "lastEventTime": "2023-06-15T10:30:23Z"
    },
    "tests": {
      "running": 2,
      "completed": 18,
      "averageDuration": 1250
    }
  }
}
```

#### performance.bottleneck
Fired when performance bottleneck is detected.

```json
{
  "type": "performance.bottleneck",
  "timestamp": "2023-06-15T10:30:30Z",
  "data": {
    "type": "slow_test",
    "testName": "should process large dataset",
    "duration": 8500,
    "threshold": 5000,
    "severity": "high",
    "suggestions": [
      "Consider breaking down into smaller tests",
      "Mock external dependencies",
      "Optimize data processing logic"
    ],
    "memoryDelta": {
      "heapUsed": 15.2,
      "external": 3.4
    }
  }
}
```

#### performance.leak
Fired when memory leak is detected.

```json
{
  "type": "performance.leak",
  "timestamp": "2023-06-15T10:30:35Z",
  "data": {
    "type": "memory_leak",
    "testName": "should cleanup resources",
    "leakType": "event_listeners",
    "size": 2.3,
    "location": "src/components/Chart.js:45",
    "stackTrace": [
      "at Chart.componentDidMount (src/components/Chart.js:45:12)",
      "at mountComponent (node_modules/react/lib/ReactCompositeComponent.js:187:21)"
    ],
    "suggestions": [
      "Remove event listeners in componentWillUnmount",
      "Use cleanup functions in useEffect hooks"
    ]
  }
}
```

### Coverage Events

#### coverage.started
Fired when coverage collection begins.

```json
{
  "type": "coverage.started",
  "timestamp": "2023-06-15T10:30:05Z",
  "data": {
    "framework": "jest",
    "provider": "nyc",
    "totalFiles": 67,
    "patterns": ["src/**/*.js", "!src/**/*.test.js"]
  }
}
```

#### coverage.progress
Fired during coverage collection.

```json
{
  "type": "coverage.progress",
  "timestamp": "2023-06-15T10:30:40Z",
  "data": {
    "filesProcessed": 45,
    "totalFiles": 67,
    "currentFile": "src/components/Button.js",
    "percentage": 67.2,
    "coverage": {
      "statements": 89.3,
      "branches": 84.7,
      "functions": 92.1,
      "lines": 88.9
    }
  }
}
```

#### coverage.completed
Fired when coverage collection completes.

```json
{
  "type": "coverage.completed",
  "timestamp": "2023-06-15T10:31:05Z",
  "data": {
    "framework": "jest",
    "provider": "nyc",
    "summary": {
      "total": 87.3,
      "statements": 89.1,
      "branches": 84.2,
      "functions": 91.5,
      "lines": 87.8
    },
    "thresholdsMet": true,
    "files": 67,
    "reports": ["html", "json", "lcov"]
  }
}
```

#### coverage.threshold
Fired when coverage thresholds are checked.

```json
{
  "type": "coverage.threshold",
  "timestamp": "2023-06-15T10:31:06Z",
  "data": {
    "passed": false,
    "thresholds": {
      "statements": 90,
      "branches": 85,
      "functions": 90,
      "lines": 90
    },
    "actual": {
      "statements": 89.1,
      "branches": 84.2,
      "functions": 91.5,
      "lines": 87.8
    },
    "failures": [
      {
        "metric": "statements",
        "threshold": 90,
        "actual": 89.1,
        "deficit": 0.9
      },
      {
        "metric": "branches",
        "threshold": 85,
        "actual": 84.2,
        "deficit": 0.8
      }
    ]
  }
}
```

### Framework Events

#### framework.detected
Fired when frameworks are detected.

```json
{
  "type": "framework.detected",
  "timestamp": "2023-06-15T10:29:30Z",
  "data": {
    "frameworks": [
      {
        "name": "jest",
        "version": "29.5.0",
        "configPath": "./jest.config.js",
        "testPatterns": ["**/__tests__/**/*.js", "**/*.test.js"]
      },
      {
        "name": "playwright",
        "version": "1.32.0",
        "configPath": "./playwright.config.js",
        "testPatterns": ["tests/**/*.spec.js"]
      }
    ],
    "active": "jest"
  }
}
```

#### framework.switched
Fired when active framework changes.

```json
{
  "type": "framework.switched",
  "timestamp": "2023-06-15T10:29:45Z",
  "data": {
    "from": "jest",
    "to": "playwright",
    "reason": "user_request",
    "success": true,
    "framework": {
      "name": "playwright",
      "version": "1.32.0",
      "configPath": "./playwright.config.js"
    }
  }
}
```

#### framework.error
Fired when framework encounters an error.

```json
{
  "type": "framework.error",
  "timestamp": "2023-06-15T10:30:10Z",
  "data": {
    "framework": "mocha",
    "error": {
      "message": "Configuration file not found",
      "code": "CONFIG_NOT_FOUND",
      "details": {
        "expectedPaths": ["./mocharc.json", "./mocha.config.js"],
        "suggestion": "Create a mocha configuration file"
      }
    },
    "severity": "error"
  }
}
```

### Baseline Events

#### baseline.saved
Fired when baseline is saved.

```json
{
  "type": "baseline.saved",
  "timestamp": "2023-06-15T10:31:10Z",
  "data": {
    "label": "v1.0.0",
    "framework": "jest",
    "path": "./.test-baselines/v1.0.0.json",
    "size": 15672,
    "tests": 45,
    "coverage": 87.3
  }
}
```

#### baseline.compared
Fired when baseline comparison completes.

```json
{
  "type": "baseline.compared",
  "timestamp": "2023-06-15T10:31:15Z",
  "data": {
    "baseline": "v1.0.0",
    "comparison": {
      "testsAdded": 3,
      "testsRemoved": 1,
      "testsChanged": 2,
      "performanceRegression": true,
      "coverageImproved": false,
      "summary": {
        "regression": true,
        "improvement": false,
        "score": 0.72
      }
    },
    "regressions": [
      {
        "test": "should calculate complex formula",
        "change": 1250,
        "percentage": 45.2
      }
    ]
  }
}
```

### System Events

#### system.health
Fired periodically with system health status.

```json
{
  "type": "system.health",
  "timestamp": "2023-06-15T10:30:00Z",
  "data": {
    "status": "healthy",
    "uptime": 7254.3,
    "version": "1.0.0",
    "components": [
      {
        "name": "test_runner",
        "status": "healthy",
        "lastCheck": "2023-06-15T10:29:58Z"
      },
      {
        "name": "coverage_collector",
        "status": "healthy",
        "lastCheck": "2023-06-15T10:29:58Z"
      },
      {
        "name": "performance_profiler",
        "status": "degraded",
        "message": "High memory usage detected",
        "lastCheck": "2023-06-15T10:29:58Z"
      }
    ],
    "metrics": {
      "memory": {
        "total": 16384,
        "used": 8192,
        "percentage": 50.0
      },
      "cpu": {
        "cores": 8,
        "usage": 25.5,
        "load": [1.2, 1.1, 0.9]
      }
    }
  }
}
```

#### system.error
Fired when system-level errors occur.

```json
{
  "type": "system.error",
  "timestamp": "2023-06-15T10:30:45Z",
  "data": {
    "component": "performance_profiler",
    "error": {
      "message": "Failed to collect CPU samples",
      "code": "CPU_SAMPLING_FAILED",
      "severity": "warning"
    },
    "impact": "Performance profiling may be incomplete",
    "recovery": "Automatic retry in 10 seconds"
  }
}
```

## 🎮 Event Subscription

### Subscribe to Events

```javascript
// Subscribe to specific events
ws.send(JSON.stringify({
  type: 'subscribe',
  events: [
    'test.progress',
    'test.result',
    'performance.metrics',
    'coverage.progress'
  ]
}));

// Subscribe to event patterns
ws.send(JSON.stringify({
  type: 'subscribe',
  patterns: [
    'test.*',        // All test events
    'performance.*', // All performance events
    'system.health'  // Specific system event
  ]
}));

// Subscribe to all events
ws.send(JSON.stringify({
  type: 'subscribe',
  events: ['*']
}));
```

### Unsubscribe from Events

```javascript
// Unsubscribe from specific events
ws.send(JSON.stringify({
  type: 'unsubscribe',
  events: ['performance.metrics']
}));

// Unsubscribe from all events
ws.send(JSON.stringify({
  type: 'unsubscribe',
  events: ['*']
}));
```

### Event Filtering

```javascript
// Subscribe with filters
ws.send(JSON.stringify({
  type: 'subscribe',
  events: ['test.result'],
  filters: {
    status: ['failed', 'error'],      // Only failed tests
    framework: 'jest',                // Only jest results
    suite: 'integration'              // Only integration suite
  }
}));

// Performance metrics with thresholds
ws.send(JSON.stringify({
  type: 'subscribe',
  events: ['performance.metrics'],
  filters: {
    memoryThreshold: 100,  // Only when memory > 100MB
    cpuThreshold: 80       // Only when CPU > 80%
  }
}));
```

## 🔧 Client Implementation Examples

### React Hook for WebSocket Events

```javascript
import { useState, useEffect, useRef } from 'react';

function useWebSocketEvents(apiKey, events = ['*']) {
  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState([]);
  const [error, setError] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    // Connect to WebSocket
    ws.current = new WebSocket(`ws://localhost:3000/ws?apiKey=${apiKey}`);

    ws.current.onopen = () => {
      setIsConnected(true);
      setError(null);

      // Subscribe to events
      ws.current.send(JSON.stringify({
        type: 'subscribe',
        events
      }));
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [...prev, data]);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
    };

    ws.current.onerror = (error) => {
      setError(error);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [apiKey, events]);

  const sendMessage = (message) => {
    if (ws.current && isConnected) {
      ws.current.send(JSON.stringify(message));
    }
  };

  return {
    isConnected,
    events,
    error,
    sendMessage
  };
}

// Usage in component
function TestDashboard() {
  const { isConnected, events, sendMessage } = useWebSocketEvents(
    process.env.REACT_APP_API_KEY,
    ['test.progress', 'test.result', 'performance.metrics']
  );

  const testEvents = events.filter(e => e.type.startsWith('test.'));
  const performanceEvents = events.filter(e => e.type.startsWith('performance.'));

  return (
    <div>
      <div>Status: {isConnected ? 'Connected' : 'Disconnected'}</div>

      <div>
        <h3>Test Progress</h3>
        {testEvents.map((event, i) => (
          <div key={i}>
            {event.type}: {JSON.stringify(event.data)}
          </div>
        ))}
      </div>

      <div>
        <h3>Performance Metrics</h3>
        {performanceEvents.map((event, i) => (
          <div key={i}>
            Memory: {event.data.memory?.heapUsed}MB
            CPU: {event.data.cpu?.usage}%
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Node.js Event Processor

```javascript
const WebSocket = require('ws');

class TestEventProcessor {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.ws = null;
    this.eventHandlers = new Map();
    this.connect();
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:3000/ws?apiKey=${this.apiKey}`);

    this.ws.on('open', () => {
      console.log('Connected to Test Framework Integrations WebSocket');

      // Subscribe to all events
      this.subscribe(['*']);
    });

    this.ws.on('message', (data) => {
      const event = JSON.parse(data);
      this.handleEvent(event);
    });

    this.ws.on('close', () => {
      console.log('WebSocket connection closed');
      // Reconnect after 5 seconds
      setTimeout(() => this.connect(), 5000);
    });

    this.ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  }

  subscribe(events) {
    this.send({
      type: 'subscribe',
      events
    });
  }

  on(eventType, handler) {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType).push(handler);
  }

  handleEvent(event) {
    // Call specific event handlers
    const handlers = this.eventHandlers.get(event.type) || [];
    handlers.forEach(handler => handler(event.data, event));

    // Call wildcard handlers
    const wildcardHandlers = this.eventHandlers.get('*') || [];
    wildcardHandlers.forEach(handler => handler(event.data, event));
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
}

// Usage
const processor = new TestEventProcessor(process.env.API_KEY);

// Handle test progress
processor.on('test.progress', (data) => {
  console.log(`Test progress: ${data.completed}/${data.total} (${(data.progress * 100).toFixed(1)}%)`);
});

// Handle test results
processor.on('test.result', (data) => {
  console.log(`Test ${data.testName}: ${data.status} (${data.duration}ms)`);
});

// Handle performance bottlenecks
processor.on('performance.bottleneck', (data) => {
  console.warn(`Performance bottleneck detected: ${data.testName} took ${data.duration}ms`);
  data.suggestions.forEach(suggestion => {
    console.log(`  Suggestion: ${suggestion}`);
  });
});

// Handle all events
processor.on('*', (data, event) => {
  console.log(`Event: ${event.type}`, data);
});
```

### Real-time Test Monitor

```javascript
class RealTimeTestMonitor {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.metrics = {
      tests: { running: 0, completed: 0, failed: 0 },
      performance: { memory: 0, cpu: 0 },
      coverage: { total: 0, progress: 0 }
    };
    this.connect();
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:3000/ws?apiKey=${this.apiKey}`);

    this.ws.onopen = () => {
      this.subscribe([
        'test.progress',
        'test.result',
        'performance.metrics',
        'coverage.progress'
      ]);
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.updateMetrics(data);
      this.displayMetrics();
    };
  }

  subscribe(events) {
    this.ws.send(JSON.stringify({
      type: 'subscribe',
      events
    }));
  }

  updateMetrics(event) {
    switch (event.type) {
      case 'test.progress':
        this.metrics.tests.running = event.data.total - event.data.completed;
        this.metrics.tests.completed = event.data.completed;
        break;

      case 'test.result':
        if (event.data.status === 'failed') {
          this.metrics.tests.failed++;
        }
        break;

      case 'performance.metrics':
        this.metrics.performance.memory = event.data.memory.heapUsed;
        this.metrics.performance.cpu = event.data.cpu.usage;
        break;

      case 'coverage.progress':
        this.metrics.coverage.total = event.data.coverage.statements;
        this.metrics.coverage.progress = event.data.percentage;
        break;
    }
  }

  displayMetrics() {
    // Clear console and display updated metrics
    console.clear();
    console.log('🧪 Test Framework Integrations - Real-time Monitor');
    console.log('================================================');
    console.log('');
    console.log('📊 Test Execution:');
    console.log(`  Running: ${this.metrics.tests.running}`);
    console.log(`  Completed: ${this.metrics.tests.completed}`);
    console.log(`  Failed: ${this.metrics.tests.failed}`);
    console.log('');
    console.log('⚡ Performance:');
    console.log(`  Memory: ${this.metrics.performance.memory.toFixed(1)}MB`);
    console.log(`  CPU: ${this.metrics.performance.cpu.toFixed(1)}%`);
    console.log('');
    console.log('📈 Coverage:');
    console.log(`  Statements: ${this.metrics.coverage.total.toFixed(1)}%`);
    console.log(`  Progress: ${this.metrics.coverage.progress.toFixed(1)}%`);
    console.log('');
  }
}

// Usage
const monitor = new RealTimeTestMonitor(process.env.API_KEY);
```

## 🔐 Security Considerations

### Authentication
- Always use HTTPS/WSS in production
- Validate API keys and JWT tokens on connection
- Implement rate limiting per connection

### Data Privacy
- Sensitive test data is filtered from events
- Personal information is masked or excluded
- Configure event filtering for compliance requirements

### Connection Management
- Implement automatic reconnection with exponential backoff
- Handle connection timeouts gracefully
- Clean up resources on disconnect

## 📚 Additional Resources

- **[WebSocket API Specification](https://tools.ietf.org/html/rfc6455)** - WebSocket protocol specification
- **[Socket.IO Documentation](https://socket.io/docs/)** - Alternative real-time library
- **[Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)** - Alternative to WebSockets