/**
 * Express.js error handling middleware for the approval system
 * Provides centralized error handling, logging, and response formatting
 */

import { Request, Response, NextFunction } from 'express';
import { BaseApprovalError, isApprovalError } from '../errors/ApprovalErrors';
import { AuditLogger } from '../security/AuditLogger';

export interface ErrorResponse {
  error: {
    name: string;
    message: string;
    code: string;
    statusCode: number;
    timestamp: string;
    requestId?: string;
    details?: Record<string, any>;
    stack?: string;
  };
}

export class ErrorHandlingMiddleware {
  private auditLogger: AuditLogger;
  private includeStackTrace: boolean;

  constructor(
    auditLogger: AuditLogger,
    includeStackTrace: boolean = process.env.NODE_ENV === 'development'
  ) {
    this.auditLogger = auditLogger;
    this.includeStackTrace = includeStackTrace;
  }

  /**
   * Main error handling middleware
   */
  handleError = async (
    error: Error,
    req: Request,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    // Generate request ID if not present
    const requestId = req.headers['x-request-id'] as string || this.generateRequestId();

    // Log the error
    await this.logError(error, req, requestId);

    // Handle approval system errors
    if (isApprovalError(error)) {
      this.handleApprovalError(error, req, res, requestId);
      return;
    }

    // Handle known error types
    if (error.name === 'ValidationError') {
      this.handleValidationError(error, req, res, requestId);
      return;
    }

    if (error.name === 'CastError') {
      this.handleCastError(error, req, res, requestId);
      return;
    }

    if (error.name === 'MongoError' || error.name === 'MongoServerError') {
      this.handleDatabaseError(error, req, res, requestId);
      return;
    }

    if (error.name === 'JsonWebTokenError') {
      this.handleJWTError(error, req, res, requestId);
      return;
    }

    if (error.name === 'MulterError') {
      this.handleMulterError(error, req, res, requestId);
      return;
    }

    // Handle unknown errors
    this.handleUnknownError(error, req, res, requestId);
  };

  /**
   * Handle approval system errors
   */
  private handleApprovalError(
    error: BaseApprovalError,
    req: Request,
    res: Response,
    requestId: string
  ): void {
    const errorResponse: ErrorResponse = {
      error: {
        name: error.name,
        message: error.message,
        code: error.code,
        statusCode: error.statusCode,
        timestamp: error.timestamp.toISOString(),
        requestId,
        details: error.details
      }
    };

    if (this.includeStackTrace) {
      errorResponse.error.stack = error.stack;
    }

    res.status(error.statusCode).json(errorResponse);
  }

  /**
   * Handle validation errors
   */
  private handleValidationError(
    error: Error,
    req: Request,
    res: Response,
    requestId: string
  ): void {
    const errorResponse: ErrorResponse = {
      error: {
        name: 'ValidationError',
        message: 'Validation failed',
        code: 'VALIDATION_ERROR',
        statusCode: 400,
        timestamp: new Date().toISOString(),
        requestId,
        details: {
          originalMessage: error.message
        }
      }
    };

    if (this.includeStackTrace) {
      errorResponse.error.stack = error.stack;
    }

    res.status(400).json(errorResponse);
  }

  /**
   * Handle database cast errors
   */
  private handleCastError(
    error: Error,
    req: Request,
    res: Response,
    requestId: string
  ): void {
    const errorResponse: ErrorResponse = {
      error: {
        name: 'CastError',
        message: 'Invalid data format',
        code: 'INVALID_DATA_FORMAT',
        statusCode: 400,
        timestamp: new Date().toISOString(),
        requestId,
        details: {
          originalMessage: error.message
        }
      }
    };

    if (this.includeStackTrace) {
      errorResponse.error.stack = error.stack;
    }

    res.status(400).json(errorResponse);
  }

  /**
   * Handle database errors
   */
  private handleDatabaseError(
    error: Error,
    req: Request,
    res: Response,
    requestId: string
  ): void {
    const errorResponse: ErrorResponse = {
      error: {
        name: 'DatabaseError',
        message: 'Database operation failed',
        code: 'DATABASE_ERROR',
        statusCode: 500,
        timestamp: new Date().toISOString(),
        requestId
      }
    };

    if (this.includeStackTrace) {
      errorResponse.error.stack = error.stack;
      errorResponse.error.details = {
        originalMessage: error.message
      };
    }

    res.status(500).json(errorResponse);
  }

  /**
   * Handle JWT errors
   */
  private handleJWTError(
    error: Error,
    req: Request,
    res: Response,
    requestId: string
  ): void {
    const errorResponse: ErrorResponse = {
      error: {
        name: 'AuthenticationError',
        message: 'Invalid authentication token',
        code: 'INVALID_TOKEN',
        statusCode: 401,
        timestamp: new Date().toISOString(),
        requestId
      }
    };

    if (this.includeStackTrace) {
      errorResponse.error.stack = error.stack;
    }

    res.status(401).json(errorResponse);
  }

