import {
  AuditEvent,
  AuditAction,
  AuditLevel,
  User,
  ApprovalRequest,
  BaselineUpdateRequest
} from '../types/approval.types.js';
import { EventEmitter } from 'events';
import * as fs from 'fs-extra';
import * as path from 'path';

export interface AuditLoggerOptions {
  enableFileLogging: boolean;
  enableDatabaseLogging: boolean;
  enableRemoteLogging: boolean;
  logDirectory: string;
  logFilePrefix: string;
  maxLogFileSize: number; // bytes
  maxLogFiles: number;
  logLevel: AuditLevel;
  enableEncryption: boolean;
  encryptionKey?: string;
  remoteEndpoint?: string;
  remoteApiKey?: string;
  batchSize: number;
  flushInterval: number; // milliseconds
  enableCompression: boolean;
  retentionDays: number;
}

export interface AuditLogEntry {
  id: string;
  timestamp: Date;
  level: AuditLevel;
  action: AuditAction;
  userId: string;
  userEmail: string;
  resourceType: string;
  resourceId: string;
  details: Record<string, any>;
  ipAddress?: string;
  userAgent?: string;
  sessionId?: string;
  correlationId?: string;
  metadata?: Record<string, any>;
}

export interface AuditQuery {
  startDate?: Date;
  endDate?: Date;
  userId?: string;
  action?: AuditAction;
  resourceType?: string;
  resourceId?: string;
  level?: AuditLevel;
  limit?: number;
  offset?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface AuditReport {
  summary: AuditSummary;
  activities: AuditActivity[];
  userActivities: UserActivity[];
  riskAssessment: RiskAssessment;
  timeRange: {
    start: Date;
    end: Date;
  };
  generatedAt: Date;
}

export interface AuditSummary {
  totalEvents: number;
  uniqueUsers: number;
  actions: Record<AuditAction, number>;
  riskLevels: Record<string, number>;
  resourceTypes: Record<string, number>;
}

export interface AuditActivity {
  timestamp: Date;
  action: AuditAction;
  user: string;
  resource: string;
  outcome: 'success' | 'failure' | 'warning';
  details: string;
}

export interface UserActivity {
  userId: string;
  userEmail: string;
  totalActions: number;
  lastActivity: Date;
  actions: Record<AuditAction, number>;
  riskScore: number;
}

export interface RiskAssessment {
  overallRisk: 'low' | 'medium' | 'high' | 'critical';
  riskFactors: string[];
  recommendations: string[];
  score: number; // 0-100
}

export class AuditLogger extends EventEmitter {
  private options: AuditLoggerOptions;
  private logBuffer: AuditLogEntry[] = [];
  private currentLogFile?: string;
  private writeStream?: fs.WriteStream;
  private flushTimer?: NodeJS.Timeout;

  constructor(options: Partial<AuditLoggerOptions> = {}) {
    super();
    this.options = {
      enableFileLogging: true,
      enableDatabaseLogging: false,
      enableRemoteLogging: false,
      logDirectory: './logs/audit',
      logFilePrefix: 'audit',
      maxLogFileSize: 100 * 1024 * 1024, // 100MB
      maxLogFiles: 10,
      logLevel: AuditLevel.STANDARD,
      enableEncryption: false,
      batchSize: 100,
      flushInterval: 5000, // 5 seconds
      enableCompression: true,
      retentionDays: 365,
      ...options
    };

    this.initialize();
  }

  /**
   * Log an audit event
   */
  async logEvent(
    action: AuditAction,
    user: User,
    resourceType: string,
    resourceId: string,
    details: Record<string, any>,
    metadata?: {
      ipAddress?: string;
      userAgent?: string;
      sessionId?: string;
      correlationId?: string;
    }
  ): Promise<void> {
    const logEntry: AuditLogEntry = {
      id: this.generateId(),
      timestamp: new Date(),
      level: this.determineLogLevel(action),
      action,
      userId: user.id,
      userEmail: user.email,
      resourceType,
      resourceId,
      details: this.sanitizeDetails(details),
      ipAddress: metadata?.ipAddress,
      userAgent: metadata?.userAgent,
      sessionId: metadata?.sessionId,
      correlationId: metadata?.correlationId || this.generateCorrelationId(),
      metadata: metadata ? { ...metadata } : undefined
    };

    // Add to buffer
    this.logBuffer.push(logEntry);

    // Emit event for real-time listeners
    this.emit('auditEvent', logEntry);

    // Flush if buffer is full
    if (this.logBuffer.length >= this.options.batchSize) {
      await this.flush();
    }
  }

