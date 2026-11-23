# API Layer for External Integrations

## API Architecture Overview

The Test Baseline Tracking System provides a comprehensive RESTful API layer with GraphQL support, enabling seamless integration with external tools, custom dashboards, and third-party services.

## API Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐│
│  │   REST API  │  │   GraphQL   │  │  Webhook    │  │ Real-time││
│  │  Endpoints  │  │    API      │  │   Server    │  │WebSocket ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘│
│         │               │               │               │       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Authentication & Authorization                 ││
│  └─────────────────────────────────────────────────────────────┘│
│                            │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  Rate Limiting & Validation                ││
│  └─────────────────────────────────────────────────────────────┘│
│                            │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   Business Logic Layer                     ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 1. RESTful API Design

### Core API Endpoints
```javascript
// api-routes.js
const express = require('express');
const router = express.Router();

// ============================================================================
// PROJECTS API
// ============================================================================

/**
 * @swagger
 * /api/v1/projects:
 *   get:
 *     summary: List all projects
 *     tags: [Projects]
 *     parameters:
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 50
 *       - in: query
 *         name: offset
 *         schema:
 *           type: integer
 *           default: 0
 *     responses:
 *       200:
 *         description: List of projects
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 projects:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/Project'
 *                 pagination:
 *                   $ref: '#/components/schemas/Pagination'
 */
router.get('/projects', async (req, res) => {
  const { limit = 50, offset = 0 } = req.query;
  const projects = await projectService.listProjects(limit, offset);
  res.json(projects);
});

/**
 * @swagger
 * /api/v1/projects/{projectId}:
 *   get:
 *     summary: Get project details
 *     tags: [Projects]
 *     parameters:
 *       - in: path
 *         name: projectId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Project details
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Project'
 */
router.get('/projects/:projectId', async (req, res) => {
  const project = await projectService.getProject(req.params.projectId);
  if (!project) {
    return res.status(404).json({ error: 'Project not found' });
  }
  res.json(project);
});

// ============================================================================
// BASELINES API
// ============================================================================

/**
 * @swagger
 * /api/v1/projects/{projectId}/baselines:
 *   get:
 *     summary: List baselines for a project
 *     tags: [Baselines]
 *     parameters:
 *       - in: path
 *         name: projectId
 *         required: true
 *         schema:
 *           type: string
 *       - in: query
 *         name: branch
 *         schema:
 *           type: string
 *       - in: query
 *         name: environment
 *         schema:
 *           type: string
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 20
 *     responses:
 *       200:
 *         description: List of baselines
 */
router.get('/projects/:projectId/baselines', async (req, res) => {
  const { branch, environment, limit = 20 } = req.query;
  const baselines = await baselineService.listBaselines(
    req.params.projectId,
    { branch, environment, limit }
  );
  res.json(baselines);
});

/**
 * @swagger
 * /api/v1/projects/{projectId}/baselines:
 *   post:
 *     summary: Create a new baseline
 *     tags: [Baselines]
 *     parameters:
 *       - in: path
 *         name: projectId
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/CreateBaselineRequest'
 *     responses:
 *       201:
 *         description: Baseline created
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Baseline'
 */
router.post('/projects/:projectId/baselines', async (req, res) => {
  try {
    const baseline = await baselineService.createBaseline(
      req.params.projectId,
      req.body
    );
    res.status(201).json(baseline);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

/**
 * @swagger
 * /api/v1/baselines/{baselineId}:
 *   get:
 *     summary: Get baseline details
 *     tags: [Baselines]
 *     parameters:
 *       - in: path
 *         name: baselineId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Baseline details
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Baseline'
 */
router.get('/baselines/:baselineId', async (req, res) => {
  const baseline = await baselineService.getBaseline(req.params.baselineId);
  if (!baseline) {
    return res.status(404).json({ error: 'Baseline not found' });
  }
  res.json(baseline);
});

// ============================================================================
// METRICS API
// ============================================================================

/**
 * @swagger
 * /api/v1/baselines/{baselineId}/metrics:
 *   post:
 *     summary: Submit metrics for a baseline
 *     tags: [Metrics]
 *     parameters:
 *       - in: path
 *         name: baselineId
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/MetricsData'
 *     responses:
 *       200:
 *         description: Metrics submitted successfully
 */
router.post('/baselines/:baselineId/metrics', async (req, res) => {
  try {
    const result = await metricsService.submitMetrics(
      req.params.baselineId,
      req.body
    );
    res.json(result);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

/**
 * @swagger
 * /api/v1/baselines/{baselineId}/metrics:
 *   get:
 *     summary: Get metrics for a baseline
 *     tags: [Metrics]
 *     parameters:
 *       - in: path
 *         name: baselineId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Baseline metrics
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/MetricsData'
 */
router.get('/baselines/:baselineId/metrics', async (req, res) => {
  const metrics = await metricsService.getMetrics(req.params.baselineId);
  if (!metrics) {
    return res.status(404).json({ error: 'Metrics not found' });
  }
  res.json(metrics);
});

// ============================================================================
// COMPARISON API
// ============================================================================

/**
 * @swagger
 * /api/v1/baselines/{baselineId}/compare:
 *   post:
 *     summary: Compare baseline with another baseline or current metrics
 *     tags: [Comparison]
 *     parameters:
 *       - in: path
 *         name: baselineId
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/ComparisonRequest'
 *     responses:
 *       200:
 *         description: Comparison results
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ComparisonResult'
 */
router.post('/baselines/:baselineId/compare', async (req, res) => {
  try {
    const result = await comparisonService.compareBaselines(
      req.params.baselineId,
      req.body
    );
    res.json(result);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// ============================================================================
// TRENDS API
// ============================================================================

/**
 * @swagger
 * /api/v1/projects/{projectId}/trends:
 *   get:
 *     summary: Get trend analysis for a project
 *     tags: [Trends]
 *     parameters:
 *       - in: path
 *         name: projectId
 *         required: true
 *         schema:
 *           type: string
 *       - in: query
 *         name: branch
 *         schema:
 *           type: string
 *       - in: query
 *         name: environment
 *         schema:
 *           type: string
 *       - in: query
 *         name: timeframe
 *         schema:
 *           type: string
 *           enum: [7d, 30d, 90d]
 *           default: 30d
 *       - in: query
 *         name: metrics
 *         schema:
 *           type: array
 *           items:
 *             type: string
 *     responses:
 *       200:
 *         description: Trend analysis results
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/TrendAnalysis'
 */
router.get('/projects/:projectId/trends', async (req, res) => {
  const { branch, environment, timeframe = '30d', metrics } = req.query;
  const trends = await trendsService.getTrends(
    req.params.projectId,
    { branch, environment, timeframe, metrics }
  );
  res.json(trends);
});

// ============================================================================
// ALERTS API
// ============================================================================

/**
 * @swagger
 * /api/v1/projects/{projectId}/alerts:
 *   get:
 *     summary: Get alerts for a project
 *     tags: [Alerts]
 *     parameters:
 *       - in: path
 *         name: projectId
 *         required: true
 *         schema:
 *           type: string
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *           enum: [active, resolved, all]
 *           default: active
 *       - in: query
 *         name: severity
 *         schema:
 *           type: string
 *           enum: [critical, major, minor, info]
 *     responses:
 *       200:
 *         description: List of alerts
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 alerts:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/Alert'
 */
router.get('/projects/:projectId/alerts', async (req, res) => {
  const { status = 'active', severity } = req.query;
  const alerts = await alertService.getAlerts(
    req.params.projectId,
    { status, severity }
  );
  res.json({ alerts });
});

/**
 * @swagger
 * /api/v1/alerts/{alertId}:
 *   patch:
 *     summary: Update alert status
 *     tags: [Alerts]
 *     parameters:
 *       - in: path
 *         name: alertId
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               status:
 *                 type: string
 *                 enum: [acknowledged, resolved]
 *               note:
 *                 type: string
 *     responses:
 *       200:
 *         description: Alert updated
 */
router.patch('/alerts/:alertId', async (req, res) => {
  try {
    const alert = await alertService.updateAlert(
      req.params.alertId,
      req.body
    );
    res.json(alert);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

module.exports = router;
```

