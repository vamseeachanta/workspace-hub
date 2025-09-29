const ReportGenerator = require('../../src/reports/report-generator');
const MockFactory = require('../fixtures/mock-factories');
const { sampleBaseline, sampleComparison, sampleAlerts } = require('../fixtures/baseline-data');
const fs = require('fs').promises;
const path = require('path');

describe('ReportGenerator', () => {
  let reportGenerator;
  let mockLogger;
  let mockTemplateEngine;
  let mockFileSystem;

  beforeEach(() => {
    mockLogger = createMockLogger();
    mockTemplateEngine = {
      render: jest.fn(),
      compile: jest.fn(),
      registerHelper: jest.fn()
    };
    mockFileSystem = {
      writeFile: jest.fn(),
      readFile: jest.fn(),
      ensureDir: jest.fn()
    };
    
    reportGenerator = new ReportGenerator({
      logger: mockLogger,
      templateEngine: mockTemplateEngine,
      fileSystem: mockFileSystem
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    it('should initialize with default configuration', () => {
      const generator = new ReportGenerator();
      expect(generator.config).toBeDefined();
      expect(generator.config.outputDir).toBeDefined();
    });

    it('should use custom configuration', () => {
      const customConfig = {
        outputDir: '/custom/reports',
        templateDir: '/custom/templates'
      };
      
      const generator = new ReportGenerator({ config: customConfig });
      expect(generator.config.outputDir).toBe('/custom/reports');
      expect(generator.config.templateDir).toBe('/custom/templates');
    });

    it('should register template helpers', () => {
      expect(mockTemplateEngine.registerHelper).toHaveBeenCalledWith('formatPercent', expect.any(Function));
      expect(mockTemplateEngine.registerHelper).toHaveBeenCalledWith('formatDuration', expect.any(Function));
      expect(mockTemplateEngine.registerHelper).toHaveBeenCalledWith('statusIcon', expect.any(Function));
    });
  });

  describe('generateSummaryReport', () => {
    it('should generate HTML summary report', async () => {
      const comparisonData = sampleComparison;
      const baseline = sampleBaseline;
      
      const expectedHtml = '<html><body>Summary Report</body></html>';
      mockTemplateEngine.render.mockResolvedValueOnce(expectedHtml);
      mockFileSystem.writeFile.mockResolvedValueOnce();

      const result = await reportGenerator.generateSummaryReport(comparisonData, baseline, {
        format: 'html',
        fileName: 'summary-report.html'
      });

      expect(mockTemplateEngine.render).toHaveBeenCalledWith(
        'summary-report.html',
        expect.objectContaining({
          comparison: comparisonData,
          baseline: baseline,
          generatedAt: expect.any(String)
        })
      );
      
      expect(result).toEqual({
        fileName: 'summary-report.html',
        filePath: expect.stringContaining('summary-report.html'),
        format: 'html',
        size: expectedHtml.length,
        generatedAt: expect.any(String)
      });
    });

    it('should generate PDF summary report', async () => {
      const comparisonData = sampleComparison;
      const baseline = sampleBaseline;
      
      // Mock PDF generation
      reportGenerator.generatePDF = jest.fn().mockResolvedValueOnce({
        buffer: Buffer.from('PDF content'),
        size: 1024
      });

      const result = await reportGenerator.generateSummaryReport(comparisonData, baseline, {
        format: 'pdf',
        fileName: 'summary-report.pdf'
      });

      expect(reportGenerator.generatePDF).toHaveBeenCalled();
      expect(result.format).toBe('pdf');
      expect(result.size).toBe(1024);
    });

    it('should generate JSON summary report', async () => {
      const comparisonData = sampleComparison;
      const baseline = sampleBaseline;

      const result = await reportGenerator.generateSummaryReport(comparisonData, baseline, {
        format: 'json',
        fileName: 'summary-report.json'
      });

      expect(mockFileSystem.writeFile).toHaveBeenCalledWith(
        expect.stringContaining('summary-report.json'),
        expect.stringMatching(/^\{.*\}$/s) // Valid JSON
      );
      
      expect(result.format).toBe('json');
    });

    it('should include trend analysis when historical data provided', async () => {
      const comparisonData = sampleComparison;
      const baseline = sampleBaseline;
      const historicalData = [
        MockFactory.createComparison('baseline-1', 'run-1'),
        MockFactory.createComparison('baseline-1', 'run-2'),
        MockFactory.createComparison('baseline-1', 'run-3')
      ];

      await reportGenerator.generateSummaryReport(comparisonData, baseline, {
        format: 'html',
        includeHistoricalData: historicalData
      });

      expect(mockTemplateEngine.render).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          trends: expect.objectContaining({
            passRateTrend: expect.any(Array),
            coverageTrend: expect.any(Array),
            performanceTrend: expect.any(Array)
          })
        })
      );
    });
  });

  describe('generateDetailedReport', () => {
    it('should generate detailed comparison report', async () => {
      const comparisonData = sampleComparison;
      const baseline = sampleBaseline;
      const testResults = MockFactory.createTestRun();
      
      const expectedHtml = '<html><body>Detailed Report</body></html>';
      mockTemplateEngine.render.mockResolvedValueOnce(expectedHtml);

      const result = await reportGenerator.generateDetailedReport({
        comparison: comparisonData,
        baseline: baseline,
        testResults: testResults,
        format: 'html'
      });

      expect(mockTemplateEngine.render).toHaveBeenCalledWith(
        'detailed-report.html',
        expect.objectContaining({
          comparison: comparisonData,
          baseline: baseline,
          testResults: testResults,
          sections: expect.objectContaining({
            overview: expect.any(Object),
            metrics: expect.any(Object),
            violations: expect.any(Object),
            testDetails: expect.any(Object)
          })
        })
      );
      
      expect(result.format).toBe('html');
    });

    it('should include code coverage visualization', async () => {
      const comparisonData = {
        ...sampleComparison,
        coverageDetails: {
          files: [
            {
              path: '/src/auth.js',
              coverage: { lines: 85.0, branches: 78.0 },
              uncoveredLines: [45, 67, 89]
            },
            {
              path: '/src/utils.js',
              coverage: { lines: 92.0, branches: 88.0 },
              uncoveredLines: [12, 34]
            }
          ]
        }
      };

      await reportGenerator.generateDetailedReport({
        comparison: comparisonData,
        format: 'html',
        includeCoverageDetails: true
      });

      expect(mockTemplateEngine.render).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          coverageVisualization: expect.objectContaining({
            fileDetails: expect.any(Array),
            overallCoverage: expect.any(Object)
          })
        })
      );
    });

    it('should include performance charts', async () => {
      const performanceData = {
        testDurations: [
          { name: 'test1', baseline: 100, current: 120 },
          { name: 'test2', baseline: 200, current: 180 },
          { name: 'test3', baseline: 150, current: 300 }
        ],
        memoryUsage: {
          baseline: [100, 105, 102],
          current: [110, 125, 115]
        }
      };

      await reportGenerator.generateDetailedReport({
        comparison: { ...sampleComparison, performanceData },
        format: 'html',
        includeCharts: true
      });

      expect(mockTemplateEngine.render).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          charts: expect.objectContaining({
            performanceChart: expect.any(Object),
            memoryChart: expect.any(Object)
          })
        })
      );
    });
  });

  describe('generateAlertReport', () => {
    it('should generate alert summary report', async () => {
      const alerts = sampleAlerts;
      const baseline = sampleBaseline;

      const result = await reportGenerator.generateAlertReport(alerts, baseline, {
        format: 'html',
        severity: 'critical'
      });

      expect(mockTemplateEngine.render).toHaveBeenCalledWith(
        'alert-report.html',
        expect.objectContaining({
          alerts: expect.any(Array),
          baseline: baseline,
          summary: expect.objectContaining({
            totalAlerts: expect.any(Number),
            criticalAlerts: expect.any(Number),
            warningAlerts: expect.any(Number)
          })
        })
      );
      
      expect(result.format).toBe('html');
    });

    it('should filter alerts by severity', async () => {
      const alerts = [
        { ...sampleAlerts[0], severity: 'critical' },
        { ...sampleAlerts[1], severity: 'warning' },
        { severity: 'info', type: 'info_alert' }
      ];

      await reportGenerator.generateAlertReport(alerts, sampleBaseline, {
        format: 'html',
        severity: 'critical'
      });

      const renderCall = mockTemplateEngine.render.mock.calls[0];
      const templateData = renderCall[1];
      
      expect(templateData.alerts).toHaveLength(1);
      expect(templateData.alerts[0].severity).toBe('critical');
    });

    it('should group alerts by type', async () => {
      const alerts = [
        { type: 'threshold_violation', severity: 'critical' },
        { type: 'threshold_violation', severity: 'warning' },
        { type: 'performance_degradation', severity: 'warning' }
      ];

      await reportGenerator.generateAlertReport(alerts, sampleBaseline, {
        format: 'html',
        groupBy: 'type'
      });

      const renderCall = mockTemplateEngine.render.mock.calls[0];
      const templateData = renderCall[1];
      
      expect(templateData.alertGroups).toEqual({
        threshold_violation: expect.arrayContaining([expect.any(Object)]),
        performance_degradation: expect.arrayContaining([expect.any(Object)])
      });
    });
  });

  describe('generateTrendReport', () => {
    it('should generate trend analysis report', async () => {
      const historicalData = Array(30).fill(null).map((_, i) => 
        MockFactory.createComparison('baseline-1', `run-${i}`)
      );

      const result = await reportGenerator.generateTrendReport(historicalData, {
        format: 'html',
        timeframe: '30d'
      });

      expect(mockTemplateEngine.render).toHaveBeenCalledWith(
        'trend-report.html',
        expect.objectContaining({
          trends: expect.objectContaining({
            passRate: expect.any(Object),
            coverage: expect.any(Object),
            performance: expect.any(Object)
          }),
          statistics: expect.objectContaining({
            mean: expect.any(Object),
            median: expect.any(Object),
            standardDeviation: expect.any(Object)
          }),
          forecasting: expect.any(Object)
        })
      );
    });

    it('should calculate trend statistics', () => {
      const data = [85, 87, 89, 91, 88, 90, 92, 89, 91, 93];
      
      const stats = reportGenerator.calculateTrendStatistics(data);
      
      expect(stats).toEqual({
        mean: expect.any(Number),
        median: expect.any(Number),
        standardDeviation: expect.any(Number),
        min: 85,
        max: 93,
        trend: expect.stringMatching(/increasing|decreasing|stable/),
        correlation: expect.any(Number)
      });
    });

    it('should detect trend direction', () => {
      const increasingData = [70, 75, 80, 85, 90];
      const decreasingData = [90, 85, 80, 75, 70];
      const stableData = [80, 81, 79, 80, 82];
      
      expect(reportGenerator.detectTrendDirection(increasingData)).toBe('increasing');
      expect(reportGenerator.detectTrendDirection(decreasingData)).toBe('decreasing');
      expect(reportGenerator.detectTrendDirection(stableData)).toBe('stable');
    });

    it('should generate forecasting data', () => {
      const historicalData = [85, 87, 89, 91, 88, 90, 92];
      
      const forecast = reportGenerator.generateForecast(historicalData, 5);
      
      expect(forecast).toEqual({
        predictions: expect.arrayContaining([
          expect.objectContaining({
            value: expect.any(Number),
            confidence: expect.any(Number)
          })
        ]),
        model: expect.any(String),
        accuracy: expect.any(Number)
      });
    });
  });

  describe('template helpers', () => {
    it('should format percentages correctly', () => {
      const formatPercent = reportGenerator.templateHelpers.formatPercent;
      
      expect(formatPercent(0.856)).toBe('85.6%');
      expect(formatPercent(85.6)).toBe('85.6%'); // Already percentage
      expect(formatPercent(1.0)).toBe('100.0%');
      expect(formatPercent(0)).toBe('0.0%');
    });

    it('should format durations correctly', () => {
      const formatDuration = reportGenerator.templateHelpers.formatDuration;
      
      expect(formatDuration(1000)).toBe('1.0s');
      expect(formatDuration(500)).toBe('500ms');
      expect(formatDuration(2500)).toBe('2.5s');
      expect(formatDuration(65000)).toBe('1m 5s');
    });

    it('should provide status icons', () => {
      const statusIcon = reportGenerator.templateHelpers.statusIcon;
      
      expect(statusIcon('improvement')).toContain('green');
      expect(statusIcon('degradation')).toContain('red');
      expect(statusIcon('stable')).toContain('gray');
      expect(statusIcon('warning')).toContain('orange');
      expect(statusIcon('critical')).toContain('red');
    });

    it('should format change values', () => {
      const formatChange = reportGenerator.templateHelpers.formatChange;
      
      expect(formatChange(5.0)).toBe('+5.0');
      expect(formatChange(-3.2)).toBe('-3.2');
      expect(formatChange(0)).toBe('0.0');
      expect(formatChange(0.1)).toBe('+0.1');
    });
  });

  describe('export functionality', () => {
    it('should export report to multiple formats', async () => {
      const comparisonData = sampleComparison;
      const formats = ['html', 'pdf', 'json'];

      const results = await reportGenerator.exportReport(comparisonData, {
        formats: formats,
        fileName: 'multi-format-report'
      });

      expect(results).toHaveLength(3);
      expect(results.map(r => r.format)).toEqual(formats);
    });

    it('should compress reports when requested', async () => {
      reportGenerator.compressFiles = jest.fn().mockResolvedValueOnce({
        zipFile: 'reports.zip',
        originalSize: 1024,
        compressedSize: 512
      });

      const result = await reportGenerator.exportReport(sampleComparison, {
        formats: ['html', 'json'],
        compress: true
      });

      expect(reportGenerator.compressFiles).toHaveBeenCalled();
      expect(result.compressed).toBe(true);
      expect(result.zipFile).toBe('reports.zip');
    });

    it('should email reports when configured', async () => {
      const emailService = {
        send: jest.fn().mockResolvedValueOnce({ messageId: 'msg-123' })
      };
      
      reportGenerator.emailService = emailService;

      await reportGenerator.exportReport(sampleComparison, {
        formats: ['pdf'],
        email: {
          to: ['team@example.com'],
          subject: 'Test Report',
          body: 'Please find the test report attached.'
        }
      });

      expect(emailService.send).toHaveBeenCalledWith(expect.objectContaining({
        to: ['team@example.com'],
        subject: 'Test Report',
        attachments: expect.any(Array)
      }));
    });
  });

  describe('error handling and edge cases', () => {
    it('should handle template rendering errors', async () => {
      const templateError = new Error('Template not found');
      mockTemplateEngine.render.mockRejectedValueOnce(templateError);

      await expect(reportGenerator.generateSummaryReport(sampleComparison, sampleBaseline))
        .rejects.toThrow('Failed to generate report');
      
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Template rendering failed',
        expect.objectContaining({ error: templateError.message })
      );
    });

    it('should handle file system errors', async () => {
      const fsError = new Error('Permission denied');
      mockFileSystem.writeFile.mockRejectedValueOnce(fsError);

      await expect(reportGenerator.generateSummaryReport(sampleComparison, sampleBaseline))
        .rejects.toThrow('Failed to save report');
    });

    it('should handle empty data gracefully', async () => {
      const emptyComparison = {
        summary: { overallStatus: 'stable', changesDetected: 0 },
        metrics: {},
        violations: []
      };

      const result = await reportGenerator.generateSummaryReport(emptyComparison, {});

      expect(result).toBeDefined();
      expect(mockTemplateEngine.render).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          comparison: emptyComparison
        })
      );
    });

    it('should handle large datasets efficiently', async () => {
      const largeComparison = {
        ...sampleComparison,
        testResults: Array(10000).fill(null).map(() => MockFactory.createTestResults(1)[0])
      };

      const startTime = Date.now();
      await reportGenerator.generateDetailedReport({
        comparison: largeComparison,
        format: 'html'
      });
      const endTime = Date.now();

      // Should complete within reasonable time
      expect(endTime - startTime).toBeLessThan(5000);
    });

    it('should sanitize user inputs in reports', async () => {
      const maliciousComparison = {
        ...sampleComparison,
        summary: {
          ...sampleComparison.summary,
          description: '<script>alert("xss")</script>'
        }
      };

      await reportGenerator.generateSummaryReport(maliciousComparison, sampleBaseline);

      const renderCall = mockTemplateEngine.render.mock.calls[0];
      const templateData = renderCall[1];
      
      expect(templateData.comparison.summary.description)
        .toBe('&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;');
    });
  });
});
