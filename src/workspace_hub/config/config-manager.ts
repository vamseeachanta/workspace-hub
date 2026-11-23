/**
 * Configuration Manager - Centralized configuration system for rules and settings
 */

import * as path from 'path';
import * as yaml from 'js-yaml';
import * as fs from 'fs-extra';
import { FileUtils } from '../utils/file-utils';
import { ValidationUtils } from '../utils/validation';
import {
  EngineConfig,
  BaselineConfig,
  ThresholdRule,
  BaselineEngineError,
  ValidationError,
  DeepPartial
} from '../types';
import { MetricsCollectorConfig } from '../metrics/metrics-collector';
import { ReportConfig } from '../reports/report-generator';
import { RuleEngineConfig } from '../rules/rule-engine';

export interface ConfigSchema {
  version: string;
  engine: EngineConfig;
  metricsCollector: MetricsCollectorConfig;
  reportGenerator: ReportConfig;
  ruleEngine: RuleEngineConfig;
}

export interface ConfigValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export class ConfigManager {
  private config: ConfigSchema | null = null;
  private configPath: string;
  private defaultConfig: ConfigSchema;

  constructor(configPath: string = './baseline-config.yml') {
    this.configPath = configPath;
    this.defaultConfig = this.createDefaultConfig();
  }

  /**
   * Loads configuration from file
   */
  async loadConfig(): Promise<ConfigSchema> {
    try {
      if (await FileUtils.fileExists(this.configPath)) {
        const configContent = await fs.readFile(this.configPath, 'utf-8');

        let parsedConfig: any;
        if (this.configPath.endsWith('.yml') || this.configPath.endsWith('.yaml')) {
          parsedConfig = yaml.load(configContent);
        } else {
          parsedConfig = JSON.parse(configContent);
        }

        // Merge with defaults to ensure all required fields are present
        this.config = this.mergeWithDefaults(parsedConfig);
      } else {
        // Use default configuration
        this.config = this.defaultConfig;
        await this.saveConfig(); // Save default config for future reference
      }

      // Validate configuration
      const validation = this.validateConfig(this.config);
      if (!validation.valid) {
        throw new ValidationError(
          `Configuration validation failed: ${validation.errors.join(', ')}`
        );
      }

      return this.config;
    } catch (error) {
      throw new BaselineEngineError(
        'Failed to load configuration',
        'CONFIG_LOAD_ERROR',
        error
      );
    }
  }

  /**
   * Saves configuration to file
   */
  async saveConfig(config?: ConfigSchema): Promise<void> {
    try {
      const configToSave = config || this.config || this.defaultConfig;

      // Validate before saving
      const validation = this.validateConfig(configToSave);
      if (!validation.valid) {
        throw new ValidationError(
          `Cannot save invalid configuration: ${validation.errors.join(', ')}`
        );
      }

      await FileUtils.ensureDirectory(path.dirname(this.configPath));

      let configContent: string;
      if (this.configPath.endsWith('.yml') || this.configPath.endsWith('.yaml')) {
        configContent = yaml.dump(configToSave, {
          indent: 2,
          lineWidth: 120,
          noRefs: true
        });
      } else {
        configContent = JSON.stringify(configToSave, null, 2);
      }

      await fs.writeFile(this.configPath, configContent, 'utf-8');
      this.config = configToSave;
    } catch (error) {
      throw new BaselineEngineError(
        'Failed to save configuration',
        'CONFIG_SAVE_ERROR',
        error
      );
    }
  }

  /**
   * Updates specific configuration section
   */
  async updateConfig(updates: DeepPartial<ConfigSchema>): Promise<ConfigSchema> {
    if (!this.config) {
      await this.loadConfig();
    }

    const updatedConfig = this.deepMerge(this.config!, updates);

    // Validate updated configuration
    const validation = this.validateConfig(updatedConfig);
    if (!validation.valid) {
      throw new ValidationError(
        `Updated configuration is invalid: ${validation.errors.join(', ')}`
      );
    }

    await this.saveConfig(updatedConfig);
    return updatedConfig;
  }

