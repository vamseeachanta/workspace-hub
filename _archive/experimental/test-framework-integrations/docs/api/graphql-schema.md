# GraphQL API Documentation

Complete GraphQL schema and operations for Test Framework Integrations.

## 📚 Overview

The GraphQL API provides a flexible alternative to the REST API, allowing clients to:
- Request exactly the data they need
- Get multiple resources in a single request
- Subscribe to real-time updates
- Explore the API with built-in introspection

## 🔗 Endpoints

- **GraphQL Endpoint**: `/graphql`
- **GraphQL Playground**: `/graphql/playground` (development only)
- **Schema Introspection**: Available via GraphQL introspection queries

## 📋 Schema Definition

### Root Types

```graphql
type Query {
  # Framework queries
  frameworks: [Framework!]!
  framework(name: String!): Framework

  # Test queries
  tests: TestDiscovery!
  testResults(filter: TestResultFilter): TestResults

  # Baseline queries
  baselines: [Baseline!]!
  baseline(label: String!): Baseline

  # Coverage queries
  coverageReports: [CoverageReport!]!
  coverageReport(name: String!): CoverageReport

  # Profiling queries
  currentMetrics: PerformanceMetrics
  bottlenecks: BottleneckAnalysis

  # System queries
  health: HealthStatus!
}

type Mutation {
  # Framework mutations
  switchFramework(name: String!): SwitchFrameworkResult!

  # Test mutations
  runTests(input: RunTestsInput!): TestResults!
  runAllFrameworks(input: RunAllFrameworksInput!): MultiFrameworkResults!
  stopTests: StopTestsResult!

  # Baseline mutations
  saveBaseline(input: SaveBaselineInput!): Baseline!
  compareWithBaseline(input: CompareBaselineInput!): BaselineComparison!

  # Coverage mutations
  generateCoverageReport(input: GenerateCoverageReportInput!): CoverageReport!
}

type Subscription {
  # Test execution subscriptions
  testProgress: TestProgress!
  testOutput: TestOutput!

  # Performance monitoring subscriptions
  performanceMetrics: PerformanceMetrics!
  memoryUsage: MemoryMetrics!

  # Coverage subscriptions
  coverageProgress: CoverageProgress!

  # System subscriptions
  systemHealth: HealthStatus!
}
```

### Framework Types

```graphql
type Framework {
  name: String!
  version: String!
  configPath: String
  isActive: Boolean!
  testPatterns: [String!]!
  capabilities: [String!]!
  status: FrameworkStatus!
}

enum FrameworkStatus {
  AVAILABLE
  ACTIVE
  INITIALIZING
  ERROR
  NOT_FOUND
}

type SwitchFrameworkResult {
  success: Boolean!
  framework: Framework
  message: String
  errors: [String!]
}
```

### Test Types

```graphql
type TestDiscovery {
  files: [String!]!
  count: Int!
  framework: String!
  patterns: [String!]!
}

type TestResults {
  framework: FrameworkInfo!
  tests: [TestResult!]!
  summary: TestSummary!
  coverage: CoverageData
  profiling: ProfilingData
  baseline: BaselineComparison
  timestamp: DateTime!
}

type TestResult {
  name: String!
  suite: String
  status: TestStatus!
  duration: Float
  error: String
  file: String
  line: Int
  tags: [String!]
  metadata: JSON
}

enum TestStatus {
  PASSED
  FAILED
  SKIPPED
  PENDING
  RUNNING
}

type TestSummary {
  total: Int!
  passed: Int!
  failed: Int!
  skipped: Int!
  pending: Int!
  duration: Float!
  success: Boolean!
  startTime: DateTime
  endTime: DateTime
}

type MultiFrameworkResults {
  results: [FrameworkResults!]!
  errors: [FrameworkError!]!
  summary: MultiFrameworkSummary!
}

type FrameworkResults {
  framework: String!
  results: TestResults!
}

type FrameworkError {
  framework: String!
  error: String!
  code: String
}

type MultiFrameworkSummary {
  frameworks: FrameworksSummary!
  tests: TestSummary!
  coverage: CoverageData
  duration: Float!
}

type FrameworksSummary {
  total: Int!
  successful: Int!
  failed: Int!
}
```

