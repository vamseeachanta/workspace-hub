#!/usr/bin/env node

/**
 * Comprehensive Test Runner
 * Executes all test suites with proper sequencing and reporting
 */

const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const chalk = require('chalk');

class TestRunner {
  constructor() {
    this.results = {
      unit: null,
      integration: null,
      e2e: null,
      performance: null,
      property: null,
      mutation: null,
      coverage: null
    };
    
    this.startTime = Date.now();
    this.config = {
      parallel: process.argv.includes('--parallel'),
      skipSlow: process.argv.includes('--skip-slow'),
      verbose: process.argv.includes('--verbose'),
      mutation: process.argv.includes('--mutation'),
      coverage: !process.argv.includes('--no-coverage')
    };
  }

  async run() {
    console.log(chalk.blue('🧪 Starting Comprehensive Test Suite\n'));
    
    if (this.config.verbose) {
      console.log('Configuration:', this.config);
      console.log('');
    }

    try {
      // Setup
      await this.setup();
      
      // Run test suites in order
      if (this.config.parallel && !this.config.coverage) {
        await this.runTestsInParallel();
      } else {
        await this.runTestsSequentially();
      }
      
      // Generate reports
      await this.generateReports();
      
      // Display summary
      this.displaySummary();
      
    } catch (error) {
      console.error(chalk.red('❌ Test suite failed:'), error.message);
      process.exit(1);
    }
  }

  async setup() {
    console.log(chalk.yellow('📋 Setting up test environment...'));
    
    // Ensure directories exist
    const dirs = ['coverage', 'reports', 'reports/mutation', 'reports/e2e'];
    for (const dir of dirs) {
      await fs.mkdir(dir, { recursive: true });
    }
    
    // Check if dependencies are available
    const requiredDeps = ['jest', 'playwright'];
    if (this.config.mutation) {
      requiredDeps.push('@stryker-mutator/core');
    }
    
    console.log(chalk.green('✅ Environment setup complete\n'));
  }

  async runTestsSequentially() {
    console.log(chalk.blue('🔄 Running tests sequentially...\n'));
    
    // 1. Unit Tests (fastest, most reliable)
    await this.runUnitTests();
    
    // 2. Integration Tests
    await this.runIntegrationTests();
    
    // 3. Property-based Tests
    if (!this.config.skipSlow) {
      await this.runPropertyTests();
    }
    
    // 4. E2E Tests (slowest)
    if (!this.config.skipSlow) {
      await this.runE2ETests();
    }
    
    // 5. Performance Tests (resource intensive)
    if (!this.config.skipSlow) {
      await this.runPerformanceTests();
    }
    
    // 6. Mutation Testing (very slow)
    if (this.config.mutation) {
      await this.runMutationTests();
    }
    
    // 7. Coverage Verification
    if (this.config.coverage) {
      await this.verifyCoverage();
    }
  }

  async runTestsInParallel() {
    console.log(chalk.blue('⚡ Running tests in parallel...\n'));
    
    const testPromises = [
      this.runUnitTests(),
      this.runIntegrationTests(),
      this.runPropertyTests()
    ];
    
    if (!this.config.skipSlow) {
      testPromises.push(
        this.runE2ETests(),
        this.runPerformanceTests()
      );
    }
    
    await Promise.all(testPromises);
    
    // Mutation testing runs separately (too resource intensive)
    if (this.config.mutation) {
      await this.runMutationTests();
    }
  }

  async runUnitTests() {
    console.log(chalk.cyan('📦 Running Unit Tests...'));
    
    const result = await this.executeCommand('npm', ['run', 'test:unit'], {
      description: 'Unit Tests',
      timeout: 60000
    });
    
    this.results.unit = result;
    this.logResult('Unit Tests', result);
  }

  async runIntegrationTests() {
    console.log(chalk.cyan('🔗 Running Integration Tests...'));
    
    const result = await this.executeCommand('npm', ['run', 'test:integration'], {
      description: 'Integration Tests',
      timeout: 120000
    });
    
    this.results.integration = result;
    this.logResult('Integration Tests', result);
  }