### API Data Models
```javascript
// api-schemas.js

/**
 * @swagger
 * components:
 *   schemas:
 *     Project:
 *       type: object
 *       properties:
 *         id:
 *           type: string
 *         name:
 *           type: string
 *         description:
 *           type: string
 *         framework:
 *           type: string
 *           enum: [jest, mocha, pytest, custom]
 *         created_at:
 *           type: string
 *           format: date-time
 *         updated_at:
 *           type: string
 *           format: date-time
 *         settings:
 *           type: object
 *           properties:
 *             default_branch:
 *               type: string
 *             environments:
 *               type: array
 *               items:
 *                 type: string
 *             thresholds:
 *               $ref: '#/components/schemas/ThresholdConfig'
 *
 *     Baseline:
 *       type: object
 *       properties:
 *         id:
 *           type: string
 *         project_id:
 *           type: string
 *         branch:
 *           type: string
 *         environment:
 *           type: string
 *         commit_hash:
 *           type: string
 *         build_number:
 *           type: string
 *         created_at:
 *           type: string
 *           format: date-time
 *         metrics:
 *           $ref: '#/components/schemas/MetricsData'
 *         tags:
 *           type: array
 *           items:
 *             type: string
 *
 *     MetricsData:
 *       type: object
 *       properties:
 *         execution:
 *           type: object
 *           properties:
 *             total_tests:
 *               type: integer
 *             passed_tests:
 *               type: integer
 *             failed_tests:
 *               type: integer
 *             skipped_tests:
 *               type: integer
 *             pass_rate_percentage:
 *               type: number
 *             total_execution_time_ms:
 *               type: integer
 *             average_test_duration_ms:
 *               type: number
 *         coverage:
 *           type: object
 *           properties:
 *             overall:
 *               type: object
 *               properties:
 *                 line_coverage:
 *                   type: number
 *                 branch_coverage:
 *                   type: number
 *                 function_coverage:
 *                   type: number
 *                 statement_coverage:
 *                   type: number
 *             by_file:
 *               type: object
 *               additionalProperties:
 *                 type: object
 *         performance:
 *           type: object
 *           properties:
 *             memory_usage:
 *               type: object
 *               properties:
 *                 peak_memory_mb:
 *                   type: number
 *                 average_memory_mb:
 *                   type: number
 *             timing:
 *               type: object
 *         quality:
 *           type: object
 *           properties:
 *             flaky_tests:
 *               type: array
 *               items:
 *                 type: object
 *             stability_score:
 *               type: number
 *
 *     ComparisonRequest:
 *       type: object
 *       properties:
 *         compare_with:
 *           type: string
 *           enum: [baseline, current_metrics]
 *         target_baseline_id:
 *           type: string
 *         current_metrics:
 *           $ref: '#/components/schemas/MetricsData'
 *         gate_type:
 *           type: string
 *           enum: [development, quality_gate, release_gate]
 *         context:
 *           type: object
 *           properties:
 *             branch:
 *               type: string
 *             environment:
 *               type: string
 *             commit:
 *               type: string
 *
 *     ComparisonResult:
 *       type: object
 *       properties:
 *         summary:
 *           type: object
 *           properties:
 *             overall_result:
 *               type: string
 *               enum: [passed, passed_with_improvements, warning, failed]
 *             gate_type:
 *               type: string
 *             issues_count:
 *               type: object
 *               properties:
 *                 blocking:
 *                   type: integer
 *                 non_blocking:
 *                   type: integer
 *         detailed_analysis:
 *           type: object
 *         recommendations:
 *           type: array
 *           items:
 *             type: object
 *         improvements:
 *           type: array
 *           items:
 *             type: object
 *
 *     ThresholdConfig:
 *       type: object
 *       properties:
 *         execution:
 *           type: object
 *         coverage:
 *           type: object
 *         performance:
 *           type: object
 *         quality:
 *           type: object
 *
 *     Alert:
 *       type: object
 *       properties:
 *         id:
 *           type: string
 *         title:
 *           type: string
 *         message:
 *           type: string
 *         severity:
 *           type: string
 *           enum: [critical, major, minor, info]
 *         status:
 *           type: string
 *           enum: [active, acknowledged, resolved]
 *         triggered_at:
 *           type: string
 *           format: date-time
 *         resolved_at:
 *           type: string
 *           format: date-time
 *         context:
 *           type: object
 *           properties:
 *             project:
 *               type: string
 *             branch:
 *               type: string
 *             environment:
 *               type: string
 *
 *     TrendAnalysis:
 *       type: object
 *       properties:
 *         timeframe:
 *           type: string
 *         metrics:
 *           type: object
 *         trends:
 *           type: object
 *         forecasts:
 *           type: object
 *         change_points:
 *           type: array
 *           items:
 *             type: object
 *
 *     Pagination:
 *       type: object
 *       properties:
 *         total:
 *           type: integer
 *         limit:
 *           type: integer
 *         offset:
 *           type: integer
 *         has_more:
 *           type: boolean
 */
```

