/**
 * Validation utilities for baseline tracking engine
 */

import { ValidationError } from '../types';
import type { MetricsSnapshot, BaselineData, ThresholdRule, EngineConfig } from '../types';

export class ValidationUtils {
  /**
   * Validates a metrics snapshot
   */
  static validateMetricsSnapshot(snapshot: unknown): asserts snapshot is MetricsSnapshot {
    if (!snapshot || typeof snapshot !== 'object') {
      throw new ValidationError('Metrics snapshot must be an object');
    }

    const s = snapshot as Record<string, unknown>;

    if (!s.id || typeof s.id !== 'string') {
      throw new ValidationError('Metrics snapshot must have a valid id');
    }

    if (!s.branch || typeof s.branch !== 'string') {
      throw new ValidationError('Metrics snapshot must have a valid branch');
    }

    if (!s.commit || typeof s.commit !== 'string') {
      throw new ValidationError('Metrics snapshot must have a valid commit');
    }

    if (!s.environment || typeof s.environment !== 'string') {
      throw new ValidationError('Metrics snapshot must have a valid environment');
    }

    if (!s.version || typeof s.version !== 'string') {
      throw new ValidationError('Metrics snapshot must have a valid version');
    }

    if (!s.created || !(s.created instanceof Date)) {
      throw new ValidationError('Metrics snapshot must have a valid created timestamp');
    }

    if (!s.tests || typeof s.tests !== 'object') {
      throw new ValidationError('Metrics snapshot must have test data');
    }

    if (!s.coverage || typeof s.coverage !== 'object') {
      throw new ValidationError('Metrics snapshot must have coverage data');
    }

    if (!Array.isArray(s.performance)) {
      throw new ValidationError('Metrics snapshot must have performance data array');
    }
  }

  /**
   * Validates baseline data
   */
  static validateBaselineData(baseline: unknown): asserts baseline is BaselineData {
    if (!baseline || typeof baseline !== 'object') {
      throw new ValidationError('Baseline data must be an object');
    }

    const b = baseline as Record<string, unknown>;

    if (!b.id || typeof b.id !== 'string') {
      throw new ValidationError('Baseline data must have a valid id');
    }

    if (!b.name || typeof b.name !== 'string') {
      throw new ValidationError('Baseline data must have a valid name');
    }

    if (typeof b.isDefault !== 'boolean') {
      throw new ValidationError('Baseline data must have a valid isDefault flag');
    }

    if (!Array.isArray(b.tags)) {
      throw new ValidationError('Baseline data must have a tags array');
    }

    if (!b.metrics) {
      throw new ValidationError('Baseline data must have metrics');
    }

    this.validateMetricsSnapshot(b.metrics);
  }

  /**
   * Validates a threshold rule
   */
  static validateThresholdRule(rule: unknown): asserts rule is ThresholdRule {
    if (!rule || typeof rule !== 'object') {
      throw new ValidationError('Threshold rule must be an object');
    }

    const r = rule as Record<string, unknown>;

    if (!r.id || typeof r.id !== 'string') {
      throw new ValidationError('Threshold rule must have a valid id');
    }

    if (!r.name || typeof r.name !== 'string') {
      throw new ValidationError('Threshold rule must have a valid name');
    }

    if (!r.metric || typeof r.metric !== 'string') {
      throw new ValidationError('Threshold rule must have a valid metric');
    }

    if (!['absolute', 'percentage'].includes(r.type as string)) {
      throw new ValidationError('Threshold rule type must be absolute or percentage');
    }

    if (!['gte', 'lte', 'eq', 'ne', 'gt', 'lt'].includes(r.comparison as string)) {
      throw new ValidationError('Threshold rule comparison must be valid operator');
    }

    if (typeof r.value !== 'number') {
      throw new ValidationError('Threshold rule must have a numeric value');
    }

    if (!['error', 'warning', 'info'].includes(r.severity as string)) {
      throw new ValidationError('Threshold rule severity must be error, warning, or info');
    }

    if (typeof r.enabled !== 'boolean') {
      throw new ValidationError('Threshold rule must have a valid enabled flag');
    }
  }

  /**
   * Validates engine configuration
   */
  static validateEngineConfig(config: unknown): asserts config is EngineConfig {
    if (!config || typeof config !== 'object') {
      throw new ValidationError('Engine config must be an object');
    }

    const c = config as Record<string, unknown>;

    if (!c.baseline || typeof c.baseline !== 'object') {
      throw new ValidationError('Engine config must have baseline configuration');
    }

    if (!Array.isArray(c.rules)) {
      throw new ValidationError('Engine config must have rules array');
    }

    // Validate each rule
    for (const rule of c.rules) {
      this.validateThresholdRule(rule);
    }

    if (!c.reporting || typeof c.reporting !== 'object') {
      throw new ValidationError('Engine config must have reporting configuration');
    }

    if (!c.metrics || typeof c.metrics !== 'object') {
      throw new ValidationError('Engine config must have metrics configuration');
    }
  }

  /**
   * Validates that a value is a positive number
   */
  static validatePositiveNumber(value: unknown, fieldName: string): asserts value is number {
    if (typeof value !== 'number' || value < 0 || !isFinite(value)) {
      throw new ValidationError(`${fieldName} must be a positive number`);
    }
  }

  /**
   * Validates that a value is a non-empty string
   */
  static validateNonEmptyString(value: unknown, fieldName: string): asserts value is string {
    if (typeof value !== 'string' || value.trim().length === 0) {
      throw new ValidationError(`${fieldName} must be a non-empty string`);
    }
  }

  /**
   * Validates that a value is a valid date
   */
  static validateDate(value: unknown, fieldName: string): asserts value is Date {
    if (!(value instanceof Date) || isNaN(value.getTime())) {
      throw new ValidationError(`${fieldName} must be a valid date`);
    }
  }

  /**
   * Validates that a value exists and is not null/undefined
   */
  static validateRequired<T>(value: T | null | undefined, fieldName: string): asserts value is T {
    if (value === null || value === undefined) {
      throw new ValidationError(`${fieldName} is required`);
    }
  }

  /**
   * Validates that a value is one of the allowed options
   */
  static validateEnum<T extends string>(
    value: unknown,
    allowedValues: readonly T[],
    fieldName: string
  ): asserts value is T {
    if (!allowedValues.includes(value as T)) {
      throw new ValidationError(
        `${fieldName} must be one of: ${allowedValues.join(', ')}`
      );
    }
  }
}