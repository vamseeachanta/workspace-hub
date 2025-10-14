/**
 * Baseline Manager - Core component for loading, saving, and managing baseline files
 */

import * as path from 'path';
import * as semver from 'semver';
import { FileUtils } from '../utils/file-utils';
import { ValidationUtils } from '../utils/validation';
import {
  BaselineData,
  BaselineConfig,
  MetricsSnapshot,
  FilterOptions,
  SortOptions,
  BaselineEngineError,
  ValidationError,
  FileSystemError
} from '../types';

export class BaselineManager {
  private config: BaselineConfig;
  private baselineCache: Map<string, BaselineData> = new Map();

  constructor(config: BaselineConfig) {
    ValidationUtils.validateRequired(config, 'config');
    this.config = config;
  }

  /**
   * Loads a baseline by ID
   */
  async loadBaseline(id: string): Promise<BaselineData> {
    ValidationUtils.validateNonEmptyString(id, 'id');

    // Check cache first
    if (this.baselineCache.has(id)) {
      return this.baselineCache.get(id)!;
    }

    const filePath = this.getBaselineFilePath(id);

    if (!(await FileUtils.fileExists(filePath))) {
      throw new FileSystemError(`Baseline not found: ${id}`);
    }

    try {
      const baseline = await FileUtils.readJsonFile<BaselineData>(filePath);
      ValidationUtils.validateBaselineData(baseline);

      // Cache the loaded baseline
      this.baselineCache.set(id, baseline);
      return baseline;
    } catch (error) {
      if (error instanceof ValidationError) {
        throw error;
      }
      throw new BaselineEngineError(
        `Failed to load baseline: ${id}`,
        'LOAD_ERROR',
        error
      );
    }
  }

  /**
   * Saves a baseline
   */
  async saveBaseline(baseline: BaselineData): Promise<void> {
    ValidationUtils.validateBaselineData(baseline);

    const filePath = this.getBaselineFilePath(baseline.id);

    // Create backup if file exists
    if (await FileUtils.fileExists(filePath)) {
      if (this.config.backupEnabled) {
        const backupPath = this.config.backupPath || path.dirname(filePath);
        await FileUtils.createBackup(filePath, backupPath);
      }
    }

    try {
      // Update timestamps
      baseline.updated = new Date();

      await FileUtils.writeJsonFile(filePath, baseline);

      // Update cache
      this.baselineCache.set(baseline.id, baseline);

      // Apply retention policy
      await this.applyRetentionPolicy();
    } catch (error) {
      throw new BaselineEngineError(
        `Failed to save baseline: ${baseline.id}`,
        'SAVE_ERROR',
        error
      );
    }
  }

  /**
   * Creates a new baseline from metrics snapshot
   */
  async createBaseline(
    name: string,
    snapshot: MetricsSnapshot,
    options: {
      isDefault?: boolean;
      tags?: string[];
      metadata?: Record<string, unknown>;
    } = {}
  ): Promise<BaselineData> {
    ValidationUtils.validateNonEmptyString(name, 'name');
    ValidationUtils.validateMetricsSnapshot(snapshot);

    const baseline: BaselineData = {
      id: this.generateBaselineId(name, snapshot.branch),
      name,
      branch: snapshot.branch,
      commit: snapshot.commit,
      environment: snapshot.environment,
      version: snapshot.version,
      previousVersion: undefined,
      metrics: snapshot,
      isDefault: options.isDefault || false,
      tags: options.tags || [],
      metadata: options.metadata || {},
      created: new Date(),
      updated: new Date()
    };

    await this.saveBaseline(baseline);
    return baseline;
  }

  /**
   * Updates an existing baseline
   */
  async updateBaseline(
    id: string,
    updates: Partial<Omit<BaselineData, 'id' | 'created'>>
  ): Promise<BaselineData> {
    const baseline = await this.loadBaseline(id);

    const updatedBaseline: BaselineData = {
      ...baseline,
      ...updates,
      id: baseline.id, // Ensure ID cannot be changed
      created: baseline.created, // Preserve creation timestamp
      updated: new Date()
    };

    await this.saveBaseline(updatedBaseline);
    return updatedBaseline;
  }

