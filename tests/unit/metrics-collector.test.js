const MetricsCollector = require('../../src/metrics/metrics-collector');
const MockFactory = require('../fixtures/mock-factories');

describe('MetricsCollector', () => {
  let metricsCollector;
  let mockLogger;
  let mockMetrics;
  let mockCache;

  beforeEach(() => {
    mockLogger = createMockLogger();
    mockMetrics = createMockMetrics();
    mockCache = {
      get: jest.fn(),
      set: jest.fn(),
      delete: jest.fn()
    };
    
    metricsCollector = new MetricsCollector({
      logger: mockLogger,
      metrics: mockMetrics,
      cache: mockCache
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    it('should initialize with default configuration', () => {
      const collector = new MetricsCollector();
      expect(collector).toBeInstanceOf(MetricsCollector);
      expect(collector.config).toBeDefined();
    });

    it('should merge custom configuration', () => {
      const customConfig = {
        timeoutMs: 10000,
        retryAttempts: 5
      };
      
      const collector = new MetricsCollector({ config: customConfig });
      expect(collector.config.timeoutMs).toBe(10000);
      expect(collector.config.retryAttempts).toBe(5);
    });
  });

  describe('collectFromJest', () => {
    const mockJestResults = {
      testResults: [
        {
          testFilePath: '/path/to/test1.test.js',
          testResults: [
            { status: 'passed', duration: 150 },
            { status: 'passed', duration: 89 },
            { status: 'failed', duration: 2340, failureMessages: ['Test failed'] }
          ]
        },
        {
          testFilePath: '/path/to/test2.test.js',
          testResults: [
            { status: 'passed', duration: 67 },
            { status: 'skipped', duration: 0 }
          ]
        }
      ],
      coverageMap: {
        '/src/file1.js': {
          lines: { pct: 85.5 },
          branches: { pct: 78.2 },
          functions: { pct: 92.1 },
          statements: { pct: 84.7 }
        },
        '/src/file2.js': {
          lines: { pct: 95.0 },
          branches: { pct: 88.9 },
          functions: { pct: 100.0 },
          statements: { pct: 96.2 }
        }
      },
      startTime: Date.now() - 5000,
      endTime: Date.now()
    };

    it('should collect metrics from Jest results', async () => {
      const result = await metricsCollector.collectFromJest(mockJestResults);

      expect(result).toEqual({
        testCount: 5,
        passRate: 60.0, // 3 passed out of 5 total
        coverage: {
          lines: 90.25,
          branches: 83.55,
          functions: 96.05,
          statements: 90.45
        },
        performance: {
          totalDuration: 5000,
          averageTestDuration: 529.2,
          slowestTest: 2340,
          fastestTest: 67
        },
        tests: expect.arrayContaining([
          expect.objectContaining({
            file: expect.stringContaining('test1.test.js'),
            status: 'passed',
            duration: 150
          })
        ])
      });
    });

    it('should handle empty Jest results', async () => {
      const emptyResults = {
        testResults: [],
        coverageMap: {},
        startTime: Date.now(),
        endTime: Date.now()
      };

      const result = await metricsCollector.collectFromJest(emptyResults);

      expect(result).toEqual({
        testCount: 0,
        passRate: 0,
        coverage: {
          lines: 0,
          branches: 0,
          functions: 0,
          statements: 0
        },
        performance: {
          totalDuration: 0,
          averageTestDuration: 0,
          slowestTest: 0,
          fastestTest: 0
        },
        tests: []
      });
    });

    it('should handle malformed Jest results', async () => {
      const malformedResults = {
        testResults: [
          {
            testFilePath: null,
            testResults: null
          }
        ],
        coverageMap: null
      };

      await expect(metricsCollector.collectFromJest(malformedResults))
        .rejects.toThrow('Invalid Jest results format');
    });

    it('should cache expensive calculations', async () => {
      const cacheKey = 'jest_metrics_hash123';
      const cachedResult = { testCount: 10, passRate: 90 };
      
      mockCache.get.mockResolvedValueOnce(cachedResult);

      const result = await metricsCollector.collectFromJest(mockJestResults);

      expect(result).toEqual(cachedResult);
      expect(mockCache.get).toHaveBeenCalledWith(expect.stringContaining('jest_metrics'));
    });
  });

  describe('collectFromPytest', () => {
    const mockPytestResults = {
      summary: {
        passed: 85,
        failed: 3,
        skipped: 2,
        error: 1
      },
      tests: [
        {
          nodeid: 'tests/test_auth.py::test_login_success',
          outcome: 'passed',
          duration: 0.156
        },
        {
          nodeid: 'tests/test_auth.py::test_login_failure',
          outcome: 'failed',
          duration: 2.340,
          call: {
            longrepr: 'AssertionError: Expected login to fail'
          }
        }
      ],
      coverage: {
        totals: {
          percent_covered: 87.5,
          num_statements: 1000,
          missing_lines: 125
        },
        files: {
          'src/auth.py': {
            summary: {
              percent_covered: 92.3,
              covered_lines: 120,
              missing_lines: 10
            }
          }
        }
      }
    };

    it('should collect metrics from Pytest results', async () => {
      const result = await metricsCollector.collectFromPytest(mockPytestResults);

      expect(result).toEqual({
        testCount: 91,
        passRate: 93.41, // 85 passed out of 91 total
        coverage: {
          lines: 87.5,
          statements: 87.5
        },
        performance: {
          averageTestDuration: expect.any(Number),
          slowestTest: 2.340,
          fastestTest: 0.156
        },
        tests: expect.arrayContaining([
          expect.objectContaining({
            name: 'test_login_success',
            status: 'passed',
            duration: 156 // converted to ms
          })
        ])
      });
    });

    it('should handle Pytest XML format', async () => {
      const xmlResults = `
        <?xml version="1.0" encoding="utf-8"?>
        <testsuite name="pytest" tests="2" failures="1" skipped="0">
          <testcase classname="tests.test_auth" name="test_login" time="0.156"/>
          <testcase classname="tests.test_auth" name="test_logout" time="0.234">
            <failure message="AssertionError">Test failed</failure>
          </testcase>
        </testsuite>
      `;

      const result = await metricsCollector.collectFromPytestXML(xmlResults);

      expect(result.testCount).toBe(2);
      expect(result.passRate).toBe(50.0);
    });
  });

  describe('collectFromMocha', () => {
    const mockMochaResults = {
      stats: {
        passes: 45,
        failures: 2,
        pending: 1,
        duration: 5432
      },
      tests: [
        {
          title: 'should authenticate user',
          fullTitle: 'Auth API should authenticate user',
          state: 'passed',
          duration: 123,
          file: '/tests/auth.test.js'
        },
        {
          title: 'should reject invalid token',
          fullTitle: 'Auth API should reject invalid token',
          state: 'failed',
          duration: 456,
          file: '/tests/auth.test.js',
          err: {
            message: 'Expected 401 but got 200'
          }
        }
      ]
    };

    it('should collect metrics from Mocha results', async () => {
      const result = await metricsCollector.collectFromMocha(mockMochaResults);

      expect(result).toEqual({
        testCount: 48, // passes + failures + pending
        passRate: 93.75, // 45 passed out of 48 total
        performance: {
          totalDuration: 5432,
          averageTestDuration: expect.any(Number),
          slowestTest: 456,
          fastestTest: 123
        },
        tests: expect.arrayContaining([
          expect.objectContaining({
            name: 'should authenticate user',
            status: 'passed',
            duration: 123
          })
        ])
      });
    });
  });

  describe('collectSystemMetrics', () => {
    it('should collect system performance metrics', async () => {
      // Mock process.memoryUsage
      const originalMemoryUsage = process.memoryUsage;
      process.memoryUsage = jest.fn().mockReturnValue({
        rss: 52428800, // 50MB
        heapTotal: 20971520, // 20MB
        heapUsed: 15728640, // 15MB
        external: 1048576 // 1MB
      });

      // Mock process.cpuUsage
      const originalCpuUsage = process.cpuUsage;
      process.cpuUsage = jest.fn().mockReturnValue({
        user: 500000, // 500ms
        system: 200000 // 200ms
      });

      const result = await metricsCollector.collectSystemMetrics();

      expect(result).toEqual({
        memory: {
          rss: 50, // MB
          heapTotal: 20,
          heapUsed: 15,
          heapUtilization: 75 // 15/20 * 100
        },
        cpu: {
          user: 500,
          system: 200,
          total: 700
        },
        timestamp: expect.any(String)
      });

      // Restore original functions
      process.memoryUsage = originalMemoryUsage;
      process.cpuUsage = originalCpuUsage;
    });

    it('should handle system metrics collection errors', async () => {
      const originalMemoryUsage = process.memoryUsage;
      process.memoryUsage = jest.fn().mockImplementation(() => {
        throw new Error('Memory access denied');
      });

      await expect(metricsCollector.collectSystemMetrics())
        .rejects.toThrow('Failed to collect system metrics');

      process.memoryUsage = originalMemoryUsage;
    });
  });

  describe('calculateComplexityMetrics', () => {
    const mockSourceFiles = [
      {
        path: '/src/auth.js',
        content: `
          function authenticate(username, password) {
            if (!username || !password) {
              return false;
            }
            if (username === 'admin') {
              if (password === 'secret') {
                return true;
              }
            }
            return checkDatabase(username, password);
          }
        `
      },
      {
        path: '/src/utils.js',
        content: `
          function simpleFunction() {
            return 'hello world';
          }
        `
      }
    ];

    it('should calculate cyclomatic complexity', async () => {
      const result = await metricsCollector.calculateComplexityMetrics(mockSourceFiles);

      expect(result).toEqual({
        averageCyclomaticComplexity: expect.any(Number),
        maxCyclomaticComplexity: expect.any(Number),
        totalFunctions: expect.any(Number),
        complexFiles: expect.arrayContaining([
          expect.objectContaining({
            path: expect.stringContaining('auth.js'),
            complexity: expect.any(Number)
          })
        ]),
        maintainabilityIndex: expect.any(Number)
      });

      expect(result.averageCyclomaticComplexity).toBeGreaterThan(0);
    });

    it('should handle empty source files', async () => {
      const result = await metricsCollector.calculateComplexityMetrics([]);

      expect(result).toEqual({
        averageCyclomaticComplexity: 0,
        maxCyclomaticComplexity: 0,
        totalFunctions: 0,
        complexFiles: [],
        maintainabilityIndex: 100
      });
    });

    it('should handle malformed source files', async () => {
      const malformedFiles = [
        {
          path: '/src/broken.js',
          content: 'function broken( { // Invalid syntax'
        }
      ];

      const result = await metricsCollector.calculateComplexityMetrics(malformedFiles);

      expect(result.complexFiles).toEqual([
        expect.objectContaining({
          path: '/src/broken.js',
          error: expect.stringContaining('Parse error')
        })
      ]);
    });
  });

  describe('aggregateMetrics', () => {
    it('should aggregate metrics from multiple sources', async () => {
      const testMetrics = MockFactory.createMetrics();
      const systemMetrics = {
        memory: { heapUsed: 15, heapUtilization: 75 },
        cpu: { total: 700 }
      };
      const complexityMetrics = {
        averageCyclomaticComplexity: 3.2,
        maintainabilityIndex: 78.5
      };

      const result = await metricsCollector.aggregateMetrics({
        testMetrics,
        systemMetrics,
        complexityMetrics
      });

      expect(result).toEqual({
        testCount: testMetrics.testCount,
        passRate: testMetrics.passRate,
        coverage: testMetrics.coverage,
        performance: expect.objectContaining({
          ...testMetrics.performance,
          memoryUsage: systemMetrics.memory.heapUsed,
          cpuUsage: systemMetrics.cpu.total
        }),
        complexity: expect.objectContaining({
          cyclomaticComplexity: complexityMetrics.averageCyclomaticComplexity,
          maintainabilityIndex: complexityMetrics.maintainabilityIndex
        }),
        timestamp: expect.any(String)
      });
    });

    it('should handle missing metrics gracefully', async () => {
      const partialMetrics = {
        testMetrics: { testCount: 10, passRate: 90 }
      };

      const result = await metricsCollector.aggregateMetrics(partialMetrics);

      expect(result.testCount).toBe(10);
      expect(result.passRate).toBe(90);
      expect(result.performance).toBeDefined();
      expect(result.complexity).toBeDefined();
    });
  });

  describe('performance and edge cases', () => {
    it('should handle large test suites efficiently', async () => {
      const largeTestResults = {
        testResults: Array(1000).fill(null).map((_, i) => ({
          testFilePath: `/test${i}.test.js`,
          testResults: Array(10).fill(null).map(() => ({
            status: 'passed',
            duration: Math.floor(Math.random() * 1000)
          }))
        })),
        coverageMap: {},
        startTime: Date.now() - 60000,
        endTime: Date.now()
      };

      const startTime = Date.now();
      const result = await metricsCollector.collectFromJest(largeTestResults);
      const endTime = Date.now();

      expect(result.testCount).toBe(10000);
      expect(endTime - startTime).toBeLessThan(5000); // Should complete within 5 seconds
    });

    it('should handle concurrent metric collection', async () => {
      const mockResults = {
        testResults: [{
          testFilePath: '/test.js',
          testResults: [{ status: 'passed', duration: 100 }]
        }],
        coverageMap: {},
        startTime: Date.now(),
        endTime: Date.now()
      };

      const promises = Array(10).fill(null).map(() => 
        metricsCollector.collectFromJest(mockResults)
      );

      const results = await Promise.all(promises);
      
      expect(results).toHaveLength(10);
      results.forEach(result => {
        expect(result.testCount).toBe(1);
        expect(result.passRate).toBe(100);
      });
    });

    it('should handle memory pressure gracefully', async () => {
      // Simulate low memory condition
      const originalMemoryUsage = process.memoryUsage;
      process.memoryUsage = jest.fn().mockReturnValue({
        rss: 2147483648, // 2GB
        heapTotal: 1073741824, // 1GB
        heapUsed: 1073741824, // 1GB (100% utilization)
        external: 0
      });

      const result = await metricsCollector.collectSystemMetrics();

      expect(result.memory.heapUtilization).toBe(100);
      expect(mockLogger.warn).toHaveBeenCalledWith(
        'High memory utilization detected',
        expect.any(Object)
      );

      process.memoryUsage = originalMemoryUsage;
    });

    it('should validate metric values', async () => {
      const invalidMetrics = {
        testCount: -1,
        passRate: 150,
        coverage: {
          lines: 'invalid',
          branches: null
        }
      };

      expect(() => metricsCollector.validateMetrics(invalidMetrics))
        .toThrow('Invalid metric values detected');
    });

    it('should handle timeout scenarios', async () => {
      const timeoutCollector = new MetricsCollector({
        config: { timeoutMs: 100 }
      });

      // Mock a slow operation
      const slowPromise = new Promise(resolve => setTimeout(resolve, 200));
      
      await expect(timeoutCollector.collectWithTimeout(slowPromise))
        .rejects.toThrow('Metrics collection timed out');
    });
  });
});
