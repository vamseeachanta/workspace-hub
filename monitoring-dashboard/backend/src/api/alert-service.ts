import { Alert, AlertType, AlertSeverity } from '@monitoring-dashboard/shared';
import { logger } from '../utils/logger';
import { cacheService } from '../cache/redis-cache';
import { v4 as uuidv4 } from 'uuid';

export interface AlertRule {
  id: string;
  name: string;
  type: AlertType;
  condition: {
    metric: string;
    operator: 'gt' | 'lt' | 'eq' | 'gte' | 'lte';
    threshold: number;
    timeWindow: number; // in minutes
  };
  severity: AlertSeverity;
  enabled: boolean;
  cooldownPeriod: number; // in minutes
}

export class AlertService {
  private rules: Map<string, AlertRule> = new Map();
  private alertHistory: Map<string, Date> = new Map(); // Track when rules last fired
  private anomalyDetectionEnabled = true;

  async initialize(): Promise<void> {
    await this.loadDefaultRules();
    this.startMonitoring();
    logger.info('Alert service initialized');
  }

  private async loadDefaultRules(): Promise<void> {
    const defaultRules: AlertRule[] = [
      {
        id: 'test-failure-rate',
        name: 'High Test Failure Rate',
        type: 'regression',
        condition: {
          metric: 'test_failure_rate',
          operator: 'gt',
          threshold: 10, // 10%
          timeWindow: 30
        },
        severity: 'high',
        enabled: true,
        cooldownPeriod: 60
      },
      {
        id: 'coverage-drop',
        name: 'Coverage Drop',
        type: 'coverage_drop',
        condition: {
          metric: 'coverage_percentage',
          operator: 'lt',
          threshold: 80, // 80%
          timeWindow: 60
        },
        severity: 'medium',
        enabled: true,
        cooldownPeriod: 120
      },
      {
        id: 'response-time-degradation',
        name: 'Response Time Degradation',
        type: 'performance_degradation',
        condition: {
          metric: 'avg_response_time',
          operator: 'gt',
          threshold: 500, // 500ms
          timeWindow: 15
        },
        severity: 'high',
        enabled: true,
        cooldownPeriod: 30
      },
      {
        id: 'flaky-test-detection',
        name: 'Flaky Test Detection',
        type: 'flaky_test',
        condition: {
          metric: 'test_inconsistency_rate',
          operator: 'gt',
          threshold: 20, // 20% inconsistency
          timeWindow: 120
        },
        severity: 'medium',
        enabled: true,
        cooldownPeriod: 240
      },
      {
        id: 'error-rate-spike',
        name: 'Error Rate Spike',
        type: 'anomaly',
        condition: {
          metric: 'error_rate',
          operator: 'gt',
          threshold: 5, // 5%
          timeWindow: 10
        },
        severity: 'critical',
        enabled: true,
        cooldownPeriod: 15
      }
    ];

    for (const rule of defaultRules) {
      this.rules.set(rule.id, rule);
    }

    logger.info(`Loaded ${defaultRules.length} default alert rules`);
  }

  private startMonitoring(): void {
    // Check rules every minute
    setInterval(async () => {
      await this.evaluateRules();
    }, 60000);

    // Run anomaly detection every 5 minutes
    if (this.anomalyDetectionEnabled) {
      setInterval(async () => {
        await this.detectAnomalies();
      }, 300000);
    }

    logger.info('Alert monitoring started');
  }

  private async evaluateRules(): Promise<void> {
    try {
      for (const [ruleId, rule] of this.rules) {
        if (!rule.enabled) {
          continue;
        }

        // Check cooldown period
        const lastAlerted = this.alertHistory.get(ruleId);
        if (lastAlerted) {
          const cooldownMs = rule.cooldownPeriod * 60 * 1000;
          if (Date.now() - lastAlerted.getTime() < cooldownMs) {
            continue;
          }
        }

        const shouldAlert = await this.evaluateRule(rule);
        if (shouldAlert) {
          await this.triggerAlert(rule);
          this.alertHistory.set(ruleId, new Date());
        }
      }
    } catch (error) {
      logger.error('Error evaluating alert rules:', error);
    }
  }