  /**
   * Lists all baselines with optional filtering and sorting
   */
  async listBaselines(
    filter?: FilterOptions,
    sort?: SortOptions
  ): Promise<BaselineData[]> {
    const baselineFiles = await FileUtils.listFiles(
      this.config.storagePath,
      /\.baseline\.json$/
    );

    const baselines: BaselineData[] = [];

    for (const file of baselineFiles) {
      try {
        const filePath = path.join(this.config.storagePath, file);
        const baseline = await FileUtils.readJsonFile<BaselineData>(filePath);
        ValidationUtils.validateBaselineData(baseline);
        baselines.push(baseline);
      } catch (error) {
        // Log warning but continue processing other files
        console.warn(`Failed to load baseline file ${file}:`, error);
      }
    }

    let filteredBaselines = this.applyFilters(baselines, filter);

    if (sort) {
      filteredBaselines = this.applySorting(filteredBaselines, sort);
    }

    return filteredBaselines;
  }

  /**
   * Gets the default baseline for a branch and environment
   */
  async getDefaultBaseline(
    branch: string,
    environment: string
  ): Promise<BaselineData | null> {
    const baselines = await this.listBaselines({
      branch,
      environment
    });

    return baselines.find(b => b.isDefault) || null;
  }

  /**
   * Sets a baseline as the default for its branch and environment
   */
  async setAsDefault(id: string): Promise<void> {
    const baseline = await this.loadBaseline(id);

    // Clear existing default for this branch/environment
    const existingDefaults = await this.listBaselines({
      branch: baseline.branch,
      environment: baseline.environment
    });

    for (const existing of existingDefaults) {
      if (existing.isDefault && existing.id !== id) {
        await this.updateBaseline(existing.id, { isDefault: false });
      }
    }

    // Set new default
    await this.updateBaseline(id, { isDefault: true });
  }

  /**
   * Deletes a baseline
   */
  async deleteBaseline(id: string): Promise<void> {
    ValidationUtils.validateNonEmptyString(id, 'id');

    const filePath = this.getBaselineFilePath(id);

    if (!(await FileUtils.fileExists(filePath))) {
      throw new FileSystemError(`Baseline not found: ${id}`);
    }

    try {
      // Create backup before deletion if enabled
      if (this.config.backupEnabled) {
        const backupPath = this.config.backupPath || path.dirname(filePath);
        await FileUtils.createBackup(filePath, backupPath);
      }

      await FileUtils.deleteFile(filePath);
      this.baselineCache.delete(id);
    } catch (error) {
      throw new BaselineEngineError(
        `Failed to delete baseline: ${id}`,
        'DELETE_ERROR',
        error
      );
    }
  }

  /**
   * Merges baselines using the configured strategy
   */
  async mergeBaselines(
    sourceId: string,
    targetId: string,
    strategy?: 'latest' | 'best' | 'manual'
  ): Promise<BaselineData> {
    const source = await this.loadBaseline(sourceId);
    const target = await this.loadBaseline(targetId);

    const mergeStrategy = strategy || this.config.mergeStrategy;

    switch (mergeStrategy) {
      case 'latest':
        return source.updated > target.updated ? source : target;

      case 'best':
        return this.selectBestBaseline(source, target);

      case 'manual':
        throw new BaselineEngineError(
          'Manual merge strategy requires user intervention',
          'MANUAL_MERGE_REQUIRED'
        );

      default:
        throw new BaselineEngineError(
          `Unknown merge strategy: ${mergeStrategy}`,
          'INVALID_MERGE_STRATEGY'
        );
    }
  }