  /**
   * Gets current configuration
   */
  async getConfig(): Promise<ConfigSchema> {
    if (!this.config) {
      await this.loadConfig();
    }
    return this.config!;
  }

  /**
   * Gets specific configuration section
   */
  async getSection<K extends keyof ConfigSchema>(section: K): Promise<ConfigSchema[K]> {
    const config = await this.getConfig();
    return config[section];
  }

  /**
   * Creates a backup of current configuration
   */
  async createBackup(): Promise<string> {
    if (!this.config) {
      await this.loadConfig();
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = this.configPath.replace(/\.(yml|yaml|json)$/, `.backup.${timestamp}.$1`);

    await FileUtils.copyFile(this.configPath, backupPath);
    return backupPath;
  }

  /**
   * Restores configuration from backup
   */
  async restoreFromBackup(backupPath: string): Promise<void> {
    if (!(await FileUtils.fileExists(backupPath))) {
      throw new ValidationError(`Backup file not found: ${backupPath}`);
    }

    await FileUtils.copyFile(backupPath, this.configPath);
    this.config = null; // Force reload
    await this.loadConfig();
  }

  /**
   * Validates configuration against schema
   */
  validateConfig(config: ConfigSchema): ConfigValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    try {
      // Validate version
      if (!config.version || typeof config.version !== 'string') {
        errors.push('Configuration version is required');
      }

      // Validate engine configuration
      if (!config.engine) {
        errors.push('Engine configuration is required');
      } else {
        try {
          ValidationUtils.validateEngineConfig(config.engine);
        } catch (error) {
          errors.push(`Engine config validation failed: ${error instanceof Error ? error.message : String(error)}`);
        }
      }

      // Validate metrics collector configuration
      if (!config.metricsCollector) {
        errors.push('Metrics collector configuration is required');
      } else {
        this.validateMetricsCollectorConfig(config.metricsCollector, errors, warnings);
      }

      // Validate report generator configuration
      if (!config.reportGenerator) {
        errors.push('Report generator configuration is required');
      } else {
        this.validateReportGeneratorConfig(config.reportGenerator, errors, warnings);
      }

      // Validate rule engine configuration
      if (!config.ruleEngine) {
        errors.push('Rule engine configuration is required');
      } else {
        this.validateRuleEngineConfig(config.ruleEngine, errors, warnings);
      }

      // Cross-validation checks
      this.performCrossValidation(config, errors, warnings);

    } catch (error) {
      errors.push(`Configuration validation error: ${error instanceof Error ? error.message : String(error)}`);
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Gets available configuration templates
   */
  getConfigTemplates(): { [templateName: string]: ConfigSchema } {
    return {
      minimal: this.createMinimalConfig(),
      standard: this.createDefaultConfig(),
      comprehensive: this.createComprehensiveConfig(),
      ci_cd: this.createCiCdConfig()
    };
  }

  /**
   * Applies a configuration template
   */
  async applyTemplate(templateName: string, overrides?: DeepPartial<ConfigSchema>): Promise<ConfigSchema> {
    const templates = this.getConfigTemplates();
    const template = templates[templateName];

    if (!template) {
      throw new ValidationError(`Configuration template '${templateName}' not found`);
    }

    let config = template;
    if (overrides) {
      config = this.deepMerge(template, overrides);
    }

    await this.saveConfig(config);
    return config;
  }

  /**
   * Migrates configuration to newer version
   */
  async migrateConfig(targetVersion: string): Promise<ConfigSchema> {
    if (!this.config) {
      await this.loadConfig();
    }

    const currentVersion = this.config!.version;
    if (currentVersion === targetVersion) {
      return this.config!;
    }

    // Create backup before migration
    await this.createBackup();

    // Perform version-specific migrations
    let migratedConfig = { ...this.config! };

    // Example migration logic (add more as needed)
    if (currentVersion === '1.0.0' && targetVersion === '1.1.0') {
      migratedConfig = this.migrateFrom1_0_0To1_1_0(migratedConfig);
    }

    migratedConfig.version = targetVersion;

    // Validate migrated configuration
    const validation = this.validateConfig(migratedConfig);
    if (!validation.valid) {
      throw new BaselineEngineError(
        `Configuration migration failed validation: ${validation.errors.join(', ')}`,
        'MIGRATION_ERROR'
      );
    }

    await this.saveConfig(migratedConfig);
    return migratedConfig;
  }

  /**
   * Private helper methods
   */
  private createDefaultConfig(): ConfigSchema {
    return {
      version: '1.0.0',
      engine: {
        baseline: {
          storagePath: './baselines',
          retentionPolicy: {
            maxVersions: 10,
            maxAge: 30
          },
          mergeStrategy: 'latest',
          backupEnabled: true,
          backupPath: './baselines/backups'
        },
        rules: [],
        reporting: {
          formats: ['json', 'html'],
          outputPath: './reports',
          includeDetails: true,
          includeTrends: false
        },
        metrics: {
          parseFormats: ['jest', 'mocha', 'nyc'],
          customParsers: []
        }
      },
      metricsCollector: {
        parsers: {
          jest: {
            enabled: true,
            resultsPath: './test-results.json',
            coveragePath: './coverage'
          },
          mocha: {
            enabled: false,
            resultsPath: './test-results.json',
            format: 'json'
          },
          nyc: {
            enabled: false,
            coveragePath: './coverage'
          }
        },
        performance: {
          enabled: false,
          sources: []
        }
      },
      reportGenerator: {
        outputPath: './reports',
        formats: ['json', 'html'],
        includeDetails: true,
        includeTrends: false,
        includeCharts: false
      },
      ruleEngine: {
        rulesPath: './baseline-rules.json',
        autoSave: true,
        enableProgressive: false,
        progressiveSteps: 5,
        defaultSeverity: 'warning'
      }
    };
  }

  private createMinimalConfig(): ConfigSchema {
    const defaultConfig = this.createDefaultConfig();
    return {
      ...defaultConfig,
      reportGenerator: {
        ...defaultConfig.reportGenerator,
        formats: ['json'],
        includeDetails: false,
        includeTrends: false
      },
      metricsCollector: {
        parsers: {
          jest: {
            enabled: true,
            resultsPath: './test-results.json'
          }
        },
        performance: {
          enabled: false,
          sources: []
        }
      }
    };
  }

  private createComprehensiveConfig(): ConfigSchema {
    const defaultConfig = this.createDefaultConfig();
    return {
      ...defaultConfig,
      reportGenerator: {
        ...defaultConfig.reportGenerator,
        formats: ['json', 'html', 'markdown', 'csv'],
        includeDetails: true,
        includeTrends: true,
        includeCharts: true
      },
      metricsCollector: {
        parsers: {
          jest: {
            enabled: true,
            resultsPath: './test-results.json',
            coveragePath: './coverage'
          },
          mocha: {
            enabled: true,
            resultsPath: './mocha-results.json',
            format: 'json'
          },
          nyc: {
            enabled: true,
            coveragePath: './coverage'
          },
          lcov: {
            enabled: true,
            lcovPath: './coverage/lcov.info'
          }
        },
        performance: {
          enabled: true,
          sources: ['./performance-metrics.json']
        }
      },
      ruleEngine: {
        ...defaultConfig.ruleEngine,
        enableProgressive: true,
        progressiveSteps: 10
      }
    };
  }

  private createCiCdConfig(): ConfigSchema {
    const defaultConfig = this.createDefaultConfig();
    return {
      ...defaultConfig,
      engine: {
        ...defaultConfig.engine,
        baseline: {
          ...defaultConfig.engine.baseline,
          storagePath: './ci/baselines',
          backupPath: './ci/baselines/backups'
        },
        reporting: {
          ...defaultConfig.engine.reporting,
          formats: ['json', 'markdown'],
          outputPath: './ci/reports'
        }
      },
      reportGenerator: {
        ...defaultConfig.reportGenerator,
        outputPath: './ci/reports',
        formats: ['json', 'markdown'],
        includeDetails: false,
        includeTrends: true
      }
    };
  }

  private validateMetricsCollectorConfig(
    config: MetricsCollectorConfig,
    errors: string[],
    warnings: string[]
  ): void {
    if (!config.parsers) {
      errors.push('Metrics collector parsers configuration is required');
      return;
    }

    const enabledParsers = Object.values(config.parsers).filter(p => {
      if (Array.isArray(p)) {
        return p.some(parser => parser.enabled);
      }
      return p?.enabled;
    }).length;
    if (enabledParsers === 0) {
      warnings.push('No metrics parsers are enabled');
    }

    // Validate individual parser configurations
    if (config.parsers.jest?.enabled && !config.parsers.jest.resultsPath) {
      errors.push('Jest parser requires resultsPath');
    }

    if (config.parsers.mocha?.enabled && !config.parsers.mocha.resultsPath) {
      errors.push('Mocha parser requires resultsPath');
    }

    if (config.parsers.nyc?.enabled && !config.parsers.nyc.coveragePath) {
      errors.push('NYC parser requires coveragePath');
    }
  }

  private validateReportGeneratorConfig(
    config: ReportConfig,
    errors: string[],
    warnings: string[]
  ): void {
    if (!config.outputPath) {
      errors.push('Report generator output path is required');
    }

    if (!config.formats || config.formats.length === 0) {
      errors.push('At least one report format must be specified');
    }

    const validFormats = ['json', 'html', 'markdown', 'csv'];
    const invalidFormats = config.formats.filter(f => !validFormats.includes(f));
    if (invalidFormats.length > 0) {
      errors.push(`Invalid report formats: ${invalidFormats.join(', ')}`);
    }
  }

  private validateRuleEngineConfig(
    config: RuleEngineConfig,
    errors: string[],
    warnings: string[]
  ): void {
    if (!config.rulesPath) {
      errors.push('Rule engine rules path is required');
    }

    if (config.enableProgressive && config.progressiveSteps <= 1) {
      errors.push('Progressive steps must be greater than 1 when progressive mode is enabled');
    }

    if (!['error', 'warning', 'info'].includes(config.defaultSeverity)) {
      errors.push('Default severity must be error, warning, or info');
    }
  }

  private performCrossValidation(
    config: ConfigSchema,
    errors: string[],
    warnings: string[]
  ): void {
    // Validate that report output path is accessible
    if (config.reportGenerator.outputPath === config.engine.baseline.storagePath) {
      warnings.push('Report output path is the same as baseline storage path');
    }

    // Validate that rule engine and engine configurations are consistent
    if (config.ruleEngine.rulesPath === config.engine.baseline.storagePath) {
      warnings.push('Rules path is the same as baseline storage path');
    }

    // Check for conflicting configurations
    if (config.engine.reporting.formats.length !== config.reportGenerator.formats.length) {
      warnings.push('Engine reporting formats differ from report generator formats');
    }
  }

  private mergeWithDefaults(userConfig: any): ConfigSchema {
    return this.deepMerge(this.defaultConfig, userConfig);
  }

  private deepMerge<T>(target: T, source: any): T {
    const result = { ...target };

    for (const key in source) {
      if (source.hasOwnProperty(key)) {
        if (
          source[key] &&
          typeof source[key] === 'object' &&
          !Array.isArray(source[key]) &&
          result[key as keyof T] &&
          typeof result[key as keyof T] === 'object' &&
          !Array.isArray(result[key as keyof T])
        ) {
          (result as any)[key] = this.deepMerge(result[key as keyof T], source[key]);
        } else {
          (result as any)[key] = source[key];
        }
      }
    }

    return result;
  }

  private migrateFrom1_0_0To1_1_0(config: ConfigSchema): ConfigSchema {
    // Example migration logic
    return {
      ...config,
      // Add new fields or modify existing ones as needed for version 1.1.0
      ruleEngine: {
        ...config.ruleEngine,
        // Add new fields that didn't exist in 1.0.0
        progressiveSteps: config.ruleEngine.progressiveSteps || 5
      }
    };
  }
}