  private async evaluateRule(rule: AlertRule): Promise<boolean> {
    try {
      // This would typically query your metrics storage
      // For demo purposes, we'll simulate metric evaluation
      const currentValue = await this.getCurrentMetricValue(rule.condition.metric);

      if (currentValue === null) {
        return false;
      }

      switch (rule.condition.operator) {
        case 'gt':
          return currentValue > rule.condition.threshold;
        case 'lt':
          return currentValue < rule.condition.threshold;
        case 'gte':
          return currentValue >= rule.condition.threshold;
        case 'lte':
          return currentValue <= rule.condition.threshold;
        case 'eq':
          return currentValue === rule.condition.threshold;
        default:
          return false;
      }
    } catch (error) {
      logger.error(`Error evaluating rule ${rule.id}:`, error);
      return false;
    }
  }

  private async getCurrentMetricValue(metric: string): Promise<number | null> {
    // Simulate getting current metric values
    // In a real implementation, this would query your metrics database
    const mockValues: Record<string, number> = {
      test_failure_rate: Math.random() * 20, // 0-20%
      coverage_percentage: Math.random() * 20 + 75, // 75-95%
      avg_response_time: Math.random() * 300 + 100, // 100-400ms
      test_inconsistency_rate: Math.random() * 30, // 0-30%
      error_rate: Math.random() * 10 // 0-10%
    };

    return mockValues[metric] || null;
  }

  private async triggerAlert(rule: AlertRule): Promise<void> {
    const alert: Alert = {
      id: uuidv4(),
      type: rule.type,
      severity: rule.severity,
      title: rule.name,
      description: this.generateAlertDescription(rule),
      timestamp: new Date().toISOString(),
      resolved: false,
      metadata: {
        ruleId: rule.id,
        condition: rule.condition,
        triggeredBy: 'alert_service'
      }
    };

    // Store alert (in a real implementation, this would be in a database)
    await this.storeAlert(alert);

    // Send real-time notification (this would integrate with WebSocket service)
    await this.sendAlertNotification(alert);

    logger.warn(`Alert triggered: ${alert.title}`, {
      alertId: alert.id,
      severity: alert.severity,
      type: alert.type
    });
  }

  private generateAlertDescription(rule: AlertRule): string {
    const { condition } = rule;
    const operatorText = {
      gt: 'greater than',
      lt: 'less than',
      gte: 'greater than or equal to',
      lte: 'less than or equal to',
      eq: 'equal to'
    };

    return `${condition.metric} is ${operatorText[condition.operator]} ${condition.threshold} over the last ${condition.timeWindow} minutes`;
  }

  private async storeAlert(alert: Alert): Promise<void> {
    // In a real implementation, this would store to a database
    // For now, we'll cache it
    await cacheService.set(`alert:${alert.id}`, alert, 86400); // 24 hours
    logger.debug(`Alert stored: ${alert.id}`);
  }

  private async sendAlertNotification(alert: Alert): Promise<void> {
    // This would integrate with the WebSocket service to send real-time notifications
    // For now, we'll just log it
    logger.info(`Alert notification sent: ${alert.title}`, {
      alertId: alert.id,
      severity: alert.severity
    });
  }

  private async detectAnomalies(): Promise<void> {
    try {
      logger.debug('Running anomaly detection');

      // This is a simplified anomaly detection implementation
      // In production, you'd use more sophisticated algorithms
      const metrics = ['test_execution_time', 'memory_usage', 'cpu_usage'];

      for (const metric of metrics) {
        const anomaly = await this.detectMetricAnomaly(metric);
        if (anomaly) {
          await this.triggerAnomalyAlert(metric, anomaly);
        }
      }
    } catch (error) {
      logger.error('Error in anomaly detection:', error);
    }
  }

