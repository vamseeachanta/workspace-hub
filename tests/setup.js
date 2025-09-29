// Global test setup
const { TextEncoder, TextDecoder } = require('util');

// Polyfills for Node.js environment
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock console methods for cleaner test output
const originalConsole = { ...console };

beforeEach(() => {
  // Reset console mocks before each test
  console.error = jest.fn();
  console.warn = jest.fn();
  console.log = jest.fn();
});

afterEach(() => {
  // Restore console after each test
  Object.assign(console, originalConsole);
});

// Global test utilities
global.createMockDatabase = () => {
  return {
    query: jest.fn(),
    transaction: jest.fn(),
    close: jest.fn()
  };
};

global.createMockLogger = () => {
  return {
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    debug: jest.fn()
  };
};

global.createMockMetrics = () => {
  return {
    increment: jest.fn(),
    gauge: jest.fn(),
    histogram: jest.fn(),
    timer: jest.fn()
  };
};

// Mock environment variables
process.env.NODE_ENV = 'test';
process.env.DB_CONNECTION_STRING = 'test://localhost/testdb';
process.env.REDIS_URL = 'redis://localhost:6379/15';

// Increase timeout for integration tests
jest.setTimeout(30000);