### Coverage Types

```graphql
type CoverageData {
  total: Float!
  statements: Float!
  branches: Float!
  functions: Float!
  lines: Float!
  files: [FileCoverage!]!
  thresholds: CoverageThresholds
  timestamp: DateTime!
}

type FileCoverage {
  path: String!
  statements: CoverageMetric!
  branches: CoverageMetric!
  functions: CoverageMetric!
  lines: CoverageMetric!
  uncoveredLines: [Int!]!
}

type CoverageMetric {
  total: Int!
  covered: Int!
  percentage: Float!
}

type CoverageThresholds {
  statements: Float
  branches: Float
  functions: Float
  lines: Float
}

type CoverageReport {
  name: String!
  timestamp: DateTime!
  formats: [String!]!
  paths: JSON!
  summary: CoverageData!
  size: Int!
}

type CoverageProgress {
  filesProcessed: Int!
  totalFiles: Int!
  currentFile: String
  percentage: Float!
  timestamp: DateTime!
}
```

### Profiling Types

```graphql
type ProfilingData {
  duration: Float!
  memory: MemoryMetrics!
  cpu: CpuMetrics
  gc: GcMetrics
  tests: [TestProfilingData!]!
  timeline: [ProfileEvent!]!
}

type MemoryMetrics {
  initial: MemorySnapshot!
  peak: MemorySnapshot!
  final: MemorySnapshot!
  leaks: [MemoryLeak!]!
  timeline: [MemoryDataPoint!]!
}

type MemorySnapshot {
  heapUsed: Float!
  heapTotal: Float!
  external: Float!
  rss: Float!
  timestamp: DateTime!
}

type MemoryLeak {
  type: String!
  size: Float!
  location: String!
  stackTrace: [String!]!
}

type MemoryDataPoint {
  timestamp: DateTime!
  heapUsed: Float!
  heapTotal: Float!
  external: Float!
}

type CpuMetrics {
  samples: Int!
  topFunctions: [CpuFunction!]!
  usage: Float!
  utilization: CpuUtilization!
}

type CpuFunction {
  name: String!
  selfTime: Float!
  totalTime: Float!
  percentage: Float!
  calls: Int!
}

type CpuUtilization {
  user: Float!
  system: Float!
  idle: Float!
}

type GcMetrics {
  totalEvents: Int!
  totalTime: Float!
  averageTime: Float!
  maxTime: Float!
  events: [GcEvent!]!
}

type GcEvent {
  type: String!
  duration: Float!
  beforeHeap: Float!
  afterHeap: Float!
  timestamp: DateTime!
}

type TestProfilingData {
  testName: String!
  duration: Float!
  memoryDelta: MemoryDelta!
  cpuUsage: Float!
  gcEvents: Int!
}

type MemoryDelta {
  heapUsed: Float!
  heapTotal: Float!
  external: Float!
}

type ProfileEvent {
  type: String!
  timestamp: DateTime!
  data: JSON!
}

type PerformanceMetrics {
  timestamp: DateTime!
  memory: MemorySnapshot!
  cpu: CpuUtilization!
  uptime: Float!
  gc: GcStatus!
  tests: ActiveTestMetrics
}

type GcStatus {
  recentEvents: Int!
  totalTime: Float!
  lastEventTime: DateTime
}

type ActiveTestMetrics {
  running: Int!
  completed: Int!
  averageDuration: Float!
}

type BottleneckAnalysis {
  slowTests: [SlowTest!]!
  memoryLeaks: [MemoryLeak!]!
  cpuBottlenecks: [CpuBottleneck!]!
  recommendations: [Recommendation!]!
  analysis: AnalysisMetadata!
}

type SlowTest {
  name: String!
  duration: Float!
  memoryDelta: MemoryDelta
  reasons: [String!]!
  suggestions: [String!]!
}

type CpuBottleneck {
  function: String!
  usage: Float!
  duration: Float!
  file: String
  line: Int
}

type Recommendation {
  severity: Severity!
  category: RecommendationCategory!
  message: String!
  suggestion: String!
  impact: String
  effort: String
}

enum Severity {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

enum RecommendationCategory {
  PERFORMANCE
  MEMORY
  CPU
  TESTING
  CONFIGURATION
}

type AnalysisMetadata {
  timestamp: DateTime!
  duration: Float!
  dataPoints: Int!
  confidence: Float!
}
```