  /**
   * Log approval request creation
   */
  async logApprovalRequestCreated(
    user: User,
    request: ApprovalRequest,
    metadata?: Record<string, any>
  ): Promise<void> {
    await this.logEvent(
      AuditAction.CREATE,
      user,
      'approval_request',
      request.id,
      {
        title: request.title,
        type: request.type,
        priority: request.priority,
        approversCount: request.approvers.length,
        baselineUpdate: !!request.baselineUpdate
      },
      metadata
    );
  }

  /**
   * Log approval response
   */
  async logApprovalResponse(
    user: User,
    request: ApprovalRequest,
    decision: string,
    stepId: string,
    reason?: string,
    metadata?: Record<string, any>
  ): Promise<void> {
    await this.logEvent(
      AuditAction.APPROVE,
      user,
      'approval_request',
      request.id,
      {
        decision,
        stepId,
        reason,
        requestTitle: request.title,
        requestType: request.type,
        requestPriority: request.priority
      },
      metadata
    );
  }

  /**
   * Log baseline update execution
   */
  async logBaselineUpdateExecution(
    user: User,
    updateRequest: BaselineUpdateRequest,
    result: any,
    metadata?: Record<string, any>
  ): Promise<void> {
    await this.logEvent(
      AuditAction.UPDATE,
      user,
      'baseline_update',
      updateRequest.id,
      {
        environment: updateRequest.targetEnvironment,
        updateType: updateRequest.updateType,
        changesCount: updateRequest.changes.length,
        riskLevel: updateRequest.impactAssessment.riskLevel,
        success: result.success,
        duration: result.duration,
        rollbackAvailable: result.rollbackAvailable
      },
      metadata
    );
  }

  /**
   * Log data access
   */
  async logDataAccess(
    user: User,
    resourceType: string,
    resourceId: string,
    accessType: 'read' | 'export' | 'search',
    metadata?: Record<string, any>
  ): Promise<void> {
    await this.logEvent(
      AuditAction.VIEW,
      user,
      resourceType,
      resourceId,
      {
        accessType,
        timestamp: new Date().toISOString()
      },
      metadata
    );
  }

  /**
   * Log security event
   */
  async logSecurityEvent(
    user: User,
    eventType: string,
    severity: 'low' | 'medium' | 'high' | 'critical',
    details: Record<string, any>,
    metadata?: Record<string, any>
  ): Promise<void> {
    await this.logEvent(
      AuditAction.UPDATE, // Security events use UPDATE action
      user,
      'security_event',
      this.generateId(),
      {
        eventType,
        severity,
        ...details
      },
      metadata
    );
  }

  /**
   * Query audit logs
   */
  async queryLogs(query: AuditQuery): Promise<AuditLogEntry[]> {
    // This is a simplified implementation
    // In a real system, this would query a database or search through log files

    let results: AuditLogEntry[] = [];

    if (this.options.enableFileLogging) {
      results = await this.searchLogFiles(query);
    }

    if (this.options.enableDatabaseLogging) {
      // Database query implementation would go here
    }

    return this.applyQueryFilters(results, query);
  }

