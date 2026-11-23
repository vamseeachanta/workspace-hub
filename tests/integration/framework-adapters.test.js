const JestAdapter = require('../../src/adapters/jest-adapter');
const PytestAdapter = require('../../src/adapters/pytest-adapter');
const MochaAdapter = require('../../src/adapters/mocha-adapter');
const PlaywrightAdapter = require('../../src/adapters/playwright-adapter');
const MockFactory = require('../fixtures/mock-factories');
const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

describe('Framework Adapters Integration', () => {
  let tempDir;
  let mockProject;

  beforeAll(async () => {
    // Create temporary test project
    tempDir = path.join(__dirname, '../temp', `test-${Date.now()}`);
    await fs.mkdir(tempDir, { recursive: true });
    
    mockProject = {
      rootDir: tempDir,
      packageJson: path.join(tempDir, 'package.json'),
      testDir: path.join(tempDir, 'tests')
    };
    
    await fs.mkdir(mockProject.testDir, { recursive: true });
  });

  afterAll(async () => {
    // Cleanup temporary files
    try {
      await fs.rmdir(tempDir, { recursive: true });
    } catch (error) {
      console.warn('Failed to cleanup temp directory:', error.message);
    }
  });

  describe('JestAdapter', () => {
    let jestAdapter;
    
    beforeEach(() => {
      jestAdapter = new JestAdapter({
        projectRoot: mockProject.rootDir,
        logger: createMockLogger()
      });
    });

    it('should detect Jest configuration', async () => {
      // Create mock jest.config.js
      const jestConfig = `
        module.exports = {
          testEnvironment: 'node',
          testMatch: ['**/*.test.js'],
          collectCoverage: true
        };
      `;
      
      await fs.writeFile(path.join(tempDir, 'jest.config.js'), jestConfig);
      
      const isSupported = await jestAdapter.isSupported();
      expect(isSupported).toBe(true);
    });

    it('should run Jest tests and collect results', async () => {
      // Create sample test file
      const testContent = `
        describe('Sample Test', () => {
          test('should pass', () => {
            expect(1 + 1).toBe(2);
          });
          
          test('should also pass', () => {
            expect(true).toBeTruthy();
          });
        });
      `;
      
      await fs.writeFile(path.join(mockProject.testDir, 'sample.test.js'), testContent);
      
      // Create package.json with jest dependency
      const packageJson = {
        name: 'test-project',
        scripts: { test: 'jest' },
        devDependencies: { jest: '^29.0.0' }
      };
      
      await fs.writeFile(mockProject.packageJson, JSON.stringify(packageJson, null, 2));
      
      // Mock Jest execution result
      jestAdapter.executeJest = jest.fn().mockResolvedValueOnce({
        success: true,
        testResults: [{
          testFilePath: path.join(mockProject.testDir, 'sample.test.js'),
          testResults: [
            { title: 'should pass', status: 'passed', duration: 5 },
            { title: 'should also pass', status: 'passed', duration: 3 }
          ]
        }],
        coverageMap: {
          [path.join(tempDir, 'src/math.js')]: {
            lines: { pct: 100 },
            branches: { pct: 100 },
            functions: { pct: 100 },
            statements: { pct: 100 }
          }
        }
      });
      
      const results = await jestAdapter.runTests();
      
      expect(results).toEqual({
        framework: 'jest',
        success: true,
        metrics: expect.objectContaining({
          testCount: 2,
          passCount: 2,
          failCount: 0,
          passRate: 100,
          coverage: expect.objectContaining({
            lines: 100,
            branches: 100,
            functions: 100,
            statements: 100
          })
        }),
        tests: expect.arrayContaining([
          expect.objectContaining({
            name: 'should pass',
            status: 'passed',
            duration: 5
          })
        ])
      });
    });

    it('should handle Jest test failures', async () => {
      jestAdapter.executeJest = jest.fn().mockResolvedValueOnce({
        success: false,
        testResults: [{
          testFilePath: '/path/to/failing.test.js',
          testResults: [
            {
              title: 'should fail',
              status: 'failed',
              duration: 10,
              failureMessages: ['Expected 2 but received 3']
            }
          ]
        }]
      });
      
      const results = await jestAdapter.runTests();
      
      expect(results.success).toBe(false);
      expect(results.metrics.failCount).toBe(1);
      expect(results.tests[0].status).toBe('failed');
      expect(results.tests[0].error).toContain('Expected 2 but received 3');
    });

    it('should parse Jest coverage reports', async () => {
      const coverageData = {
        '/src/file1.js': {
          lines: { pct: 85.5, total: 100, covered: 85, skipped: 0 },
          branches: { pct: 78.2, total: 50, covered: 39, skipped: 0 },
          functions: { pct: 92.1, total: 25, covered: 23, skipped: 0 },
          statements: { pct: 84.7, total: 95, covered: 80, skipped: 0 }
        },
        '/src/file2.js': {
          lines: { pct: 95.0, total: 80, covered: 76, skipped: 0 },
          branches: { pct: 88.9, total: 30, covered: 26, skipped: 0 },
          functions: { pct: 100.0, total: 15, covered: 15, skipped: 0 },
          statements: { pct: 96.2, total: 75, covered: 72, skipped: 0 }
        }
      };
      
      const aggregatedCoverage = jestAdapter.aggregateCoverage(coverageData);
      
      expect(aggregatedCoverage).toEqual({
        lines: expect.closeTo(89.44, 1), // (85+76)/(100+80)
        branches: expect.closeTo(81.25, 1), // (39+26)/(50+30)
        functions: expect.closeTo(95.0, 1), // (23+15)/(25+15)
        statements: expect.closeTo(89.41, 1) // (80+72)/(95+75)
      });
    });
  });

  describe('PytestAdapter', () => {
    let pytestAdapter;
    
    beforeEach(() => {
      pytestAdapter = new PytestAdapter({
        projectRoot: mockProject.rootDir,
        logger: createMockLogger()
      });
    });

    it('should detect pytest configuration', async () => {
      // Create pytest.ini
      const pytestConfig = `
        [tool:pytest]
        testpaths = tests
        python_files = test_*.py
        addopts = --cov=src --cov-report=xml
      `;
      
      await fs.writeFile(path.join(tempDir, 'pytest.ini'), pytestConfig);
      
      const isSupported = await pytestAdapter.isSupported();
      expect(isSupported).toBe(true);
    });

    it('should run pytest and collect results', async () => {
      // Mock pytest execution
      pytestAdapter.executePytest = jest.fn().mockResolvedValueOnce({
        returnCode: 0,
        stdout: JSON.stringify({
          summary: {
            passed: 8,
            failed: 1,
            skipped: 1,
            error: 0
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
              duration: 0.234,
              call: {
                longrepr: 'AssertionError: Expected login to fail'
              }
            }
          ]
        })
      });
      
      // Mock coverage data
      const coverageXml = `
        <coverage>
          <packages>
            <package name="src">
              <classes>
                <class name="auth.py" line-rate="0.85" branch-rate="0.78">
                  <lines>
                    <line number="1" hits="1"/>
                    <line number="2" hits="0"/>
                  </lines>
                </class>
              </classes>
            </package>
          </packages>
        </coverage>
      `;
      
      await fs.writeFile(path.join(tempDir, 'coverage.xml'), coverageXml);
      
      const results = await pytestAdapter.runTests();
      
      expect(results).toEqual({
        framework: 'pytest',
        success: false, // Has failures
        metrics: expect.objectContaining({
          testCount: 10,
          passCount: 8,
          failCount: 1,
          skipCount: 1,
          passRate: 80.0
        }),
        tests: expect.arrayContaining([
          expect.objectContaining({
            name: 'test_login_success',
            file: 'tests/test_auth.py',
            status: 'passed',
            duration: 156 // converted to ms
          })
        ])
      });
    });

    it('should parse pytest XML coverage reports', async () => {
      const xmlContent = `
        <?xml version="1.0"?>
        <coverage line-rate="0.87" branch-rate="0.82">
          <packages>
            <package name="src" line-rate="0.87">
              <classes>
                <class name="auth.py" filename="src/auth.py" line-rate="0.90">
                  <lines>
                    <line number="1" hits="5"/>
                    <line number="2" hits="3"/>
                    <line number="3" hits="0"/>
                  </lines>
                </class>
              </classes>
            </package>
          </packages>
        </coverage>
      `;
      
      const coverage = await pytestAdapter.parseCoverageXML(xmlContent);
      
      expect(coverage).toEqual({
        overall: {
          lines: 87.0,
          branches: 82.0
        },
        files: {
          'src/auth.py': {
            lineRate: 90.0,
            coveredLines: [1, 2],
            missedLines: [3]
          }
        }
      });
    });
  });

  describe('MochaAdapter', () => {
    let mochaAdapter;
    
    beforeEach(() => {
      mochaAdapter = new MochaAdapter({
        projectRoot: mockProject.rootDir,
        logger: createMockLogger()
      });
    });

    it('should detect Mocha configuration', async () => {
      const mochaOpts = `
        --reporter json
        --timeout 5000
        --recursive
        tests/**/*.test.js
      `;
      
      await fs.writeFile(path.join(tempDir, 'test/mocha.opts'), mochaOpts);
      
      const isSupported = await mochaAdapter.isSupported();
      expect(isSupported).toBe(true);
    });

    it('should run Mocha tests and collect results', async () => {
      mochaAdapter.executeMocha = jest.fn().mockResolvedValueOnce({
        returnCode: 0,
        stdout: JSON.stringify({
          stats: {
            suites: 2,
            tests: 5,
            passes: 4,
            pending: 1,
            failures: 0,
            duration: 1234
          },
          tests: [
            {
              title: 'should authenticate user',
              fullTitle: 'Auth API should authenticate user',
              state: 'passed',
              duration: 123
            },
            {
              title: 'should reject invalid credentials',
              fullTitle: 'Auth API should reject invalid credentials',
              state: 'passed',
              duration: 89
            }
          ],
          failures: []
        })
      });
      
      const results = await mochaAdapter.runTests();
      
      expect(results).toEqual({
        framework: 'mocha',
        success: true,
        metrics: expect.objectContaining({
          testCount: 5,
          passCount: 4,
          failCount: 0,
          pendingCount: 1,
          passRate: 80.0,
          totalDuration: 1234
        })
      });
    });

    it('should handle Mocha test failures', async () => {
      mochaAdapter.executeMocha = jest.fn().mockResolvedValueOnce({
        returnCode: 1,
        stdout: JSON.stringify({
          stats: {
            tests: 3,
            passes: 2,
            failures: 1,
            duration: 890
          },
          failures: [
            {
              title: 'should handle error case',
              fullTitle: 'Error handling should handle error case',
              err: {
                message: 'Expected error to be thrown',
                stack: 'AssertionError: Expected error to be thrown\n    at test.js:15:20'
              },
              duration: 45
            }
          ]
        })
      });
      
      const results = await mochaAdapter.runTests();
      
      expect(results.success).toBe(false);
      expect(results.metrics.failCount).toBe(1);
      expect(results.failures).toHaveLength(1);
      expect(results.failures[0].error.message).toBe('Expected error to be thrown');
    });
  });

  describe('PlaywrightAdapter', () => {
    let playwrightAdapter;
    
    beforeEach(() => {
      playwrightAdapter = new PlaywrightAdapter({
        projectRoot: mockProject.rootDir,
        logger: createMockLogger()
      });
    });

    it('should detect Playwright configuration', async () => {
      const playwrightConfig = `
        const { defineConfig } = require('@playwright/test');
        
        module.exports = defineConfig({
          testDir: './tests',
          timeout: 30000,
          use: {
            baseURL: 'http://localhost:3000'
          }
        });
      `;
      
      await fs.writeFile(path.join(tempDir, 'playwright.config.js'), playwrightConfig);
      
      const isSupported = await playwrightAdapter.isSupported();
      expect(isSupported).toBe(true);
    });

    it('should run Playwright tests and collect results', async () => {
      playwrightAdapter.executePlaywright = jest.fn().mockResolvedValueOnce({
        returnCode: 0,
        stdout: JSON.stringify({
          config: {
            rootDir: tempDir,
            testDir: 'tests'
          },
          suites: [
            {
              title: 'Authentication Flow',
              file: 'tests/auth.spec.js',
              tests: [
                {
                  title: 'should login successfully',
                  outcome: 'expected',
                  duration: 2340,
                  errors: []
                },
                {
                  title: 'should logout successfully',
                  outcome: 'expected',
                  duration: 1560,
                  errors: []
                }
              ]
            }
          ]
        })
      });
      
      const results = await playwrightAdapter.runTests();
      
      expect(results).toEqual({
        framework: 'playwright',
        success: true,
        metrics: expect.objectContaining({
          testCount: 2,
          passCount: 2,
          failCount: 0,
          passRate: 100,
          averageDuration: 1950 // (2340 + 1560) / 2
        }),
        tests: expect.arrayContaining([
          expect.objectContaining({
            name: 'should login successfully',
            file: 'tests/auth.spec.js',
            status: 'passed',
            duration: 2340
          })
        ])
      });
    });

    it('should handle browser test failures with screenshots', async () => {
      playwrightAdapter.executePlaywright = jest.fn().mockResolvedValueOnce({
        returnCode: 1,
        stdout: JSON.stringify({
          suites: [
            {
              title: 'UI Tests',
              file: 'tests/ui.spec.js',
              tests: [
                {
                  title: 'should display welcome message',
                  outcome: 'unexpected',
                  duration: 5670,
                  errors: [
                    {
                      message: 'locator.click: Timeout 30000ms exceeded',
                      stack: 'Error: locator.click: Timeout 30000ms exceeded\n    at ui.spec.js:25:30'
                    }
                  ],
                  attachments: [
                    {
                      name: 'screenshot',
                      path: 'test-results/ui-should-display-welcome-message/screenshot.png',
                      contentType: 'image/png'
                    }
                  ]
                }
              ]
            }
          ]
        })
      });
      
      const results = await playwrightAdapter.runTests();
      
      expect(results.success).toBe(false);
      expect(results.metrics.failCount).toBe(1);
      expect(results.tests[0].status).toBe('failed');
      expect(results.tests[0].attachments).toContainEqual(expect.objectContaining({
        name: 'screenshot',
        contentType: 'image/png'
      }));
    });
  });

  describe('Cross-framework integration', () => {
    it('should run multiple frameworks in the same project', async () => {
      const adapters = [
        new JestAdapter({ projectRoot: mockProject.rootDir }),
        new MochaAdapter({ projectRoot: mockProject.rootDir }),
        new PlaywrightAdapter({ projectRoot: mockProject.rootDir })
      ];
      
      // Mock each adapter to be supported and return results
      adapters[0].isSupported = jest.fn().mockResolvedValue(true);
      adapters[0].runTests = jest.fn().mockResolvedValue({
        framework: 'jest',
        success: true,
        metrics: { testCount: 10, passCount: 9, failCount: 1 }
      });
      
      adapters[1].isSupported = jest.fn().mockResolvedValue(true);
      adapters[1].runTests = jest.fn().mockResolvedValue({
        framework: 'mocha',
        success: true,
        metrics: { testCount: 5, passCount: 5, failCount: 0 }
      });
      
      adapters[2].isSupported = jest.fn().mockResolvedValue(true);
      adapters[2].runTests = jest.fn().mockResolvedValue({
        framework: 'playwright',
        success: true,
        metrics: { testCount: 3, passCount: 3, failCount: 0 }
      });
      
      const allResults = [];
      
      for (const adapter of adapters) {
        if (await adapter.isSupported()) {
          const results = await adapter.runTests();
          allResults.push(results);
        }
      }
      
      expect(allResults).toHaveLength(3);
      
      const aggregatedMetrics = {
        totalTests: allResults.reduce((sum, r) => sum + r.metrics.testCount, 0),
        totalPassed: allResults.reduce((sum, r) => sum + r.metrics.passCount, 0),
        totalFailed: allResults.reduce((sum, r) => sum + r.metrics.failCount, 0)
      };
      
      expect(aggregatedMetrics).toEqual({
        totalTests: 18,
        totalPassed: 17,
        totalFailed: 1
      });
    });

    it('should handle framework conflicts gracefully', async () => {
      // Create conflicting configuration files
      await fs.writeFile(path.join(tempDir, 'jest.config.js'), 'module.exports = {};');
      await fs.writeFile(path.join(tempDir, 'mocha.opts'), '--timeout 5000');
      
      const jestAdapter = new JestAdapter({ projectRoot: tempDir });
      const mochaAdapter = new MochaAdapter({ projectRoot: tempDir });
      
      const jestSupported = await jestAdapter.isSupported();
      const mochaSupported = await mochaAdapter.isSupported();
      
      // Both should be detected, but priority should be given to explicit config
      expect(jestSupported).toBe(true);
      expect(mochaSupported).toBe(true);
    });
  });
});
