import {
  ApprovalRequest,
  ApprovalResponse,
  ApprovalStep,
  ApprovalStatus,
  ApprovalDecision,
  StepStatus,
  User,
  EscalationRule,
  EscalationTrigger,
  EscalationAction,
  AuditEvent,
  AuditAction,
  ApprovalCondition,
  WorkflowMetrics
} from '../types/approval.types.js';
import { EventEmitter } from 'events';
import {
  ApprovalNotFoundError,
  WorkflowNotFoundError,
  InvalidWorkflowStateError,
  DuplicateApprovalError,
  ApprovalTimeoutError,
  InsufficientPermissionsError,
  ValidationError
} from '../errors/ApprovalErrors';
import { ValidationUtils, ValidationSchemas, ValidateInput } from '../validation/ValidationUtils';
import { RetryUtils, CircuitBreaker, TimeoutUtils } from '../utils/RetryUtils';

export interface ApprovalWorkflowEngineOptions {
  enableEscalation: boolean;
  enableDelegation: boolean;
  enableAuditLogging: boolean;
  maxParallelSteps: number;
  defaultTimeout: number; // minutes
  autoSave: boolean;
}

export class ApprovalWorkflowEngine extends EventEmitter {
  private requests: Map<string, ApprovalRequest> = new Map();
  private escalationTimers: Map<string, NodeJS.Timeout> = new Map();
  private options: ApprovalWorkflowEngineOptions;

  constructor(options: Partial<ApprovalWorkflowEngineOptions> = {}) {
    super();
    this.options = {
      enableEscalation: true,
      enableDelegation: true,
      enableAuditLogging: true,
      maxParallelSteps: 5,
      defaultTimeout: 1440, // 24 hours
      autoSave: true,
      ...options
    };
  }

  /**
   * Create a new approval request
   */
  @ValidateInput(ValidationSchemas.ApprovalRequest, 'CreateRequest')
  async createRequest(request: Omit<ApprovalRequest, 'id' | 'status' | 'currentStep' | 'createdAt' | 'updatedAt' | 'auditTrail'>): Promise<ApprovalRequest> {
    const approvalRequest: ApprovalRequest = {
      ...request,
      id: this.generateId(),
      status: ApprovalStatus.PENDING,
      currentStep: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
      auditTrail: []
    };

    // Validate the request structure and business rules
    await this.validateRequest(approvalRequest);

    // Additional validation for workflow integrity
    await this.validateWorkflowIntegrity(approvalRequest);

    // Initialize first step
    await this.initializeFirstStep(approvalRequest);

    // Store the request
    this.requests.set(approvalRequest.id, approvalRequest);

    // Log audit event
    await this.logAuditEvent(approvalRequest.id, AuditAction.CREATE, request.requester, {
      title: request.title,
      type: request.type,
      priority: request.priority
    });

    // Emit event
    this.emit('requestCreated', approvalRequest);

    // Auto-save if enabled
    if (this.options.autoSave) {
      await this.saveRequest(approvalRequest);
    }

    return approvalRequest;
  }

