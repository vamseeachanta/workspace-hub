/**
 * Baseline Tracking Engine - Main entry point
 */

export * from './workspace_hub/types';
export * from './workspace_hub/baseline/baseline-manager';
export * from './workspace_hub/metrics/metrics-collector';
export * from './workspace_hub/comparison/comparison-engine';
export * from './workspace_hub/rules/rule-engine';
export * from './workspace_hub/reports/report-generator';
export * from './workspace_hub/config/config-manager';
export * from './workspace_hub/utils/validation';
export * from './workspace_hub/utils/file-utils';

// Main engine class
export { BaselineTrackingEngine } from './workspace_hub/engine/baseline-tracking-engine';

// Version
export const VERSION = '1.0.0';