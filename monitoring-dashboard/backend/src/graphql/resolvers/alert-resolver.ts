import { Resolver, Query, Mutation, Arg, ID, Int } from 'type-graphql';
import { Alert, AlertInput, AlertFilter, AlertConnection, PageInfo } from '../types';
import { logger } from '../../utils/logger';
import { v4 as uuidv4 } from 'uuid';

@Resolver(() => Alert)
export class AlertResolver {
  private alerts: Map<string, Alert> = new Map();

  @Query(() => AlertConnection)
  async alerts(
    @Arg('filter', () => AlertFilter, { nullable: true }) filter?: AlertFilter,
    @Arg('page', () => Int, { defaultValue: 1 }) page: number = 1,
    @Arg('limit', () => Int, { defaultValue: 50 }) limit: number = 50
  ): Promise<AlertConnection> {
    try {
      let filteredAlerts = Array.from(this.alerts.values());

      // Apply filters
      if (filter) {
        if (filter.severity) {
          filteredAlerts = filteredAlerts.filter(alert => alert.severity === filter.severity);
        }

        if (filter.type) {
          filteredAlerts = filteredAlerts.filter(alert => alert.type === filter.type);
        }

        if (filter.resolved !== undefined) {
          filteredAlerts = filteredAlerts.filter(alert => alert.resolved === filter.resolved);
        }

        if (filter.startDate || filter.endDate) {
          filteredAlerts = filteredAlerts.filter(alert => {
            const alertDate = alert.timestamp;
            const start = filter.startDate || new Date(0);
            const end = filter.endDate || new Date();
            return alertDate >= start && alertDate <= end;
          });
        }
      }

      // Sort by timestamp (newest first)
      filteredAlerts.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

      // Pagination
      const total = filteredAlerts.length;
      const totalPages = Math.ceil(total / limit);
      const startIndex = (page - 1) * limit;
      const paginatedAlerts = filteredAlerts.slice(startIndex, startIndex + limit);

      const pageInfo: PageInfo = {
        page,
        limit,
        total,
        totalPages,
        hasNextPage: page < totalPages,
        hasPrevPage: page > 1
      };

      return {
        nodes: paginatedAlerts,
        pageInfo
      };

    } catch (error) {
      logger.error('Error in alerts resolver:', error);
      throw new Error('Failed to retrieve alerts');
    }
  }

  @Query(() => Alert, { nullable: true })
  async alert(@Arg('id', () => ID) id: string): Promise<Alert | null> {
    try {
      return this.alerts.get(id) || null;
    } catch (error) {
      logger.error('Error in alert resolver:', error);
      throw new Error('Failed to retrieve alert');
    }
  }

  @Mutation(() => Alert)
  async createAlert(@Arg('input') input: AlertInput): Promise<Alert> {
    try {
      const alert: Alert = {
        id: uuidv4(),
        type: input.type,
        severity: input.severity,
        title: input.title,
        description: input.description,
        timestamp: new Date(),
        resolved: false
      };

      this.alerts.set(alert.id, alert);

      logger.info(`Alert created: ${alert.id}`);
      return alert;

    } catch (error) {
      logger.error('Error in createAlert mutation:', error);
      throw new Error('Failed to create alert');
    }
  }

  @Mutation(() => Alert)
  async resolveAlert(@Arg('id', () => ID) id: string): Promise<Alert> {
    try {
      const alert = this.alerts.get(id);

      if (!alert) {
        throw new Error('Alert not found');
      }

      if (alert.resolved) {
        throw new Error('Alert is already resolved');
      }

      const updatedAlert: Alert = {
        ...alert,
        resolved: true,
        resolvedAt: new Date()
      };

      this.alerts.set(id, updatedAlert);

      logger.info(`Alert resolved: ${id}`);
      return updatedAlert;

    } catch (error) {
      logger.error('Error in resolveAlert mutation:', error);
      throw new Error('Failed to resolve alert');
    }
  }

  // Add mock data
  constructor() {
    this.addMockData();
  }

  private addMockData(): void {
    // Mock data added in constructor
  }
}