## 2. GraphQL API

### GraphQL Schema Definition
```graphql
# schema.graphql

scalar DateTime
scalar JSON

type Query {
  # Projects
  projects(limit: Int = 50, offset: Int = 0): ProjectConnection!
  project(id: ID!): Project

  # Baselines
  baselines(
    projectId: ID!
    branch: String
    environment: String
    limit: Int = 20
    offset: Int = 0
  ): BaselineConnection!

  baseline(id: ID!): Baseline

  # Metrics
  metrics(baselineId: ID!): MetricsData

  # Trends
  trends(
    projectId: ID!
    branch: String
    environment: String
    timeframe: Timeframe = THIRTY_DAYS
    metrics: [String!]
  ): TrendAnalysis!

  # Alerts
  alerts(
    projectId: ID!
    status: AlertStatus = ACTIVE
    severity: AlertSeverity
    limit: Int = 50
    offset: Int = 0
  ): AlertConnection!

  # Search
  search(
    query: String!
    type: SearchType
    limit: Int = 20
  ): SearchResults!
}

type Mutation {
  # Projects
  createProject(input: CreateProjectInput!): Project!
  updateProject(id: ID!, input: UpdateProjectInput!): Project!
  deleteProject(id: ID!): Boolean!

  # Baselines
  createBaseline(input: CreateBaselineInput!): Baseline!
  updateBaseline(id: ID!, input: UpdateBaselineInput!): Baseline!
  deleteBaseline(id: ID!): Boolean!

  # Metrics
  submitMetrics(baselineId: ID!, metrics: MetricsInput!): SubmitMetricsResult!

  # Comparison
  compareBaselines(input: ComparisonInput!): ComparisonResult!

  # Alerts
  updateAlert(id: ID!, input: UpdateAlertInput!): Alert!
  acknowledgeAlert(id: ID!, note: String): Alert!
  resolveAlert(id: ID!, note: String): Alert!

  # Thresholds
  updateThresholds(projectId: ID!, input: ThresholdConfigInput!): ThresholdConfig!
}

type Subscription {
  # Real-time metrics
  metricsUpdated(projectId: ID!, branch: String, environment: String): MetricsData!

  # Alert notifications
  alertTriggered(projectId: ID!): Alert!
  alertResolved(projectId: ID!): Alert!

  # Comparison results
  comparisonCompleted(projectId: ID!): ComparisonResult!
}

# Types
type Project {
  id: ID!
  name: String!
  description: String
  framework: TestFramework!
  createdAt: DateTime!
  updatedAt: DateTime!
  settings: ProjectSettings!
  baselines(
    branch: String
    environment: String
    limit: Int = 20
    offset: Int = 0
  ): BaselineConnection!
  alerts(
    status: AlertStatus = ACTIVE
    severity: AlertSeverity
    limit: Int = 20
  ): AlertConnection!
  trends(
    branch: String
    environment: String
    timeframe: Timeframe = THIRTY_DAYS
  ): TrendAnalysis!
}

type ProjectSettings {
  defaultBranch: String!
  environments: [String!]!
  thresholds: ThresholdConfig!
  notifications: NotificationConfig!
}

type Baseline {
  id: ID!
  projectId: ID!
  project: Project!
  branch: String!
  environment: String!
  commitHash: String
  buildNumber: String
  createdAt: DateTime!
  metrics: MetricsData
  tags: [String!]!
  comparisons: [ComparisonResult!]!
}

type MetricsData {
  execution: ExecutionMetrics!
  coverage: CoverageMetrics
  performance: PerformanceMetrics
  quality: QualityMetrics
}

type ExecutionMetrics {
  totalTests: Int!
  passedTests: Int!
  failedTests: Int!
  skippedTests: Int!
  passRatePercentage: Float!
  totalExecutionTimeMs: Int!
  averageTestDurationMs: Float!
  slowestTests: [TestResult!]!
  fastestTests: [TestResult!]!
}

type CoverageMetrics {
  overall: CoverageData!
  byFile: JSON!
  uncoveredLines: [UncoveredLine!]!
}

type CoverageData {
  lineCoverage: Float!
  branchCoverage: Float!
  functionCoverage: Float!
  statementCoverage: Float!
}

type PerformanceMetrics {
  memoryUsage: MemoryMetrics!
  timing: TimingMetrics!
  benchmarks: JSON!
}

type QualityMetrics {
  flakyTests: [FlakyTest!]!
  newTests: [TestInfo!]!
  deletedTests: [TestInfo!]!
  stabilityScore: Float!
  complexity: JSON!
}

type Alert {
  id: ID!
  title: String!
  message: String!
  severity: AlertSeverity!
  status: AlertStatus!
  triggeredAt: DateTime!
  resolvedAt: DateTime
  acknowledgedAt: DateTime
  context: AlertContext!
  evaluation: JSON
  project: Project!
}

type TrendAnalysis {
  timeframe: String!
  metrics: JSON!
  trends: JSON!
  forecasts: JSON!
  changePoints: [ChangePoint!]!
  patterns: [Pattern!]!
}

type ComparisonResult {
  id: ID!
  summary: ComparisonSummary!
  detailedAnalysis: JSON!
  recommendations: [Recommendation!]!
  improvements: [Improvement!]!
  rawData: JSON!
  createdAt: DateTime!
}

# Enums
enum TestFramework {
  JEST
  MOCHA
  PYTEST
  CUSTOM
}

enum AlertSeverity {
  CRITICAL
  MAJOR
  MINOR
  INFO
}

enum AlertStatus {
  ACTIVE
  ACKNOWLEDGED
  RESOLVED
}

enum Timeframe {
  SEVEN_DAYS
  THIRTY_DAYS
  NINETY_DAYS
}

enum SearchType {
  PROJECTS
  BASELINES
  ALERTS
  ALL
}

# Input Types
input CreateProjectInput {
  name: String!
  description: String
  framework: TestFramework!
  settings: ProjectSettingsInput
}

input UpdateProjectInput {
  name: String
  description: String
  settings: ProjectSettingsInput
}

input CreateBaselineInput {
  projectId: ID!
  branch: String!
  environment: String!
  commitHash: String
  buildNumber: String
  metrics: MetricsInput
  tags: [String!]
}

input MetricsInput {
  execution: ExecutionMetricsInput!
  coverage: CoverageMetricsInput
  performance: PerformanceMetricsInput
  quality: QualityMetricsInput
}

input ComparisonInput {
  baselineId: ID!
  compareWith: CompareWith!
  targetBaselineId: ID
  currentMetrics: MetricsInput
  gateType: GateType!
  context: ComparisonContextInput!
}

# Connection Types
type ProjectConnection {
  edges: [ProjectEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type ProjectEdge {
  node: Project!
  cursor: String!
}

type BaselineConnection {
  edges: [BaselineEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type BaselineEdge {
  node: Baseline!
  cursor: String!
}

type AlertConnection {
  edges: [AlertEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type AlertEdge {
  node: Alert!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

### GraphQL Resolvers
```javascript
// graphql-resolvers.js
const { PubSub } = require('graphql-subscriptions');

