#!/usr/bin/env node

/**
 * Basic Test Framework Integrations Example
 *
 * This example demonstrates the simplest way to use the Test Framework Integrations
 * system to run tests with unified reporting and basic configuration.
 */

const TestFrameworkIntegrations = require('test-framework-integrations');
const path = require('path');

async function runBasicTest() {
  console.log('🚀 Starting Basic Test Framework Integrations Example\n');

  try {
    // Step 1: Create integration instance with minimal configuration
    console.log('📋 Step 1: Creating integration instance...');

    const integration = new TestFrameworkIntegrations({
      framework: {
        type: 'jest',
        testDir: path.join(__dirname, 'tests'),
        testPattern: '**/*.test.js'
      },
      execution: {
        coverage: true,
        verbose: true
      },
      reporting: {
        formats: ['console', 'json'],
        outputDir: 'test-results'
      }
    });

    console.log('✅ Integration instance created\n');

    // Step 2: Initialize the system
    console.log('🔧 Step 2: Initializing system...');
    await integration.initialize();
    console.log('✅ System initialized\n');

    // Step 3: Run tests
    console.log('🧪 Step 3: Running tests...');
    const startTime = Date.now();

    const results = await integration.runTests({
      testPaths: ['tests/sample.test.js', 'tests/math.test.js']
    });

    const duration = Date.now() - startTime;
    console.log(`✅ Tests completed in ${duration}ms\n`);

    // Step 4: Display results
    console.log('📊 Step 4: Test Results Summary');
    console.log('================================');
    console.log(`Framework: ${results.framework}`);
    console.log(`Total Tests: ${results.summary.total}`);
    console.log(`✅ Passed: ${results.summary.passed}`);
    console.log(`❌ Failed: ${results.summary.failed}`);
    console.log(`⏭️ Skipped: ${results.summary.skipped}`);
    console.log(`⏱️ Duration: ${results.duration}ms`);

    if (results.coverage) {
      console.log('\n📈 Coverage Summary:');
      console.log(`Lines: ${results.coverage.lines.percentage.toFixed(2)}%`);
      console.log(`Functions: ${results.coverage.functions.percentage.toFixed(2)}%`);
      console.log(`Branches: ${results.coverage.branches.percentage.toFixed(2)}%`);
      console.log(`Statements: ${results.coverage.statements.percentage.toFixed(2)}%`);
    }

    // Step 5: Show individual test results
    if (results.tests && results.tests.length > 0) {
      console.log('\n🔍 Individual Test Results:');
      results.tests.forEach(test => {
        const status = test.status === 'passed' ? '✅' :
                      test.status === 'failed' ? '❌' : '⏭️';
        console.log(`  ${status} ${test.name} (${test.duration}ms)`);

        if (test.status === 'failed' && test.error) {
          console.log(`    Error: ${test.error.message}`);
        }
      });
    }

    console.log('\n🎉 Basic example completed successfully!');
    console.log(`📁 Test results saved to: ${path.join(__dirname, 'test-results')}`);

  } catch (error) {
    console.error('❌ Error running basic example:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Helper function to create sample test files if they don't exist
async function ensureTestFiles() {
  const fs = require('fs').promises;
  const testsDir = path.join(__dirname, 'tests');

  try {
    await fs.access(testsDir);
  } catch {
    await fs.mkdir(testsDir, { recursive: true });
  }

  // Create sample.test.js
  const sampleTestContent = `
// Sample test file for basic example
describe('Sample Tests', () => {
  test('should pass basic assertion', () => {
    expect(1 + 1).toBe(2);
  });

  test('should handle string operations', () => {
    const str = 'hello world';
    expect(str.toUpperCase()).toBe('HELLO WORLD');
    expect(str.length).toBe(11);
  });

  test('should work with arrays', () => {
    const arr = [1, 2, 3, 4, 5];
    expect(arr).toHaveLength(5);
    expect(arr).toContain(3);
    expect(arr.slice(0, 3)).toEqual([1, 2, 3]);
  });
});
`;

  // Create math.test.js
  const mathTestContent = `
// Math operations test file
describe('Math Operations', () => {
  test('addition should work correctly', () => {
    expect(2 + 3).toBe(5);
    expect(-1 + 1).toBe(0);
    expect(0.1 + 0.2).toBeCloseTo(0.3);
  });

  test('multiplication should work correctly', () => {
    expect(3 * 4).toBe(12);
    expect(-2 * 5).toBe(-10);
    expect(0 * 100).toBe(0);
  });

  test('division should work correctly', () => {
    expect(10 / 2).toBe(5);
    expect(7 / 2).toBe(3.5);
    expect(() => 1 / 0).not.toThrow();
  });

  test('should handle edge cases', () => {
    expect(Number.isNaN(0 / 0)).toBe(true);
    expect(Number.isFinite(1 / 0)).toBe(false);
    expect(Math.pow(2, 3)).toBe(8);
  });
});
`;

  try {
    await fs.writeFile(path.join(testsDir, 'sample.test.js'), sampleTestContent);
    await fs.writeFile(path.join(testsDir, 'math.test.js'), mathTestContent);
    console.log('📝 Sample test files created');
  } catch (error) {
    console.warn('⚠️ Could not create sample test files:', error.message);
  }
}

// Main execution
async function main() {
  await ensureTestFiles();
  await runBasicTest();
}

// Run the example if this file is executed directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = { runBasicTest, ensureTestFiles };