  /**
   * Generate audit report
   */
  async generateReport(
    startDate: Date,
    endDate: Date,
    options: {
      includeUserActivities?: boolean;
      includeRiskAssessment?: boolean;
      format?: 'json' | 'csv' | 'pdf';
    } = {}
  ): Promise<AuditReport> {
    const logs = await this.queryLogs({
      startDate,
      endDate,
      limit: 10000 // Large limit for comprehensive report
    });

    const summary = this.generateSummary(logs);
    const activities = this.extractActivities(logs);
    const userActivities = options.includeUserActivities ? this.analyzeUserActivities(logs) : [];
    const riskAssessment = options.includeRiskAssessment ? this.assessRisk(logs) : {
      overallRisk: 'low' as const,
      riskFactors: [],
      recommendations: [],
      score: 0
    };

    return {
      summary,
      activities,
      userActivities,
      riskAssessment,
      timeRange: { start: startDate, end: endDate },
      generatedAt: new Date()
    };
  }

  /**
   * Export audit logs
   */
  async exportLogs(
    query: AuditQuery,
    format: 'json' | 'csv' | 'xml' = 'json'
  ): Promise<string> {
    const logs = await this.queryLogs(query);

    switch (format) {
      case 'csv':
        return this.convertToCSV(logs);
      case 'xml':
        return this.convertToXML(logs);
      default:
        return JSON.stringify(logs, null, 2);
    }
  }

  /**
   * Flush pending log entries
   */
  async flush(): Promise<void> {
    if (this.logBuffer.length === 0) return;

    const entries = [...this.logBuffer];
    this.logBuffer = [];

    try {
      if (this.options.enableFileLogging) {
        await this.writeToFile(entries);
      }

      if (this.options.enableDatabaseLogging) {
        await this.writeToDatabase(entries);
      }

      if (this.options.enableRemoteLogging) {
        await this.writeToRemote(entries);
      }

      this.emit('logsFlushed', { count: entries.length });

    } catch (error) {
      // Return entries to buffer on failure
      this.logBuffer.unshift(...entries);
      this.emit('flushError', error);
      throw error;
    }
  }

  /**
   * Get audit statistics
   */
  async getStatistics(timeRange: { start: Date; end: Date }): Promise<any> {
    const logs = await this.queryLogs({
      startDate: timeRange.start,
      endDate: timeRange.end
    });

    return {
      totalEvents: logs.length,
      uniqueUsers: new Set(logs.map(l => l.userId)).size,
      actionsBreakdown: this.groupBy(logs, 'action'),
      levelBreakdown: this.groupBy(logs, 'level'),
      resourceBreakdown: this.groupBy(logs, 'resourceType'),
      hourlyDistribution: this.getHourlyDistribution(logs),
      topUsers: this.getTopUsers(logs, 10)
    };
  }

  /**
   * Clean up old logs
   */
  async cleanup(): Promise<void> {
    if (!this.options.enableFileLogging) return;

    const cutoffDate = new Date(Date.now() - this.options.retentionDays * 24 * 60 * 60 * 1000);
    const logFiles = await this.getLogFiles();

    for (const file of logFiles) {
      const filePath = path.join(this.options.logDirectory, file);
      const stats = await fs.stat(filePath);

      if (stats.mtime < cutoffDate) {
        await fs.remove(filePath);
        this.emit('logFileRemoved', file);
      }
    }
  }

  // Private methods

  private async initialize(): Promise<void> {
    if (this.options.enableFileLogging) {
      await fs.ensureDir(this.options.logDirectory);
    }

    // Start flush timer
    this.flushTimer = setInterval(() => {
      if (this.logBuffer.length > 0) {
        this.flush().catch(error => this.emit('flushError', error));
      }
    }, this.options.flushInterval);

    // Setup cleanup timer (daily)
    setInterval(() => {
      this.cleanup().catch(error => this.emit('cleanupError', error));
    }, 24 * 60 * 60 * 1000);
  }

  private determineLogLevel(action: AuditAction): AuditLevel {
    const highRiskActions = [AuditAction.DELETE, AuditAction.ADMIN];
    const mediumRiskActions = [AuditAction.APPROVE, AuditAction.UPDATE];

    if (highRiskActions.includes(action)) {
      return AuditLevel.DETAILED;
    } else if (mediumRiskActions.includes(action)) {
      return AuditLevel.STANDARD;
    } else {
      return AuditLevel.MINIMAL;
    }
  }