const pubsub = new PubSub();

const resolvers = {
  Query: {
    projects: async (_, { limit, offset }, { dataSources }) => {
      return await dataSources.projectAPI.getProjects(limit, offset);
    },

    project: async (_, { id }, { dataSources }) => {
      return await dataSources.projectAPI.getProject(id);
    },

    baselines: async (_, args, { dataSources }) => {
      return await dataSources.baselineAPI.getBaselines(args);
    },

    baseline: async (_, { id }, { dataSources }) => {
      return await dataSources.baselineAPI.getBaseline(id);
    },

    metrics: async (_, { baselineId }, { dataSources }) => {
      return await dataSources.metricsAPI.getMetrics(baselineId);
    },

    trends: async (_, args, { dataSources }) => {
      return await dataSources.trendsAPI.getTrends(args);
    },

    alerts: async (_, args, { dataSources }) => {
      return await dataSources.alertAPI.getAlerts(args);
    },

    search: async (_, { query, type, limit }, { dataSources }) => {
      return await dataSources.searchAPI.search(query, type, limit);
    }
  },

  Mutation: {
    createProject: async (_, { input }, { dataSources, user }) => {
      const project = await dataSources.projectAPI.createProject(input, user);

      // Publish event for real-time updates
      pubsub.publish('PROJECT_CREATED', { projectCreated: project });

      return project;
    },

    submitMetrics: async (_, { baselineId, metrics }, { dataSources, user }) => {
      const result = await dataSources.metricsAPI.submitMetrics(
        baselineId,
        metrics,
        user
      );

      // Publish real-time update
      pubsub.publish('METRICS_UPDATED', {
        metricsUpdated: result.metrics,
        projectId: result.projectId,
        branch: result.branch,
        environment: result.environment
      });

      return result;
    },

    compareBaselines: async (_, { input }, { dataSources, user }) => {
      const result = await dataSources.comparisonAPI.compareBaselines(input, user);

      // Publish comparison completion
      pubsub.publish('COMPARISON_COMPLETED', {
        comparisonCompleted: result,
        projectId: input.projectId
      });

      return result;
    },

    updateAlert: async (_, { id, input }, { dataSources, user }) => {
      const alert = await dataSources.alertAPI.updateAlert(id, input, user);

      if (input.status === 'RESOLVED') {
        pubsub.publish('ALERT_RESOLVED', {
          alertResolved: alert,
          projectId: alert.projectId
        });
      }

      return alert;
    }
  },

  Subscription: {
    metricsUpdated: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(['METRICS_UPDATED']),
        (payload, variables) => {
          return payload.projectId === variables.projectId &&
                 (!variables.branch || payload.branch === variables.branch) &&
                 (!variables.environment || payload.environment === variables.environment);
        }
      )
    },

    alertTriggered: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(['ALERT_TRIGGERED']),
        (payload, variables) => {
          return payload.alertTriggered.projectId === variables.projectId;
        }
      )
    },

    alertResolved: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(['ALERT_RESOLVED']),
        (payload, variables) => {
          return payload.alertResolved.projectId === variables.projectId;
        }
      )
    },

    comparisonCompleted: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(['COMPARISON_COMPLETED']),
        (payload, variables) => {
          return payload.projectId === variables.projectId;
        }
      )
    }
  },

  // Field resolvers
  Project: {
    baselines: async (project, args, { dataSources }) => {
      return await dataSources.baselineAPI.getBaselines({
        projectId: project.id,
        ...args
      });
    },

    alerts: async (project, args, { dataSources }) => {
      return await dataSources.alertAPI.getAlerts({
        projectId: project.id,
        ...args
      });
    },

    trends: async (project, args, { dataSources }) => {
      return await dataSources.trendsAPI.getTrends({
        projectId: project.id,
        ...args
      });
    }
  },

  Baseline: {
    project: async (baseline, _, { dataSources }) => {
      return await dataSources.projectAPI.getProject(baseline.projectId);
    },

    metrics: async (baseline, _, { dataSources }) => {
      return await dataSources.metricsAPI.getMetrics(baseline.id);
    },

    comparisons: async (baseline, _, { dataSources }) => {
      return await dataSources.comparisonAPI.getComparisons(baseline.id);
    }
  },

  Alert: {
    project: async (alert, _, { dataSources }) => {
      return await dataSources.projectAPI.getProject(alert.projectId);
    }
  }
};