  /**
   * Process an approval response
   */
  @ValidateInput(ValidationSchemas.ApprovalResponse, 'ProcessResponse')
  async processResponse(requestId: string, stepId: string, response: Omit<ApprovalResponse, 'id' | 'timestamp'>): Promise<ApprovalRequest> {
    // Validate input parameters
    if (!ValidationUtils.isValidUUID(requestId)) {
      throw new ValidationError('Invalid request ID format', 'requestId', requestId);
    }

    if (!ValidationUtils.isValidUUID(stepId)) {
      throw new ValidationError('Invalid step ID format', 'stepId', stepId);
    }

    const request = this.requests.get(requestId);
    if (!request) {
      throw new ApprovalNotFoundError(requestId);
    }

    const step = request.approvers.find(s => s.id === stepId);
    if (!step) {
      throw new WorkflowNotFoundError(stepId);
    }

    // Check workflow state
    if (request.status === ApprovalStatus.APPROVED || request.status === ApprovalStatus.REJECTED) {
      throw new InvalidWorkflowStateError(
        'Cannot process response for completed workflow',
        requestId,
        request.status,
        [ApprovalStatus.PENDING, ApprovalStatus.IN_PROGRESS]
      );
    }

    // Validate response and check for duplicates
    await this.validateResponse(request, step, response);

    // Check for duplicate responses
    if (step.responses.some(r => r.approver.id === response.approver.id)) {
      throw new DuplicateApprovalError(requestId, response.approver.id);
    }

    // Check for timeout
    if (request.dueDate && new Date() > request.dueDate) {
      throw new ApprovalTimeoutError(requestId, request.dueDate);
    }

    // Create response record
    const approvalResponse: ApprovalResponse = {
      ...response,
      id: this.generateId(),
      timestamp: new Date()
    };

    // Add response to step
    step.responses.push(approvalResponse);

    // Update request timestamp
    request.updatedAt = new Date();

    // Log audit event
    await this.logAuditEvent(requestId, AuditAction.APPROVE, response.approver, {
      stepId,
      decision: response.decision,
      reason: response.reason
    });

    // Check if step is complete
    if (await this.isStepComplete(step)) {
      step.status = StepStatus.COMPLETED;
      await this.clearEscalationTimer(stepId);

      // Check if all steps are complete
      if (await this.areAllStepsComplete(request)) {
        request.status = ApprovalStatus.APPROVED;
        this.emit('requestApproved', request);
      } else {
        // Move to next step
        await this.moveToNextStep(request);
      }
    } else if (response.decision === ApprovalDecision.REJECT) {
      // Handle rejection
      await this.handleRejection(request, step, approvalResponse);
    }

    // Auto-save if enabled
    if (this.options.autoSave) {
      await this.saveRequest(request);
    }

    this.emit('responseProcessed', { request, response: approvalResponse });

    return request;
  }

  /**
   * Delegate approval to another user
   */
  async delegateApproval(requestId: string, stepId: string, fromUser: User, toUser: User, reason?: string): Promise<void> {
    // Validate input parameters
    if (!ValidationUtils.isValidUUID(requestId)) {
      throw new ValidationError('Invalid request ID format', 'requestId', requestId);
    }

    if (!ValidationUtils.isValidUUID(stepId)) {
      throw new ValidationError('Invalid step ID format', 'stepId', stepId);
    }

    if (!this.options.enableDelegation) {
      throw new InvalidWorkflowStateError(
        'Delegation is not enabled for this workflow engine',
        requestId,
        'delegation_disabled',
        ['delegation_enabled']
      );
    }

    const request = this.requests.get(requestId);
    if (!request) {
      throw new ApprovalNotFoundError(requestId);
    }

    const step = request.approvers.find(s => s.id === stepId);
    if (!step) {
      throw new WorkflowNotFoundError(stepId);
    }

    // Validate delegation permissions
    if (!step.approvers.some(a => a.id === fromUser.id)) {
      throw new InsufficientPermissionsError(
        fromUser.id,
        ['step_approver'],
        fromUser.permissions,
        `step:${stepId}`
      );
    }

    // Validate that target user can receive delegation
    await this.validateUserCanReceiveDelegation(toUser, step);

    // Replace approver
    const approverIndex = step.approvers.findIndex(a => a.id === fromUser.id);
    step.approvers[approverIndex] = toUser;

    // Update request timestamp
    request.updatedAt = new Date();

    // Log audit event
    await this.logAuditEvent(requestId, AuditAction.DELEGATE, fromUser, {
      stepId,
      fromUser: fromUser.id,
      toUser: toUser.id,
      reason
    });

    this.emit('approvalDelegated', { request, fromUser, toUser, stepId });

    // Auto-save if enabled
    if (this.options.autoSave) {
      await this.saveRequest(request);
    }
  }

