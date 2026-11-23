import { Request, Response } from 'express';
import { DashboardConfig, DashboardConfigSchema, ApiResponse } from '@monitoring-dashboard/shared';
import { cacheService } from '../../cache/redis-cache';
import { logger, performanceLogger } from '../../utils/logger';

export class DashboardController {
  private readonly CACHE_TTL = 600; // 10 minutes
  private dashboardConfigs: Map<string, DashboardConfig> = new Map();

  // Get dashboard summary with key metrics
  public async getDashboardSummary(req: Request, res: Response): Promise<void> {
    const perf = performanceLogger.start('getDashboardSummary');

    try {
      const cacheKey = 'dashboard:summary';
      let summary = await cacheService.get<any>(cacheKey);

      if (!summary) {
        // This would typically fetch from your data stores
        // For demo purposes, we'll create mock data
        summary = {
          tests: {
            total: 1247,
            passed: 1156,
            failed: 67,
            skipped: 24,
            passRate: 92.7,
            avgDuration: 2.4,
            trend: 'improving'
          },
          coverage: {
            overall: 87.3,
            lines: 89.1,
            functions: 85.7,
            branches: 84.2,
            statements: 88.9,
            trend: 'stable'
          },
          performance: {
            avgResponseTime: 145,
            p95ResponseTime: 320,
            throughput: 1240,
            errorRate: 0.8,
            trend: 'improving'
          },
          alerts: {
            total: 23,
            critical: 2,
            high: 5,
            medium: 11,
            low: 5,
            resolved: 18,
            unresolved: 5
          },
          activity: {
            testsLast24h: 89,
            deploymentsLast24h: 3,
            alertsLast24h: 7,
            coverageChanges: '+2.1%'
          }
        };

        await cacheService.set(cacheKey, summary, this.CACHE_TTL);
      }

      perf.end();

      res.json({
        success: true,
        data: summary,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      perf.end();
      logger.error('Error in getDashboardSummary:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve dashboard summary',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get dashboard configuration
  public async getDashboardConfig(req: Request, res: Response): Promise<void> {
    try {
      const { id = 'default' } = req.query;
      const cacheKey = `dashboard:config:${id}`;

      let config = await cacheService.get<DashboardConfig>(cacheKey);

      if (!config) {
        config = this.dashboardConfigs.get(id as string);

        if (!config) {
          // Return default configuration
          config = this.getDefaultDashboardConfig();
        }

        await cacheService.set(cacheKey, config, this.CACHE_TTL);
      }

      res.json({
        success: true,
        data: config,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getDashboardConfig:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve dashboard configuration',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Save dashboard configuration
  public async saveDashboardConfig(req: Request, res: Response): Promise<void> {
    try {
      const configData = DashboardConfigSchema.parse(req.body);

      this.dashboardConfigs.set(configData.id, configData);

      // Invalidate cache
      await cacheService.del(`dashboard:config:${configData.id}`);

      logger.info(`Dashboard configuration saved: ${configData.id}`);

      res.json({
        success: true,
        data: configData,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in saveDashboardConfig:', error);
      res.status(400).json({
        success: false,
        error: 'Invalid dashboard configuration',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get trend data for dashboard charts
  public async getTrends(req: Request, res: Response): Promise<void> {
    try {
      const { metric, period = 'day', limit = 30 } = req.query;
      const cacheKey = `dashboard:trends:${metric}:${period}:${limit}`;

      let trends = await cacheService.get<any>(cacheKey);

      if (!trends) {
        // Generate mock trend data
        trends = this.generateMockTrends(metric as string, period as string, Number(limit));
        await cacheService.set(cacheKey, trends, this.CACHE_TTL);
      }

      res.json({
        success: true,
        data: trends,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getTrends:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve trend data',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get real-time data for live updates
  public async getRealtimeData(req: Request, res: Response): Promise<void> {
    try {
      const cacheKey = 'dashboard:realtime';
      let realtimeData = await cacheService.get<any>(cacheKey);

      if (!realtimeData) {
        realtimeData = {
          activeTests: 12,
          queuedTests: 5,
          runningBuilds: 3,
          recentAlerts: [
            {
              id: 'alert-1',
              type: 'performance_degradation',
              severity: 'medium',
              title: 'API response time increased',
              timestamp: new Date(Date.now() - 300000).toISOString()
            },
            {
              id: 'alert-2',
              type: 'coverage_drop',
              severity: 'low',
              title: 'Coverage dropped below 85%',
              timestamp: new Date(Date.now() - 600000).toISOString()
            }
          ],
          systemStatus: {
            api: 'healthy',
            database: 'healthy',
            cache: 'healthy',
            monitoring: 'healthy'
          },
          metrics: {
            testsPerMinute: 3.2,
            errorRate: 0.4,
            avgResponseTime: 142,
            activeConnections: 45
          }
        };

        await cacheService.set(cacheKey, realtimeData, 30); // Short cache for real-time data
      }

      res.json({
        success: true,
        data: realtimeData,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getRealtimeData:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve real-time data',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get default dashboard configuration
  private getDefaultDashboardConfig(): DashboardConfig {
    return {
      id: 'default',
      name: 'Default Dashboard',
      layout: [
        {
          id: 'test-summary',
          type: 'metric',
          position: { x: 0, y: 0, width: 6, height: 4 },
          config: {
            title: 'Test Summary',
            metrics: ['total', 'passed', 'failed', 'pass_rate']
          }
        },
        {
          id: 'coverage-chart',
          type: 'chart',
          position: { x: 6, y: 0, width: 6, height: 4 },
          config: {
            title: 'Coverage Trends',
            chartType: 'line',
            metric: 'coverage'
          }
        },
        {
          id: 'performance-heatmap',
          type: 'heatmap',
          position: { x: 0, y: 4, width: 8, height: 6 },
          config: {
            title: 'Performance Heatmap',
            metric: 'response_time'
          }
        },
        {
          id: 'alerts-table',
          type: 'table',
          position: { x: 8, y: 4, width: 4, height: 6 },
          config: {
            title: 'Recent Alerts',
            columns: ['severity', 'type', 'timestamp']
          }
        },
        {
          id: 'test-timeline',
          type: 'timeline',
          position: { x: 0, y: 10, width: 12, height: 4 },
          config: {
            title: 'Test Execution Timeline',
            timeRange: '24h'
          }
        }
      ],
      filters: {
        timeRange: '24h',
        testSuites: [],
        environments: ['all']
      },
      theme: 'dark'
    };
  }

  // Generate mock trend data for demonstration
  private generateMockTrends(metric: string, period: string, limit: number): any {
    const data = [];
    const now = new Date();

    for (let i = limit - 1; i >= 0; i--) {
      const date = new Date(now);

      if (period === 'hour') {
        date.setHours(date.getHours() - i);
      } else if (period === 'day') {
        date.setDate(date.getDate() - i);
      } else if (period === 'week') {
        date.setDate(date.getDate() - (i * 7));
      }

      let value: number;
      switch (metric) {
        case 'tests':
          value = Math.floor(Math.random() * 100) + 950;
          break;
        case 'coverage':
          value = Math.random() * 10 + 85;
          break;
        case 'performance':
          value = Math.random() * 50 + 120;
          break;
        case 'alerts':
          value = Math.floor(Math.random() * 10);
          break;
        default:
          value = Math.random() * 100;
      }

      data.push({
        timestamp: date.toISOString(),
        value: Math.round(value * 100) / 100
      });
    }

    return {
      metric,
      period,
      data
    };
  }
}