  private async detectMetricAnomaly(metric: string): Promise<any | null> {
    // Simple anomaly detection based on standard deviation
    // In production, you'd use more sophisticated algorithms like isolation forests,
    // LSTM autoencoders, or statistical process control

    const recentValues = await this.getRecentMetricValues(metric, 100);
    if (recentValues.length < 10) {
      return null; // Not enough data
    }

    const mean = recentValues.reduce((sum, val) => sum + val, 0) / recentValues.length;
    const variance = recentValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / recentValues.length;
    const stdDev = Math.sqrt(variance);

    const currentValue = recentValues[recentValues.length - 1];
    const zScore = Math.abs((currentValue - mean) / stdDev);

    // Consider it an anomaly if z-score > 3 (99.7% confidence)
    if (zScore > 3) {
      return {
        metric,
        currentValue,
        expectedRange: [mean - 2 * stdDev, mean + 2 * stdDev],
        zScore,
        confidence: 'high'
      };
    }

    return null;
  }

  private async getRecentMetricValues(metric: string, count: number): Promise<number[]> {
    // Mock implementation - in production, this would query your metrics database
    const values = [];
    const baseValue = Math.random() * 100 + 50;

    for (let i = 0; i < count; i++) {
      // Generate normal distribution around base value, with occasional spikes
      let value = baseValue + (Math.random() - 0.5) * 20;

      // Introduce occasional anomalies for testing
      if (Math.random() < 0.02) { // 2% chance of anomaly
        value += (Math.random() > 0.5 ? 1 : -1) * (baseValue * 0.5);
      }

      values.push(Math.max(0, value));
    }

    return values;
  }

  private async triggerAnomalyAlert(metric: string, anomaly: any): Promise<void> {
    const alert: Alert = {
      id: uuidv4(),
      type: 'anomaly',
      severity: anomaly.confidence === 'high' ? 'high' : 'medium',
      title: `Anomaly Detected in ${metric}`,
      description: `Unusual behavior detected in ${metric}. Current value: ${anomaly.currentValue.toFixed(2)}, Expected range: ${anomaly.expectedRange[0].toFixed(2)} - ${anomaly.expectedRange[1].toFixed(2)}`,
      timestamp: new Date().toISOString(),
      resolved: false,
      metadata: {
        detectionType: 'statistical_anomaly',
        metric,
        anomaly,
        triggeredBy: 'anomaly_detection'
      }
    };

    await this.storeAlert(alert);
    await this.sendAlertNotification(alert);

    logger.warn(`Anomaly alert triggered for ${metric}`, {
      alertId: alert.id,
      zScore: anomaly.zScore,
      confidence: anomaly.confidence
    });
  }

  // Public methods for managing rules

  public addRule(rule: AlertRule): void {
    this.rules.set(rule.id, rule);
    logger.info(`Alert rule added: ${rule.name}`);
  }

  public removeRule(ruleId: string): boolean {
    const removed = this.rules.delete(ruleId);
    if (removed) {
      this.alertHistory.delete(ruleId);
      logger.info(`Alert rule removed: ${ruleId}`);
    }
    return removed;
  }

  public updateRule(ruleId: string, updates: Partial<AlertRule>): boolean {
    const existing = this.rules.get(ruleId);
    if (!existing) {
      return false;
    }

    const updated = { ...existing, ...updates };
    this.rules.set(ruleId, updated);
    logger.info(`Alert rule updated: ${ruleId}`);
    return true;
  }

  public getRules(): AlertRule[] {
    return Array.from(this.rules.values());
  }

  public getRule(ruleId: string): AlertRule | undefined {
    return this.rules.get(ruleId);
  }

  public enableAnomalyDetection(enabled: boolean): void {
    this.anomalyDetectionEnabled = enabled;
    logger.info(`Anomaly detection ${enabled ? 'enabled' : 'disabled'}`);
  }
}