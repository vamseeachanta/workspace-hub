/**
 * Comprehensive error handling for the approval system
 * Provides specialized error classes for different types of approval-related errors
 */

export abstract class BaseApprovalError extends Error {
  public readonly code: string;
  public readonly statusCode: number;
  public readonly timestamp: Date;
  public readonly details?: Record<string, any>;

  constructor(
    message: string,
    code: string,
    statusCode: number = 500,
    details?: Record<string, any>
  ) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.statusCode = statusCode;
    this.timestamp = new Date();
    this.details = details;

    // Capture stack trace
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      statusCode: this.statusCode,
      timestamp: this.timestamp,
      details: this.details,
      stack: this.stack
    };
  }
}

// Validation Errors
export class ValidationError extends BaseApprovalError {
  constructor(
    message: string,
    field?: string,
    value?: any,
    details?: Record<string, any>
  ) {
    super(
      message,
      'VALIDATION_ERROR',
      400,
      {
        field,
        value,
        ...details
      }
    );
  }
}

export class SchemaValidationError extends ValidationError {
  constructor(
    message: string,
    schema: string,
    errors: Array<{ field: string; message: string }>
  ) {
    super(
      message,
      undefined,
      undefined,
      {
        schema,
        validationErrors: errors
      }
    );
    this.code = 'SCHEMA_VALIDATION_ERROR';
  }
}

// Workflow Errors
export class WorkflowError extends BaseApprovalError {
  constructor(
    message: string,
    workflowId?: string,
    stepId?: string,
    details?: Record<string, any>
  ) {
    super(
      message,
      'WORKFLOW_ERROR',
      422,
      {
        workflowId,
        stepId,
        ...details
      }
    );
  }
}

export class WorkflowNotFoundError extends WorkflowError {
  constructor(workflowId: string) {
    super(
      `Workflow not found: ${workflowId}`,
      workflowId
    );
    this.code = 'WORKFLOW_NOT_FOUND';
    this.statusCode = 404;
  }
}

export class InvalidWorkflowStateError extends WorkflowError {
  constructor(
    message: string,
    workflowId: string,
    currentState: string,
    expectedStates: string[]
  ) {
    super(
      message,
      workflowId,
      undefined,
      {
        currentState,
        expectedStates
      }
    );
    this.code = 'INVALID_WORKFLOW_STATE';
  }
}

// Approval Errors
export class ApprovalError extends BaseApprovalError {
  constructor(
    message: string,
    approvalId?: string,
    userId?: string,
    details?: Record<string, any>
  ) {
    super(
      message,
      'APPROVAL_ERROR',
      422,
      {
        approvalId,
        userId,
        ...details
      }
    );
  }
}

export class ApprovalNotFoundError extends ApprovalError {
  constructor(approvalId: string) {
    super(
      `Approval request not found: ${approvalId}`,
      approvalId
    );
    this.code = 'APPROVAL_NOT_FOUND';
    this.statusCode = 404;
  }
}

export class DuplicateApprovalError extends ApprovalError {
  constructor(approvalId: string, userId: string) {
    super(
      `User ${userId} has already responded to approval ${approvalId}`,
      approvalId,
      userId
    );
    this.code = 'DUPLICATE_APPROVAL';
    this.statusCode = 409;
  }
}

export class ApprovalTimeoutError extends ApprovalError {
  constructor(approvalId: string, timeoutDate: Date) {
    super(
      `Approval request ${approvalId} has timed out`,
      approvalId,
      undefined,
      {
        timeoutDate,
        currentTime: new Date()
      }
    );
    this.code = 'APPROVAL_TIMEOUT';
  }
}

// Permission Errors
export class PermissionError extends BaseApprovalError {
  constructor(
    message: string,
    userId: string,
    requiredPermission: string,
    resource?: string,
    details?: Record<string, any>
  ) {
    super(
      message,
      'PERMISSION_DENIED',
      403,
      {
        userId,
        requiredPermission,
        resource,
        ...details
      }
    );
  }
}

export class InsufficientPermissionsError extends PermissionError {
  constructor(
    userId: string,
    requiredPermissions: string[],
    userPermissions: string[],
    resource?: string
  ) {
    const missingPermissions = requiredPermissions.filter(
      perm => !userPermissions.includes(perm)
    );
    
    super(
      `User ${userId} lacks required permissions: ${missingPermissions.join(', ')}`,
      userId,
      requiredPermissions.join(', '),
      resource,
      {
        missingPermissions,
        userPermissions
      }
    );
    this.code = 'INSUFFICIENT_PERMISSIONS';
  }
}

// Authentication Errors
export class AuthenticationError extends BaseApprovalError {
  constructor(
    message: string,
    userId?: string,
    details?: Record<string, any>
  ) {
    super(
      message,
      'AUTHENTICATION_ERROR',
      401,
      {
        userId,
        ...details
      }
    );
  }
}