  /**
   * Escalate an approval step
   */
  async escalateStep(requestId: string, stepId: string, trigger: EscalationTrigger, initiatedBy?: User): Promise<void> {
    // Validate input parameters
    if (!ValidationUtils.isValidUUID(requestId)) {
      throw new ValidationError('Invalid request ID format', 'requestId', requestId);
    }

    if (!ValidationUtils.isValidUUID(stepId)) {
      throw new ValidationError('Invalid step ID format', 'stepId', stepId);
    }

    if (!this.options.enableEscalation) {
      throw new InvalidWorkflowStateError(
        'Escalation is not enabled for this workflow engine',
        requestId,
        'escalation_disabled',
        ['escalation_enabled']
      );
    }

    const request = this.requests.get(requestId);
    if (!request) {
      throw new ApprovalNotFoundError(requestId);
    }

    const step = request.approvers.find(s => s.id === stepId);
    if (!step) {
      throw new WorkflowNotFoundError(stepId);
    }

    if (!step.escalation) {
      throw new InvalidWorkflowStateError(
        'Step does not have escalation rules configured',
        requestId,
        'no_escalation_rules',
        ['escalation_configured']
      );
    }

    const escalation = step.escalation;

    // Perform escalation action
    switch (escalation.action) {
      case EscalationAction.NOTIFY:
        await this.sendEscalationNotifications(request, step, escalation);
        break;
      case EscalationAction.REASSIGN:
        await this.reassignApprovers(request, step, escalation);
        break;
      case EscalationAction.AUTO_APPROVE:
        await this.autoApproveStep(request, step);
        break;
      case EscalationAction.AUTO_REJECT:
        await this.autoRejectStep(request, step);
        break;
    }

    // Update status
    request.status = ApprovalStatus.ESCALATED;
    request.updatedAt = new Date();

    // Log audit event
    await this.logAuditEvent(requestId, AuditAction.ESCALATE, initiatedBy, {
      stepId,
      trigger,
      action: escalation.action
    });

    this.emit('stepEscalated', { request, step, trigger });

    // Auto-save if enabled
    if (this.options.autoSave) {
      await this.saveRequest(request);
    }
  }

  /**
   * Withdraw an approval request
   */
  async withdrawRequest(requestId: string, user: User, reason?: string): Promise<ApprovalRequest> {
    // Validate input parameters
    if (!ValidationUtils.isValidUUID(requestId)) {
      throw new ValidationError('Invalid request ID format', 'requestId', requestId);
    }

    const request = this.requests.get(requestId);
    if (!request) {
      throw new ApprovalNotFoundError(requestId);
    }

    // Check if request is in a state that allows withdrawal
    if (request.status === ApprovalStatus.APPROVED || request.status === ApprovalStatus.REJECTED) {
      throw new InvalidWorkflowStateError(
        'Cannot withdraw completed request',
        requestId,
        request.status,
        [ApprovalStatus.PENDING, ApprovalStatus.IN_PROGRESS]
      );
    }

    // Validate withdrawal permission
    const canWithdraw = request.requester.id === user.id ||
                       user.permissions.includes('admin' as any) ||
                       user.permissions.includes('withdraw_any_request' as any);

    if (!canWithdraw) {
      throw new InsufficientPermissionsError(
        user.id,
        ['request_owner', 'admin', 'withdraw_any_request'],
        user.permissions,
        `request:${requestId}`
      );
    }

    // Update status
    request.status = ApprovalStatus.WITHDRAWN;
    request.updatedAt = new Date();

    // Clear all escalation timers
    for (const step of request.approvers) {
      await this.clearEscalationTimer(step.id);
    }

    // Log audit event
    await this.logAuditEvent(requestId, AuditAction.WITHDRAW, user, { reason });

    this.emit('requestWithdrawn', request);

    // Auto-save if enabled
    if (this.options.autoSave) {
      await this.saveRequest(request);
    }

    return request;
  }

  /**
   * Get approval request by ID
   */
  getRequest(requestId: string): ApprovalRequest | undefined {
    return this.requests.get(requestId);
  }

  /**
   * Get all approval requests
   */
  getAllRequests(): ApprovalRequest[] {
    return Array.from(this.requests.values());
  }

  /**
   * Get requests by status
   */
  getRequestsByStatus(status: ApprovalStatus): ApprovalRequest[] {
    return Array.from(this.requests.values()).filter(r => r.status === status);
  }