module.exports = resolvers;
```

## 3. Authentication and Authorization

### JWT-based Authentication
```javascript
// auth-middleware.js
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');

class AuthenticationService {
  constructor(config) {
    this.config = config;
    this.secretKey = config.jwtSecret;
    this.refreshSecretKey = config.jwtRefreshSecret;
    this.tokenExpiry = config.tokenExpiry || '1h';
    this.refreshTokenExpiry = config.refreshTokenExpiry || '7d';
  }

  // Rate limiting
  createRateLimiter(windowMs = 15 * 60 * 1000, max = 100) {
    return rateLimit({
      windowMs,
      max,
      message: {
        error: 'Too many requests',
        message: 'Rate limit exceeded. Please try again later.'
      },
      standardHeaders: true,
      legacyHeaders: false
    });
  }

  // JWT middleware
  authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
      return res.status(401).json({ error: 'Access token required' });
    }

    jwt.verify(token, this.secretKey, (err, user) => {
      if (err) {
        if (err.name === 'TokenExpiredError') {
          return res.status(401).json({ error: 'Token expired' });
        }
        return res.status(403).json({ error: 'Invalid token' });
      }

      req.user = user;
      next();
    });
  }

  // API Key authentication
  authenticateApiKey(req, res, next) {
    const apiKey = req.headers['x-api-key'];

    if (!apiKey) {
      return res.status(401).json({ error: 'API key required' });
    }

    // Validate API key
    this.validateApiKey(apiKey)
      .then(keyInfo => {
        if (!keyInfo) {
          return res.status(401).json({ error: 'Invalid API key' });
        }

        req.apiKey = keyInfo;
        req.user = {
          id: keyInfo.userId,
          type: 'api_key',
          permissions: keyInfo.permissions
        };

        next();
      })
      .catch(error => {
        console.error('API key validation error:', error);
        res.status(500).json({ error: 'Authentication error' });
      });
  }

  // Flexible authentication (JWT or API Key)
  authenticate(req, res, next) {
    const authHeader = req.headers['authorization'];
    const apiKey = req.headers['x-api-key'];

    if (authHeader && authHeader.startsWith('Bearer ')) {
      return this.authenticateToken(req, res, next);
    } else if (apiKey) {
      return this.authenticateApiKey(req, res, next);
    } else {
      return res.status(401).json({
        error: 'Authentication required',
        message: 'Provide either Bearer token or API key'
      });
    }
  }

  // Permission checking
  requirePermission(permission) {
    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({ error: 'Authentication required' });
      }

      if (!this.hasPermission(req.user, permission)) {
        return res.status(403).json({
          error: 'Insufficient permissions',
          required: permission
        });
      }

      next();
    };
  }

  hasPermission(user, requiredPermission) {
    if (user.type === 'admin') {
      return true; // Admins have all permissions
    }

    if (user.permissions && user.permissions.includes(requiredPermission)) {
      return true;
    }

    if (user.permissions && user.permissions.includes('*')) {
      return true; // Wildcard permission
    }

    return false;
  }

  // Project-specific authorization
  requireProjectAccess(accessLevel = 'read') {
    return async (req, res, next) => {
      const projectId = req.params.projectId || req.body.projectId;

      if (!projectId) {
        return res.status(400).json({ error: 'Project ID required' });
      }

      try {
        const hasAccess = await this.checkProjectAccess(
          req.user,
          projectId,
          accessLevel
        );

        if (!hasAccess) {
          return res.status(403).json({
            error: 'Project access denied',
            project: projectId,
            required_access: accessLevel
          });
        }

        req.projectId = projectId;
        next();
      } catch (error) {
        console.error('Project access check error:', error);
        res.status(500).json({ error: 'Authorization error' });
      }
    };
  }

  async checkProjectAccess(user, projectId, accessLevel) {
    // Check if user has access to the project
    const userProjects = await this.getUserProjects(user.id);
    const projectAccess = userProjects.find(p => p.projectId === projectId);

    if (!projectAccess) {
      return false;
    }

    // Check access level
    const accessLevels = ['read', 'write', 'admin'];
    const userLevel = accessLevels.indexOf(projectAccess.accessLevel);
    const requiredLevel = accessLevels.indexOf(accessLevel);

    return userLevel >= requiredLevel;
  }

  async validateApiKey(apiKey) {
    // This would typically query a database
    // For demo purposes, using a simple validation
    try {
      const keyInfo = await this.config.database.query(
        'SELECT * FROM api_keys WHERE key_hash = ? AND active = true',
        [this.hashApiKey(apiKey)]
      );

      if (keyInfo.length === 0) {
        return null;
      }

      return {
        id: keyInfo[0].id,
        userId: keyInfo[0].user_id,
        permissions: keyInfo[0].permissions.split(','),
        lastUsed: new Date(),
        rateLimit: keyInfo[0].rate_limit
      };
    } catch (error) {
      console.error('API key validation error:', error);
      return null;
    }
  }

  hashApiKey(apiKey) {
    return require('crypto')
      .createHash('sha256')
      .update(apiKey)
      .digest('hex');
  }

  async getUserProjects(userId) {
    try {
      return await this.config.database.query(
        'SELECT project_id, access_level FROM user_projects WHERE user_id = ?',
        [userId]
      );
    } catch (error) {
      console.error('Get user projects error:', error);
      return [];
    }
  }
}

