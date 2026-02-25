import {
  User,
  Permission,
  ApprovalRequest,
  AuditEvent,
  AuditAction,
  AuditLevel
} from '../types/approval.types.js';
import { EventEmitter } from 'events';
import * as crypto from 'crypto';

export interface SecurityManagerOptions {
  enableEncryption: boolean;
  encryptionAlgorithm: string;
  encryptionKey: string;
  enableAccessControl: boolean;
  enableAuditLogging: boolean;
  auditLevel: AuditLevel;
  enableSessionManagement: boolean;
  sessionTimeout: number; // minutes
  maxFailedAttempts: number;
  lockoutDuration: number; // minutes
  enableIPWhitelist: boolean;
  allowedIPs: string[];
  enableRoleBasedAccess: boolean;
}

export interface SecurityContext {
  user: User;
  sessionId: string;
  ipAddress: string;
  userAgent: string;
  permissions: Permission[];
  isAuthenticated: boolean;
  isAuthorized: boolean;
  securityToken: string;
  createdAt: Date;
  lastActivity: Date;
  metadata?: Record<string, any>;
}

export interface AccessControlRule {
  id: string;
  resource: string;
  action: string;
  requiredPermissions: Permission[];
  requiredRoles: string[];
  conditions: AccessCondition[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface AccessCondition {
  type: ConditionType;
  field: string;
  operator: ComparisonOperator;
  value: any;
  logic: LogicOperator;
}

export interface SecurityEvent {
  id: string;
  type: SecurityEventType;
  userId?: string;
  ipAddress: string;
  userAgent: string;
  resource: string;
  action: string;
  success: boolean;
  details: Record<string, any>;
  timestamp: Date;
  severity: SecuritySeverity;
}

export interface UserSession {
  id: string;
  userId: string;
  ipAddress: string;
  userAgent: string;
  createdAt: Date;
  lastActivity: Date;
  isActive: boolean;
  securityToken: string;
  permissions: Permission[];
  metadata?: Record<string, any>;
}

export interface FailedAttempt {
  userId: string;
  ipAddress: string;
  timestamp: Date;
  reason: string;
}

export enum SecurityEventType {
  LOGIN_SUCCESS = 'login_success',
  LOGIN_FAILURE = 'login_failure',
  LOGOUT = 'logout',
  ACCESS_GRANTED = 'access_granted',
  ACCESS_DENIED = 'access_denied',
  PERMISSION_ESCALATION = 'permission_escalation',
  SESSION_EXPIRED = 'session_expired',
  SUSPICIOUS_ACTIVITY = 'suspicious_activity',
  SECURITY_VIOLATION = 'security_violation',
  DATA_ACCESS = 'data_access',
  DATA_MODIFICATION = 'data_modification'
}

export enum SecuritySeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum ConditionType {
  TIME_RANGE = 'time_range',
  IP_RANGE = 'ip_range',
  USER_ATTRIBUTE = 'user_attribute',
  RESOURCE_ATTRIBUTE = 'resource_attribute',
  CUSTOM = 'custom'
}

export enum ComparisonOperator {
  EQUALS = 'equals',
  NOT_EQUALS = 'not_equals',
  GREATER_THAN = 'greater_than',
  LESS_THAN = 'less_than',
  CONTAINS = 'contains',
  IN = 'in',
  NOT_IN = 'not_in',
  MATCHES = 'matches'
}

export enum LogicOperator {
  AND = 'and',
  OR = 'or',
  NOT = 'not'
}

export class SecurityManager extends EventEmitter {
  private options: SecurityManagerOptions;
  private sessions: Map<string, UserSession> = new Map();
  private accessRules: Map<string, AccessControlRule> = new Map();
  private securityEvents: SecurityEvent[] = [];
  private failedAttempts: Map<string, FailedAttempt[]> = new Map();
  private lockedAccounts: Map<string, Date> = new Map();

  constructor(options: Partial<SecurityManagerOptions> = {}) {
    super();
    this.options = {
      enableEncryption: true,
      encryptionAlgorithm: 'aes-256-gcm',
      encryptionKey: process.env.ENCRYPTION_KEY || this.generateEncryptionKey(),
      enableAccessControl: true,
      enableAuditLogging: true,
      auditLevel: AuditLevel.STANDARD,
      enableSessionManagement: true,
      sessionTimeout: 60, // 1 hour
      maxFailedAttempts: 5,
      lockoutDuration: 30, // 30 minutes
      enableIPWhitelist: false,
      allowedIPs: [],
      enableRoleBasedAccess: true,
      ...options
    };

    this.setupDefaultAccessRules();
    this.startSessionCleanup();
  }

  /**
   * Authenticate user and create security context
   */
  async authenticate(
    user: User,
    ipAddress: string,
    userAgent: string,
    credentials?: any
  ): Promise<SecurityContext> {
    try {
      // Check if account is locked
      if (this.isAccountLocked(user.id)) {
        await this.logSecurityEvent({
          type: SecurityEventType.LOGIN_FAILURE,
          userId: user.id,
          ipAddress,
          userAgent,
          resource: 'authentication',
          action: 'login',
          success: false,
          details: { reason: 'account_locked' },
          severity: SecuritySeverity.MEDIUM
        });
        throw new Error('Account is temporarily locked due to multiple failed attempts');
      }

      // Check IP whitelist if enabled
      if (this.options.enableIPWhitelist && !this.isIPAllowed(ipAddress)) {
        await this.logSecurityEvent({
          type: SecurityEventType.ACCESS_DENIED,
          userId: user.id,
          ipAddress,
          userAgent,
          resource: 'authentication',
          action: 'login',
          success: false,
          details: { reason: 'ip_not_whitelisted' },
          severity: SecuritySeverity.HIGH
        });
        throw new Error('Access denied: IP address not whitelisted');
      }

      // Validate user status
      if (!user.isActive) {
        await this.logSecurityEvent({
          type: SecurityEventType.LOGIN_FAILURE,
          userId: user.id,
          ipAddress,
          userAgent,
          resource: 'authentication',
          action: 'login',
          success: false,
          details: { reason: 'account_inactive' },
          severity: SecuritySeverity.MEDIUM
        });
        throw new Error('Account is inactive');
      }

      // Create session
      const session = await this.createSession(user, ipAddress, userAgent);

      // Create security context
      const securityContext: SecurityContext = {
        user,
        sessionId: session.id,
        ipAddress,
        userAgent,
        permissions: user.permissions,
        isAuthenticated: true,
        isAuthorized: true,
        securityToken: session.securityToken,
        createdAt: new Date(),
        lastActivity: new Date()
      };

      // Clear failed attempts
      this.clearFailedAttempts(user.id);

      // Log successful authentication
      await this.logSecurityEvent({
        type: SecurityEventType.LOGIN_SUCCESS,
        userId: user.id,
        ipAddress,
        userAgent,
        resource: 'authentication',
        action: 'login',
        success: true,
        details: { sessionId: session.id },
        severity: SecuritySeverity.LOW
      });

      this.emit('userAuthenticated', securityContext);

      return securityContext;

    } catch (error) {
      // Record failed attempt
      await this.recordFailedAttempt(user.id, ipAddress, (error as Error).message);

      // Check if account should be locked
      if (this.shouldLockAccount(user.id)) {
        this.lockAccount(user.id);
      }

      throw error;
    }
  }

  /**
   * Authorize user access to resource/action
   */
  async authorize(
    securityContext: SecurityContext,
    resource: string,
    action: string,
    requestData?: any
  ): Promise<boolean> {
    try {
      if (!this.options.enableAccessControl) {
        return true;
      }

      // Check session validity
      if (!this.isSessionValid(securityContext.sessionId)) {
        await this.logSecurityEvent({
          type: SecurityEventType.SESSION_EXPIRED,
          userId: securityContext.user.id,
          ipAddress: securityContext.ipAddress,
          userAgent: securityContext.userAgent,
          resource,
          action,
          success: false,
          details: { sessionId: securityContext.sessionId },
          severity: SecuritySeverity.MEDIUM
        });
        return false;
      }

      // Find applicable access rules
      const applicableRules = this.findApplicableRules(resource, action);

      // Check permissions
      const hasAccess = await this.checkPermissions(
        securityContext,
        applicableRules,
        requestData
      );

      // Log access attempt
      await this.logSecurityEvent({
        type: hasAccess ? SecurityEventType.ACCESS_GRANTED : SecurityEventType.ACCESS_DENIED,
        userId: securityContext.user.id,
        ipAddress: securityContext.ipAddress,
        userAgent: securityContext.userAgent,
        resource,
        action,
        success: hasAccess,
        details: {
          permissions: securityContext.permissions,
          rules: applicableRules.map(r => r.id),
          requestData: this.sanitizeRequestData(requestData)
        },
        severity: hasAccess ? SecuritySeverity.LOW : SecuritySeverity.MEDIUM
      });

      // Update session activity
      this.updateSessionActivity(securityContext.sessionId);

      return hasAccess;

    } catch (error) {
      await this.logSecurityEvent({
        type: SecurityEventType.SECURITY_VIOLATION,
        userId: securityContext.user.id,
        ipAddress: securityContext.ipAddress,
        userAgent: securityContext.userAgent,
        resource,
        action,
        success: false,
        details: { error: (error as Error).message },
        severity: SecuritySeverity.HIGH
      });

      return false;
    }
  }

  /**
   * Encrypt sensitive data
   */
  encrypt(data: string): string {
    if (!this.options.enableEncryption) {
      return data;
    }

    const cipher = crypto.createCipher(this.options.encryptionAlgorithm, this.options.encryptionKey);
    let encrypted = cipher.update(data, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
  }

  /**
   * Decrypt sensitive data
   */
  decrypt(encryptedData: string): string {
    if (!this.options.enableEncryption) {
      return encryptedData;
    }

    const decipher = crypto.createDecipher(this.options.encryptionAlgorithm, this.options.encryptionKey);
    let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  }

  /**
   * Create audit event
   */
  async createAuditEvent(
    action: AuditAction,
    user: User,
    details: Record<string, any>,
    ipAddress?: string,
    userAgent?: string
  ): Promise<AuditEvent> {
    const auditEvent: AuditEvent = {
      id: this.generateId(),
      timestamp: new Date(),
      action,
      user,
      details,
      ipAddress,
      userAgent
    };

    // Log to security events if audit logging is enabled
    if (this.options.enableAuditLogging) {
      await this.logSecurityEvent({
        type: SecurityEventType.DATA_MODIFICATION,
        userId: user.id,
        ipAddress: ipAddress || '',
        userAgent: userAgent || '',
        resource: 'audit',
        action: action,
        success: true,
        details,
        severity: SecuritySeverity.LOW
      });
    }

    this.emit('auditEventCreated', auditEvent);

    return auditEvent;
  }

  /**
   * Validate security token
   */
  validateSecurityToken(token: string, sessionId: string): boolean {
    const session = this.sessions.get(sessionId);
    if (!session || !session.isActive) {
      return false;
    }

    return session.securityToken === token;
  }

  /**
   * Logout user and invalidate session
   */
  async logout(securityContext: SecurityContext): Promise<void> {
    const session = this.sessions.get(securityContext.sessionId);
    if (session) {
      session.isActive = false;
      session.lastActivity = new Date();
    }

    await this.logSecurityEvent({
      type: SecurityEventType.LOGOUT,
      userId: securityContext.user.id,
      ipAddress: securityContext.ipAddress,
      userAgent: securityContext.userAgent,
      resource: 'authentication',
      action: 'logout',
      success: true,
      details: { sessionId: securityContext.sessionId },
      severity: SecuritySeverity.LOW
    });

    this.emit('userLoggedOut', securityContext);
  }

  /**
   * Add access control rule
   */
  addAccessRule(rule: Omit<AccessControlRule, 'id' | 'createdAt' | 'updatedAt'>): AccessControlRule {
    const accessRule: AccessControlRule = {
      ...rule,
      id: this.generateId(),
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.accessRules.set(accessRule.id, accessRule);
    this.emit('accessRuleAdded', accessRule);

    return accessRule;
  }

  /**
   * Get security events with filtering
   */
  getSecurityEvents(
    filters: {
      userId?: string;
      type?: SecurityEventType;
      severity?: SecuritySeverity;
      startDate?: Date;
      endDate?: Date;
      limit?: number;
    } = {}
  ): SecurityEvent[] {
    let events = this.securityEvents;

    if (filters.userId) {
      events = events.filter(e => e.userId === filters.userId);
    }

    if (filters.type) {
      events = events.filter(e => e.type === filters.type);
    }

    if (filters.severity) {
      events = events.filter(e => e.severity === filters.severity);
    }

    if (filters.startDate) {
      events = events.filter(e => e.timestamp >= filters.startDate!);
    }

    if (filters.endDate) {
      events = events.filter(e => e.timestamp <= filters.endDate!);
    }

    // Sort by timestamp (newest first)
    events = events.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

    if (filters.limit) {
      events = events.slice(0, filters.limit);
    }

    return events;
  }

  /**
   * Get active sessions
   */
  getActiveSessions(userId?: string): UserSession[] {
    let sessions = Array.from(this.sessions.values()).filter(s => s.isActive);

    if (userId) {
      sessions = sessions.filter(s => s.userId === userId);
    }

    return sessions;
  }

  /**
   * Invalidate all sessions for a user
   */
  invalidateUserSessions(userId: string): void {
    for (const session of this.sessions.values()) {
      if (session.userId === userId) {
        session.isActive = false;
        session.lastActivity = new Date();
      }
    }

    this.emit('userSessionsInvalidated', userId);
  }

  /**
   * Check for suspicious activity
   */
  detectSuspiciousActivity(userId: string): boolean {
    const recentEvents = this.getSecurityEvents({
      userId,
      startDate: new Date(Date.now() - 60 * 60 * 1000), // Last hour
      limit: 100
    });

    // Multiple failed login attempts
    const failedLogins = recentEvents.filter(e => e.type === SecurityEventType.LOGIN_FAILURE).length;
    if (failedLogins > 3) {
      return true;
    }

    // Multiple access denied events
    const accessDenied = recentEvents.filter(e => e.type === SecurityEventType.ACCESS_DENIED).length;
    if (accessDenied > 5) {
      return true;
    }

    // Multiple different IP addresses
    const ipAddresses = new Set(recentEvents.map(e => e.ipAddress));
    if (ipAddresses.size > 3) {
      return true;
    }

    return false;
  }

  // Private methods

  private async createSession(user: User, ipAddress: string, userAgent: string): Promise<UserSession> {
    const session: UserSession = {
      id: this.generateId(),
      userId: user.id,
      ipAddress,
      userAgent,
      createdAt: new Date(),
      lastActivity: new Date(),
      isActive: true,
      securityToken: this.generateSecurityToken(),
      permissions: user.permissions
    };

    this.sessions.set(session.id, session);
    return session;
  }

  private isSessionValid(sessionId: string): boolean {
    const session = this.sessions.get(sessionId);
    if (!session || !session.isActive) {
      return false;
    }

    // Check session timeout
    const now = new Date();
    const sessionAge = now.getTime() - session.lastActivity.getTime();
    const timeoutMs = this.options.sessionTimeout * 60 * 1000;

    if (sessionAge > timeoutMs) {
      session.isActive = false;
      return false;
    }

    return true;
  }

  private updateSessionActivity(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.lastActivity = new Date();
    }
  }

  private findApplicableRules(resource: string, action: string): AccessControlRule[] {
    return Array.from(this.accessRules.values()).filter(rule => {
      if (!rule.isActive) return false;

      // Check resource match (support wildcards)
      const resourceMatch = rule.resource === '*' || rule.resource === resource ||
        (rule.resource.endsWith('*') && resource.startsWith(rule.resource.slice(0, -1)));

      // Check action match (support wildcards)
      const actionMatch = rule.action === '*' || rule.action === action ||
        (rule.action.endsWith('*') && action.startsWith(rule.action.slice(0, -1)));

      return resourceMatch && actionMatch;
    });
  }

  private async checkPermissions(
    securityContext: SecurityContext,
    rules: AccessControlRule[],
    requestData?: any
  ): Promise<boolean> {
    // If no rules apply, default to checking user permissions
    if (rules.length === 0) {
      return this.checkDefaultPermissions(securityContext);
    }

    // Check each rule
    for (const rule of rules) {
      const hasRequiredPermissions = rule.requiredPermissions.every(permission =>
        securityContext.permissions.includes(permission)
      );

      const hasRequiredRoles = rule.requiredRoles.every(role =>
        securityContext.user.role === role
      );

      const conditionsMet = await this.evaluateConditions(rule.conditions, securityContext, requestData);

      if (hasRequiredPermissions && hasRequiredRoles && conditionsMet) {
        return true;
      }
    }

    return false;
  }

  private checkDefaultPermissions(securityContext: SecurityContext): boolean {
    // Default permission check based on user role
    switch (securityContext.user.role) {
      case 'admin':
        return true;
      case 'approver':
        return securityContext.permissions.includes(Permission.APPROVE);
      case 'reviewer':
        return securityContext.permissions.includes(Permission.READ);
      default:
        return false;
    }
  }

  private async evaluateConditions(
    conditions: AccessCondition[],
    securityContext: SecurityContext,
    requestData?: any
  ): Promise<boolean> {
    if (conditions.length === 0) return true;

    // Simple condition evaluation - can be enhanced for complex logic
    for (const condition of conditions) {
      const result = await this.evaluateCondition(condition, securityContext, requestData);
      if (!result) return false;
    }

    return true;
  }

  private async evaluateCondition(
    condition: AccessCondition,
    securityContext: SecurityContext,
    requestData?: any
  ): Promise<boolean> {
    let value: any;

    switch (condition.type) {
      case ConditionType.TIME_RANGE:
        value = new Date().getHours();
        break;
      case ConditionType.IP_RANGE:
        value = securityContext.ipAddress;
        break;
      case ConditionType.USER_ATTRIBUTE:
        value = this.getNestedValue(securityContext.user, condition.field);
        break;
      case ConditionType.RESOURCE_ATTRIBUTE:
        value = this.getNestedValue(requestData, condition.field);
        break;
      default:
        return true;
    }

    return this.compareValues(value, condition.operator, condition.value);
  }

  private compareValues(value: any, operator: ComparisonOperator, expectedValue: any): boolean {
    switch (operator) {
      case ComparisonOperator.EQUALS:
        return value === expectedValue;
      case ComparisonOperator.NOT_EQUALS:
        return value !== expectedValue;
      case ComparisonOperator.GREATER_THAN:
        return value > expectedValue;
      case ComparisonOperator.LESS_THAN:
        return value < expectedValue;
      case ComparisonOperator.CONTAINS:
        return String(value).includes(String(expectedValue));
      case ComparisonOperator.IN:
        return Array.isArray(expectedValue) && expectedValue.includes(value);
      case ComparisonOperator.NOT_IN:
        return Array.isArray(expectedValue) && !expectedValue.includes(value);
      case ComparisonOperator.MATCHES:
        return new RegExp(expectedValue).test(String(value));
      default:
        return true;
    }
  }

  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  private async logSecurityEvent(event: Omit<SecurityEvent, 'id' | 'timestamp'>): Promise<void> {
    const securityEvent: SecurityEvent = {
      ...event,
      id: this.generateId(),
      timestamp: new Date()
    };

    this.securityEvents.push(securityEvent);

    // Keep only recent events (last 10000)
    if (this.securityEvents.length > 10000) {
      this.securityEvents = this.securityEvents.slice(-10000);
    }

    // Emit event for external handling
    this.emit('securityEvent', securityEvent);

    // Check for suspicious activity
    if (event.userId && this.detectSuspiciousActivity(event.userId)) {
      this.emit('suspiciousActivity', {
        userId: event.userId,
        event: securityEvent
      });
    }
  }

  private async recordFailedAttempt(userId: string, ipAddress: string, reason: string): Promise<void> {
    const attempts = this.failedAttempts.get(userId) || [];
    attempts.push({
      userId,
      ipAddress,
      timestamp: new Date(),
      reason
    });

    // Keep only recent attempts (last 24 hours)
    const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const recentAttempts = attempts.filter(a => a.timestamp > dayAgo);

    this.failedAttempts.set(userId, recentAttempts);
  }

  private shouldLockAccount(userId: string): boolean {
    const attempts = this.failedAttempts.get(userId) || [];
    const recentAttempts = attempts.filter(a => {
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
      return a.timestamp > fiveMinutesAgo;
    });

    return recentAttempts.length >= this.options.maxFailedAttempts;
  }

  private lockAccount(userId: string): void {
    const lockUntil = new Date(Date.now() + this.options.lockoutDuration * 60 * 1000);
    this.lockedAccounts.set(userId, lockUntil);

    this.emit('accountLocked', { userId, lockUntil });
  }

  private isAccountLocked(userId: string): boolean {
    const lockUntil = this.lockedAccounts.get(userId);
    if (!lockUntil) return false;

    if (new Date() > lockUntil) {
      this.lockedAccounts.delete(userId);
      return false;
    }

    return true;
  }

  private clearFailedAttempts(userId: string): void {
    this.failedAttempts.delete(userId);
  }

  private isIPAllowed(ipAddress: string): boolean {
    if (!this.options.enableIPWhitelist || this.options.allowedIPs.length === 0) {
      return true;
    }

    return this.options.allowedIPs.includes(ipAddress);
  }

  private sanitizeRequestData(data: any): any {
    if (!data) return data;

    // Remove sensitive fields
    const sanitized = { ...data };
    const sensitiveFields = ['password', 'token', 'secret', 'key', 'credential'];

    for (const field of sensitiveFields) {
      if (sanitized[field]) {
        sanitized[field] = '[REDACTED]';
      }
    }

    return sanitized;
  }

  private setupDefaultAccessRules(): void {
    // Admin access rule
    this.addAccessRule({
      resource: '*',
      action: '*',
      requiredPermissions: [],
      requiredRoles: ['admin'],
      conditions: [],
      isActive: true
    });

    // Approver access rule
    this.addAccessRule({
      resource: 'approval',
      action: 'approve',
      requiredPermissions: [Permission.APPROVE],
      requiredRoles: ['approver'],
      conditions: [],
      isActive: true
    });

    // Read access rule
    this.addAccessRule({
      resource: 'approval',
      action: 'read',
      requiredPermissions: [Permission.READ],
      requiredRoles: ['reviewer', 'approver', 'developer'],
      conditions: [],
      isActive: true
    });
  }

  private startSessionCleanup(): void {
    if (!this.options.enableSessionManagement) return;

    // Clean up expired sessions every 5 minutes
    setInterval(() => {
      const now = new Date();
      const timeoutMs = this.options.sessionTimeout * 60 * 1000;

      for (const [sessionId, session] of this.sessions) {
        if (session.isActive && (now.getTime() - session.lastActivity.getTime()) > timeoutMs) {
          session.isActive = false;
          this.emit('sessionExpired', session);
        }
      }
    }, 5 * 60 * 1000);
  }

  private generateEncryptionKey(): string {
    return crypto.randomBytes(32).toString('hex');
  }

  private generateSecurityToken(): string {
    return crypto.randomBytes(32).toString('hex');
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}