  /**
   * Get pending requests for a user
   */
  getPendingRequestsForUser(userId: string): ApprovalRequest[] {
    return Array.from(this.requests.values()).filter(request => {
      if (request.status !== ApprovalStatus.PENDING && request.status !== ApprovalStatus.IN_PROGRESS) {
        return false;
      }

      const currentStep = request.approvers[request.currentStep];
      return currentStep && currentStep.approvers.some(a => a.id === userId);
    });
  }

  /**
   * Get workflow metrics
   */
  getMetrics(): WorkflowMetrics {
    const requests = Array.from(this.requests.values());
    const totalRequests = requests.length;
    const pendingRequests = requests.filter(r => r.status === ApprovalStatus.PENDING || r.status === ApprovalStatus.IN_PROGRESS).length;
    const approvedRequests = requests.filter(r => r.status === ApprovalStatus.APPROVED).length;
    const rejectedRequests = requests.filter(r => r.status === ApprovalStatus.REJECTED).length;
    const expiredRequests = requests.filter(r => r.status === ApprovalStatus.EXPIRED).length;

    // Calculate average approval time
    const completedRequests = requests.filter(r => r.status === ApprovalStatus.APPROVED || r.status === ApprovalStatus.REJECTED);
    const averageApprovalTime = completedRequests.length > 0
      ? completedRequests.reduce((sum, r) => sum + (r.updatedAt.getTime() - r.createdAt.getTime()), 0) / completedRequests.length
      : 0;

    const approvalRate = totalRequests > 0 ? approvedRequests / totalRequests : 0;
    const escalationRate = requests.filter(r => r.status === ApprovalStatus.ESCALATED).length / totalRequests;

    return {
      totalRequests,
      pendingRequests,
      approvedRequests,
      rejectedRequests,
      expiredRequests,
      averageApprovalTime,
      approvalRate,
      escalationRate,
      timeByStep: {},
      userMetrics: {}
    };
  }

  // Private methods

  private async validateRequest(request: ApprovalRequest): Promise<void> {
    // Basic validation
    if (!request.title || request.title.trim().length === 0) {
      throw new ValidationError('Request title is required', 'title', request.title);
    }

    if (request.title.length > 200) {
      throw new ValidationError('Request title cannot exceed 200 characters', 'title', request.title);
    }

    if (!request.description || request.description.trim().length === 0) {
      throw new ValidationError('Request description is required', 'description', request.description);
    }

    if (!request.approvers || request.approvers.length === 0) {
      throw new ValidationError('At least one approval step is required', 'approvers', request.approvers);
    }

    if (request.approvers.length > this.options.maxParallelSteps) {
      throw new ValidationError(
        `Number of approval steps cannot exceed ${this.options.maxParallelSteps}`,
        'approvers',
        request.approvers.length
      );
    }

    // Validate each step
    for (let i = 0; i < request.approvers.length; i++) {
      const step = request.approvers[i];
      await this.validateApprovalStep(step, i);
    }

    // Validate due date
    if (request.dueDate && request.dueDate <= new Date()) {
      throw new ValidationError('Due date must be in the future', 'dueDate', request.dueDate);
    }

    // Validate requester
    if (!request.requester || !request.requester.id) {
      throw new ValidationError('Request requester is required', 'requester', request.requester);
    }
  }