module.exports = AuthenticationService;
```

## 4. Webhook System

### Webhook Management API
```javascript
// webhook-service.js
class WebhookService {
  constructor(config) {
    this.config = config;
    this.webhooks = new Map();
    this.deliveryQueue = [];
    this.retryDelays = [1000, 5000, 15000, 60000, 300000]; // Exponential backoff
  }

  async registerWebhook(userId, webhook) {
    const webhookConfig = {
      id: this.generateWebhookId(),
      userId,
      url: webhook.url,
      events: webhook.events || ['*'],
      secret: webhook.secret || this.generateSecret(),
      active: true,
      createdAt: new Date(),
      filters: webhook.filters || {},
      retryPolicy: webhook.retryPolicy || {
        maxRetries: 3,
        retryDelay: 'exponential'
      }
    };

    // Validate webhook URL
    if (!this.isValidWebhookUrl(webhookConfig.url)) {
      throw new Error('Invalid webhook URL');
    }

    // Test webhook endpoint
    await this.testWebhookEndpoint(webhookConfig);

    // Store webhook
    await this.storeWebhook(webhookConfig);
    this.webhooks.set(webhookConfig.id, webhookConfig);

    return webhookConfig;
  }

  async deliverWebhook(eventType, payload, context = {}) {
    const applicableWebhooks = Array.from(this.webhooks.values()).filter(
      webhook => this.shouldDeliverToWebhook(webhook, eventType, payload, context)
    );

    for (const webhook of applicableWebhooks) {
      await this.queueWebhookDelivery(webhook, eventType, payload);
    }
  }

