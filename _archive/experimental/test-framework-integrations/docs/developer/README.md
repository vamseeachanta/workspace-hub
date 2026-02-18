# Developer Guide

## Overview

This guide provides comprehensive information for developers who want to contribute to the Test Framework Integrations system, create custom plugins, or extend the platform's functionality. Whether you're fixing bugs, adding features, or building integrations, this guide will help you get started.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Architecture Overview](#architecture-overview)
4. [Contributing Guidelines](#contributing-guidelines)
5. [Plugin Development](#plugin-development)
6. [Framework Adapter Development](#framework-adapter-development)
7. [API Development](#api-development)
8. [Testing Guidelines](#testing-guidelines)
9. [Documentation Guidelines](#documentation-guidelines)
10. [Release Process](#release-process)

## Getting Started

### Prerequisites

- Node.js 16+ with npm/yarn
- Git
- Code editor with TypeScript support (VS Code recommended)
- Docker (for integration testing)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/test-framework-integrations/test-framework-integrations.git
cd test-framework-integrations

# Install dependencies
npm install

# Run tests
npm test

# Build the project
npm run build

# Start development mode
npm run dev
```

### Project Structure

```
test-framework-integrations/
├── src/                          # Source code
│   ├── core/                     # Core system components
│   │   ├── engine.js            # Main test engine
│   │   ├── orchestrator.js      # Test orchestration
│   │   └── events.js            # Event system
│   ├── adapters/                 # Framework adapters
│   │   ├── base-adapter.js      # Base adapter interface
│   │   ├── jest-adapter.js      # Jest integration
│   │   ├── mocha-adapter.js     # Mocha integration
│   │   └── ...
│   ├── features/                 # Feature modules
│   │   ├── baseline/            # Baseline management
│   │   ├── performance/         # Performance monitoring
│   │   ├── coverage/           # Coverage collection
│   │   └── reporting/          # Report generation
│   ├── plugins/                 # Built-in plugins
│   ├── utils/                   # Utility functions
│   └── index.js                # Main entry point
├── tests/                       # Test files
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── e2e/                    # End-to-end tests
│   └── fixtures/               # Test fixtures
├── docs/                       # Documentation
├── examples/                   # Example configurations
├── scripts/                    # Build and utility scripts
└── packages/                   # Monorepo packages (if applicable)
```

## Development Environment Setup

### IDE Configuration

#### VS Code Setup

Create `.vscode/settings.json`:

```json
{
  "typescript.preferences.includePackageJsonAutoImports": "on",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "jest.autoRun": "watch",
  "jest.showCoverageOnLoad": true
}
```

Create `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "ms-vscode.vscode-typescript-next",
    "orta.vscode-jest",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint",
    "ms-vscode.test-adapter-converter"
  ]
}
```

#### ESLint Configuration

`.eslintrc.js`:

```javascript
module.exports = {
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'prettier'
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module'
  },
  plugins: ['@typescript-eslint', 'jest'],
  env: {
    node: true,
    jest: true,
    es2022: true
  },
  rules: {
    'no-console': 'warn',
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    'jest/no-disabled-tests': 'warn',
    'jest/no-focused-tests': 'error'
  },
  overrides: [
    {
      files: ['tests/**/*'],
      rules: {
        'no-console': 'off'
      }
    }
  ]
};
```

#### Prettier Configuration

`.prettierrc`:

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

### Development Scripts

Add to `package.json`:

```json
{
  "scripts": {
    "dev": "nodemon --exec 'npm run build && node dist/index.js'",
    "build": "tsc && npm run copy-assets",
    "build:watch": "tsc --watch",
    "copy-assets": "copyfiles -u 1 'src/**/*.json' 'src/**/*.yaml' dist/",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:e2e": "jest --config jest.e2e.config.js",
    "lint": "eslint src tests --ext .ts,.js",
    "lint:fix": "eslint src tests --ext .ts,.js --fix",
    "format": "prettier --write 'src/**/*.{ts,js}' 'tests/**/*.{ts,js}'",
    "type-check": "tsc --noEmit",
    "docs:dev": "vuepress dev docs",
    "docs:build": "vuepress build docs",
    "release": "semantic-release"
  }
}
```

## Architecture Overview

### Core Components

The system is built around several core components:

#### Test Engine

```typescript
// src/core/engine.ts
export class TestEngine {
  private config: Configuration;
  private orchestrator: TestOrchestrator;
  private eventBus: EventBus;

  constructor(config: Configuration) {
    this.config = config;
    this.orchestrator = new TestOrchestrator(config);
    this.eventBus = new EventBus();
  }

  async initialize(): Promise<void> {
    await this.loadPlugins();
    await this.setupFrameworkAdapter();
    await this.initializeFeatureModules();
  }

  async runTests(options: TestRunOptions): Promise<TestResults> {
    const startTime = Date.now();

    try {
      this.eventBus.emit('test:start', { options, timestamp: startTime });

      const results = await this.orchestrator.execute(options);

      this.eventBus.emit('test:complete', {
        results,
        duration: Date.now() - startTime
      });

      return results;
    } catch (error) {
      this.eventBus.emit('test:failed', { error, options });
      throw error;
    }
  }
}
```

#### Event System

```typescript
// src/core/events.ts
export class EventBus {
  private listeners: Map<string, EventListener[]> = new Map();

  on(event: string, listener: EventListener): void {
    const listeners = this.listeners.get(event) || [];
    listeners.push(listener);
    this.listeners.set(event, listeners);
  }

  off(event: string, listener: EventListener): void {
    const listeners = this.listeners.get(event) || [];
    const index = listeners.indexOf(listener);
    if (index !== -1) {
      listeners.splice(index, 1);
    }
  }

  emit(event: string, data: any): void {
    const listeners = this.listeners.get(event) || [];
    listeners.forEach(listener => {
      try {
        listener(data);
      } catch (error) {
        console.error(`Error in event listener for ${event}:`, error);
      }
    });
  }

  async emitAsync(event: string, data: any): Promise<void> {
    const listeners = this.listeners.get(event) || [];
    await Promise.all(
      listeners.map(async listener => {
        try {
          await listener(data);
        } catch (error) {
          console.error(`Error in async event listener for ${event}:`, error);
        }
      })
    );
  }
}
```

### Plugin Architecture

```typescript
// src/core/plugin-system.ts
export interface Plugin {
  name: string;
  version: string;
  dependencies?: string[];
  initialize(context: PluginContext): Promise<void>;
  cleanup?(): Promise<void>;
}

export interface PluginContext {
  config: Configuration;
  eventBus: EventBus;
  logger: Logger;
  registerHook(name: string, handler: HookHandler): void;
}

export class PluginManager {
  private plugins: Map<string, Plugin> = new Map();
  private hooks: Map<string, HookHandler[]> = new Map();

  async loadPlugin(pluginPath: string): Promise<void> {
    const plugin = await this.importPlugin(pluginPath);

    // Validate plugin
    this.validatePlugin(plugin);

    // Check dependencies
    await this.checkDependencies(plugin);

    // Initialize plugin
    const context = this.createPluginContext(plugin);
    await plugin.initialize(context);

    this.plugins.set(plugin.name, plugin);
  }

  async executeHook(name: string, data: any): Promise<any> {
    const handlers = this.hooks.get(name) || [];

    let result = data;
    for (const handler of handlers) {
      result = await handler(result);
    }

    return result;
  }
}
```

## Contributing Guidelines

### Code Style and Standards

#### TypeScript Guidelines

1. **Use strict TypeScript configuration**:

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

2. **Define clear interfaces**:

```typescript
export interface TestResult {
  readonly id: string;
  readonly name: string;
  readonly status: TestStatus;
  readonly duration: number;
  readonly error?: Error;
  readonly metadata?: Record<string, unknown>;
}

export enum TestStatus {
  PASSED = 'passed',
  FAILED = 'failed',
  SKIPPED = 'skipped',
  PENDING = 'pending'
}
```

3. **Use proper error handling**:

```typescript
export class TestExecutionError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly cause?: Error
  ) {
    super(message);
    this.name = 'TestExecutionError';
  }
}

// Usage
try {
  await this.executeTest(test);
} catch (error) {
  throw new TestExecutionError(
    `Failed to execute test ${test.name}`,
    'TEST_EXECUTION_FAILED',
    error
  );
}
```

#### Documentation Standards

1. **Use JSDoc for all public APIs**:

```typescript
/**
 * Executes a test suite with the specified options.
 *
 * @param options - Configuration options for test execution
 * @param options.framework - The testing framework to use
 * @param options.testPaths - Array of test file paths
 * @param options.coverage - Whether to collect coverage data
 * @returns Promise resolving to test results
 *
 * @throws {TestExecutionError} When test execution fails
 * @throws {ConfigurationError} When configuration is invalid
 *
 * @example
 * ```typescript
 * const results = await engine.runTests({
 *   framework: 'jest',
 *   testPaths: ['src/**/*.test.js'],
 *   coverage: true
 * });
 * ```
 */
async runTests(options: TestRunOptions): Promise<TestResults> {
  // Implementation
}
```

2. **README template for new features**:

```markdown
# Feature Name

## Overview
Brief description of what this feature does.

## Usage
Basic usage examples.

## Configuration
Configuration options and their descriptions.

## API Reference
Link to detailed API documentation.

## Examples
Real-world usage examples.
```

### Git Workflow

#### Branch Naming

- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-fix` - Critical production fixes
- `docs/documentation-update` - Documentation updates
- `refactor/component-name` - Code refactoring

#### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(baseline): add compression support for baseline storage
fix(jest-adapter): resolve memory leak in test execution
docs(api): update OpenAPI specification for v2.0
refactor(core): extract event handling into separate module
```

#### Pull Request Process

1. **Create feature branch** from `main`
2. **Implement changes** with tests
3. **Update documentation** if needed
4. **Run full test suite** and ensure all pass
5. **Create pull request** with descriptive title and description
6. **Address review feedback**
7. **Squash and merge** after approval

#### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Documentation
- [ ] Code comments updated
- [ ] API documentation updated
- [ ] User documentation updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests pass locally
- [ ] No new warnings or errors
```

## Plugin Development

### Plugin Interface

```typescript
// src/types/plugin.ts
export interface BasePlugin {
  readonly name: string;
  readonly version: string;
  readonly description?: string;
  readonly author?: string;
  readonly dependencies?: PluginDependency[];

  initialize(context: PluginContext): Promise<void>;
  cleanup?(): Promise<void>;
}

export interface PluginDependency {
  name: string;
  version: string;
  optional?: boolean;
}

export interface PluginContext {
  config: Configuration;
  eventBus: EventBus;
  logger: Logger;
  storage: StorageProvider;
  registerHook(name: string, handler: HookHandler): void;
  registerCommand(name: string, command: Command): void;
}
```

### Plugin Example: Custom Reporter

```typescript
// plugins/slack-reporter.ts
import { BasePlugin, PluginContext, TestResults } from '../src/types';

export class SlackReporterPlugin implements BasePlugin {
  readonly name = 'slack-reporter';
  readonly version = '1.0.0';
  readonly description = 'Send test results to Slack';

  private webhookUrl: string;
  private eventBus: EventBus;

  async initialize(context: PluginContext): Promise<void> {
    this.webhookUrl = context.config.plugins?.slackReporter?.webhookUrl;
    this.eventBus = context.eventBus;

    if (!this.webhookUrl) {
      throw new Error('Slack webhook URL is required');
    }

    // Register event listeners
    this.eventBus.on('test:complete', this.handleTestComplete.bind(this));
    this.eventBus.on('baseline:regression', this.handleRegression.bind(this));
  }

  private async handleTestComplete(data: { results: TestResults }): Promise<void> {
    const message = this.formatTestResults(data.results);
    await this.sendSlackMessage(message);
  }

  private async handleRegression(data: { baseline: string; details: any }): Promise<void> {
    const message = this.formatRegressionAlert(data);
    await this.sendSlackMessage(message);
  }

  private formatTestResults(results: TestResults): SlackMessage {
    const { summary } = results;
    const color = summary.failed > 0 ? 'danger' : 'good';

    return {
      attachments: [{
        color,
        title: 'Test Results',
        fields: [
          { title: 'Total', value: summary.total.toString(), short: true },
          { title: 'Passed', value: summary.passed.toString(), short: true },
          { title: 'Failed', value: summary.failed.toString(), short: true },
          { title: 'Duration', value: `${results.duration}ms`, short: true }
        ]
      }]
    };
  }

  private async sendSlackMessage(message: SlackMessage): Promise<void> {
    try {
      const response = await fetch(this.webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
      });

      if (!response.ok) {
        throw new Error(`Slack API error: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to send Slack message:', error);
    }
  }
}

// Plugin registration
export default SlackReporterPlugin;
```

### Plugin Configuration

```typescript
// Plugin configuration schema
export const slackReporterSchema = {
  type: 'object',
  properties: {
    webhookUrl: {
      type: 'string',
      format: 'uri',
      description: 'Slack webhook URL for notifications'
    },
    channels: {
      type: 'array',
      items: { type: 'string' },
      description: 'Slack channels to notify'
    },
    conditions: {
      type: 'object',
      properties: {
        onFailure: { type: 'boolean', default: true },
        onSuccess: { type: 'boolean', default: false },
        onRegression: { type: 'boolean', default: true }
      }
    }
  },
  required: ['webhookUrl']
};

// Usage in configuration
const config = {
  plugins: {
    enabled: ['slack-reporter'],
    slackReporter: {
      webhookUrl: 'https://hooks.slack.com/services/...',
      channels: ['#testing', '#ci-cd'],
      conditions: {
        onFailure: true,
        onSuccess: false,
        onRegression: true
      }
    }
  }
};
```

### Testing Plugins

```typescript
// tests/plugins/slack-reporter.test.ts
import { SlackReporterPlugin } from '../../plugins/slack-reporter';
import { createMockContext, createMockTestResults } from '../helpers';

describe('SlackReporterPlugin', () => {
  let plugin: SlackReporterPlugin;
  let mockContext: PluginContext;
  let mockFetch: jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    mockFetch = jest.fn();
    global.fetch = mockFetch;

    mockContext = createMockContext({
      config: {
        plugins: {
          slackReporter: {
            webhookUrl: 'https://hooks.slack.com/test'
          }
        }
      }
    });

    plugin = new SlackReporterPlugin();
  });

  it('should initialize with valid webhook URL', async () => {
    await expect(plugin.initialize(mockContext)).resolves.not.toThrow();
  });

  it('should throw error without webhook URL', async () => {
    mockContext.config.plugins.slackReporter.webhookUrl = undefined;

    await expect(plugin.initialize(mockContext))
      .rejects.toThrow('Slack webhook URL is required');
  });

  it('should send message on test completion', async () => {
    await plugin.initialize(mockContext);

    const results = createMockTestResults({
      summary: { total: 10, passed: 8, failed: 2 }
    });

    mockContext.eventBus.emit('test:complete', { results });

    expect(mockFetch).toHaveBeenCalledWith(
      'https://hooks.slack.com/test',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: expect.stringContaining('Test Results')
      })
    );
  });
});
```

## Framework Adapter Development

### Base Adapter Interface

```typescript
// src/adapters/base-adapter.ts
export abstract class BaseAdapter {
  protected config: FrameworkConfig;
  protected logger: Logger;

  constructor(config: FrameworkConfig, logger: Logger) {
    this.config = config;
    this.logger = logger;
  }

  abstract get framework(): string;
  abstract get version(): string;

  abstract initialize(): Promise<void>;
  abstract execute(options: ExecutionOptions): Promise<RawResults>;
  abstract cleanup(): Promise<void>;

  protected abstract normalizeResults(results: any): TestResults;
  protected abstract handleError(error: any): Error;

  // Common utility methods
  protected validateConfig(): void {
    if (!this.config.testDir) {
      throw new Error('Test directory must be specified');
    }
  }

  protected async findTestFiles(pattern: string): Promise<string[]> {
    const glob = require('glob');
    return new Promise((resolve, reject) => {
      glob(pattern, { cwd: this.config.testDir }, (err, files) => {
        if (err) reject(err);
        else resolve(files);
      });
    });
  }
}
```

### Example: Custom Adapter

```typescript
// src/adapters/custom-adapter.ts
import { BaseAdapter } from './base-adapter';
import { spawn } from 'child_process';

export class CustomFrameworkAdapter extends BaseAdapter {
  get framework(): string {
    return 'custom';
  }

  get version(): string {
    return '1.0.0';
  }

  async initialize(): Promise<void> {
    this.validateConfig();

    // Check if custom framework is available
    await this.checkFrameworkAvailability();

    // Setup framework-specific configuration
    await this.setupFrameworkConfig();
  }

  async execute(options: ExecutionOptions): Promise<RawResults> {
    const command = this.buildTestCommand(options);

    return new Promise((resolve, reject) => {
      const process = spawn(command.cmd, command.args, {
        cwd: this.config.testDir,
        env: { ...process.env, ...options.env }
      });

      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve(this.parseResults(stdout));
        } else {
          reject(this.handleError(new Error(stderr)));
        }
      });
    });
  }

  async cleanup(): Promise<void> {
    // Cleanup framework-specific resources
    await this.cleanupFrameworkResources();
  }

  protected normalizeResults(results: any): TestResults {
    return {
      framework: this.framework,
      summary: {
        total: results.tests.length,
        passed: results.tests.filter(t => t.status === 'passed').length,
        failed: results.tests.filter(t => t.status === 'failed').length,
        skipped: results.tests.filter(t => t.status === 'skipped').length
      },
      tests: results.tests.map(test => ({
        id: test.id,
        name: test.name,
        file: test.file,
        status: test.status,
        duration: test.duration,
        error: test.error
      })),
      duration: results.duration,
      timestamp: new Date().toISOString()
    };
  }

  protected handleError(error: any): Error {
    return new FrameworkAdapterError(
      `Custom framework execution failed: ${error.message}`,
      'CUSTOM_EXECUTION_FAILED',
      error
    );
  }

  private async checkFrameworkAvailability(): Promise<void> {
    // Implementation to check if framework is available
  }

  private async setupFrameworkConfig(): Promise<void> {
    // Implementation to setup framework configuration
  }

  private buildTestCommand(options: ExecutionOptions): { cmd: string; args: string[] } {
    const cmd = 'custom-test-runner';
    const args = [
      '--config', this.config.configFile,
      '--output', 'json'
    ];

    if (options.coverage) {
      args.push('--coverage');
    }

    if (options.watch) {
      args.push('--watch');
    }

    return { cmd, args };
  }

  private parseResults(output: string): RawResults {
    try {
      return JSON.parse(output);
    } catch (error) {
      throw new Error(`Failed to parse test results: ${error.message}`);
    }
  }

  private async cleanupFrameworkResources(): Promise<void> {
    // Cleanup implementation
  }
}
```

### Adapter Testing

```typescript
// tests/adapters/custom-adapter.test.ts
import { CustomFrameworkAdapter } from '../../src/adapters/custom-adapter';
import { createMockConfig, createMockLogger } from '../helpers';

describe('CustomFrameworkAdapter', () => {
  let adapter: CustomFrameworkAdapter;
  let mockConfig: FrameworkConfig;
  let mockLogger: Logger;

  beforeEach(() => {
    mockConfig = createMockConfig({
      testDir: '/path/to/tests',
      configFile: 'custom.config.js'
    });
    mockLogger = createMockLogger();

    adapter = new CustomFrameworkAdapter(mockConfig, mockLogger);
  });

  describe('initialization', () => {
    it('should initialize successfully with valid config', async () => {
      await expect(adapter.initialize()).resolves.not.toThrow();
    });

    it('should throw error without test directory', async () => {
      mockConfig.testDir = undefined;

      await expect(adapter.initialize())
        .rejects.toThrow('Test directory must be specified');
    });
  });

  describe('execution', () => {
    beforeEach(async () => {
      await adapter.initialize();
    });

    it('should execute tests successfully', async () => {
      const mockResults = {
        tests: [
          { id: '1', name: 'test1', status: 'passed', duration: 100 }
        ],
        duration: 100
      };

      jest.spyOn(adapter as any, 'parseResults')
        .mockReturnValue(mockResults);

      const results = await adapter.execute({
        coverage: true,
        watch: false
      });

      expect(results).toEqual(mockResults);
    });
  });
});
```

## API Development

### REST API Guidelines

#### Controller Structure

```typescript
// src/api/controllers/test-controller.ts
import { Request, Response } from 'express';
import { TestService } from '../services/test-service';
import { ValidationMiddleware } from '../middleware/validation';
import { schemas } from '../schemas/test-schemas';

export class TestController {
  constructor(private testService: TestService) {}

  @ValidationMiddleware.validate(schemas.runTests)
  async runTests(req: Request, res: Response): Promise<void> {
    try {
      const options = req.validatedBody;
      const results = await this.testService.runTests(options);

      res.status(200).json({
        success: true,
        data: results
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  async getTestResults(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const results = await this.testService.getResults(id);

      if (!results) {
        return res.status(404).json({
          success: false,
          error: 'Test results not found'
        });
      }

      res.status(200).json({
        success: true,
        data: results
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }
}
```

#### Service Layer

```typescript
// src/api/services/test-service.ts
import { TestEngine } from '../../core/engine';
import { TestRepository } from '../repositories/test-repository';

export class TestService {
  constructor(
    private testEngine: TestEngine,
    private testRepository: TestRepository
  ) {}

  async runTests(options: TestRunOptions): Promise<TestResults> {
    // Validate options
    this.validateTestOptions(options);

    // Execute tests
    const results = await this.testEngine.runTests(options);

    // Store results
    await this.testRepository.saveResults(results);

    return results;
  }

  async getResults(id: string): Promise<TestResults | null> {
    return await this.testRepository.findById(id);
  }

  async getResultsByFramework(framework: string): Promise<TestResults[]> {
    return await this.testRepository.findByFramework(framework);
  }

  private validateTestOptions(options: TestRunOptions): void {
    if (!options.framework) {
      throw new Error('Framework is required');
    }

    if (!options.testPaths || options.testPaths.length === 0) {
      throw new Error('Test paths are required');
    }
  }
}
```

#### Error Handling

```typescript
// src/api/middleware/error-handler.ts
import { Request, Response, NextFunction } from 'express';

export class ErrorHandler {
  static handle(
    error: Error,
    req: Request,
    res: Response,
    next: NextFunction
  ): void {
    const statusCode = this.getStatusCode(error);
    const message = this.getMessage(error);

    res.status(statusCode).json({
      success: false,
      error: message,
      ...(process.env.NODE_ENV === 'development' && {
        stack: error.stack
      })
    });
  }

  private static getStatusCode(error: Error): number {
    if (error instanceof ValidationError) return 400;
    if (error instanceof NotFoundError) return 404;
    if (error instanceof UnauthorizedError) return 401;
    if (error instanceof ForbiddenError) return 403;
    return 500;
  }

  private static getMessage(error: Error): string {
    if (process.env.NODE_ENV === 'production') {
      return error instanceof ApiError ? error.message : 'Internal server error';
    }
    return error.message;
  }
}
```

### GraphQL API

```typescript
// src/api/graphql/resolvers/test-resolvers.ts
import { TestService } from '../services/test-service';

export const testResolvers = {
  Query: {
    testResults: async (_, { id }, { testService }: { testService: TestService }) => {
      return await testService.getResults(id);
    },

    testResultsByFramework: async (
      _,
      { framework },
      { testService }: { testService: TestService }
    ) => {
      return await testService.getResultsByFramework(framework);
    }
  },

  Mutation: {
    runTests: async (
      _,
      { input },
      { testService }: { testService: TestService }
    ) => {
      return await testService.runTests(input);
    }
  },

  Subscription: {
    testProgress: {
      subscribe: (_, __, { pubsub }) => pubsub.asyncIterator(['TEST_PROGRESS']),
      resolve: (payload) => payload.testProgress
    }
  }
};
```

## Testing Guidelines

### Unit Testing

```typescript
// tests/unit/core/engine.test.ts
import { TestEngine } from '../../../src/core/engine';
import { createMockConfiguration } from '../../helpers/mock-config';

describe('TestEngine', () => {
  let engine: TestEngine;
  let mockConfig: Configuration;

  beforeEach(() => {
    mockConfig = createMockConfiguration();
    engine = new TestEngine(mockConfig);
  });

  describe('initialization', () => {
    it('should initialize with valid configuration', async () => {
      await expect(engine.initialize()).resolves.not.toThrow();
    });

    it('should load plugins during initialization', async () => {
      const pluginSpy = jest.spyOn(engine as any, 'loadPlugins');
      await engine.initialize();
      expect(pluginSpy).toHaveBeenCalled();
    });
  });

  describe('test execution', () => {
    beforeEach(async () => {
      await engine.initialize();
    });

    it('should execute tests and return results', async () => {
      const options = { framework: 'jest', testPaths: ['test.js'] };
      const results = await engine.runTests(options);

      expect(results).toHaveProperty('summary');
      expect(results).toHaveProperty('tests');
      expect(results).toHaveProperty('duration');
    });

    it('should emit events during test execution', async () => {
      const startSpy = jest.fn();
      const completeSpy = jest.fn();

      engine.eventBus.on('test:start', startSpy);
      engine.eventBus.on('test:complete', completeSpy);

      await engine.runTests({ framework: 'jest', testPaths: ['test.js'] });

      expect(startSpy).toHaveBeenCalled();
      expect(completeSpy).toHaveBeenCalled();
    });
  });
});
```

### Integration Testing

```typescript
// tests/integration/api/test-endpoints.test.ts
import request from 'supertest';
import { createTestApp } from '../../helpers/test-app';
import { setupTestDatabase, cleanupTestDatabase } from '../../helpers/test-db';

describe('Test API Endpoints', () => {
  let app: Express.Application;

  beforeAll(async () => {
    await setupTestDatabase();
    app = await createTestApp();
  });

  afterAll(async () => {
    await cleanupTestDatabase();
  });

  describe('POST /api/tests/run', () => {
    it('should run tests and return results', async () => {
      const testOptions = {
        framework: 'jest',
        testPaths: ['tests/sample.test.js'],
        coverage: true
      };

      const response = await request(app)
        .post('/api/tests/run')
        .send(testOptions)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('summary');
      expect(response.body.data.summary.total).toBeGreaterThan(0);
    });

    it('should return 400 for invalid test options', async () => {
      const invalidOptions = {
        framework: 'invalid'
      };

      const response = await request(app)
        .post('/api/tests/run')
        .send(invalidOptions)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('validation');
    });
  });
});
```

### Test Helpers

```typescript
// tests/helpers/mock-config.ts
export function createMockConfiguration(overrides: Partial<Configuration> = {}): Configuration {
  return {
    framework: {
      type: 'jest',
      testDir: 'tests',
      configFile: 'jest.config.js'
    },
    execution: {
      timeout: 30000,
      retries: 0,
      maxWorkers: 1
    },
    baseline: {
      enabled: false,
      directory: 'baselines'
    },
    performance: {
      enabled: false
    },
    reporting: {
      formats: ['json'],
      outputDir: 'test-results'
    },
    ...overrides
  };
}

// tests/helpers/test-app.ts
export async function createTestApp(): Promise<Express.Application> {
  const app = express();

  // Setup middleware
  app.use(express.json());
  app.use(cors());

  // Setup routes
  const testController = new TestController(mockTestService);
  app.use('/api/tests', createTestRoutes(testController));

  // Setup error handling
  app.use(ErrorHandler.handle);

  return app;
}
```

## Documentation Guidelines

### API Documentation

Use OpenAPI 3.0 specification with detailed examples:

```yaml
# docs/api/openapi.yaml
paths:
  /api/tests/run:
    post:
      summary: Execute test suite
      description: Runs tests using the specified framework and configuration
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TestRunOptions'
            examples:
              jest-basic:
                summary: Basic Jest execution
                value:
                  framework: "jest"
                  testPaths: ["src/**/*.test.js"]
                  coverage: true
      responses:
        '200':
          description: Test execution completed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TestResults'
              examples:
                success:
                  summary: Successful test run
                  value:
                    success: true
                    data:
                      summary:
                        total: 10
                        passed: 8
                        failed: 2
                        skipped: 0
```

### Code Documentation

```typescript
/**
 * Main test engine for orchestrating test execution across different frameworks.
 *
 * The TestEngine is responsible for:
 * - Loading and managing framework adapters
 * - Coordinating test execution
 * - Managing plugins and feature modules
 * - Emitting events throughout the test lifecycle
 *
 * @example
 * ```typescript
 * const engine = new TestEngine(config);
 * await engine.initialize();
 *
 * const results = await engine.runTests({
 *   framework: 'jest',
 *   testPaths: ['src/**/*.test.js']
 * });
 * ```
 */
export class TestEngine {
  // Implementation
}
```

## Release Process

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Workflow

1. **Feature Development**
   ```bash
   git checkout -b feature/new-feature
   # Implement feature
   git commit -m "feat: add new feature"
   ```

2. **Testing and Review**
   ```bash
   npm test
   npm run lint
   npm run type-check
   # Create PR and get approval
   ```

3. **Release Preparation**
   ```bash
   git checkout main
   git pull origin main
   npm version patch  # or minor/major
   ```

4. **Release Creation**
   ```bash
   git push origin main --tags
   npm publish
   ```

### Automated Release

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
          registry-url: 'https://registry.npmjs.org'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build

      - name: Semantic Release
        run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

This developer guide provides the foundation for contributing to the Test Framework Integrations system. Whether you're fixing bugs, adding features, or creating plugins, following these guidelines will ensure consistent, high-quality contributions.