  private async validateApprovalStep(step: ApprovalStep, stepIndex: number): Promise<void> {
    if (!step.name || step.name.trim().length === 0) {
      throw new ValidationError(`Step ${stepIndex + 1} name is required`, `approvers[${stepIndex}].name`, step.name);
    }

    if (!step.approvers || step.approvers.length === 0) {
      throw new ValidationError(`Step ${step.name} must have at least one approver`, `approvers[${stepIndex}].approvers`, step.approvers);
    }

    if (step.requiredApprovals <= 0) {
      throw new ValidationError(
        `Step ${step.name} must require at least one approval`,
        `approvers[${stepIndex}].requiredApprovals`,
        step.requiredApprovals
      );
    }

    if (step.requiredApprovals > step.approvers.length) {
      throw new ValidationError(
        `Step ${step.name} requires more approvals (${step.requiredApprovals}) than available approvers (${step.approvers.length})`,
        `approvers[${stepIndex}].requiredApprovals`,
        step.requiredApprovals
      );
    }

    // Validate approvers
    for (let j = 0; j < step.approvers.length; j++) {
      const approver = step.approvers[j];
      if (!approver.id || !approver.email) {
        throw new ValidationError(
          `Invalid approver at step ${step.name}, position ${j + 1}`,
          `approvers[${stepIndex}].approvers[${j}]`,
          approver
        );
      }

      if (!ValidationUtils.isValidEmail(approver.email)) {
        throw new ValidationError(
          `Invalid email for approver ${approver.fullName}`,
          `approvers[${stepIndex}].approvers[${j}].email`,
          approver.email
        );
      }
    }

    // Validate timeout
    if (step.timeout && (step.timeout < 0 || step.timeout > 43200)) { // Max 30 days
      throw new ValidationError(
        `Step timeout must be between 0 and 43200 minutes (30 days)`,
        `approvers[${stepIndex}].timeout`,
        step.timeout
      );
    }

    // Validate escalation rules
    if (step.escalation) {
      await this.validateEscalationRule(step.escalation, stepIndex);
    }
  }

  private async validateEscalationRule(escalation: EscalationRule, stepIndex: number): Promise<void> {
    if (!escalation.trigger) {
      throw new ValidationError(
        `Escalation trigger is required`,
        `approvers[${stepIndex}].escalation.trigger`,
        escalation.trigger
      );
    }

    if (!escalation.action) {
      throw new ValidationError(
        `Escalation action is required`,
        `approvers[${stepIndex}].escalation.action`,
        escalation.action
      );
    }

    if ((escalation.action === EscalationAction.NOTIFY || escalation.action === EscalationAction.REASSIGN) &&
        (!escalation.escalateTo || escalation.escalateTo.length === 0)) {
      throw new ValidationError(
        `Escalation target users are required for ${escalation.action} action`,
        `approvers[${stepIndex}].escalation.escalateTo`,
        escalation.escalateTo
      );
    }
  }

  private async validateWorkflowIntegrity(request: ApprovalRequest): Promise<void> {
    // Check for circular dependencies
    const stepIds = new Set(request.approvers.map(s => s.id));
    if (stepIds.size !== request.approvers.length) {
      throw new ValidationError('Duplicate step IDs found in workflow', 'approvers', request.approvers);
    }

    // Validate step dependencies
    for (const step of request.approvers) {
      if (step.dependencies) {
        for (const depId of step.dependencies) {
          if (!stepIds.has(depId)) {
            throw new ValidationError(
              `Step ${step.name} depends on non-existent step ${depId}`,
              'dependencies',
              depId
            );
          }
        }
      }
    }
  }

  private async validateUserCanReceiveDelegation(user: User, step: ApprovalStep): Promise<void> {
    // Check if user is active
    if (!user.isActive) {
      throw new ValidationError('Cannot delegate to inactive user', 'toUser', user);
    }

    // Check if user has required permissions for the step
    if (step.requiredPermissions) {
      const hasPermissions = step.requiredPermissions.every(perm => user.permissions.includes(perm));
      if (!hasPermissions) {
        throw new InsufficientPermissionsError(
          user.id,
          step.requiredPermissions,
          user.permissions,
          `step:${step.id}`
        );
      }
    }
  }

