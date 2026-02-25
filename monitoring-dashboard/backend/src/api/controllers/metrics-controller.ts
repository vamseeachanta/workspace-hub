import { Request, Response } from 'express';
import { PerformanceMetric, PerformanceMetricSchema, ApiResponse } from '@monitoring-dashboard/shared';
import { cacheService } from '../../cache/redis-cache';
import { logger, performanceLogger } from '../../utils/logger';
import { v4 as uuidv4 } from 'uuid';

export class MetricsController {
  private readonly CACHE_TTL = 300; // 5 minutes
  private metrics: Map<string, PerformanceMetric> = new Map();

  // Get metrics with filtering and aggregation
  public async getMetrics(req: Request, res: Response): Promise<void> {
    const perf = performanceLogger.start('getMetrics');

    try {
      const {
        type,
        testSuite,
        startDate,
        endDate,
        aggregation = 'none',
        interval = 'hour'
      } = req.query;

      const cacheKey = `metrics:${JSON.stringify(req.query)}`;
      const cached = await cacheService.get<any>(cacheKey);

      if (cached) {
        perf.end();
        res.json({
          success: true,
          data: cached,
          timestamp: new Date().toISOString()
        } as ApiResponse);
        return;
      }

      let filteredMetrics = Array.from(this.metrics.values());

      // Apply filters
      if (type) {
        filteredMetrics = filteredMetrics.filter(metric => metric.metric === type);
      }

      if (testSuite) {
        filteredMetrics = filteredMetrics.filter(metric => metric.testSuite === testSuite);
      }

      if (startDate || endDate) {
        filteredMetrics = filteredMetrics.filter(metric => {
          const metricDate = new Date(metric.timestamp);
          const start = startDate ? new Date(startDate as string) : new Date(0);
          const end = endDate ? new Date(endDate as string) : new Date();
          return metricDate >= start && metricDate <= end;
        });
      }

      // Sort by timestamp
      filteredMetrics.sort((a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );

      let result: any = filteredMetrics;

      // Apply aggregation if requested
      if (aggregation !== 'none') {
        result = this.aggregateMetrics(filteredMetrics, aggregation as string, interval as string);
      }

      await cacheService.set(cacheKey, result, this.CACHE_TTL);

      perf.end();

      res.json({
        success: true,
        data: result,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      perf.end();
      logger.error('Error in getMetrics:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve metrics',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Record a new metric
  public async recordMetric(req: Request, res: Response): Promise<void> {
    try {
      const metricData = PerformanceMetricSchema.parse({
        ...req.body,
        id: req.body.id || uuidv4(),
        timestamp: req.body.timestamp || new Date().toISOString()
      });

      this.metrics.set(metricData.id, metricData);

      // Invalidate related cache
      await this.invalidateMetricsCache();

      logger.info(`Metric recorded: ${metricData.metric} for ${metricData.testSuite}`);

      res.status(201).json({
        success: true,
        data: metricData,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in recordMetric:', error);
      res.status(400).json({
        success: false,
        error: 'Invalid metric data',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get metrics by type
  public async getMetricsByType(req: Request, res: Response): Promise<void> {
    try {
      const { type } = req.params;
      const { limit = 100 } = req.query;

      const cacheKey = `metrics:type:${type}:${limit}`;
      let metrics = await cacheService.get<PerformanceMetric[]>(cacheKey);

      if (!metrics) {
        metrics = Array.from(this.metrics.values())
          .filter(metric => metric.metric === type)
          .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
          .slice(0, Number(limit));

        await cacheService.set(cacheKey, metrics, this.CACHE_TTL);
      }

      res.json({
        success: true,
        data: metrics,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getMetricsByType:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve metrics by type',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get metric trends
  public async getMetricTrends(req: Request, res: Response): Promise<void> {
    try {
      const { type } = req.params;
      const { days = 7, testSuite } = req.query;

      const cacheKey = `metrics:trends:${type}:${days}:${testSuite || 'all'}`;
      let trends = await cacheService.get<any>(cacheKey);

      if (!trends) {
        const endDate = new Date();
        const startDate = new Date(endDate.getTime() - (Number(days) * 24 * 60 * 60 * 1000));

        let filteredMetrics = Array.from(this.metrics.values())
          .filter(metric => {
            const metricDate = new Date(metric.timestamp);
            return metric.metric === type &&
                   metricDate >= startDate &&
                   metricDate <= endDate &&
                   (!testSuite || metric.testSuite === testSuite);
          });

        // Group by day and calculate averages
        const groupedMetrics = this.groupMetricsByDay(filteredMetrics);

        trends = {
          type,
          testSuite: testSuite || 'all',
          period: `${days} days`,
          data: groupedMetrics,
          summary: this.calculateTrendSummary(groupedMetrics)
        };

        await cacheService.set(cacheKey, trends, this.CACHE_TTL);
      }

      res.json({
        success: true,
        data: trends,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getMetricTrends:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve metric trends',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get performance metrics summary
  public async getPerformanceMetrics(req: Request, res: Response): Promise<void> {
    try {
      const cacheKey = 'metrics:performance:summary';
      let summary = await cacheService.get<any>(cacheKey);

      if (!summary) {
        const allMetrics = Array.from(this.metrics.values());

        // Calculate summaries by metric type
        const metricTypes = ['duration', 'memory', 'cpu', 'throughput'];
        const summaries: any = {};

        for (const metricType of metricTypes) {
          const typeMetrics = allMetrics.filter(m => m.metric === metricType);

          if (typeMetrics.length > 0) {
            const values = typeMetrics.map(m => m.value);
            summaries[metricType] = {
              count: typeMetrics.length,
              min: Math.min(...values),
              max: Math.max(...values),
              average: values.reduce((sum, val) => sum + val, 0) / values.length,
              latest: typeMetrics.sort((a, b) =>
                new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
              )[0]
            };
          }
        }

        // Calculate performance trends (last 24 hours)
        const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
        const recentMetrics = allMetrics.filter(m =>
          new Date(m.timestamp) >= twentyFourHoursAgo
        );

        summary = {
          overall: summaries,
          recent24h: {
            totalMetrics: recentMetrics.length,
            byType: this.groupMetricsByType(recentMetrics)
          },
          testSuites: this.getTestSuiteSummary(allMetrics)
        };

        await cacheService.set(cacheKey, summary, this.CACHE_TTL);
      }

      res.json({
        success: true,
        data: summary,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getPerformanceMetrics:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve performance metrics',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Aggregate metrics based on specified method and interval
  private aggregateMetrics(metrics: PerformanceMetric[], aggregation: string, interval: string): any {
    const grouped = this.groupMetricsByInterval(metrics, interval);

    const aggregated = Object.entries(grouped).map(([timeKey, metrics]) => {
      const values = metrics.map(m => m.value);

      let aggregatedValue: number;
      switch (aggregation) {
        case 'avg':
          aggregatedValue = values.reduce((sum, val) => sum + val, 0) / values.length;
          break;
        case 'min':
          aggregatedValue = Math.min(...values);
          break;
        case 'max':
          aggregatedValue = Math.max(...values);
          break;
        case 'sum':
          aggregatedValue = values.reduce((sum, val) => sum + val, 0);
          break;
        default:
          aggregatedValue = values.reduce((sum, val) => sum + val, 0) / values.length;
      }

      return {
        timestamp: timeKey,
        value: aggregatedValue,
        count: metrics.length,
        unit: metrics[0]?.unit || ''
      };
    });

    return aggregated.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  }

  // Group metrics by time interval
  private groupMetricsByInterval(metrics: PerformanceMetric[], interval: string): Record<string, PerformanceMetric[]> {
    const grouped: Record<string, PerformanceMetric[]> = {};

    metrics.forEach(metric => {
      const date = new Date(metric.timestamp);
      let key: string;

      switch (interval) {
        case 'hour':
          key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:00`;
          break;
        case 'day':
          key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
          break;
        case 'minute':
          key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
          break;
        default:
          key = date.toISOString();
      }

      if (!grouped[key]) {
        grouped[key] = [];
      }
      grouped[key].push(metric);
    });

    return grouped;
  }

  // Group metrics by day for trend analysis
  private groupMetricsByDay(metrics: PerformanceMetric[]): any[] {
    const grouped = this.groupMetricsByInterval(metrics, 'day');

    return Object.entries(grouped).map(([day, dayMetrics]) => {
      const values = dayMetrics.map(m => m.value);
      return {
        date: day,
        average: values.reduce((sum, val) => sum + val, 0) / values.length,
        min: Math.min(...values),
        max: Math.max(...values),
        count: values.length
      };
    });
  }

  // Calculate trend summary statistics
  private calculateTrendSummary(trendData: any[]): any {
    if (trendData.length < 2) {
      return { trend: 'insufficient_data', change: 0 };
    }

    const values = trendData.map(d => d.average);
    const recent = values.slice(-3); // Last 3 data points
    const previous = values.slice(-6, -3); // Previous 3 data points

    if (previous.length === 0) {
      return { trend: 'insufficient_data', change: 0 };
    }

    const recentAvg = recent.reduce((sum, val) => sum + val, 0) / recent.length;
    const previousAvg = previous.reduce((sum, val) => sum + val, 0) / previous.length;

    const change = ((recentAvg - previousAvg) / previousAvg) * 100;

    let trend: string;
    if (Math.abs(change) < 5) {
      trend = 'stable';
    } else if (change > 0) {
      trend = 'increasing';
    } else {
      trend = 'decreasing';
    }

    return { trend, change: Math.round(change * 100) / 100 };
  }

  // Group metrics by type for summary
  private groupMetricsByType(metrics: PerformanceMetric[]): Record<string, any> {
    const grouped: Record<string, PerformanceMetric[]> = {};

    metrics.forEach(metric => {
      if (!grouped[metric.metric]) {
        grouped[metric.metric] = [];
      }
      grouped[metric.metric].push(metric);
    });

    const summary: Record<string, any> = {};
    Object.entries(grouped).forEach(([type, typeMetrics]) => {
      const values = typeMetrics.map(m => m.value);
      summary[type] = {
        count: typeMetrics.length,
        average: values.reduce((sum, val) => sum + val, 0) / values.length,
        min: Math.min(...values),
        max: Math.max(...values)
      };
    });

    return summary;
  }

  // Get test suite summary
  private getTestSuiteSummary(metrics: PerformanceMetric[]): Record<string, any> {
    const suiteGroups: Record<string, PerformanceMetric[]> = {};

    metrics.forEach(metric => {
      if (!suiteGroups[metric.testSuite]) {
        suiteGroups[metric.testSuite] = [];
      }
      suiteGroups[metric.testSuite].push(metric);
    });

    const summary: Record<string, any> = {};
    Object.entries(suiteGroups).forEach(([suite, suiteMetrics]) => {
      summary[suite] = {
        totalMetrics: suiteMetrics.length,
        byType: this.groupMetricsByType(suiteMetrics),
        lastUpdated: suiteMetrics.sort((a, b) =>
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        )[0]?.timestamp
      };
    });

    return summary;
  }

  // Utility method to invalidate metrics-related cache
  private async invalidateMetricsCache(): Promise<void> {
    try {
      const cacheKeys = await cacheService.keys('metrics:*');
      for (const key of cacheKeys) {
        await cacheService.del(key);
      }
    } catch (error) {
      logger.error('Error invalidating metrics cache:', error);
    }
  }
}