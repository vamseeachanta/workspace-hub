/**
 * Baseline Tracking Engine - Main entry point
 */

export * from './types';
export * from './baseline/baseline-manager';
export * from './metrics/metrics-collector';
export * from './comparison/comparison-engine';
export * from './rules/rule-engine';
export * from './reports/report-generator';
export * from './config/config-manager';
export * from './utils/validation';
export * from './utils/file-utils';

// Main engine class
export { BaselineTrackingEngine } from './engine/baseline-tracking-engine';

// Version
export const VERSION = '1.0.0';