  shouldDeliverToWebhook(webhook, eventType, payload, context) {
    if (!webhook.active) {
      return false;
    }

    // Check event type
    if (!webhook.events.includes('*') && !webhook.events.includes(eventType)) {
      return false;
    }

    // Apply filters
    if (webhook.filters.projects && context.projectId) {
      if (!webhook.filters.projects.includes(context.projectId)) {
        return false;
      }
    }

    if (webhook.filters.branches && context.branch) {
      if (!webhook.filters.branches.includes(context.branch)) {
        return false;
      }
    }

    if (webhook.filters.environments && context.environment) {
      if (!webhook.filters.environments.includes(context.environment)) {
        return false;
      }
    }

    return true;
  }

  async queueWebhookDelivery(webhook, eventType, payload) {
    const delivery = {
      id: this.generateDeliveryId(),
      webhookId: webhook.id,
      eventType,
      payload,
      webhook,
      attempts: 0,
      createdAt: new Date(),
      nextAttempt: new Date()
    };

    this.deliveryQueue.push(delivery);
    await this.processDeliveryQueue();
  }

  async processDeliveryQueue() {
    const now = new Date();
    const readyDeliveries = this.deliveryQueue.filter(
      delivery => delivery.nextAttempt <= now
    );

    for (const delivery of readyDeliveries) {
      await this.attemptWebhookDelivery(delivery);
    }
  }

