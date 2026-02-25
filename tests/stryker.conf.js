/**
 * Stryker Mutation Testing Configuration
 * Tests the quality of our test suite by introducing mutations
 */
module.exports = {
  // Test runner configuration
  testRunner: 'jest',
  testRunnerNodeArgs: ['--max_old_space_size=4096'],
  
  // Coverage analysis
  coverageAnalysis: 'perTest',
  
  // Files to mutate
  mutate: [
    'src/**/*.js',
    '!src/**/*.test.js',
    '!src/**/*.spec.js',
    '!src/**/index.js',
    '!src/**/*.d.ts'
  ],
  
  // Test files
  testFramework: 'jest',
  
  // Mutation testing thresholds
  thresholds: {
    high: 90,
    low: 75,
    break: 70
  },
  
  // Mutators to use
  mutator: {
    name: 'javascript',
    plugins: [
      '@stryker-mutator/javascript-mutator'
    ],
    excludedMutations: [
      // Exclude console.log mutations as they don't affect functionality
      'ConsoleLog',
      // Exclude string literal mutations for error messages
      'StringLiteral'
    ]
  },
  
  // Reporters
  reporters: [
    'clear-text',
    'progress',
    'html',
    'json',
    'dashboard'
  ],
  
  // HTML report configuration
  htmlReporter: {
    baseDir: 'reports/mutation'
  },
  
  // JSON report configuration
  jsonReporter: {
    fileName: 'reports/mutation/mutation-report.json'
  },
  
  // Dashboard reporter (for CI/CD integration)
  dashboard: {
    project: 'baseline-system',
    version: process.env.npm_package_version || '1.0.0',
    module: 'baseline-core'
  },
  
  // Timeout configuration
  timeoutMS: 30000,
  timeoutFactor: 2,
  
  // Concurrency
  concurrency: require('os').cpus().length,
  
  // Temp directory
  tempDirName: 'stryker-tmp',
  
  // Logging
  logLevel: 'info',
  fileLogLevel: 'debug',
  
  // Plugin configuration
  plugins: [
    '@stryker-mutator/core',
    '@stryker-mutator/javascript-mutator',
    '@stryker-mutator/jest-runner'
  ],
  
  // Ignored files/patterns
  ignoredPatterns: [
    'node_modules/**',
    'coverage/**',
    'reports/**',
    'dist/**',
    '*.config.js'
  ],
  
  // Custom mutation testing rules
  customMutations: {
    // Test arithmetic operators
    'ArithmeticOperator': {
      '+': ['-', '*'],
      '-': ['+', '*'],
      '*': ['+', '/'],
      '/': ['*', '%']
    },
    
    // Test comparison operators
    'EqualityOperator': {
      '==': ['!=', '==='],
      '!=': ['==', '!=='],
      '===': ['!==', '=='],
      '!==': ['===', '!=']
    },
    
    // Test logical operators
    'LogicalOperator': {
      '&&': ['||', ''],
      '||': ['&&', ''],
      '!': ['']
    },
    
    // Test conditional boundaries
    'ConditionalExpression': {
      'true': ['false'],
      'false': ['true']
    }
  },
  
  // File-specific mutation settings
  fileSettings: {
    // Core modules require higher mutation scores
    'src/baseline/**/*.js': {
      mutationScore: 95
    },
    'src/comparison/**/*.js': {
      mutationScore: 95
    },
    'src/metrics/**/*.js': {
      mutationScore: 95
    },
    'src/rules/**/*.js': {
      mutationScore: 95
    },
    'src/reports/**/*.js': {
      mutationScore: 95
    },

    // Utility modules can have slightly lower scores
    'src/utils/**/*.js': {
      mutationScore: 90
    }
  },
  
  // CI/CD integration
  buildCommand: 'npm run build',
  
  // Environment variables
  env: {
    NODE_ENV: 'test',
    STRYKER_MUTATION_TESTING: 'true'
  }
};