export class InvalidTokenError extends AuthenticationError {
  constructor(tokenType: string = 'access') {
    super(
      `Invalid ${tokenType} token`,
      undefined,
      {
        tokenType
      }
    );
    this.code = 'INVALID_TOKEN';
  }
}

export class TokenExpiredError extends AuthenticationError {
  constructor(tokenType: string = 'access', expiredAt?: Date) {
    super(
      `${tokenType} token has expired`,
      undefined,
      {
        tokenType,
        expiredAt
      }
    );
    this.code = 'TOKEN_EXPIRED';
  }
}

// Integration Errors
export class IntegrationError extends BaseApprovalError {
  constructor(
    message: string,
    service: string,
    operation?: string,
    details?: Record<string, any>
  ) {
    super(
      message,
      'INTEGRATION_ERROR',
      502,
      {
        service,
        operation,
        ...details
      }
    );
  }
}

export class GitHubIntegrationError extends IntegrationError {
  constructor(
    message: string,
    operation: string,
    githubError?: any,
    details?: Record<string, any>
  ) {
    super(
      message,
      'github',
      operation,
      {
        githubError,
        ...details
      }
    );
    this.code = 'GITHUB_INTEGRATION_ERROR';
  }
}

export class NotificationError extends IntegrationError {
  constructor(
    message: string,
    channel: string,
    recipient?: string,
    details?: Record<string, any>
  ) {
    super(
      message,
      'notification',
      channel,
      {
        recipient,
        ...details
      }
    );
    this.code = 'NOTIFICATION_ERROR';
  }
}

// Configuration Errors
export class ConfigurationError extends BaseApprovalError {
  constructor(
    message: string,
    configKey?: string,
    details?: Record<string, any>
  ) {
    super(
      message,
      'CONFIGURATION_ERROR',
      500,
      {
        configKey,
        ...details
      }
    );
  }
}

export class MissingConfigurationError extends ConfigurationError {
  constructor(configKeys: string | string[]) {
    const keys = Array.isArray(configKeys) ? configKeys : [configKeys];
    super(
      `Missing required configuration: ${keys.join(', ')}`,
      keys[0],
      {
        missingKeys: keys
      }
    );
    this.code = 'MISSING_CONFIGURATION';
  }
}

// Template Errors
export class TemplateError extends BaseApprovalError {
  constructor(
    message: string,
    templateId?: string,
    templateType?: string,
    details?: Record<string, any>
  ) {
    super(
      message,
      'TEMPLATE_ERROR',
      422,
      {
        templateId,
        templateType,
        ...details
      }
    );
  }
}

export class TemplateNotFoundError extends TemplateError {
  constructor(templateId: string, templateType?: string) {
    super(
      `Template not found: ${templateId}`,
      templateId,
      templateType
    );
    this.code = 'TEMPLATE_NOT_FOUND';
    this.statusCode = 404;
  }
}

export class TemplateValidationError extends TemplateError {
  constructor(
    templateId: string,
    validationErrors: Array<{ field: string; message: string }>
  ) {
    super(
      `Template validation failed: ${templateId}`,
      templateId,
      undefined,
      {
        validationErrors
      }
    );
    this.code = 'TEMPLATE_VALIDATION_ERROR';
  }
}

// Utility function to check if error is an approval system error
export function isApprovalError(error: any): error is BaseApprovalError {
  return error instanceof BaseApprovalError;
}

// Error factory for creating errors from objects
export class ErrorFactory {
  static fromObject(errorData: any): BaseApprovalError {
    const { name, message, code, statusCode, details } = errorData;
    
    // Map error types to classes
    const errorMap: Record<string, typeof BaseApprovalError> = {
      ValidationError,
      SchemaValidationError,
      WorkflowError,
      WorkflowNotFoundError,
      InvalidWorkflowStateError,
      ApprovalError,
      ApprovalNotFoundError,
      DuplicateApprovalError,
      ApprovalTimeoutError,
      PermissionError,
      InsufficientPermissionsError,
      AuthenticationError,
      InvalidTokenError,
      TokenExpiredError,
      IntegrationError,
      GitHubIntegrationError,
      NotificationError,
      ConfigurationError,
      MissingConfigurationError,
      TemplateError,
      TemplateNotFoundError,
      TemplateValidationError
    };
    
    const ErrorClass = errorMap[name] || BaseApprovalError;
    const error = Object.create(ErrorClass.prototype);
    error.message = message;
    error.code = code;
    error.statusCode = statusCode;
    error.details = details;
    error.timestamp = new Date(errorData.timestamp);
    
    return error;
  }
}