### Baseline Types

```graphql
type Baseline {
  label: String!
  timestamp: DateTime!
  framework: FrameworkInfo!
  results: BaselineResults!
  metadata: JSON
  size: Int!
}

type BaselineResults {
  tests: [TestResult!]!
  summary: TestSummary!
  coverage: CoverageData
  profiling: ProfilingData
}

type BaselineComparison {
  testsAdded: [TestResult!]!
  testsRemoved: [TestResult!]!
  testsChanged: [TestChange!]!
  performance: PerformanceComparison!
  coverage: CoverageComparison!
  overall: ComparisonSummary!
}

type TestChange {
  name: String!
  from: TestStatus!
  to: TestStatus!
  durationChange: Float
}

type PerformanceComparison {
  faster: [PerformanceChange!]!
  slower: [PerformanceChange!]!
  unchanged: [String!]!
  avgChange: Float!
  significantChanges: [PerformanceChange!]!
}

type PerformanceChange {
  name: String!
  baselineDuration: Float!
  currentDuration: Float!
  change: Float!
  percentage: Float!
  significance: Significance!
}

enum Significance {
  MINOR
  MODERATE
  MAJOR
  CRITICAL
}

type CoverageComparison {
  improved: Boolean!
  degraded: Boolean!
  change: Float!
  details: CoverageChangeDetails!
}

type CoverageChangeDetails {
  statements: Float!
  branches: Float!
  functions: Float!
  lines: Float!
  fileChanges: [FileCoverageChange!]!
}

type FileCoverageChange {
  path: String!
  change: Float!
  from: Float!
  to: Float!
}

type ComparisonSummary {
  regression: Boolean!
  improvement: Boolean!
  stability: Float!
  score: Float!
  recommendations: [String!]!
}
```

### System Types

```graphql
type HealthStatus {
  status: HealthLevel!
  timestamp: DateTime!
  version: String!
  uptime: Float!
  components: [ComponentHealth!]!
  metrics: SystemMetrics!
}

enum HealthLevel {
  HEALTHY
  DEGRADED
  DOWN
}

type ComponentHealth {
  name: String!
  status: HealthLevel!
  message: String
  lastCheck: DateTime!
}

type SystemMetrics {
  memory: SystemMemory!
  cpu: SystemCpu!
  disk: SystemDisk!
  network: SystemNetwork!
}

type SystemMemory {
  total: Float!
  used: Float!
  free: Float!
  percentage: Float!
}

type SystemCpu {
  cores: Int!
  usage: Float!
  load: [Float!]!
}

type SystemDisk {
  total: Float!
  used: Float!
  free: Float!
  percentage: Float!
}

type SystemNetwork {
  bytesIn: Float!
  bytesOut: Float!
  packetsIn: Int!
  packetsOut: Int!
}
```

### Input Types