  private sanitizeDetails(details: Record<string, any>): Record<string, any> {
    const sanitized = { ...details };
    const sensitiveFields = ['password', 'token', 'secret', 'key', 'credential', 'apiKey'];

    for (const field of sensitiveFields) {
      if (sanitized[field]) {
        sanitized[field] = '[REDACTED]';
      }
    }

    // Recursively sanitize nested objects
    for (const [key, value] of Object.entries(sanitized)) {
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        sanitized[key] = this.sanitizeDetails(value);
      }
    }

    return sanitized;
  }

  private async writeToFile(entries: AuditLogEntry[]): Promise<void> {
    if (!this.currentLogFile || await this.shouldRotateLogFile()) {
      await this.rotateLogFile();
    }

    if (!this.writeStream) {
      this.writeStream = fs.createWriteStream(this.currentLogFile!, { flags: 'a' });
    }

    for (const entry of entries) {
      const logLine = JSON.stringify(entry) + '\n';
      this.writeStream.write(logLine);
    }
  }

  private async writeToDatabase(entries: AuditLogEntry[]): Promise<void> {
    // Database implementation would go here
    // This could use any database (PostgreSQL, MongoDB, etc.)
    console.log(`Would write ${entries.length} entries to database`);
  }

  private async writeToRemote(entries: AuditLogEntry[]): Promise<void> {
    if (!this.options.remoteEndpoint) return;

    // Remote logging implementation (e.g., to SIEM system)
    try {
      const response = await fetch(this.options.remoteEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.options.remoteApiKey}`,
        },
        body: JSON.stringify({ entries })
      });

      if (!response.ok) {
        throw new Error(`Remote logging failed: ${response.statusText}`);
      }
    } catch (error) {
      this.emit('remoteLoggingError', error);
      throw error;
    }
  }

  private async shouldRotateLogFile(): Promise<boolean> {
    if (!this.currentLogFile) return true;

    try {
      const stats = await fs.stat(this.currentLogFile);
      return stats.size >= this.options.maxLogFileSize;
    } catch (error) {
      return true;
    }
  }

  private async rotateLogFile(): Promise<void> {
    // Close current stream
    if (this.writeStream) {
      this.writeStream.end();
      this.writeStream = undefined;
    }

    // Generate new log file name
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    this.currentLogFile = path.join(
      this.options.logDirectory,
      `${this.options.logFilePrefix}-${timestamp}.log`
    );

    // Remove old log files if necessary
    await this.removeOldLogFiles();
  }

  private async removeOldLogFiles(): Promise<void> {
    const files = await this.getLogFiles();

    if (files.length >= this.options.maxLogFiles) {
      // Sort by modification time and remove oldest
      const fileStats = await Promise.all(
        files.map(async file => ({
          name: file,
          mtime: (await fs.stat(path.join(this.options.logDirectory, file))).mtime
        }))
      );

      fileStats.sort((a, b) => a.mtime.getTime() - b.mtime.getTime());

      const filesToRemove = fileStats.slice(0, files.length - this.options.maxLogFiles + 1);

      for (const file of filesToRemove) {
        await fs.remove(path.join(this.options.logDirectory, file.name));
      }
    }
  }

  private async getLogFiles(): Promise<string[]> {
    try {
      const files = await fs.readdir(this.options.logDirectory);
      return files.filter(file =>
        file.startsWith(this.options.logFilePrefix) && file.endsWith('.log')
      );
    } catch (error) {
      return [];
    }
  }

  private async searchLogFiles(query: AuditQuery): Promise<AuditLogEntry[]> {
    const results: AuditLogEntry[] = [];
    const files = await this.getLogFiles();

    for (const file of files) {
      const filePath = path.join(this.options.logDirectory, file);
      const content = await fs.readFile(filePath, 'utf8');
      const lines = content.split('\n').filter(line => line.trim());

      for (const line of lines) {
        try {
          const entry = JSON.parse(line) as AuditLogEntry;
          results.push(entry);
        } catch (error) {
          // Skip malformed lines
        }
      }
    }

    return results;
  }

  private applyQueryFilters(logs: AuditLogEntry[], query: AuditQuery): AuditLogEntry[] {
    let filtered = logs;

    if (query.startDate) {
      filtered = filtered.filter(log => log.timestamp >= query.startDate!);
    }

    if (query.endDate) {
      filtered = filtered.filter(log => log.timestamp <= query.endDate!);
    }

    if (query.userId) {
      filtered = filtered.filter(log => log.userId === query.userId);
    }

    if (query.action) {
      filtered = filtered.filter(log => log.action === query.action);
    }

    if (query.resourceType) {
      filtered = filtered.filter(log => log.resourceType === query.resourceType);
    }

    if (query.resourceId) {
      filtered = filtered.filter(log => log.resourceId === query.resourceId);
    }

    if (query.level) {
      filtered = filtered.filter(log => log.level === query.level);
    }

    // Sort
    filtered.sort((a, b) => {
      const order = query.sortOrder === 'asc' ? 1 : -1;
      return (b.timestamp.getTime() - a.timestamp.getTime()) * order;
    });

    // Pagination
    if (query.offset) {
      filtered = filtered.slice(query.offset);
    }

    if (query.limit) {
      filtered = filtered.slice(0, query.limit);
    }

    return filtered;
  }

  private generateSummary(logs: AuditLogEntry[]): AuditSummary {
    return {
      totalEvents: logs.length,
      uniqueUsers: new Set(logs.map(l => l.userId)).size,
      actions: this.groupBy(logs, 'action') as Record<AuditAction, number>,
      riskLevels: this.groupBy(logs, 'level'),
      resourceTypes: this.groupBy(logs, 'resourceType')
    };
  }

  private extractActivities(logs: AuditLogEntry[]): AuditActivity[] {
    return logs.slice(0, 100).map(log => ({
      timestamp: log.timestamp,
      action: log.action,
      user: log.userEmail,
      resource: `${log.resourceType}:${log.resourceId}`,
      outcome: 'success', // This would be determined from log details
      details: JSON.stringify(log.details)
    }));
  }

  private analyzeUserActivities(logs: AuditLogEntry[]): UserActivity[] {
    const userMap = new Map<string, UserActivity>();

    for (const log of logs) {
      let activity = userMap.get(log.userId);
      if (!activity) {
        activity = {
          userId: log.userId,
          userEmail: log.userEmail,
          totalActions: 0,
          lastActivity: log.timestamp,
          actions: {} as Record<AuditAction, number>,
          riskScore: 0
        };
        userMap.set(log.userId, activity);
      }

      activity.totalActions++;
      activity.actions[log.action] = (activity.actions[log.action] || 0) + 1;
      if (log.timestamp > activity.lastActivity) {
        activity.lastActivity = log.timestamp;
      }
    }

    // Calculate risk scores
    for (const activity of userMap.values()) {
      activity.riskScore = this.calculateUserRiskScore(activity);
    }

    return Array.from(userMap.values())
      .sort((a, b) => b.riskScore - a.riskScore)
      .slice(0, 50); // Top 50 users
  }

  private assessRisk(logs: AuditLogEntry[]): RiskAssessment {
    const riskFactors: string[] = [];
    let score = 0;

    // Check for high-risk activities
    const highRiskActions = logs.filter(l =>
      [AuditAction.DELETE, AuditAction.ADMIN].includes(l.action)
    ).length;

    if (highRiskActions > 10) {
      riskFactors.push('High number of high-risk administrative actions');
      score += 30;
    }

    // Check for unusual activity patterns
    const nightTimeActivity = logs.filter(l => {
      const hour = l.timestamp.getHours();
      return hour < 6 || hour > 22;
    }).length;

    if (nightTimeActivity > logs.length * 0.1) {
      riskFactors.push('Significant after-hours activity detected');
      score += 20;
    }

    // Check for failed actions
    const failedActions = logs.filter(l =>
      l.details.success === false
    ).length;

    if (failedActions > logs.length * 0.05) {
      riskFactors.push('High failure rate in actions');
      score += 15;
    }

    let overallRisk: 'low' | 'medium' | 'high' | 'critical';
    if (score >= 75) overallRisk = 'critical';
    else if (score >= 50) overallRisk = 'high';
    else if (score >= 25) overallRisk = 'medium';
    else overallRisk = 'low';

    return {
      overallRisk,
      riskFactors,
      recommendations: this.generateRecommendations(riskFactors),
      score
    };
  }

  private calculateUserRiskScore(activity: UserActivity): number {
    let score = 0;

    // High-risk actions
    const highRiskActions = (activity.actions[AuditAction.DELETE] || 0) +
                           (activity.actions[AuditAction.ADMIN] || 0);
    score += highRiskActions * 10;

    // Activity volume
    if (activity.totalActions > 1000) {
      score += 20;
    }

    return Math.min(score, 100);
  }

  private generateRecommendations(riskFactors: string[]): string[] {
    const recommendations: string[] = [];

    if (riskFactors.some(f => f.includes('administrative'))) {
      recommendations.push('Review administrative permissions and implement additional approval steps');
    }

    if (riskFactors.some(f => f.includes('after-hours'))) {
      recommendations.push('Implement time-based access controls for sensitive operations');
    }

    if (riskFactors.some(f => f.includes('failure rate'))) {
      recommendations.push('Investigate and address causes of high failure rates');
    }

    if (recommendations.length === 0) {
      recommendations.push('Continue monitoring current activity levels');
    }

    return recommendations;
  }

  private groupBy(array: any[], key: string): Record<string, number> {
    return array.reduce((groups, item) => {
      const value = item[key];
      groups[value] = (groups[value] || 0) + 1;
      return groups;
    }, {});
  }

  private getHourlyDistribution(logs: AuditLogEntry[]): Record<number, number> {
    const distribution: Record<number, number> = {};

    for (let hour = 0; hour < 24; hour++) {
      distribution[hour] = 0;
    }

    for (const log of logs) {
      const hour = log.timestamp.getHours();
      distribution[hour]++;
    }

    return distribution;
  }

  private getTopUsers(logs: AuditLogEntry[], limit: number): any[] {
    const userCounts = this.groupBy(logs, 'userEmail');
    return Object.entries(userCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, limit)
      .map(([email, count]) => ({ email, count }));
  }

  private convertToCSV(logs: AuditLogEntry[]): string {
    if (logs.length === 0) return '';

    const headers = [
      'Timestamp', 'Action', 'User', 'Resource Type', 'Resource ID',
      'IP Address', 'Details'
    ];

    const rows = logs.map(log => [
      log.timestamp.toISOString(),
      log.action,
      log.userEmail,
      log.resourceType,
      log.resourceId,
      log.ipAddress || '',
      JSON.stringify(log.details).replace(/"/g, '""')
    ]);

    return [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n');
  }

  private convertToXML(logs: AuditLogEntry[]): string {
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<auditLogs>\n';

    for (const log of logs) {
      xml += '  <entry>\n';
      xml += `    <id>${log.id}</id>\n`;
      xml += `    <timestamp>${log.timestamp.toISOString()}</timestamp>\n`;
      xml += `    <action>${log.action}</action>\n`;
      xml += `    <userId>${log.userId}</userId>\n`;
      xml += `    <userEmail>${log.userEmail}</userEmail>\n`;
      xml += `    <resourceType>${log.resourceType}</resourceType>\n`;
      xml += `    <resourceId>${log.resourceId}</resourceId>\n`;
      if (log.ipAddress) xml += `    <ipAddress>${log.ipAddress}</ipAddress>\n`;
      xml += `    <details>${JSON.stringify(log.details)}</details>\n`;
      xml += '  </entry>\n';
    }

    xml += '</auditLogs>';
    return xml;
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Cleanup resources
   */
  async destroy(): Promise<void> {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }

    if (this.writeStream) {
      this.writeStream.end();
    }

    await this.flush();
  }
}