  /**
   * Creates a version history for a baseline
   */
  async getVersionHistory(id: string): Promise<BaselineData[]> {
    const baseline = await this.loadBaseline(id);
    const history: BaselineData[] = [baseline];

    let currentBaseline = baseline;
    while (currentBaseline.previousVersion) {
      try {
        currentBaseline = await this.loadBaseline(currentBaseline.previousVersion);
        history.push(currentBaseline);
      } catch (error) {
        // Break if previous version is not found
        break;
      }
    }

    return history;
  }

  /**
   * Private helper methods
   */
  private getBaselineFilePath(id: string): string {
    return path.join(this.config.storagePath, `${id}.baseline.json`);
  }

  private generateBaselineId(name: string, branch: string): string {
    const timestamp = Date.now();
    const sanitizedName = name.replace(/[^a-zA-Z0-9-_]/g, '-');
    const sanitizedBranch = branch.replace(/[^a-zA-Z0-9-_]/g, '-');
    return `${sanitizedName}-${sanitizedBranch}-${timestamp}`;
  }

  private applyFilters(
    baselines: BaselineData[],
    filter?: FilterOptions
  ): BaselineData[] {
    if (!filter) return baselines;

    return baselines.filter(baseline => {
      if (filter.branch && baseline.branch !== filter.branch) return false;
      if (filter.environment && baseline.environment !== filter.environment) return false;
      if (filter.version && baseline.version !== filter.version) return false;
      if (filter.dateFrom && baseline.created < filter.dateFrom) return false;
      if (filter.dateTo && baseline.created > filter.dateTo) return false;
      if (filter.tags && !filter.tags.every(tag => baseline.tags.includes(tag))) return false;

      return true;
    });
  }

  private applySorting(
    baselines: BaselineData[],
    sort: SortOptions
  ): BaselineData[] {
    return baselines.sort((a, b) => {
      const aValue = this.getNestedValue(a, sort.field);
      const bValue = this.getNestedValue(b, sort.field);

      let comparison = 0;
      if (aValue < bValue) comparison = -1;
      else if (aValue > bValue) comparison = 1;

      return sort.order === 'desc' ? -comparison : comparison;
    });
  }

  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  private selectBestBaseline(baseline1: BaselineData, baseline2: BaselineData): BaselineData {
    // Simple heuristic: prefer baseline with better test coverage
    const coverage1 = baseline1.metrics.coverage.lines.percentage;
    const coverage2 = baseline2.metrics.coverage.lines.percentage;

    return coverage1 >= coverage2 ? baseline1 : baseline2;
  }

  private async applyRetentionPolicy(): Promise<void> {
    if (this.config.retentionPolicy.maxVersions <= 0 &&
        this.config.retentionPolicy.maxAge <= 0) {
      return;
    }

    const baselines = await this.listBaselines();

    // Apply age-based retention
    if (this.config.retentionPolicy.maxAge > 0) {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - this.config.retentionPolicy.maxAge);

      for (const baseline of baselines) {
        if (baseline.created < cutoffDate && !baseline.isDefault) {
          await this.deleteBaseline(baseline.id);
        }
      }
    }

    // Apply count-based retention per branch/environment
    if (this.config.retentionPolicy.maxVersions > 0) {
      const groupedBaselines = new Map<string, BaselineData[]>();

      for (const baseline of baselines) {
        const key = `${baseline.branch}-${baseline.environment}`;
        if (!groupedBaselines.has(key)) {
          groupedBaselines.set(key, []);
        }
        groupedBaselines.get(key)!.push(baseline);
      }

      for (const [, group] of groupedBaselines) {
        const sorted = group.sort((a, b) => b.created.getTime() - a.created.getTime());
        const toDelete = sorted.slice(this.config.retentionPolicy.maxVersions);

        for (const baseline of toDelete) {
          if (!baseline.isDefault) {
            await this.deleteBaseline(baseline.id);
          }
        }
      }
    }
  }
}