```graphql
input RunTestsInput {
  framework: String
  coverage: Boolean = false
  profiling: Boolean = false
  baseline: String
  parallel: Boolean = false
  bail: Boolean = false
  verbose: Boolean = false
  timeout: Int
  retries: Int
  testPattern: String
  tags: [String!]
  environment: JSON
}

input RunAllFrameworksInput {
  coverage: Boolean = false
  profiling: Boolean = false
  parallel: Boolean = false
  frameworks: [String!]
  timeout: Int
}

input SaveBaselineInput {
  label: String!
  results: TestResultsInput!
  metadata: JSON
}

input TestResultsInput {
  framework: FrameworkInfoInput!
  tests: [TestResultInput!]!
  summary: TestSummaryInput!
  coverage: CoverageDataInput
  profiling: ProfilingDataInput
}

input FrameworkInfoInput {
  name: String!
  version: String!
  adapter: String!
}

input TestResultInput {
  name: String!
  suite: String
  status: TestStatus!
  duration: Float
  error: String
  file: String
  line: Int
}

input TestSummaryInput {
  total: Int!
  passed: Int!
  failed: Int!
  skipped: Int!
  pending: Int!
  duration: Float!
  success: Boolean!
}

input CoverageDataInput {
  total: Float!
  statements: Float!
  branches: Float!
  functions: Float!
  lines: Float!
  files: [FileCoverageInput!]!
}

input FileCoverageInput {
  path: String!
  statements: CoverageMetricInput!
  branches: CoverageMetricInput!
  functions: CoverageMetricInput!
  lines: CoverageMetricInput!
}

input CoverageMetricInput {
  total: Int!
  covered: Int!
  percentage: Float!
}

input ProfilingDataInput {
  duration: Float!
  memory: MemoryMetricsInput!
  cpu: CpuMetricsInput
  gc: GcMetricsInput
}

input MemoryMetricsInput {
  initial: MemorySnapshotInput!
  peak: MemorySnapshotInput!
  final: MemorySnapshotInput!
}

input MemorySnapshotInput {
  heapUsed: Float!
  heapTotal: Float!
  external: Float!
  rss: Float!
}

input CpuMetricsInput {
  samples: Int!
  usage: Float!
}

input GcMetricsInput {
  totalEvents: Int!
  totalTime: Float!
  averageTime: Float!
  maxTime: Float!
}

input CompareBaselineInput {
  label: String!
  results: TestResultsInput!
}

input GenerateCoverageReportInput {
  name: String!
  formats: [String!]!
  coverage: CoverageDataInput!
}

input TestResultFilter {
  status: TestStatus
  suite: String
  framework: String
  tags: [String!]
  dateRange: DateRangeInput
}

input DateRangeInput {
  from: DateTime!
  to: DateTime!
}
```

### Scalar Types

```graphql
scalar DateTime
scalar JSON
```

### Subscription Types

```graphql
type TestProgress {
  testName: String!
  status: TestStatus!
  progress: Float!
  timestamp: DateTime!
  suite: String
  duration: Float
}

type TestOutput {
  testName: String!
  output: String!
  type: OutputType!
  timestamp: DateTime!
}

enum OutputType {
  STDOUT
  STDERR
  LOG
  ERROR
}
```

## 🚀 Usage Examples

### Query Examples

#### Get All Frameworks

```graphql
query GetFrameworks {
  frameworks {
    name
    version
    isActive
    testPatterns
    capabilities
    status
  }
}
```

#### Get Test Results with Coverage

```graphql
query GetTestResults($filter: TestResultFilter) {
  testResults(filter: $filter) {
    framework {
      name
      version
    }
    summary {
      total
      passed
      failed
      duration
      success
    }
    coverage {
      total
      statements
      branches
      functions
      lines
      files {
        path
        statements {
          percentage
        }
      }
    }
    tests {
      name
      status
      duration
      file
    }
  }
}
```

#### Get Performance Bottlenecks

```graphql
query GetBottlenecks {
  bottlenecks {
    slowTests {
      name
      duration
      reasons
      suggestions
    }
    memoryLeaks {
      type
      size
      location
    }
    recommendations {
      severity
      category
      message
      suggestion
    }
  }
}
```

