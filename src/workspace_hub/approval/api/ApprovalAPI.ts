import {
  ApprovalRequest,
  ApprovalResponse,
  ApprovalDecision,
  BaselineUpdateRequest,
  User,
  ApprovalTemplate,
  WorkflowMetrics,
  NotificationMessage,
  DeploymentState,
  ApprovalStatus,
  ApprovalPriority
} from '../types/approval.types.js';
import { ApprovalWorkflowEngine } from '../engine/ApprovalWorkflowEngine.js';
import { BaselineUpdateManager } from '../manager/BaselineUpdateManager.js';
import { GitHubIntegration } from '../github/GitHubIntegration.js';
import { NotificationSystem } from '../notifications/NotificationSystem.js';

export interface ApprovalAPIOptions {
  enableRateLimit: boolean;
  rateLimitRequests: number;
  rateLimitWindow: number; // milliseconds
  enableAuthentication: boolean;
  enableAuditLogging: boolean;
  enableCaching: boolean;
  cacheTimeout: number; // milliseconds
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  pagination?: PaginationInfo;
  metadata?: Record<string, any>;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface APIRequest {
  user: User;
  headers: Record<string, string>;
  query: Record<string, string>;
  params: Record<string, string>;
  body: any;
  ip: string;
  userAgent: string;
}

export interface RequestFilters {
  status?: ApprovalStatus;
  priority?: ApprovalPriority;
  type?: string;
  assignedTo?: string;
  createdBy?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export class ApprovalAPI {
  private workflowEngine: ApprovalWorkflowEngine;
  private updateManager: BaselineUpdateManager;
  private githubIntegration?: GitHubIntegration;
  private notificationSystem: NotificationSystem;
  private options: ApprovalAPIOptions;
  private rateLimitMap: Map<string, { count: number; resetTime: number }> = new Map();
  private cache: Map<string, { data: any; expires: number }> = new Map();

  constructor(
    workflowEngine: ApprovalWorkflowEngine,
    updateManager: BaselineUpdateManager,
    notificationSystem: NotificationSystem,
    githubIntegration?: GitHubIntegration,
    options: Partial<ApprovalAPIOptions> = {}
  ) {
    this.workflowEngine = workflowEngine;
    this.updateManager = updateManager;
    this.githubIntegration = githubIntegration;
    this.notificationSystem = notificationSystem;
    this.options = {
      enableRateLimit: true,
      rateLimitRequests: 100,
      rateLimitWindow: 60000, // 1 minute
      enableAuthentication: true,
      enableAuditLogging: true,
      enableCaching: true,
      cacheTimeout: 300000, // 5 minutes
      ...options
    };
  }

  // Approval Request Endpoints

  /**
   * GET /api/approvals
   * Get approval requests with filtering and pagination
   */
  async getApprovalRequests(request: APIRequest): Promise<APIResponse<ApprovalRequest[]>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const filters: RequestFilters = this.parseFilters(request.query);
      const cacheKey = `approvals:${JSON.stringify(filters)}:${request.user.id}`;

      // Check cache
      if (this.options.enableCaching) {
        const cached = this.getFromCache(cacheKey);
        if (cached) {
          return cached;
        }
      }

      // Get requests based on user permissions
      let requests = this.workflowEngine.getAllRequests();

      // Apply access control
      requests = this.filterRequestsByAccess(requests, request.user);

      // Apply filters
      requests = this.applyFilters(requests, filters);

      // Apply sorting
      requests = this.applySorting(requests, filters.sortBy, filters.sortOrder);

      // Apply pagination
      const pagination = this.calculatePagination(requests.length, filters.page, filters.limit);
      const paginatedRequests = this.applyPagination(requests, filters.page, filters.limit);

      const response: APIResponse<ApprovalRequest[]> = {
        success: true,
        data: paginatedRequests,
        pagination
      };

      // Cache response
      if (this.options.enableCaching) {
        this.setCache(cacheKey, response);
      }

      return response;

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  /**
   * GET /api/approvals/:id
   * Get specific approval request
   */
  async getApprovalRequest(request: APIRequest): Promise<APIResponse<ApprovalRequest>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const requestId = request.params.id;
      const approvalRequest = this.workflowEngine.getRequest(requestId);

      if (!approvalRequest) {
        return {
          success: false,
          error: 'APPROVAL_REQUEST_NOT_FOUND',
          message: 'Approval request not found'
        };
      }

      // Check access permissions
      if (!this.hasRequestAccess(approvalRequest, request.user)) {
        return {
          success: false,
          error: 'ACCESS_DENIED',
          message: 'You do not have permission to view this request'
        };
      }

      return {
        success: true,
        data: approvalRequest
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  /**
   * POST /api/approvals
   * Create new approval request
   */
  async createApprovalRequest(request: APIRequest): Promise<APIResponse<ApprovalRequest>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const approvalData = request.body;

      // Validate request data
      const validation = this.validateApprovalRequestData(approvalData);
      if (!validation.valid) {
        return {
          success: false,
          error: 'VALIDATION_ERROR',
          message: validation.message
        };
      }

      // Create approval request
      const approvalRequest = await this.workflowEngine.createRequest({
        ...approvalData,
        requester: request.user
      });

      // Send notifications
      if (approvalRequest.approvers.length > 0) {
        const currentStepApprovers = approvalRequest.approvers[0].approvers;
        await this.notificationSystem.sendApprovalRequest(
          approvalRequest,
          currentStepApprovers
        );
      }

      // Create GitHub PR if baseline update
      if (approvalRequest.baselineUpdate && this.githubIntegration) {
        try {
          await this.githubIntegration.createApprovalPR(
            approvalRequest,
            approvalRequest.baselineUpdate
          );
        } catch (error) {
          console.warn('Failed to create GitHub PR:', error);
        }
      }

      // Clear relevant caches
      this.clearCachePattern('approvals:');

      return {
        success: true,
        data: approvalRequest,
        message: 'Approval request created successfully'
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  /**
   * POST /api/approvals/:id/respond
   * Respond to approval request
   */
  async respondToApproval(request: APIRequest): Promise<APIResponse<ApprovalRequest>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const requestId = request.params.id;
      const { stepId, decision, reason, comments } = request.body;

      // Validate response data
      if (!stepId || !decision) {
        return {
          success: false,
          error: 'VALIDATION_ERROR',
          message: 'Step ID and decision are required'
        };
      }

      if (!Object.values(ApprovalDecision).includes(decision)) {
        return {
          success: false,
          error: 'VALIDATION_ERROR',
          message: 'Invalid decision value'
        };
      }

      // Process the response
      const updatedRequest = await this.workflowEngine.processResponse(
        requestId,
        stepId,
        {
          approver: request.user,
          decision,
          reason,
          comments,
          ipAddress: request.ip,
          metadata: {
            userAgent: request.userAgent
          }
        }
      );

      // Send decision notifications
      const recipients = [updatedRequest.requester];
      if (updatedRequest.approvers[updatedRequest.currentStep]) {
        recipients.push(...updatedRequest.approvers[updatedRequest.currentStep].approvers);
      }

      await this.notificationSystem.sendApprovalDecision(
        updatedRequest,
        updatedRequest.approvers.find(s => s.id === stepId)?.responses.slice(-1)[0]!,
        recipients
      );

      // Update GitHub PR status
      if (this.githubIntegration) {
        try {
          await this.githubIntegration.updatePRStatus(requestId, updatedRequest.status);
        } catch (error) {
          console.warn('Failed to update GitHub PR:', error);
        }
      }

      // Execute baseline update if approved
      if (updatedRequest.status === ApprovalStatus.APPROVED && updatedRequest.baselineUpdate) {
        this.executeBaselineUpdate(updatedRequest.baselineUpdate, updatedRequest.id);
      }

      // Clear relevant caches
      this.clearCachePattern('approvals:');

      return {
        success: true,
        data: updatedRequest,
        message: 'Response submitted successfully'
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  /**
   * POST /api/approvals/:id/delegate
   * Delegate approval to another user
   */
  async delegateApproval(request: APIRequest): Promise<APIResponse<void>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const requestId = request.params.id;
      const { stepId, toUserId, reason } = request.body;

      // Validate delegation data
      if (!stepId || !toUserId) {
        return {
          success: false,
          error: 'VALIDATION_ERROR',
          message: 'Step ID and target user ID are required'
        };
      }

      // Get target user (this would typically come from a user service)
      const toUser = await this.getUserById(toUserId);
      if (!toUser) {
        return {
          success: false,
          error: 'USER_NOT_FOUND',
          message: 'Target user not found'
        };
      }

      await this.workflowEngine.delegateApproval(
        requestId,
        stepId,
        request.user,
        toUser,
        reason
      );

      // Clear relevant caches
      this.clearCachePattern('approvals:');

      return {
        success: true,
        message: 'Approval delegated successfully'
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  /**
   * POST /api/approvals/:id/withdraw
   * Withdraw approval request
   */
  async withdrawApproval(request: APIRequest): Promise<APIResponse<ApprovalRequest>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const requestId = request.params.id;
      const { reason } = request.body;

      const updatedRequest = await this.workflowEngine.withdrawRequest(
        requestId,
        request.user,
        reason
      );

      // Close GitHub PR if exists
      if (this.githubIntegration) {
        try {
          await this.githubIntegration.closePRAndCleanup(requestId, reason || 'Request withdrawn');
        } catch (error) {
          console.warn('Failed to close GitHub PR:', error);
        }
      }

      // Clear relevant caches
      this.clearCachePattern('approvals:');

      return {
        success: true,
        data: updatedRequest,
        message: 'Request withdrawn successfully'
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  // Baseline Update Endpoints

  /**
   * POST /api/baseline-updates
   * Create baseline update request
   */
  async createBaselineUpdate(request: APIRequest): Promise<APIResponse<BaselineUpdateRequest>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const updateData = request.body;

      // Validate update data
      const validation = this.validateBaselineUpdateData(updateData);
      if (!validation.valid) {
        return {
          success: false,
          error: 'VALIDATION_ERROR',
          message: validation.message
        };
      }

      // Create baseline update request
      const updateRequest = await this.updateManager.createUpdateRequest(
        updateData,
        request.user
      );

      return {
        success: true,
        data: updateRequest,
        message: 'Baseline update request created successfully'
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  /**
   * POST /api/baseline-updates/:id/execute
   * Execute approved baseline update
   */
  async executeBaselineUpdate(
    updateRequest: BaselineUpdateRequest,
    approvalRequestId?: string
  ): Promise<void> {
    try {
      // Execute the update
      const result = await this.updateManager.executeUpdate(updateRequest);

      // Update GitHub PR with deployment status
      if (this.githubIntegration && approvalRequestId) {
        const deploymentState = this.updateManager.getDeploymentStatus(updateRequest.id);
        if (deploymentState) {
          await this.githubIntegration.createDeploymentStatusCheck(
            // This would need the PR number - simplified for example
            0,
            deploymentState
          );
        }
      }

    } catch (error) {
      console.error('Baseline update execution failed:', error);
      throw error;
    }
  }

  /**
   * GET /api/baseline-updates/:id/status
   * Get deployment status
   */
  async getDeploymentStatus(request: APIRequest): Promise<APIResponse<DeploymentState>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const updateId = request.params.id;
      const deploymentState = this.updateManager.getDeploymentStatus(updateId);

      if (!deploymentState) {
        return {
          success: false,
          error: 'DEPLOYMENT_NOT_FOUND',
          message: 'Deployment not found'
        };
      }

      return {
        success: true,
        data: deploymentState
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  /**
   * POST /api/baseline-updates/:id/rollback
   * Rollback baseline update
   */
  async rollbackBaselineUpdate(request: APIRequest): Promise<APIResponse<any>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const updateId = request.params.id;
      const { reason } = request.body;

      const result = await this.updateManager.rollbackUpdate(
        updateId,
        reason || 'Manual rollback requested',
        request.user
      );

      return {
        success: true,
        data: result,
        message: 'Rollback executed successfully'
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  // Template Endpoints

  /**
   * GET /api/templates
   * Get approval templates
   */
  async getApprovalTemplates(request: APIRequest): Promise<APIResponse<ApprovalTemplate[]>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const { trigger, channel } = request.query;
      const templates = this.notificationSystem.getTemplates(trigger as any, channel as any);

      return {
        success: true,
        data: templates
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  /**
   * POST /api/templates
   * Create approval template
   */
  async createApprovalTemplate(request: APIRequest): Promise<APIResponse<ApprovalTemplate>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const templateData = request.body;

      // Validate template data
      const validation = this.validateTemplateData(templateData);
      if (!validation.valid) {
        return {
          success: false,
          error: 'VALIDATION_ERROR',
          message: validation.message
        };
      }

      const template = await this.notificationSystem.createTemplate({
        ...templateData,
        createdBy: request.user
      });

      return {
        success: true,
        data: template,
        message: 'Template created successfully'
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  // Metrics and Reporting Endpoints

  /**
   * GET /api/metrics
   * Get workflow metrics
   */
  async getWorkflowMetrics(request: APIRequest): Promise<APIResponse<WorkflowMetrics>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const cacheKey = `metrics:${request.user.id}`;

      // Check cache
      if (this.options.enableCaching) {
        const cached = this.getFromCache(cacheKey);
        if (cached) {
          return cached;
        }
      }

      const metrics = this.workflowEngine.getMetrics();

      const response: APIResponse<WorkflowMetrics> = {
        success: true,
        data: metrics
      };

      // Cache response
      if (this.options.enableCaching) {
        this.setCache(cacheKey, response);
      }

      return response;

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  /**
   * GET /api/notifications
   * Get user notifications
   */
  async getUserNotifications(request: APIRequest): Promise<APIResponse<NotificationMessage[]>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const { limit = 50 } = request.query;
      const notifications = this.notificationSystem.getUserNotifications(
        request.user.id,
        parseInt(limit as string)
      );

      return {
        success: true,
        data: notifications
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  /**
   * POST /api/notifications/:id/read
   * Mark notification as read
   */
  async markNotificationRead(request: APIRequest): Promise<APIResponse<void>> {
    try {
      await this.validateRequest(request);
      await this.checkRateLimit(request);

      const messageId = request.params.id;
      await this.notificationSystem.markAsRead(messageId, request.user.id);

      return {
        success: true,
        message: 'Notification marked as read'
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  // Webhook Endpoints

  /**
   * POST /api/webhooks/github
   * Handle GitHub webhook events
   */
  async handleGitHubWebhook(request: APIRequest): Promise<APIResponse<void>> {
    try {
      // Skip authentication for webhooks
      await this.checkRateLimit(request);

      if (!this.githubIntegration) {
        return {
          success: false,
          error: 'GITHUB_INTEGRATION_DISABLED',
          message: 'GitHub integration is not configured'
        };
      }

      await this.githubIntegration.handleWebhook(request.body);

      return {
        success: true,
        message: 'Webhook processed successfully'
      };

    } catch (error) {
      return this.handleError(error as Error);
    }
  }

  // Private helper methods

  private async validateRequest(request: APIRequest): Promise<void> {
    if (!this.options.enableAuthentication) {
      return;
    }

    if (!request.user) {
      throw new Error('Authentication required');
    }

    if (!request.user.isActive) {
      throw new Error('User account is inactive');
    }
  }

  private async checkRateLimit(request: APIRequest): Promise<void> {
    if (!this.options.enableRateLimit) {
      return;
    }

    const key = request.user?.id || request.ip;
    const now = Date.now();
    const windowStart = now - this.options.rateLimitWindow;

    let rateLimitData = this.rateLimitMap.get(key);
    if (!rateLimitData || rateLimitData.resetTime < now) {
      rateLimitData = { count: 0, resetTime: now + this.options.rateLimitWindow };
    }

    rateLimitData.count++;

    if (rateLimitData.count > this.options.rateLimitRequests) {
      throw new Error('Rate limit exceeded');
    }

    this.rateLimitMap.set(key, rateLimitData);
  }

  private parseFilters(query: Record<string, string>): RequestFilters {
    return {
      status: query.status as ApprovalStatus,
      priority: query.priority as ApprovalPriority,
      type: query.type,
      assignedTo: query.assignedTo,
      createdBy: query.createdBy,
      dateFrom: query.dateFrom,
      dateTo: query.dateTo,
      page: parseInt(query.page || '1'),
      limit: Math.min(parseInt(query.limit || '20'), 100),
      sortBy: query.sortBy || 'createdAt',
      sortOrder: (query.sortOrder as 'asc' | 'desc') || 'desc'
    };
  }

  private filterRequestsByAccess(requests: ApprovalRequest[], user: User): ApprovalRequest[] {
    // Implement access control logic based on user permissions
    return requests.filter(request => {
      // User can see their own requests
      if (request.requester.id === user.id) {
        return true;
      }

      // User can see requests they need to approve
      if (request.approvers[request.currentStep]?.approvers.some(a => a.id === user.id)) {
        return true;
      }

      // Admin users can see all requests
      if (user.role === 'admin') {
        return true;
      }

      return false;
    });
  }

  private applyFilters(requests: ApprovalRequest[], filters: RequestFilters): ApprovalRequest[] {
    let filtered = requests;

    if (filters.status) {
      filtered = filtered.filter(r => r.status === filters.status);
    }

    if (filters.priority) {
      filtered = filtered.filter(r => r.priority === filters.priority);
    }

    if (filters.type) {
      filtered = filtered.filter(r => r.type === filters.type);
    }

    if (filters.assignedTo) {
      filtered = filtered.filter(r =>
        r.approvers[r.currentStep]?.approvers.some(a => a.id === filters.assignedTo)
      );
    }

    if (filters.createdBy) {
      filtered = filtered.filter(r => r.requester.id === filters.createdBy);
    }

    if (filters.dateFrom) {
      const fromDate = new Date(filters.dateFrom);
      filtered = filtered.filter(r => r.createdAt >= fromDate);
    }

    if (filters.dateTo) {
      const toDate = new Date(filters.dateTo);
      filtered = filtered.filter(r => r.createdAt <= toDate);
    }

    return filtered;
  }

  private applySorting(
    requests: ApprovalRequest[],
    sortBy?: string,
    sortOrder?: 'asc' | 'desc'
  ): ApprovalRequest[] {
    if (!sortBy) return requests;

    return requests.sort((a, b) => {
      let aValue: any, bValue: any;

      switch (sortBy) {
        case 'createdAt':
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
          break;
        case 'updatedAt':
          aValue = a.updatedAt.getTime();
          bValue = b.updatedAt.getTime();
          break;
        case 'priority':
          const priorityOrder = ['low', 'medium', 'high', 'critical', 'emergency'];
          aValue = priorityOrder.indexOf(a.priority);
          bValue = priorityOrder.indexOf(b.priority);
          break;
        case 'title':
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
          break;
        default:
          return 0;
      }

      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
  }

  private calculatePagination(
    total: number,
    page: number = 1,
    limit: number = 20
  ): PaginationInfo {
    const totalPages = Math.ceil(total / limit);
    return {
      page,
      limit,
      total,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1
    };
  }

  private applyPagination(
    requests: ApprovalRequest[],
    page: number = 1,
    limit: number = 20
  ): ApprovalRequest[] {
    const offset = (page - 1) * limit;
    return requests.slice(offset, offset + limit);
  }

  private hasRequestAccess(request: ApprovalRequest, user: User): boolean {
    // Check if user has access to view this request
    if (request.requester.id === user.id) return true;
    if (request.approvers.some(step => step.approvers.some(a => a.id === user.id))) return true;
    if (user.role === 'admin') return true;
    return false;
  }

  private validateApprovalRequestData(data: any): { valid: boolean; message?: string } {
    if (!data.title || typeof data.title !== 'string' || data.title.trim().length === 0) {
      return { valid: false, message: 'Title is required' };
    }

    if (!data.description || typeof data.description !== 'string') {
      return { valid: false, message: 'Description is required' };
    }

    if (!data.type || typeof data.type !== 'string') {
      return { valid: false, message: 'Type is required' };
    }

    if (!data.approvers || !Array.isArray(data.approvers) || data.approvers.length === 0) {
      return { valid: false, message: 'At least one approval step is required' };
    }

    return { valid: true };
  }

  private validateBaselineUpdateData(data: any): { valid: boolean; message?: string } {
    if (!data.targetEnvironment) {
      return { valid: false, message: 'Target environment is required' };
    }

    if (!data.updateType) {
      return { valid: false, message: 'Update type is required' };
    }

    if (!data.changes || !Array.isArray(data.changes) || data.changes.length === 0) {
      return { valid: false, message: 'At least one change is required' };
    }

    return { valid: true };
  }

  private validateTemplateData(data: any): { valid: boolean; message?: string } {
    if (!data.name || typeof data.name !== 'string') {
      return { valid: false, message: 'Template name is required' };
    }

    if (!data.trigger) {
      return { valid: false, message: 'Trigger is required' };
    }

    if (!data.channel) {
      return { valid: false, message: 'Channel is required' };
    }

    if (!data.subject || !data.body) {
      return { valid: false, message: 'Subject and body are required' };
    }

    return { valid: true };
  }

  private getFromCache(key: string): any {
    if (!this.options.enableCaching) return null;

    const cached = this.cache.get(key);
    if (cached && cached.expires > Date.now()) {
      return cached.data;
    }

    this.cache.delete(key);
    return null;
  }

  private setCache(key: string, data: any): void {
    if (!this.options.enableCaching) return;

    this.cache.set(key, {
      data,
      expires: Date.now() + this.options.cacheTimeout
    });
  }

  private clearCachePattern(pattern: string): void {
    if (!this.options.enableCaching) return;

    for (const key of this.cache.keys()) {
      if (key.startsWith(pattern)) {
        this.cache.delete(key);
      }
    }
  }

  private handleError(error: Error): APIResponse {
    console.error('API Error:', error);

    // Map specific errors to user-friendly messages
    const errorMappings: Record<string, { error: string; message: string }> = {
      'Authentication required': {
        error: 'AUTHENTICATION_REQUIRED',
        message: 'Authentication is required to access this resource'
      },
      'Rate limit exceeded': {
        error: 'RATE_LIMIT_EXCEEDED',
        message: 'Too many requests. Please try again later.'
      },
      'User account is inactive': {
        error: 'ACCOUNT_INACTIVE',
        message: 'Your account is inactive. Please contact support.'
      }
    };

    const mapping = errorMappings[error.message];
    if (mapping) {
      return {
        success: false,
        error: mapping.error,
        message: mapping.message
      };
    }

    return {
      success: false,
      error: 'INTERNAL_ERROR',
      message: 'An internal error occurred. Please try again later.'
    };
  }

  private async getUserById(userId: string): Promise<User | null> {
    // This would typically fetch from a user service
    // Simplified implementation for example
    return null;
  }
}