  /**
   * Handle file upload errors
   */
  private handleMulterError(
    error: Error,
    req: Request,
    res: Response,
    requestId: string
  ): void {
    let statusCode = 400;
    let message = 'File upload failed';
    let code = 'FILE_UPLOAD_ERROR';

    // Handle specific multer error types
    if (error.message.includes('File too large')) {
      statusCode = 413;
      message = 'File size too large';
      code = 'FILE_TOO_LARGE';
    } else if (error.message.includes('Unexpected field')) {
      message = 'Unexpected file field';
      code = 'UNEXPECTED_FILE_FIELD';
    } else if (error.message.includes('Too many files')) {
      message = 'Too many files uploaded';
      code = 'TOO_MANY_FILES';
    }

    const errorResponse: ErrorResponse = {
      error: {
        name: 'FileUploadError',
        message,
        code,
        statusCode,
        timestamp: new Date().toISOString(),
        requestId
      }
    };

    if (this.includeStackTrace) {
      errorResponse.error.stack = error.stack;
    }

    res.status(statusCode).json(errorResponse);
  }

  /**
   * Handle unknown errors
   */
  private handleUnknownError(
    error: Error,
    req: Request,
    res: Response,
    requestId: string
  ): void {
    const errorResponse: ErrorResponse = {
      error: {
        name: 'InternalServerError',
        message: 'An unexpected error occurred',
        code: 'INTERNAL_SERVER_ERROR',
        statusCode: 500,
        timestamp: new Date().toISOString(),
        requestId
      }
    };

    if (this.includeStackTrace) {
      errorResponse.error.stack = error.stack;
      errorResponse.error.details = {
        originalName: error.name,
        originalMessage: error.message
      };
    }

    res.status(500).json(errorResponse);
  }

  /**
   * Log error details
   */
  private async logError(
    error: Error,
    req: Request,
    requestId: string
  ): Promise<void> {
    try {
      const errorDetails = {
        name: error.name,
        message: error.message,
        stack: error.stack,
        requestId,
        method: req.method,
        url: req.url,
        headers: req.headers,
        body: req.body,
        query: req.query,
        params: req.params,
        userAgent: req.get('User-Agent'),
        ip: req.ip || req.connection.remoteAddress,
        timestamp: new Date().toISOString()
      };

      await this.auditLogger.logEvent({
        eventType: 'error',
        userId: (req as any).user?.id || 'anonymous',
        action: 'error_occurred',
        resource: req.url,
        details: errorDetails,
        severity: this.getErrorSeverity(error),
        timestamp: new Date()
      });
    } catch (logError) {
      // Fallback logging to console if audit logger fails
      console.error('Failed to log error to audit system:', logError);
      console.error('Original error:', error);
    }
  }

  /**
   * Determine error severity
   */
  private getErrorSeverity(error: Error): 'low' | 'medium' | 'high' | 'critical' {
    if (isApprovalError(error)) {
      if (error.statusCode >= 500) return 'high';
      if (error.statusCode >= 400) return 'medium';
      return 'low';
    }

    if (error.name === 'ValidationError') return 'low';
    if (error.name === 'CastError') return 'low';
    if (error.name === 'JsonWebTokenError') return 'medium';
    if (error.name.includes('Database') || error.name.includes('Mongo')) return 'high';

    return 'high'; // Unknown errors are considered high severity
  }

  /**
   * Generate unique request ID
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Handle 404 errors
   */
  handle404 = (req: Request, res: Response): void => {
    const requestId = req.headers['x-request-id'] as string || this.generateRequestId();

    const errorResponse: ErrorResponse = {
      error: {
        name: 'NotFoundError',
        message: `Route ${req.method} ${req.url} not found`,
        code: 'ROUTE_NOT_FOUND',
        statusCode: 404,
        timestamp: new Date().toISOString(),
        requestId
      }
    };

    res.status(404).json(errorResponse);
  };

  /**
   * Handle async errors in route handlers
   */
  static asyncHandler = (
    fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
  ) => {
    return (req: Request, res: Response, next: NextFunction) => {
      Promise.resolve(fn(req, res, next)).catch(next);
    };
  };

  /**
   * Request ID middleware
   */
  static requestIdMiddleware = (
    req: Request,
    res: Response,
    next: NextFunction
  ): void => {
    const requestId = req.headers['x-request-id'] as string || 
      `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    req.headers['x-request-id'] = requestId;
    res.setHeader('X-Request-ID', requestId);
    next();
  };

  /**
   * Rate limiting error handler
   */
  static rateLimitHandler = (
    req: Request,
    res: Response
  ): void => {
    const requestId = req.headers['x-request-id'] as string;

    const errorResponse: ErrorResponse = {
      error: {
        name: 'RateLimitError',
        message: 'Too many requests, please try again later',
        code: 'RATE_LIMIT_EXCEEDED',
        statusCode: 429,
        timestamp: new Date().toISOString(),
        requestId
      }
    };

    res.status(429).json(errorResponse);
  };
}