#### Get Baseline Comparison

```graphql
query GetBaseline($label: String!) {
  baseline(label: $label) {
    label
    timestamp
    framework {
      name
      version
    }
    results {
      summary {
        total
        passed
        failed
        duration
      }
      coverage {
        total
      }
    }
  }
}
```

### Mutation Examples

#### Run Tests

```graphql
mutation RunTests($input: RunTestsInput!) {
  runTests(input: $input) {
    framework {
      name
      version
    }
    summary {
      total
      passed
      failed
      duration
      success
    }
    coverage {
      total
      statements
      branches
      functions
      lines
    }
    profiling {
      duration
      memory {
        peak {
          heapUsed
          heapTotal
        }
      }
    }
  }
}
```

Variables:
```json
{
  "input": {
    "coverage": true,
    "profiling": true,
    "verbose": true,
    "timeout": 30000
  }
}
```

#### Switch Framework

```graphql
mutation SwitchFramework($name: String!) {
  switchFramework(name: $name) {
    success
    framework {
      name
      version
      isActive
    }
    message
    errors
  }
}
```

Variables:
```json
{
  "name": "jest"
}
```

#### Save Baseline

```graphql
mutation SaveBaseline($input: SaveBaselineInput!) {
  saveBaseline(input: $input) {
    label
    timestamp
    framework {
      name
      version
    }
    results {
      summary {
        total
        passed
        failed
      }
    }
  }
}
```

#### Compare with Baseline

```graphql
mutation CompareWithBaseline($input: CompareBaselineInput!) {
  compareWithBaseline(input: $input) {
    testsAdded {
      name
      status
    }
    testsRemoved {
      name
    }
    testsChanged {
      name
      from
      to
    }
    performance {
      faster {
        name
        change
        percentage
      }
      slower {
        name
        change
        percentage
      }
      avgChange
    }
    coverage {
      improved
      degraded
      change
    }
    overall {
      regression
      improvement
      score
      recommendations
    }
  }
}
```

### Subscription Examples

#### Subscribe to Test Progress

```graphql
subscription TestProgress {
  testProgress {
    testName
    status
    progress
    timestamp
    suite
    duration
  }
}
```

#### Subscribe to Performance Metrics

```graphql
subscription PerformanceMetrics {
  performanceMetrics {
    timestamp
    memory {
      heapUsed
      heapTotal
      rss
    }
    cpu {
      user
      system
      idle
    }
    uptime
    gc {
      recentEvents
      totalTime
    }
  }
}
```

#### Subscribe to Test Output

```graphql
subscription TestOutput {
  testOutput {
    testName
    output
    type
    timestamp
  }
}
```

## 🎯 Advanced Usage Patterns

### Complex Query with Fragments

```graphql
fragment TestSummaryFields on TestSummary {
  total
  passed
  failed
  skipped
  duration
  success
}

fragment CoverageFields on CoverageData {
  total
  statements
  branches
  functions
  lines
}

query CompleteTestAnalysis($filter: TestResultFilter) {
  testResults(filter: $filter) {
    framework {
      name
      version
    }
    summary {
      ...TestSummaryFields
    }
    coverage {
      ...CoverageFields
      files {
        path
        statements {
          percentage
        }
      }
    }
    profiling {
      duration
      memory {
        peak {
          heapUsed
        }
      }
    }
  }

  bottlenecks {
    slowTests {
      name
      duration
      reasons
    }
    recommendations {
      severity
      message
      suggestion
    }
  }
}
```

### Batch Operations

```graphql
mutation BatchOperations($testInput: RunTestsInput!, $baselineLabel: String!) {
  # Run tests
  testResults: runTests(input: $testInput) {
    summary {
      total
      passed
      failed
    }
    coverage {
      total
    }
  }

  # Switch to different framework
  switchResult: switchFramework(name: "jest") {
    success
    framework {
      name
    }
  }
}
```