  private async validateResponse(request: ApprovalRequest, step: ApprovalStep, response: Omit<ApprovalResponse, 'id' | 'timestamp'>): Promise<void> {
    // Validate approver
    if (!response.approver || !response.approver.id) {
      throw new ValidationError('Approver is required', 'approver', response.approver);
    }

    // Check if user is authorized to approve this step
    if (!step.approvers.some(a => a.id === response.approver.id)) {
      throw new InsufficientPermissionsError(
        response.approver.id,
        ['step_approver'],
        response.approver.permissions,
        `step:${step.id}`
      );
    }

    // Check if user is active
    if (!response.approver.isActive) {
      throw new ValidationError('Inactive user cannot provide approval', 'approver', response.approver);
    }

    // Validate decision
    if (!response.decision || !Object.values(ApprovalDecision).includes(response.decision)) {
      throw new ValidationError('Valid approval decision is required', 'decision', response.decision);
    }

    // Validate reason for rejection
    if (response.decision === ApprovalDecision.REJECT && (!response.reason || response.reason.trim().length === 0)) {
      throw new ValidationError('Reason is required for rejection', 'reason', response.reason);
    }

    // Validate reason length
    if (response.reason && response.reason.length > 1000) {
      throw new ValidationError('Reason cannot exceed 1000 characters', 'reason', response.reason);
    }

    // Check step conditions
    if (step.conditions) {
      for (const condition of step.conditions) {
        if (!await this.evaluateCondition(condition, request, response)) {
          throw new ValidationError(
            `Approval condition not met: ${condition.field}`,
            `condition.${condition.field}`,
            condition
          );
        }
      }
    }

    // Check if step is still active
    if (step.status === StepStatus.COMPLETED || step.status === StepStatus.FAILED) {
      throw new InvalidWorkflowStateError(
        `Cannot respond to step in ${step.status} state`,
        request.id,
        step.status,
        [StepStatus.IN_PROGRESS]
      );
    }
  }

  private async initializeFirstStep(request: ApprovalRequest): Promise<void> {
    if (request.approvers.length > 0) {
      const firstStep = request.approvers[0];
      firstStep.status = StepStatus.IN_PROGRESS;
      request.status = ApprovalStatus.IN_PROGRESS;

      // Setup escalation timer if configured
      if (firstStep.escalation && this.options.enableEscalation) {
        await this.setupEscalationTimer(request.id, firstStep);
      }

      this.emit('stepStarted', { request, step: firstStep });
    }
  }

  private async isStepComplete(step: ApprovalStep): Promise<boolean> {
    const approvals = step.responses.filter(r => r.decision === ApprovalDecision.APPROVE).length;
    return approvals >= step.requiredApprovals;
  }

  private async areAllStepsComplete(request: ApprovalRequest): Promise<boolean> {
    return request.approvers.every(step => step.status === StepStatus.COMPLETED);
  }

  private async moveToNextStep(request: ApprovalRequest): Promise<void> {
    request.currentStep++;

    if (request.currentStep < request.approvers.length) {
      const nextStep = request.approvers[request.currentStep];
      nextStep.status = StepStatus.IN_PROGRESS;

      // Setup escalation timer if configured
      if (nextStep.escalation && this.options.enableEscalation) {
        await this.setupEscalationTimer(request.id, nextStep);
      }

      this.emit('stepStarted', { request, step: nextStep });
    }
  }

  private async handleRejection(request: ApprovalRequest, step: ApprovalStep, response: ApprovalResponse): Promise<void> {
    request.status = ApprovalStatus.REJECTED;
    step.status = StepStatus.FAILED;

    // Clear all escalation timers
    for (const s of request.approvers) {
      await this.clearEscalationTimer(s.id);
    }

    this.emit('requestRejected', { request, step, response });
  }

  private async setupEscalationTimer(requestId: string, step: ApprovalStep): Promise<void> {
    if (!step.escalation) return;

    const timeout = step.timeout || this.options.defaultTimeout;
    const timer = setTimeout(async () => {
      await this.escalateStep(requestId, step.id, EscalationTrigger.TIMEOUT);
    }, timeout * 60 * 1000); // Convert minutes to milliseconds

    this.escalationTimers.set(step.id, timer);
  }

  private async clearEscalationTimer(stepId: string): Promise<void> {
    const timer = this.escalationTimers.get(stepId);
    if (timer) {
      clearTimeout(timer);
      this.escalationTimers.delete(stepId);
    }
  }

  private async sendEscalationNotifications(request: ApprovalRequest, step: ApprovalStep, escalation: EscalationRule): Promise<void> {
    // Emit event for notification system to handle
    this.emit('escalationNotificationRequired', {
      request,
      step,
      escalation,
      recipients: escalation.escalateTo
    });
  }