  async runPropertyTests() {
    console.log(chalk.cyan('🎲 Running Property-based Tests...'));
    
    const result = await this.executeCommand('npm', ['run', 'test:property'], {
      description: 'Property-based Tests',
      timeout: 180000
    });
    
    this.results.property = result;
    this.logResult('Property-based Tests', result);
  }

  async runE2ETests() {
    console.log(chalk.cyan('🌐 Running E2E Tests...'));
    
    const result = await this.executeCommand('npm', ['run', 'test:e2e'], {
      description: 'E2E Tests',
      timeout: 300000
    });
    
    this.results.e2e = result;
    this.logResult('E2E Tests', result);
  }

  async runPerformanceTests() {
    console.log(chalk.cyan('⚡ Running Performance Tests...'));
    
    const result = await this.executeCommand('npm', ['run', 'test:performance'], {
      description: 'Performance Tests',
      timeout: 600000
    });
    
    this.results.performance = result;
    this.logResult('Performance Tests', result);
  }

  async runMutationTests() {
    console.log(chalk.cyan('🧬 Running Mutation Tests...'));
    
    const result = await this.executeCommand('npm', ['run', 'test:mutation'], {
      description: 'Mutation Tests',
      timeout: 1800000 // 30 minutes
    });
    
    this.results.mutation = result;
    this.logResult('Mutation Tests', result);
  }

  async verifyCoverage() {
    console.log(chalk.cyan('📊 Verifying Coverage...'));
    
    const result = await this.executeCommand('npm', ['run', 'test:coverage-verify'], {
      description: 'Coverage Verification',
      timeout: 30000
    });
    
    this.results.coverage = result;
    this.logResult('Coverage Verification', result);
  }

  async executeCommand(command, args, options = {}) {
    const { description, timeout = 60000 } = options;
    
    return new Promise((resolve) => {
      const startTime = Date.now();
      const child = spawn(command, args, {
        stdio: this.config.verbose ? 'inherit' : 'pipe',
        cwd: process.cwd()
      });
      
      let stdout = '';
      let stderr = '';
      
      if (!this.config.verbose) {
        child.stdout?.on('data', (data) => {
          stdout += data.toString();
        });
        
        child.stderr?.on('data', (data) => {
          stderr += data.toString();
        });
      }
      
      const timeoutId = setTimeout(() => {
        child.kill('SIGTERM');
        resolve({
          success: false,
          duration: Date.now() - startTime,
          error: 'Command timed out',
          code: -1
        });
      }, timeout);
      
      child.on('close', (code) => {
        clearTimeout(timeoutId);
        resolve({
          success: code === 0,
          duration: Date.now() - startTime,
          code,
          stdout,
          stderr
        });
      });
      
      child.on('error', (error) => {
        clearTimeout(timeoutId);
        resolve({
          success: false,
          duration: Date.now() - startTime,
          error: error.message,
          code: -1
        });
      });
    });
  }

  logResult(testType, result) {
    const duration = (result.duration / 1000).toFixed(2);
    
    if (result.success) {
      console.log(chalk.green(`✅ ${testType} passed in ${duration}s\n`));
    } else {
      console.log(chalk.red(`❌ ${testType} failed in ${duration}s`));
      if (result.error) {
        console.log(chalk.red(`   Error: ${result.error}`));
      }
      if (result.stderr && !this.config.verbose) {
        console.log(chalk.red('   stderr:'), result.stderr.slice(0, 500));
      }
      console.log('');
    }
  }

  async generateReports() {
    console.log(chalk.yellow('📊 Generating test reports...'));
    
    const report = {
      timestamp: new Date().toISOString(),
      duration: Date.now() - this.startTime,
      config: this.config,
      results: this.results,
      summary: this.generateSummary()
    };
    
    // Write comprehensive report
    await fs.writeFile(
      path.join('reports', 'test-results.json'),
      JSON.stringify(report, null, 2)
    );
    
    // Generate HTML report
    await this.generateHTMLReport(report);
    
    console.log(chalk.green('✅ Reports generated\n'));
  }

  generateSummary() {
    const results = Object.values(this.results).filter(r => r !== null);
    const passed = results.filter(r => r.success).length;
    const failed = results.filter(r => !r.success).length;
    const totalDuration = results.reduce((sum, r) => sum + r.duration, 0);
    
    return {
      total: results.length,
      passed,
      failed,
      successRate: results.length > 0 ? (passed / results.length) * 100 : 0,
      totalDuration,
      averageDuration: results.length > 0 ? totalDuration / results.length : 0
    };
  }