### Real-time Dashboard Query

```graphql
query Dashboard {
  frameworks {
    name
    version
    isActive
    status
  }

  testResults {
    summary {
      total
      passed
      failed
      duration
    }
    coverage {
      total
    }
  }

  currentMetrics {
    memory {
      heapUsed
      heapTotal
    }
    cpu {
      usage
    }
    uptime
  }

  health {
    status
    components {
      name
      status
    }
  }
}
```

## 🔐 Authentication

### Query with Authentication

```javascript
const query = `
  query GetFrameworks {
    frameworks {
      name
      version
      isActive
    }
  }
`;

const response = await fetch('/graphql', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-jwt-token',
    // or
    'X-API-Key': 'your-api-key'
  },
  body: JSON.stringify({ query })
});
```

## 🔍 Introspection

### Get Schema Information

```graphql
query IntrospectionQuery {
  __schema {
    types {
      name
      kind
      description
    }
    queryType {
      name
    }
    mutationType {
      name
    }
    subscriptionType {
      name
    }
  }
}
```

### Get Type Information

```graphql
query GetTestResultType {
  __type(name: "TestResult") {
    name
    fields {
      name
      type {
        name
        kind
      }
      description
    }
  }
}
```

## 🛠️ Development Tools

### GraphQL Playground

Access the interactive GraphQL Playground at `/graphql/playground` during development:

1. **Schema Explorer**: Browse the complete schema
2. **Query Builder**: Build queries with autocomplete
3. **Real-time Testing**: Execute queries and mutations
4. **Subscription Testing**: Test real-time subscriptions

### Client Libraries

#### Apollo Client (React)

```javascript
import { ApolloClient, InMemoryCache, gql, useQuery } from '@apollo/client';

const client = new ApolloClient({
  uri: '/graphql',
  cache: new InMemoryCache(),
  headers: {
    'Authorization': 'Bearer your-token'
  }
});

const GET_FRAMEWORKS = gql`
  query GetFrameworks {
    frameworks {
      name
      version
      isActive
    }
  }
`;

function FrameworksList() {
  const { loading, error, data } = useQuery(GET_FRAMEWORKS);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <ul>
      {data.frameworks.map(framework => (
        <li key={framework.name}>
          {framework.name} v{framework.version}
          {framework.isActive && ' (Active)'}
        </li>
      ))}
    </ul>
  );
}
```

#### Relay (React)

```javascript
import { graphql, useQuery } from 'react-relay';

const FrameworksQuery = graphql`
  query FrameworksQuery {
    frameworks {
      name
      version
      isActive
    }
  }
`;

function FrameworksList() {
  const data = useQuery(FrameworksQuery, {});

  return (
    <ul>
      {data.frameworks.map(framework => (
        <li key={framework.name}>
          {framework.name} v{framework.version}
        </li>
      ))}
    </ul>
  );
}
```

#### Generic JavaScript

```javascript
async function executeGraphQL(query, variables = {}) {
  const response = await fetch('/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer your-token'
    },
    body: JSON.stringify({
      query,
      variables
    })
  });

  const { data, errors } = await response.json();

  if (errors) {
    throw new Error(errors[0].message);
  }

  return data;
}

// Usage
const frameworks = await executeGraphQL(`
  query {
    frameworks {
      name
      version
      isActive
    }
  }
`);
```

## 📚 Additional Resources

- **[GraphQL Specification](https://spec.graphql.org/)** - Official GraphQL specification
- **[Apollo Documentation](https://www.apollographql.com/docs/)** - Apollo Client and Server docs
- **[Relay Documentation](https://relay.dev/)** - Facebook's GraphQL client
- **[GraphQL Best Practices](https://graphql.org/learn/best-practices/)** - GraphQL best practices guide