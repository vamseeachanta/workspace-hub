const LoadTester = require('../../src/utils/load-tester');
const BaselineService = require('../../src/services/baseline-service');
const MockFactory = require('../fixtures/mock-factories');
const cluster = require('cluster');
const os = require('os');

describe('Load Testing', () => {
  let baselineService;
  let loadTester;
  
  beforeAll(async () => {
    baselineService = new BaselineService({
      database: { connectionString: 'sqlite://memory' },
      logger: { level: 'error' }
    });
    
    await baselineService.initialize();
    
    loadTester = new LoadTester({
      service: baselineService,
      maxConcurrency: os.cpus().length,
      timeout: 30000
    });
  });
  
  afterAll(async () => {
    await baselineService.cleanup();
  });

  describe('Baseline Creation Load', () => {
    it('should handle concurrent baseline creation', async () => {
      const concurrentRequests = 50;
      const startTime = Date.now();
      
      const promises = Array(concurrentRequests).fill(null).map((_, index) => 
        baselineService.createBaseline({
          name: `Load Test Baseline ${index}`,
          projectId: `load-project-${index % 5}`, // 5 different projects
          branch: 'main',
          commit: `commit-${index}`
        })
      );
      
      const results = await Promise.all(promises);
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      expect(results).toHaveLength(concurrentRequests);
      expect(results.every(r => r.id)).toBe(true);
      expect(duration).toBeLessThan(10000); // Should complete within 10 seconds
      
      console.log(`Created ${concurrentRequests} baselines in ${duration}ms`);
      console.log(`Average: ${(duration / concurrentRequests).toFixed(2)}ms per baseline`);
    }, 15000);

    it('should maintain performance under memory pressure', async () => {
      const initialMemory = process.memoryUsage().heapUsed;
      const largeBaselines = [];
      
      for (let i = 0; i < 100; i++) {
        const baseline = await baselineService.createBaseline({
          name: `Memory Test Baseline ${i}`,
          projectId: 'memory-test-project',
          branch: 'main',
          commit: `memory-commit-${i}`,
          metrics: MockFactory.createMetrics({
            // Create large test results
            tests: Array(1000).fill(null).map(() => MockFactory.createTestResults(1)[0])
          })
        });
        
        largeBaselines.push(baseline);
        
        // Force garbage collection periodically
        if (i % 20 === 0 && global.gc) {
          global.gc();
        }
      }
      
      const finalMemory = process.memoryUsage().heapUsed;
      const memoryIncrease = finalMemory - initialMemory;
      const memoryPerBaseline = memoryIncrease / 100;
      
      expect(largeBaselines).toHaveLength(100);
      expect(memoryPerBaseline).toBeLessThan(5 * 1024 * 1024); // Less than 5MB per baseline
      
      console.log(`Memory increase: ${(memoryIncrease / 1024 / 1024).toFixed(2)}MB`);
      console.log(`Per baseline: ${(memoryPerBaseline / 1024).toFixed(2)}KB`);
    }, 30000);
  });

  describe('Comparison Engine Load', () => {
    it('should handle high-volume metric comparisons', async () => {
      // Create baseline with comprehensive metrics
      const baseline = await baselineService.createBaseline({
        name: 'Comparison Load Test Baseline',
        projectId: 'comparison-load-project',
        branch: 'main',
        commit: 'comparison-baseline-commit'
      });
      
      const baselineMetrics = MockFactory.createMetrics({
        testCount: 5000,
        passRate: 95.0,
        coverage: { lines: 85.0, branches: 80.0, functions: 90.0, statements: 85.0 },
        performance: { averageExecutionTime: 200.0, memoryUsage: 100.0 }
      });
      
      await baselineService.updateBaselineMetrics(baseline.id, baselineMetrics);
      
      // Run multiple concurrent comparisons
      const concurrentComparisons = 25;
      const startTime = Date.now();
      
      const comparisonPromises = Array(concurrentComparisons).fill(null).map((_, index) => {
        const currentMetrics = MockFactory.createMetrics({
          testCount: 5000 + Math.floor(Math.random() * 100),
          passRate: 90.0 + Math.random() * 10,
          coverage: {
            lines: 80.0 + Math.random() * 10,
            branches: 75.0 + Math.random() * 10,
            functions: 85.0 + Math.random() * 10,
            statements: 80.0 + Math.random() * 10
          },
          performance: {
            averageExecutionTime: 180.0 + Math.random() * 40,
            memoryUsage: 90.0 + Math.random() * 20
          }
        });
        
        return baselineService.compareMetrics(baseline.id, currentMetrics, {
          branch: `feature/load-test-${index}`,
          commit: `load-commit-${index}`
        });
      });
      
      const comparisons = await Promise.all(comparisonPromises);
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      expect(comparisons).toHaveLength(concurrentComparisons);
      expect(comparisons.every(c => c.id)).toBe(true);
      expect(duration).toBeLessThan(15000); // Should complete within 15 seconds
      
      console.log(`Completed ${concurrentComparisons} comparisons in ${duration}ms`);
      console.log(`Average: ${(duration / concurrentComparisons).toFixed(2)}ms per comparison`);
    }, 20000);

    it('should maintain accuracy under load', async () => {
      const baseline = await baselineService.createBaseline({
        name: 'Accuracy Under Load Baseline',
        projectId: 'accuracy-project',
        branch: 'main',
        commit: 'accuracy-baseline'
      });
      
      const baselineMetrics = {
        testCount: 100,
        passRate: 90.0,
        coverage: { lines: 85.0, branches: 80.0, functions: 90.0, statements: 85.0 }
      };
      
      await baselineService.updateBaselineMetrics(baseline.id, baselineMetrics);
      
      // Test with known degradation
      const degradedMetrics = {
        testCount: 100,
        passRate: 75.0, // 15% degradation
        coverage: { lines: 70.0, branches: 65.0, functions: 75.0, statements: 70.0 }
      };
      
      // Run comparison multiple times concurrently
      const accuracyTests = Array(20).fill(null).map(() => 
        baselineService.compareMetrics(baseline.id, degradedMetrics, {
          branch: 'feature/accuracy-test',
          commit: 'accuracy-commit'
        })
      );
      
      const results = await Promise.all(accuracyTests);
      
      // All results should be consistent
      results.forEach(result => {
        expect(result.summary.overallStatus).toBe('degradation');
        expect(result.metrics.passRate.change).toBe(-15.0);
        expect(result.metrics.passRate.status).toBe('degradation');
      });
    });
  });

  describe('Database Performance', () => {
    it('should handle large query loads efficiently', async () => {
      // Create multiple baselines for query testing
      const queryBaselines = [];
      for (let i = 0; i < 20; i++) {
        const baseline = await baselineService.createBaseline({
          name: `Query Test Baseline ${i}`,
          projectId: `query-project-${i % 5}`,
          branch: 'main',
          commit: `query-commit-${i}`
        });
        queryBaselines.push(baseline);
      }
      
      // Run concurrent queries
      const queryOperations = [
        () => baselineService.listBaselines({ limit: 50 }),
        () => baselineService.searchBaselines({ query: 'Query Test' }),
        () => baselineService.getBaselineHistory(queryBaselines[0].id),
        () => baselineService.getProjectBaselines('query-project-0'),
        () => baselineService.getBaseline(queryBaselines[Math.floor(Math.random() * queryBaselines.length)].id)
      ];
      
      const concurrentQueries = 100;
      const startTime = Date.now();
      
      const queryPromises = Array(concurrentQueries).fill(null).map(() => {
        const operation = queryOperations[Math.floor(Math.random() * queryOperations.length)];
        return operation();
      });
      
      const queryResults = await Promise.all(queryPromises);
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      expect(queryResults).toHaveLength(concurrentQueries);
      expect(queryResults.every(r => r !== null)).toBe(true);
      expect(duration).toBeLessThan(5000); // Queries should be fast
      
      console.log(`Executed ${concurrentQueries} queries in ${duration}ms`);
      console.log(`Average query time: ${(duration / concurrentQueries).toFixed(2)}ms`);
    });

    it('should handle database connection pooling under load', async () => {
      const connectionTests = [];
      const maxConnections = 50;
      
      // Simulate many concurrent database operations
      for (let i = 0; i < maxConnections; i++) {
        connectionTests.push(
          baselineService.database.transaction(async (trx) => {
            // Simulate complex transaction
            const baseline = await trx('baselines').insert({
              name: `Connection Test ${i}`,
              project_id: 'connection-test',
              branch: 'main',
              commit: `conn-commit-${i}`,
              created_at: new Date().toISOString()
            }).returning('*');
            
            await trx('baseline_metrics').insert({
              baseline_id: baseline[0].id,
              test_count: 10,
              pass_rate: 90.0,
              created_at: new Date().toISOString()
            });
            
            return baseline[0];
          })
        );
      }
      
      const startTime = Date.now();
      const results = await Promise.all(connectionTests);
      const endTime = Date.now();
      
      expect(results).toHaveLength(maxConnections);
      expect(results.every(r => r.id)).toBe(true);
      
      console.log(`${maxConnections} transactions completed in ${endTime - startTime}ms`);
    });
  });

  describe('Report Generation Load', () => {
    it('should generate reports efficiently under load', async () => {
      // Create baseline and comparisons for report testing
      const reportBaseline = await baselineService.createBaseline({
        name: 'Report Load Test Baseline',
        projectId: 'report-load-project',
        branch: 'main',
        commit: 'report-baseline'
      });
      
      const comparisons = [];
      for (let i = 0; i < 10; i++) {
        const comparison = await baselineService.compareMetrics(
          reportBaseline.id,
          MockFactory.createMetrics(),
          {
            branch: `feature/report-test-${i}`,
            commit: `report-commit-${i}`
          }
        );
        comparisons.push(comparison);
      }
      
      // Generate reports concurrently
      const reportGenerator = baselineService.getReportGenerator();
      const reportFormats = ['html', 'json', 'pdf'];
      const concurrentReports = 15;
      
      const startTime = Date.now();
      
      const reportPromises = Array(concurrentReports).fill(null).map((_, index) => {
        const comparison = comparisons[index % comparisons.length];
        const format = reportFormats[index % reportFormats.length];
        
        return reportGenerator.generateSummaryReport(
          comparison,
          reportBaseline,
          {
            format: format,
            fileName: `load-test-report-${index}.${format}`,
            includeCharts: format === 'html',
            compress: false
          }
        );
      });
      
      const reports = await Promise.all(reportPromises);
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      expect(reports).toHaveLength(concurrentReports);
      expect(reports.every(r => r.fileName)).toBe(true);
      expect(duration).toBeLessThan(20000); // Should complete within 20 seconds
      
      console.log(`Generated ${concurrentReports} reports in ${duration}ms`);
      console.log(`Average: ${(duration / concurrentReports).toFixed(2)}ms per report`);
    }, 25000);

    it('should handle large report datasets', async () => {
      // Create baseline with large dataset
      const largeDataBaseline = await baselineService.createBaseline({
        name: 'Large Dataset Baseline',
        projectId: 'large-data-project',
        branch: 'main',
        commit: 'large-data-commit'
      });
      
      // Create comparison with many test results
      const largeComparison = await baselineService.compareMetrics(
        largeDataBaseline.id,
        {
          testCount: 10000,
          passRate: 95.0,
          coverage: { lines: 85.0, branches: 80.0, functions: 90.0, statements: 85.0 },
          tests: Array(10000).fill(null).map((_, i) => ({
            name: `test_${i}`,
            status: Math.random() > 0.05 ? 'passed' : 'failed',
            duration: Math.floor(Math.random() * 1000),
            file: `test_file_${i % 100}.js`
          }))
        },
        {
          branch: 'feature/large-dataset',
          commit: 'large-dataset-commit'
        }
      );
      
      const reportGenerator = baselineService.getReportGenerator();
      const startTime = Date.now();
      
      const largeReport = await reportGenerator.generateDetailedReport({
        comparison: largeComparison,
        baseline: largeDataBaseline,
        format: 'html',
        includeTestDetails: true,
        includeCharts: true
      });
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      expect(largeReport.size).toBeGreaterThan(0);
      expect(duration).toBeLessThan(30000); // Should complete within 30 seconds
      
      console.log(`Generated large report (10k tests) in ${duration}ms`);
      console.log(`Report size: ${(largeReport.size / 1024 / 1024).toFixed(2)}MB`);
    }, 35000);
  });

  describe('Memory and Resource Management', () => {
    it('should maintain stable memory usage under sustained load', async () => {
      const memorySnapshots = [];
      const iterations = 50;
      
      for (let i = 0; i < iterations; i++) {
        // Perform various operations
        const baseline = await baselineService.createBaseline({
          name: `Memory Test ${i}`,
          projectId: 'memory-project',
          branch: 'main',
          commit: `memory-commit-${i}`
        });
        
        const comparison = await baselineService.compareMetrics(
          baseline.id,
          MockFactory.createMetrics(),
          { branch: 'feature/memory-test', commit: `memory-test-${i}` }
        );
        
        const reportGenerator = baselineService.getReportGenerator();
        await reportGenerator.generateSummaryReport(comparison, baseline, {
          format: 'json',
          fileName: `memory-report-${i}.json`
        });
        
        // Take memory snapshot every 10 iterations
        if (i % 10 === 0) {
          memorySnapshots.push({
            iteration: i,
            memory: process.memoryUsage()
          });
        }
        
        // Force cleanup
        if (global.gc && i % 25 === 0) {
          global.gc();
        }
      }
      
      // Analyze memory growth
      const initialMemory = memorySnapshots[0].memory.heapUsed;
      const finalMemory = memorySnapshots[memorySnapshots.length - 1].memory.heapUsed;
      const memoryGrowth = finalMemory - initialMemory;
      const growthPerIteration = memoryGrowth / iterations;
      
      console.log('Memory usage snapshots:');
      memorySnapshots.forEach(snapshot => {
        console.log(`Iteration ${snapshot.iteration}: ${(snapshot.memory.heapUsed / 1024 / 1024).toFixed(2)}MB`);
      });
      
      // Memory growth should be reasonable (less than 1MB per iteration)
      expect(growthPerIteration).toBeLessThan(1024 * 1024);
      
      console.log(`Total memory growth: ${(memoryGrowth / 1024 / 1024).toFixed(2)}MB`);
      console.log(`Growth per iteration: ${(growthPerIteration / 1024).toFixed(2)}KB`);
    }, 60000);

    it('should handle cleanup of temporary resources', async () => {
      const initialFiles = await baselineService.getTempFileCount();
      const tempOperations = [];
      
      // Create operations that generate temporary files
      for (let i = 0; i < 20; i++) {
        tempOperations.push(
          baselineService.exportBaseline(`temp-baseline-${i}`, {
            format: 'zip',
            includeReports: true,
            cleanup: true
          })
        );
      }
      
      await Promise.all(tempOperations);
      
      // Wait for cleanup
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const finalFiles = await baselineService.getTempFileCount();
      
      expect(finalFiles).toBeLessThanOrEqual(initialFiles + 5); // Allow some temporary files
    });
  });
});
