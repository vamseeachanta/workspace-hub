import { Request, Response } from 'express';
import { Alert, AlertSchema, ApiResponse } from '@monitoring-dashboard/shared';
import { cacheService } from '../../cache/redis-cache';
import { logger, performanceLogger } from '../../utils/logger';
import { v4 as uuidv4 } from 'uuid';

export class AlertController {
  private readonly CACHE_TTL = 300; // 5 minutes
  private alerts: Map<string, Alert> = new Map();

  // Get alerts with filtering
  public async getAlerts(req: Request, res: Response): Promise<void> {
    const perf = performanceLogger.start('getAlerts');

    try {
      const {
        severity,
        type,
        resolved,
        page = 1,
        limit = 50,
        startDate,
        endDate
      } = req.query;

      const cacheKey = `alerts:${JSON.stringify(req.query)}`;
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

      let filteredAlerts = Array.from(this.alerts.values());

      // Apply filters
      if (severity) {
        filteredAlerts = filteredAlerts.filter(alert => alert.severity === severity);
      }

      if (type) {
        filteredAlerts = filteredAlerts.filter(alert => alert.type === type);
      }

      if (resolved !== undefined) {
        const isResolved = resolved === 'true';
        filteredAlerts = filteredAlerts.filter(alert => alert.resolved === isResolved);
      }

      if (startDate || endDate) {
        filteredAlerts = filteredAlerts.filter(alert => {
          const alertDate = new Date(alert.timestamp);
          const start = startDate ? new Date(startDate as string) : new Date(0);
          const end = endDate ? new Date(endDate as string) : new Date();
          return alertDate >= start && alertDate <= end;
        });
      }

      // Sort by timestamp (newest first)
      filteredAlerts.sort((a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );

      // Pagination
      const startIndex = (Number(page) - 1) * Number(limit);
      const paginatedAlerts = filteredAlerts.slice(startIndex, startIndex + Number(limit));

      const result = {
        alerts: paginatedAlerts,
        total: filteredAlerts.length,
        page: Number(page),
        limit: Number(limit),
        summary: this.calculateAlertSummary(filteredAlerts)
      };

      await cacheService.set(cacheKey, result, this.CACHE_TTL);

      perf.end();

      res.json({
        success: true,
        data: result,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      perf.end();
      logger.error('Error in getAlerts:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve alerts',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Create a new alert
  public async createAlert(req: Request, res: Response): Promise<void> {
    try {
      const alertData = AlertSchema.parse({
        ...req.body,
        id: req.body.id || uuidv4(),
        timestamp: req.body.timestamp || new Date().toISOString()
      });

      this.alerts.set(alertData.id, alertData);

      // Invalidate cache
      await this.invalidateAlertCache();

      logger.info(`Alert created: ${alertData.type} - ${alertData.severity}`, {
        alertId: alertData.id,
        title: alertData.title
      });

      res.status(201).json({
        success: true,
        data: alertData,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in createAlert:', error);
      res.status(400).json({
        success: false,
        error: 'Invalid alert data',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get a specific alert
  public async getAlert(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const cacheKey = `alert:${id}`;

      let alert = await cacheService.get<Alert>(cacheKey);

      if (!alert) {
        alert = this.alerts.get(id);
        if (!alert) {
          res.status(404).json({
            success: false,
            error: 'Alert not found',
            timestamp: new Date().toISOString()
          } as ApiResponse);
          return;
        }

        await cacheService.set(cacheKey, alert, this.CACHE_TTL);
      }

      res.json({
        success: true,
        data: alert,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getAlert:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve alert',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Resolve an alert
  public async resolveAlert(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const { resolvedBy, notes } = req.body;

      const alert = this.alerts.get(id);

      if (!alert) {
        res.status(404).json({
          success: false,
          error: 'Alert not found',
          timestamp: new Date().toISOString()
        } as ApiResponse);
        return;
      }

      if (alert.resolved) {
        res.status(400).json({
          success: false,
          error: 'Alert is already resolved',
          timestamp: new Date().toISOString()
        } as ApiResponse);
        return;
      }

      const updatedAlert: Alert = {
        ...alert,
        resolved: true,
        resolvedAt: new Date().toISOString(),
        metadata: {
          ...alert.metadata,
          resolvedBy,
          resolutionNotes: notes
        }
      };

      this.alerts.set(id, updatedAlert);

      // Invalidate cache
      await this.invalidateAlertCache();
      await cacheService.del(`alert:${id}`);

      logger.info(`Alert resolved: ${id}`, {
        resolvedBy,
        notes
      });

      res.json({
        success: true,
        data: updatedAlert,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in resolveAlert:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to resolve alert',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Delete an alert
  public async deleteAlert(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;

      if (!this.alerts.has(id)) {
        res.status(404).json({
          success: false,
          error: 'Alert not found',
          timestamp: new Date().toISOString()
        } as ApiResponse);
        return;
      }

      this.alerts.delete(id);

      // Invalidate cache
      await this.invalidateAlertCache();
      await cacheService.del(`alert:${id}`);

      logger.info(`Alert deleted: ${id}`);

      res.json({
        success: true,
        data: { deleted: true },
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in deleteAlert:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to delete alert',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get alerts by severity
  public async getAlertsBySeverity(req: Request, res: Response): Promise<void> {
    try {
      const { severity } = req.params;
      const { resolved = 'false' } = req.query;

      const isResolved = resolved === 'true';
      const alerts = Array.from(this.alerts.values()).filter(alert =>
        alert.severity === severity && alert.resolved === isResolved
      );

      // Sort by timestamp (newest first)
      alerts.sort((a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );

      res.json({
        success: true,
        data: {
          alerts,
          count: alerts.length,
          severity,
          resolved: isResolved
        },
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getAlertsBySeverity:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve alerts by severity',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Calculate alert summary statistics
  private calculateAlertSummary(alerts: Alert[]): any {
    const total = alerts.length;
    const resolved = alerts.filter(a => a.resolved).length;
    const unresolved = total - resolved;

    const bySeverity = {
      critical: alerts.filter(a => a.severity === 'critical').length,
      high: alerts.filter(a => a.severity === 'high').length,
      medium: alerts.filter(a => a.severity === 'medium').length,
      low: alerts.filter(a => a.severity === 'low').length
    };

    const byType = alerts.reduce((acc, alert) => {
      acc[alert.type] = (acc[alert.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Calculate average resolution time for resolved alerts
    const resolvedAlerts = alerts.filter(a => a.resolved && a.resolvedAt);
    let avgResolutionTime = 0;

    if (resolvedAlerts.length > 0) {
      const totalResolutionTime = resolvedAlerts.reduce((sum, alert) => {
        const created = new Date(alert.timestamp).getTime();
        const resolved = new Date(alert.resolvedAt!).getTime();
        return sum + (resolved - created);
      }, 0);

      avgResolutionTime = totalResolutionTime / resolvedAlerts.length;
    }

    return {
      total,
      resolved,
      unresolved,
      bySeverity,
      byType,
      avgResolutionTimeMs: avgResolutionTime,
      avgResolutionTimeHours: avgResolutionTime / (1000 * 60 * 60)
    };
  }

  // Utility method to invalidate alert-related cache
  private async invalidateAlertCache(): Promise<void> {
    try {
      const cacheKeys = await cacheService.keys('alerts:*');
      for (const key of cacheKeys) {
        await cacheService.del(key);
      }
    } catch (error) {
      logger.error('Error invalidating alert cache:', error);
    }
  }
}