import { Resolver, Query, Mutation, Arg, Int } from 'type-graphql';
import { PerformanceMetric, MetricInput, MetricType } from '../types';
import { logger } from '../../utils/logger';
import { v4 as uuidv4 } from 'uuid';

@Resolver(() => PerformanceMetric)
export class MetricsResolver {
  private metrics: Map<string, PerformanceMetric> = new Map();

  @Query(() => [PerformanceMetric])
  async metrics(
    @Arg('type', () => MetricType, { nullable: true }) type?: MetricType,
    @Arg('testSuite', { nullable: true }) testSuite?: string,
    @Arg('limit', () => Int, { defaultValue: 100 }) limit: number = 100
  ): Promise<PerformanceMetric[]> {
    try {
      let filteredMetrics = Array.from(this.metrics.values());

      // Apply filters
      if (type) {
        filteredMetrics = filteredMetrics.filter(metric => metric.metric === type);
      }

      if (testSuite) {
        filteredMetrics = filteredMetrics.filter(metric => metric.testSuite === testSuite);
      }

      // Sort by timestamp (newest first)
      filteredMetrics.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

      // Apply limit
      return filteredMetrics.slice(0, limit);

    } catch (error) {
      logger.error('Error in metrics resolver:', error);
      throw new Error('Failed to retrieve metrics');
    }
  }

  @Mutation(() => PerformanceMetric)
  async recordMetric(@Arg('input') input: MetricInput): Promise<PerformanceMetric> {
    try {
      const metric: PerformanceMetric = {
        id: uuidv4(),
        timestamp: new Date(),
        testSuite: input.testSuite,
        metric: input.metric,
        value: input.value,
        unit: input.unit
      };

      this.metrics.set(metric.id, metric);

      logger.info(`Metric recorded: ${metric.metric} for ${metric.testSuite}`);
      return metric;

    } catch (error) {
      logger.error('Error in recordMetric mutation:', error);
      throw new Error('Failed to record metric');
    }
  }

  // Add mock data
  constructor() {
    this.addMockData();
  }

  private addMockData(): void {
    const mockMetrics: PerformanceMetric[] = [
      {
        id: '1',
        timestamp: new Date(Date.now() - 1000 * 60 * 5),
        testSuite: 'API Tests',
        metric: MetricType.DURATION,
        value: 1200,
        unit: 'ms'
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 1000 * 60 * 10),
        testSuite: 'UI Tests',
        metric: MetricType.MEMORY,
        value: 512,
        unit: 'MB'
      }
    ];

    mockMetrics.forEach(metric => {
      this.metrics.set(metric.id, metric);
    });
  }
}