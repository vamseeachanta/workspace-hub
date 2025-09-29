/**
 * Comprehensive validation utilities for the approval system
 * Provides validation functions, schemas, and sanitization utilities
 */

import { ValidationError, SchemaValidationError } from '../errors/ApprovalErrors';
import {
  ApprovalRequest,
  BaselineUpdateRequest,
  User,
  ApprovalResponse,
  WorkflowTemplate,
  NotificationTemplate,
  ApprovalStatus,
  Priority,
  UserRole,
  Permission
} from '../types/approval.types';

// Validation result interface
export interface ValidationResult {
  isValid: boolean;
  errors: Array<{
    field: string;
    message: string;
    value?: any;
  }>;
}

// Field validation rules
export interface FieldValidationRule {
  required?: boolean;
  type?: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'date' | 'email' | 'url';
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  pattern?: RegExp;
  enum?: any[];
  custom?: (value: any) => string | null;
}

// Schema definition
export type ValidationSchema = Record<string, FieldValidationRule>;

export class ValidationUtils {
  // Email validation regex
  private static readonly EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  // URL validation regex
  private static readonly URL_REGEX = /^https?:\/\/.+/;
  
  // UUID validation regex
  private static readonly UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

  /**
   * Validate a single field against validation rules
   */
  static validateField(
    value: any,
    fieldName: string,
    rules: FieldValidationRule
  ): string | null {
    // Check if required field is missing
    if (rules.required && (value === undefined || value === null || value === '')) {
      return `${fieldName} is required`;
    }

    // If value is empty and not required, skip validation
    if (value === undefined || value === null || value === '') {
      return null;
    }

    // Type validation
    if (rules.type) {
      const typeError = this.validateType(value, rules.type, fieldName);
      if (typeError) return typeError;
    }

    // String-specific validations
    if (typeof value === 'string') {
      if (rules.minLength && value.length < rules.minLength) {
        return `${fieldName} must be at least ${rules.minLength} characters long`;
      }
      if (rules.maxLength && value.length > rules.maxLength) {
        return `${fieldName} must be no more than ${rules.maxLength} characters long`;
      }
      if (rules.pattern && !rules.pattern.test(value)) {
        return `${fieldName} format is invalid`;
      }
    }

    // Number-specific validations
    if (typeof value === 'number') {
      if (rules.min !== undefined && value < rules.min) {
        return `${fieldName} must be at least ${rules.min}`;
      }
      if (rules.max !== undefined && value > rules.max) {
        return `${fieldName} must be no more than ${rules.max}`;
      }
    }

    // Array-specific validations
    if (Array.isArray(value)) {
      if (rules.minLength && value.length < rules.minLength) {
        return `${fieldName} must have at least ${rules.minLength} items`;
      }
      if (rules.maxLength && value.length > rules.maxLength) {
        return `${fieldName} must have no more than ${rules.maxLength} items`;
      }
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      return `${fieldName} must be one of: ${rules.enum.join(', ')}`;
    }

    // Custom validation
    if (rules.custom) {
      const customError = rules.custom(value);
      if (customError) return customError;
    }

    return null;
  }

  /**
   * Validate type of a value
   */
  private static validateType(
    value: any,
    expectedType: string,
    fieldName: string
  ): string | null {
    switch (expectedType) {
      case 'string':
        if (typeof value !== 'string') {
          return `${fieldName} must be a string`;
        }
        break;
      case 'number':
        if (typeof value !== 'number' || isNaN(value)) {
          return `${fieldName} must be a valid number`;
        }
        break;
      case 'boolean':
        if (typeof value !== 'boolean') {
          return `${fieldName} must be a boolean`;
        }
        break;
      case 'array':
        if (!Array.isArray(value)) {
          return `${fieldName} must be an array`;
        }
        break;
      case 'object':
        if (typeof value !== 'object' || Array.isArray(value) || value === null) {
          return `${fieldName} must be an object`;
        }
        break;
      case 'date':
        if (!(value instanceof Date) && !this.isValidDateString(value)) {
          return `${fieldName} must be a valid date`;
        }
        break;
      case 'email':
        if (typeof value !== 'string' || !this.EMAIL_REGEX.test(value)) {
          return `${fieldName} must be a valid email address`;
        }
        break;
      case 'url':
        if (typeof value !== 'string' || !this.URL_REGEX.test(value)) {
          return `${fieldName} must be a valid URL`;
        }
        break;
    }
    return null;
  }