  private async reassignApprovers(request: ApprovalRequest, step: ApprovalStep, escalation: EscalationRule): Promise<void> {
    step.approvers = escalation.escalateTo;
    step.responses = []; // Clear existing responses
    step.status = StepStatus.IN_PROGRESS;
  }

  private async autoApproveStep(request: ApprovalRequest, step: ApprovalStep): Promise<void> {
    // Create automatic approval response
    const autoResponse: ApprovalResponse = {
      id: this.generateId(),
      stepId: step.id,
      approver: { id: 'system', username: 'system', email: 'system@system', fullName: 'System', role: 'admin' as any, permissions: [], isActive: true, timezone: 'UTC', notificationPreferences: [] },
      decision: ApprovalDecision.APPROVE,
      reason: 'Auto-approved due to escalation',
      timestamp: new Date()
    };

    step.responses.push(autoResponse);
    step.status = StepStatus.COMPLETED;

    // Continue workflow
    if (await this.areAllStepsComplete(request)) {
      request.status = ApprovalStatus.APPROVED;
      this.emit('requestApproved', request);
    } else {
      await this.moveToNextStep(request);
    }
  }

  private async autoRejectStep(request: ApprovalRequest, step: ApprovalStep): Promise<void> {
    // Create automatic rejection response
    const autoResponse: ApprovalResponse = {
      id: this.generateId(),
      stepId: step.id,
      approver: { id: 'system', username: 'system', email: 'system@system', fullName: 'System', role: 'admin' as any, permissions: [], isActive: true, timezone: 'UTC', notificationPreferences: [] },
      decision: ApprovalDecision.REJECT,
      reason: 'Auto-rejected due to escalation',
      timestamp: new Date()
    };

    step.responses.push(autoResponse);
    await this.handleRejection(request, step, autoResponse);
  }

  private async evaluateCondition(condition: ApprovalCondition, request: ApprovalRequest, response: Omit<ApprovalResponse, 'id' | 'timestamp'>): Promise<boolean> {
    // Implement condition evaluation logic
    // This is a simplified implementation - expand based on your needs
    return true;
  }

  private async logAuditEvent(requestId: string, action: AuditAction, user: User, details: Record<string, any>): Promise<void> {
    if (!this.options.enableAuditLogging) return;

    const request = this.requests.get(requestId);
    if (!request) return;

    const auditEvent: AuditEvent = {
      id: this.generateId(),
      timestamp: new Date(),
      action,
      user,
      details
    };

    request.auditTrail.push(auditEvent);
    this.emit('auditEventLogged', auditEvent);
  }

  private async saveRequest(request: ApprovalRequest): Promise<void> {
    try {
      // Use retry logic for persistence operations
      await RetryUtils.withRetry(async () => {
        // Implement persistence logic (database, file system, etc.)
        // This will be implemented in the persistence layer
        await this.persistRequest(request);
      }, {
        maxAttempts: 3,
        baseDelay: 1000,
        exponentialBase: 2
      });

      this.emit('requestSaved', request);
    } catch (error) {
      this.emit('requestSaveError', { request, error });
      throw error;
    }
  }

  private async persistRequest(request: ApprovalRequest): Promise<void> {
    // Placeholder for actual persistence implementation
    // This would typically interact with a database or file system
    console.log(`Persisting request ${request.id}`);
  }

  private generateId(): string {
    // Generate a more robust UUID-like ID
    const timestamp = Date.now().toString(36);
    const randomPart = Math.random().toString(36).substr(2, 9);
    const additionalRandom = Math.random().toString(36).substr(2, 5);
    return `${timestamp}-${randomPart}-${additionalRandom}`;
  }

  /**
   * Validate and sanitize input data
   */
  private sanitizeInput(data: any): any {
    return ValidationUtils.sanitizeObject(data);
  }

  /**
   * Execute with timeout protection
   */
  private async executeWithTimeout<T>(
    operation: () => Promise<T>,
    timeoutMs: number = 30000,
    operationName: string = 'operation'
  ): Promise<T> {
    return TimeoutUtils.withTimeout(
      operation,
      timeoutMs,
      `${operationName} timed out after ${timeoutMs}ms`
    );
  }
}