  async generateHTMLReport(report) {
    const html = `
<!DOCTYPE html>
<html>
<head>
    <title>Test Results - ${new Date(report.timestamp).toLocaleString()}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .summary { display: flex; gap: 20px; margin: 20px 0; }
        .metric { background: white; border: 1px solid #ddd; padding: 15px; border-radius: 5px; flex: 1; }
        .test-result { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .passed { background: #d4edda; border-left: 4px solid #28a745; }
        .failed { background: #f8d7da; border-left: 4px solid #dc3545; }
        .skipped { background: #fff3cd; border-left: 4px solid #ffc107; }
        .details { font-family: monospace; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Results Summary</h1>
        <p>Generated: ${new Date(report.timestamp).toLocaleString()}</p>
        <p>Total Duration: ${(report.duration / 1000 / 60).toFixed(2)} minutes</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>Overall</h3>
            <p>Success Rate: ${report.summary.successRate.toFixed(1)}%</p>
            <p>Tests: ${report.summary.passed}/${report.summary.total}</p>
        </div>
        <div class="metric">
            <h3>Performance</h3>
            <p>Total: ${(report.summary.totalDuration / 1000).toFixed(1)}s</p>
            <p>Average: ${(report.summary.averageDuration / 1000).toFixed(1)}s</p>
        </div>
    </div>
    
    <h2>Test Suite Results</h2>
    ${this.generateTestResultsHTML(report.results)}
    
    <h2>Configuration</h2>
    <pre class="details">${JSON.stringify(report.config, null, 2)}</pre>
</body>
</html>
    `;
    
    await fs.writeFile(path.join('reports', 'test-results.html'), html);
  }

  generateTestResultsHTML(results) {
    return Object.entries(results)
      .filter(([_, result]) => result !== null)
      .map(([testType, result]) => {
        const className = result.success ? 'passed' : 'failed';
        const duration = (result.duration / 1000).toFixed(2);
        
        return `
          <div class="test-result ${className}">
            <h3>${testType.charAt(0).toUpperCase() + testType.slice(1)} Tests</h3>
            <p>Status: ${result.success ? 'PASSED' : 'FAILED'}</p>
            <p>Duration: ${duration}s</p>
            ${result.error ? `<p>Error: ${result.error}</p>` : ''}
          </div>
        `;
      }).join('');
  }

  displaySummary() {
    const summary = this.generateSummary();
    const totalDuration = (Date.now() - this.startTime) / 1000;
    
    console.log(chalk.blue('\n📋 Test Suite Summary'));
    console.log(chalk.blue('════════════════════════\n'));
    
    if (summary.failed === 0) {
      console.log(chalk.green(`🎉 All tests passed! (${summary.passed}/${summary.total})`));
    } else {
      console.log(chalk.red(`❌ ${summary.failed} test suite(s) failed`));
      console.log(chalk.yellow(`✅ ${summary.passed} test suite(s) passed`));
    }
    
    console.log(`\n⏱️  Total time: ${totalDuration.toFixed(2)}s`);
    console.log(`📊 Success rate: ${summary.successRate.toFixed(1)}%`);
    
    console.log('\n📄 Reports generated:');
    console.log('   • JSON: reports/test-results.json');
    console.log('   • HTML: reports/test-results.html');
    
    if (this.config.coverage) {
      console.log('   • Coverage: coverage/lcov-report/index.html');
    }
    
    if (this.config.mutation) {
      console.log('   • Mutation: reports/mutation/index.html');
    }
    
    if (summary.failed > 0) {
      console.log(chalk.red('\n❌ Test suite failed'));
      process.exit(1);
    } else {
      console.log(chalk.green('\n✅ Test suite completed successfully'));
    }
  }
}

// Run if called directly
if (require.main === module) {
  const runner = new TestRunner();
  runner.run().catch((error) => {
    console.error(chalk.red('Fatal error:'), error);
    process.exit(1);
  });
}

module.exports = TestRunner;