  /**
   * Validate an object against a schema
   */
  static validateSchema(
    data: any,
    schema: ValidationSchema,
    schemaName: string = 'object'
  ): ValidationResult {
    const errors: Array<{ field: string; message: string; value?: any }> = [];

    // Validate each field in the schema
    for (const [fieldPath, rules] of Object.entries(schema)) {
      const value = this.getNestedValue(data, fieldPath);
      const error = this.validateField(value, fieldPath, rules);
      
      if (error) {
        errors.push({
          field: fieldPath,
          message: error,
          value
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Get nested value from object using dot notation
   */
  private static getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
  }

  /**
   * Check if string is a valid date
   */
  private static isValidDateString(value: any): boolean {
    if (typeof value !== 'string') return false;
    const date = new Date(value);
    return !isNaN(date.getTime());
  }

  /**
   * Sanitize string input
   */
  static sanitizeString(input: string): string {
    if (typeof input !== 'string') return '';
    
    return input
      .trim()
      .replace(/[<>"'&]/g, (char) => {
        const entities: Record<string, string> = {
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#x27;',
          '&': '&amp;'
        };
        return entities[char] || char;
      });
  }

  /**
   * Sanitize object recursively
   */
  static sanitizeObject(obj: any): any {
    if (typeof obj === 'string') {
      return this.sanitizeString(obj);
    }
    
    if (Array.isArray(obj)) {
      return obj.map(item => this.sanitizeObject(item));
    }
    
    if (obj && typeof obj === 'object') {
      const sanitized: any = {};
      for (const [key, value] of Object.entries(obj)) {
        sanitized[key] = this.sanitizeObject(value);
      }
      return sanitized;
    }
    
    return obj;
  }

  /**
   * Validate UUID format
   */
  static isValidUUID(uuid: string): boolean {
    return typeof uuid === 'string' && this.UUID_REGEX.test(uuid);
  }

  /**
   * Validate email format
   */
  static isValidEmail(email: string): boolean {
    return typeof email === 'string' && this.EMAIL_REGEX.test(email);
  }

  /**
   * Validate URL format
   */
  static isValidURL(url: string): boolean {
    return typeof url === 'string' && this.URL_REGEX.test(url);
  }

  /**
   * Validate and throw error if validation fails
   */
  static validateAndThrow(
    data: any,
    schema: ValidationSchema,
    schemaName: string = 'object'
  ): void {
    const result = this.validateSchema(data, schema, schemaName);
    
    if (!result.isValid) {
      throw new SchemaValidationError(
        `Validation failed for ${schemaName}`,
        schemaName,
        result.errors
      );
    }
  }
}

// Predefined validation schemas
export const ValidationSchemas = {
  User: {
    'id': { required: true, type: 'string' as const },
    'name': { required: true, type: 'string' as const, minLength: 1, maxLength: 100 },
    'email': { required: true, type: 'email' as const },
    'role': { required: true, enum: Object.values(UserRole) },
    'permissions': { required: true, type: 'array' as const },
    'metadata': { type: 'object' as const }
  },

  ApprovalRequest: {
    'id': { required: true, type: 'string' as const },
    'title': { required: true, type: 'string' as const, minLength: 1, maxLength: 200 },
    'description': { required: true, type: 'string' as const, minLength: 1 },
    'requesterId': { required: true, type: 'string' as const },
    'workflowId': { required: true, type: 'string' as const },
    'priority': { required: true, enum: Object.values(Priority) },
    'dueDate': { type: 'date' as const },
    'metadata': { type: 'object' as const }
  },

  BaselineUpdateRequest: {
    'id': { required: true, type: 'string' as const },
    'baselineId': { required: true, type: 'string' as const },
    'changes': { required: true, type: 'array' as const, minLength: 1 },
    'description': { required: true, type: 'string' as const, minLength: 1 },
    'requesterId': { required: true, type: 'string' as const },
    'deploymentStrategy': { required: true, type: 'string' as const },
    'rollbackPlan': { required: true, type: 'object' as const },
    'metadata': { type: 'object' as const }
  },

  ApprovalResponse: {
    'id': { required: true, type: 'string' as const },
    'approvalId': { required: true, type: 'string' as const },
    'userId': { required: true, type: 'string' as const },
    'status': { required: true, enum: Object.values(ApprovalStatus) },
    'comments': { type: 'string' as const, maxLength: 1000 },
    'metadata': { type: 'object' as const }
  },

  WorkflowTemplate: {
    'id': { required: true, type: 'string' as const },
    'name': { required: true, type: 'string' as const, minLength: 1, maxLength: 100 },
    'description': { required: true, type: 'string' as const, minLength: 1 },
    'version': { required: true, type: 'string' as const },
    'steps': { required: true, type: 'array' as const, minLength: 1 },
    'metadata': { type: 'object' as const }
  },

  NotificationTemplate: {
    'id': { required: true, type: 'string' as const },
    'name': { required: true, type: 'string' as const, minLength: 1, maxLength: 100 },
    'type': { required: true, type: 'string' as const },
    'subject': { required: true, type: 'string' as const, minLength: 1 },
    'body': { required: true, type: 'string' as const, minLength: 1 },
    'metadata': { type: 'object' as const }
  }
};

// Validation decorators for class methods
export function ValidateInput(schema: ValidationSchema, schemaName?: string) {
  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function(...args: any[]) {
      if (args.length > 0) {
        ValidationUtils.validateAndThrow(
          args[0],
          schema,
          schemaName || `${target.constructor.name}.${propertyKey} input`
        );
      }
      return originalMethod.apply(this, args);
    };
    
    return descriptor;
  };
}

// Validation middleware for Express.js
export function validationMiddleware(
  schema: ValidationSchema,
  source: 'body' | 'query' | 'params' = 'body'
) {
  return (req: any, res: any, next: any) => {
    try {
      const data = req[source];
      ValidationUtils.validateAndThrow(data, schema, `${source} validation`);
      next();
    } catch (error) {
      if (error instanceof SchemaValidationError) {
        res.status(error.statusCode).json({
          error: error.toJSON()
        });
      } else {
        next(error);
      }
    }
  };
}