  async attemptWebhookDelivery(delivery) {
    try {
      delivery.attempts++;

      const webhookPayload = {
        id: delivery.id,
        event: delivery.eventType,
        timestamp: delivery.createdAt.toISOString(),
        data: delivery.payload
      };

      const signature = this.generateSignature(
        JSON.stringify(webhookPayload),
        delivery.webhook.secret
      );

      const response = await fetch(delivery.webhook.url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-TBTS-Signature': signature,
          'X-TBTS-Event': delivery.eventType,
          'X-TBTS-Delivery': delivery.id,
          'User-Agent': 'TBTS-Webhook/1.0'
        },
        body: JSON.stringify(webhookPayload),
        timeout: 30000
      });

      if (response.ok) {
        // Successful delivery
        this.removeFromQueue(delivery);
        await this.recordSuccessfulDelivery(delivery, response.status);
      } else {
        // Failed delivery
        await this.handleFailedDelivery(delivery, response.status, await response.text());
      }

    } catch (error) {
      await this.handleFailedDelivery(delivery, null, error.message);
    }
  }

  async handleFailedDelivery(delivery, statusCode, errorMessage) {
    const maxRetries = delivery.webhook.retryPolicy.maxRetries;

    if (delivery.attempts >= maxRetries) {
      // Max retries reached, mark as failed
      this.removeFromQueue(delivery);
      await this.recordFailedDelivery(delivery, statusCode, errorMessage);
    } else {
      // Schedule retry
      const retryDelay = this.calculateRetryDelay(
        delivery.attempts,
        delivery.webhook.retryPolicy.retryDelay
      );
      delivery.nextAttempt = new Date(Date.now() + retryDelay);
    }
  }

  calculateRetryDelay(attemptNumber, retryPolicy) {
    if (retryPolicy === 'exponential') {
      return this.retryDelays[Math.min(attemptNumber - 1, this.retryDelays.length - 1)];
    } else if (typeof retryPolicy === 'number') {
      return retryPolicy;
    } else {
      return 5000; // Default 5 seconds
    }
  }

  generateSignature(payload, secret) {
    return require('crypto')
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex');
  }

  async testWebhookEndpoint(webhook) {
    try {
      const testPayload = {
        id: 'test',
        event: 'webhook.test',
        timestamp: new Date().toISOString(),
        data: { message: 'This is a test webhook from TBTS' }
      };

      const signature = this.generateSignature(
        JSON.stringify(testPayload),
        webhook.secret
      );

      const response = await fetch(webhook.url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-TBTS-Signature': signature,
          'X-TBTS-Event': 'webhook.test',
          'User-Agent': 'TBTS-Webhook/1.0'
        },
        body: JSON.stringify(testPayload),
        timeout: 10000
      });

      if (!response.ok) {
        throw new Error(`Webhook test failed: ${response.status} ${response.statusText}`);
      }

      return true;
    } catch (error) {
      throw new Error(`Webhook endpoint test failed: ${error.message}`);
    }
  }

  isValidWebhookUrl(url) {
    try {
      const parsed = new URL(url);
      return ['http:', 'https:'].includes(parsed.protocol);
    } catch {
      return false;
    }
  }

  // Event emission methods
  async emitBaselineCreated(baseline) {
    await this.deliverWebhook('baseline.created', baseline, {
      projectId: baseline.projectId,
      branch: baseline.branch,
      environment: baseline.environment
    });
  }

  async emitComparisonCompleted(comparison) {
    await this.deliverWebhook('comparison.completed', comparison, {
      projectId: comparison.projectId,
      branch: comparison.branch,
      environment: comparison.environment
    });
  }

  async emitAlertTriggered(alert) {
    await this.deliverWebhook('alert.triggered', alert, {
      projectId: alert.projectId,
      branch: alert.context.branch,
      environment: alert.context.environment
    });
  }

  async emitAlertResolved(alert) {
    await this.deliverWebhook('alert.resolved', alert, {
      projectId: alert.projectId,
      branch: alert.context.branch,
      environment: alert.context.environment
    });
  }
}
```

This comprehensive API layer provides robust RESTful and GraphQL interfaces, secure authentication and authorization, real-time capabilities through WebSockets and subscriptions, and flexible webhook integrations for external systems.