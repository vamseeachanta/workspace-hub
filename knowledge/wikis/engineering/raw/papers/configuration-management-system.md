# Configuration Management System

## System Overview

The Configuration Management System provides centralized, hierarchical, and environment-aware configuration management for the Test Baseline Tracking System, supporting dynamic updates, validation, and secure secret management.

## Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                Configuration Management System                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐│
│  │ Config      │  │  Schema     │  │  Secret     │  │ Dynamic  ││
│  │ Repository  │  │ Validation  │  │ Management  │  │ Updates  ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘│
│         │               │               │               │       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │               Configuration Hierarchy                      ││
│  └─────────────────────────────────────────────────────────────┘│
│                            │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                Environment Resolution                      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 1. Configuration Hierarchy and Structure

### Hierarchical Configuration Model
```yaml
# config/hierarchy.yaml
# Configuration precedence (highest to lowest):

global:
  # System-wide defaults
  api:
    port: 3000
    cors:
      enabled: true
      origins: ["*"]
    rate_limiting:
      window_ms: 900000  # 15 minutes
      max_requests: 100

  database:
    pool:
      min: 2
      max: 10
      idle_timeout: 30000
    retry:
      max_attempts: 3
      delay: 1000

  storage:
    provider: "local"
    retention_days: 90
    compression: true

  notifications:
    enabled: true
    channels: ["email"]

environment:
  development:
    api:
      port: 3001
      cors:
        origins: ["http://localhost:3000", "http://localhost:8080"]

    database:
      host: "localhost"
      port: 5432
      name: "tbts_dev"
      ssl: false

    storage:
      provider: "local"
      path: "./data/dev"

    notifications:
      enabled: false

    logging:
      level: "debug"
      console: true

  staging:
    api:
      port: 3000
      cors:
        origins: ["https://staging.example.com"]

    database:
      host: "staging-db.example.com"
      port: 5432
      name: "tbts_staging"
      ssl: true

    storage:
      provider: "s3"
      bucket: "tbts-staging-data"
      region: "us-east-1"

    notifications:
      enabled: true
      channels: ["slack"]

    logging:
      level: "info"

  production:
    api:
      port: 3000
      cors:
        origins: ["https://app.example.com"]

    database:
      host: "prod-db.example.com"
      port: 5432
      name: "tbts_production"
      ssl: true
      pool:
        min: 5
        max: 50

    storage:
      provider: "s3"
      bucket: "tbts-production-data"
      region: "us-east-1"

    notifications:
      enabled: true
      channels: ["email", "slack", "webhook"]

    logging:
      level: "warn"
      console: false

project:
  # Project-specific overrides
  "project-alpha":
    thresholds:
      execution:
        pass_rate_min_percentage: 98.0
        execution_time_max_ms: 30000
      coverage:
        line_coverage_min: 85.0
        branch_coverage_min: 80.0

    notifications:
      channels: ["slack"]
      slack:
        webhook_url: "${ALPHA_SLACK_WEBHOOK}"
        channel: "#alpha-alerts"

    alerts:
      cooldown_ms: 600000  # 10 minutes

  "project-beta":
    thresholds:
      execution:
        pass_rate_min_percentage: 95.0
        execution_time_max_ms: 60000
      coverage:
        line_coverage_min: 80.0

    storage:
      retention_days: 180  # Extended retention

user:
  # User-specific preferences
  "user-123":
    dashboard:
      theme: "dark"
      refresh_interval: 30000
      default_filters:
        environments: ["production", "staging"]

    notifications:
      email_digest: "daily"
      immediate_alerts: ["critical", "major"]

# Feature flags
features:
  anomaly_detection: true
  ml_predictions: false
  advanced_analytics: true
  beta_dashboard: false
```

### Configuration Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TBTS Configuration Schema",
  "type": "object",
  "properties": {
    "api": {
      "type": "object",
      "properties": {
        "port": {
          "type": "integer",
          "minimum": 1024,
          "maximum": 65535,
          "description": "API server port"
        },
        "cors": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean" },
            "origins": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        },
        "rate_limiting": {
          "type": "object",
          "properties": {
            "window_ms": {
              "type": "integer",
              "minimum": 1000,
              "description": "Rate limiting window in milliseconds"
            },
            "max_requests": {
              "type": "integer",
              "minimum": 1,
              "description": "Maximum requests per window"
            }
          }
        }
      }
    },
    "database": {
      "type": "object",
      "properties": {
        "host": { "type": "string" },
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535
        },
        "name": { "type": "string" },
        "ssl": { "type": "boolean" },
        "pool": {
          "type": "object",
          "properties": {
            "min": {
              "type": "integer",
              "minimum": 0
            },
            "max": {
              "type": "integer",
              "minimum": 1
            },
            "idle_timeout": {
              "type": "integer",
              "minimum": 1000
            }
          }
        }
      },
      "required": ["host", "port", "name"]
    },
    "storage": {
      "type": "object",
      "properties": {
        "provider": {
          "type": "string",
          "enum": ["local", "s3", "gcs", "azure"]
        },
        "retention_days": {
          "type": "integer",
          "minimum": 1,
          "maximum": 3650
        },
        "compression": { "type": "boolean" }
      }
    },
    "thresholds": {
      "type": "object",
      "properties": {
        "execution": {
          "type": "object",
          "properties": {
            "pass_rate_min_percentage": {
              "type": "number",
              "minimum": 0,
              "maximum": 100
            },
            "execution_time_max_ms": {
              "type": "integer",
              "minimum": 1000
            }
          }
        },
        "coverage": {
          "type": "object",
          "properties": {
            "line_coverage_min": {
              "type": "number",
              "minimum": 0,
              "maximum": 100
            },
            "branch_coverage_min": {
              "type": "number",
              "minimum": 0,
              "maximum": 100
            }
          }
        }
      }
    },
    "notifications": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean" },
        "channels": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["email", "slack", "webhook", "teams"]
          }
        }
      }
    },
    "features": {
      "type": "object",
      "additionalProperties": { "type": "boolean" }
    }
  }
}
```

## 2. Configuration Management Service

### Core Configuration Manager
```javascript
// config-manager.js
const fs = require('fs').promises;
const path = require('path');
const yaml = require('js-yaml');
const Joi = require('joi');
const chokidar = require('chokidar');

class ConfigurationManager {
  constructor(options = {}) {
    this.configPath = options.configPath || './config';
    this.environment = options.environment || process.env.NODE_ENV || 'development';
    this.configs = new Map();
    this.schemas = new Map();
    this.watchers = new Map();
    this.listeners = new Map();
    this.secretsManager = options.secretsManager;
    this.cache = new Map();
    this.cacheTimeout = options.cacheTimeout || 300000; // 5 minutes
  }

  async initialize() {
    // Load configuration schemas
    await this.loadSchemas();

    // Load base configurations
    await this.loadConfigurations();

    // Setup file watchers for hot reload
    this.setupFileWatchers();

    // Initialize secrets manager
    if (this.secretsManager) {
      await this.secretsManager.initialize();
    }

    console.log(`Configuration manager initialized for environment: ${this.environment}`);
  }

  async loadSchemas() {
    const schemaPath = path.join(this.configPath, 'schemas');

    try {
      const schemaFiles = await fs.readdir(schemaPath);

      for (const file of schemaFiles) {
        if (file.endsWith('.json')) {
          const schemaName = path.basename(file, '.json');
          const schemaContent = await fs.readFile(path.join(schemaPath, file), 'utf8');
          const schema = JSON.parse(schemaContent);

          this.schemas.set(schemaName, Joi.object(this.convertJsonSchemaToJoi(schema)));
        }
      }

      console.log(`Loaded ${this.schemas.size} configuration schemas`);
    } catch (error) {
      console.warn('No schema directory found, skipping schema validation');
    }
  }

  async loadConfigurations() {
    const configFiles = [
      'global.yaml',
      'global.yml',
      `${this.environment}.yaml`,
      `${this.environment}.yml`,
      'local.yaml',
      'local.yml'
    ];

    for (const file of configFiles) {
      const configFile = path.join(this.configPath, file);

      try {
        const exists = await fs.access(configFile).then(() => true).catch(() => false);
        if (exists) {
          await this.loadConfigurationFile(configFile);
        }
      } catch (error) {
        console.warn(`Failed to load configuration file ${file}:`, error.message);
      }
    }

    // Merge and resolve configurations
    this.resolveConfiguration();
  }

  async loadConfigurationFile(filePath) {
    try {
      const content = await fs.readFile(filePath, 'utf8');
      const config = yaml.load(content);
      const fileName = path.basename(filePath, path.extname(filePath));

      this.configs.set(fileName, config);
      console.log(`Loaded configuration: ${fileName}`);
    } catch (error) {
      throw new Error(`Failed to load configuration file ${filePath}: ${error.message}`);
    }
  }

  resolveConfiguration() {
    // Configuration resolution order (highest to lowest priority):
    // 1. local
    // 2. environment-specific
    // 3. global

    const resolved = {};

    // Start with global config
    const globalConfig = this.configs.get('global') || {};
    this.deepMerge(resolved, globalConfig);

    // Apply environment-specific config
    const envConfig = this.configs.get(this.environment) || {};
    this.deepMerge(resolved, envConfig);

    // Apply local overrides
    const localConfig = this.configs.get('local') || {};
    this.deepMerge(resolved, localConfig);

    // Resolve environment variables
    this.resolvedConfig = this.resolveEnvironmentVariables(resolved);

    // Validate against schema
    this.validateConfiguration();

    // Cache the resolved configuration
    this.cache.set('resolved', {
      config: this.resolvedConfig,
      timestamp: Date.now()
    });
  }

  resolveEnvironmentVariables(config) {
    const resolved = JSON.parse(JSON.stringify(config));

    const resolveValue = (obj) => {
      for (const [key, value] of Object.entries(obj)) {
        if (typeof value === 'string' && value.startsWith('${') && value.endsWith('}')) {
          const envVar = value.slice(2, -1);
          const defaultValue = envVar.includes(':') ? envVar.split(':')[1] : undefined;
          const varName = envVar.includes(':') ? envVar.split(':')[0] : envVar;

          obj[key] = process.env[varName] || defaultValue || value;
        } else if (typeof value === 'object' && value !== null) {
          resolveValue(value);
        }
      }
    };

    resolveValue(resolved);
    return resolved;
  }

  validateConfiguration() {
    const schema = this.schemas.get('main') || this.schemas.get('config');

    if (schema) {
      const { error } = schema.validate(this.resolvedConfig);
      if (error) {
        throw new Error(`Configuration validation failed: ${error.message}`);
      }
    }
  }

  deepMerge(target, source) {
    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        if (!target[key]) target[key] = {};
        this.deepMerge(target[key], source[key]);
      } else {
        target[key] = source[key];
      }
    }
    return target;
  }

  setupFileWatchers() {
    const watcher = chokidar.watch(this.configPath, {
      persistent: true,
      ignoreInitial: true
    });

    watcher.on('change', async (filePath) => {
      console.log(`Configuration file changed: ${filePath}`);
      await this.reloadConfiguration();
    });

    watcher.on('add', async (filePath) => {
      console.log(`Configuration file added: ${filePath}`);
      await this.reloadConfiguration();
    });

    this.watchers.set('config', watcher);
  }

  async reloadConfiguration() {
    try {
      await this.loadConfigurations();
      this.notifyListeners('config:reload', this.resolvedConfig);
      console.log('Configuration reloaded successfully');
    } catch (error) {
      console.error('Failed to reload configuration:', error);
      this.notifyListeners('config:error', error);
    }
  }

  // Public API methods
  get(path, defaultValue = undefined) {
    return this.getConfigValue(this.resolvedConfig, path, defaultValue);
  }

  async getAsync(path, defaultValue = undefined) {
    // Check cache first
    const cached = this.cache.get(path);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.value;
    }

    // Get value and potentially resolve secrets
    let value = this.getConfigValue(this.resolvedConfig, path, defaultValue);

    // Resolve secrets if secretsManager is available
    if (this.secretsManager && typeof value === 'string' && value.startsWith('secret:')) {
      const secretPath = value.replace('secret:', '');
      value = await this.secretsManager.getSecret(secretPath);
    }

    // Cache the result
    this.cache.set(path, {
      value,
      timestamp: Date.now()
    });

    return value;
  }

  getConfigValue(config, path, defaultValue) {
    const keys = path.split('.');
    let current = config;

    for (const key of keys) {
      if (current && typeof current === 'object' && key in current) {
        current = current[key];
      } else {
        return defaultValue;
      }
    }

    return current;
  }

  set(path, value) {
    // Set runtime configuration override
    this.setConfigValue(this.resolvedConfig, path, value);
    this.notifyListeners('config:change', { path, value });
  }

  setConfigValue(config, path, value) {
    const keys = path.split('.');
    const lastKey = keys.pop();
    let current = config;

    for (const key of keys) {
      if (!current[key] || typeof current[key] !== 'object') {
        current[key] = {};
      }
      current = current[key];
    }

    current[lastKey] = value;
  }

  has(path) {
    return this.getConfigValue(this.resolvedConfig, path, Symbol('not-found')) !== Symbol('not-found');
  }

  getEnvironment() {
    return this.environment;
  }

  isFeatureEnabled(featureName) {
    return this.get(`features.${featureName}`, false);
  }

  // Project-specific configurations
  getProjectConfig(projectId, path = null) {
    const projectConfig = this.get(`projects.${projectId}`, {});

    if (path) {
      return this.getConfigValue(projectConfig, path);
    }

    return projectConfig;
  }

  setProjectConfig(projectId, config) {
    this.set(`projects.${projectId}`, config);
  }

  // User-specific configurations
  getUserConfig(userId, path = null) {
    const userConfig = this.get(`users.${userId}`, {});

    if (path) {
      return this.getConfigValue(userConfig, path);
    }

    return userConfig;
  }

  setUserConfig(userId, config) {
    this.set(`users.${userId}`, config);
  }

  // Event handling
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  notifyListeners(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in config listener for ${event}:`, error);
        }
      });
    }
  }

  // Utility methods
  convertJsonSchemaToJoi(jsonSchema) {
    // Simplified JSON Schema to Joi conversion
    // In a real implementation, this would be more comprehensive
    const convertProperty = (property) => {
      let joi;

      switch (property.type) {
        case 'string':
          joi = Joi.string();
          if (property.enum) joi = joi.valid(...property.enum);
          if (property.minLength) joi = joi.min(property.minLength);
          if (property.maxLength) joi = joi.max(property.maxLength);
          break;
        case 'number':
          joi = Joi.number();
          if (property.minimum !== undefined) joi = joi.min(property.minimum);
          if (property.maximum !== undefined) joi = joi.max(property.maximum);
          break;
        case 'integer':
          joi = Joi.number().integer();
          if (property.minimum !== undefined) joi = joi.min(property.minimum);
          if (property.maximum !== undefined) joi = joi.max(property.maximum);
          break;
        case 'boolean':
          joi = Joi.boolean();
          break;
        case 'array':
          joi = Joi.array();
          if (property.items) {
            joi = joi.items(convertProperty(property.items));
          }
          break;
        case 'object':
          joi = Joi.object();
          if (property.properties) {
            const keys = {};
            for (const [key, prop] of Object.entries(property.properties)) {
              keys[key] = convertProperty(prop);
            }
            joi = joi.keys(keys);
          }
          break;
        default:
          joi = Joi.any();
      }

      return joi;
    };

    return convertProperty(jsonSchema);
  }

  async shutdown() {
    // Close file watchers
    for (const watcher of this.watchers.values()) {
      await watcher.close();
    }

    // Shutdown secrets manager
    if (this.secretsManager) {
      await this.secretsManager.shutdown();
    }

    console.log('Configuration manager shut down');
  }
}

module.exports = ConfigurationManager;
```

## 3. Secrets Management

### Secure Secrets Manager
```javascript
// secrets-manager.js
const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');

class SecretsManager {
  constructor(options = {}) {
    this.provider = options.provider || 'file';
    this.encryptionKey = options.encryptionKey || process.env.SECRETS_ENCRYPTION_KEY;
    this.secretsPath = options.secretsPath || './secrets';
    this.vault = new Map();
    this.providers = {
      file: new FileSecretsProvider(this),
      aws: new AWSSecretsProvider(this),
      azure: new AzureSecretsProvider(this),
      vault: new HashiCorpVaultProvider(this)
    };
  }

  async initialize() {
    if (!this.encryptionKey) {
      throw new Error('Encryption key required for secrets management');
    }

    const provider = this.providers[this.provider];
    if (!provider) {
      throw new Error(`Unknown secrets provider: ${this.provider}`);
    }

    await provider.initialize();
    console.log(`Secrets manager initialized with provider: ${this.provider}`);
  }

  async getSecret(secretPath) {
    // Check cache first
    if (this.vault.has(secretPath)) {
      const cached = this.vault.get(secretPath);
      if (Date.now() - cached.timestamp < 300000) { // 5 minute cache
        return cached.value;
      }
    }

    // Fetch from provider
    const provider = this.providers[this.provider];
    const encryptedValue = await provider.getSecret(secretPath);

    if (!encryptedValue) {
      throw new Error(`Secret not found: ${secretPath}`);
    }

    // Decrypt and cache
    const decryptedValue = this.decrypt(encryptedValue);
    this.vault.set(secretPath, {
      value: decryptedValue,
      timestamp: Date.now()
    });

    return decryptedValue;
  }

  async setSecret(secretPath, value) {
    const encryptedValue = this.encrypt(value);
    const provider = this.providers[this.provider];

    await provider.setSecret(secretPath, encryptedValue);

    // Update cache
    this.vault.set(secretPath, {
      value,
      timestamp: Date.now()
    });
  }

  async deleteSecret(secretPath) {
    const provider = this.providers[this.provider];
    await provider.deleteSecret(secretPath);

    // Remove from cache
    this.vault.delete(secretPath);
  }

  encrypt(value) {
    const algorithm = 'aes-256-gcm';
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher(algorithm, this.encryptionKey);

    let encrypted = cipher.update(value, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const authTag = cipher.getAuthTag();

    return {
      encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex')
    };
  }

  decrypt(encryptedData) {
    const algorithm = 'aes-256-gcm';
    const decipher = crypto.createDecipher(algorithm, this.encryptionKey);

    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));

    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }

  async shutdown() {
    const provider = this.providers[this.provider];
    if (provider.shutdown) {
      await provider.shutdown();
    }

    // Clear cache
    this.vault.clear();
  }
}

class FileSecretsProvider {
  constructor(secretsManager) {
    this.secretsManager = secretsManager;
    this.secretsPath = secretsManager.secretsPath;
  }

  async initialize() {
    try {
      await fs.access(this.secretsPath);
    } catch {
      await fs.mkdir(this.secretsPath, { recursive: true });
    }
  }

  async getSecret(secretPath) {
    const filePath = path.join(this.secretsPath, `${secretPath}.json`);

    try {
      const content = await fs.readFile(filePath, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      if (error.code === 'ENOENT') {
        return null;
      }
      throw error;
    }
  }

  async setSecret(secretPath, encryptedValue) {
    const filePath = path.join(this.secretsPath, `${secretPath}.json`);
    const dir = path.dirname(filePath);

    await fs.mkdir(dir, { recursive: true });
    await fs.writeFile(filePath, JSON.stringify(encryptedValue, null, 2));
  }

  async deleteSecret(secretPath) {
    const filePath = path.join(this.secretsPath, `${secretPath}.json`);

    try {
      await fs.unlink(filePath);
    } catch (error) {
      if (error.code !== 'ENOENT') {
        throw error;
      }
    }
  }
}

class AWSSecretsProvider {
  constructor(secretsManager) {
    this.secretsManager = secretsManager;
    this.client = null;
  }

  async initialize() {
    const { SecretsManagerClient } = require('@aws-sdk/client-secrets-manager');
    this.client = new SecretsManagerClient({
      region: process.env.AWS_REGION || 'us-east-1'
    });
  }

  async getSecret(secretPath) {
    const { GetSecretValueCommand } = require('@aws-sdk/client-secrets-manager');

    try {
      const command = new GetSecretValueCommand({
        SecretId: secretPath
      });

      const response = await this.client.send(command);
      return JSON.parse(response.SecretString);
    } catch (error) {
      if (error.name === 'ResourceNotFoundException') {
        return null;
      }
      throw error;
    }
  }

  async setSecret(secretPath, encryptedValue) {
    const { CreateSecretCommand, UpdateSecretCommand } = require('@aws-sdk/client-secrets-manager');

    try {
      // Try to update existing secret
      const updateCommand = new UpdateSecretCommand({
        SecretId: secretPath,
        SecretString: JSON.stringify(encryptedValue)
      });

      await this.client.send(updateCommand);
    } catch (error) {
      if (error.name === 'ResourceNotFoundException') {
        // Create new secret
        const createCommand = new CreateSecretCommand({
          Name: secretPath,
          SecretString: JSON.stringify(encryptedValue)
        });

        await this.client.send(createCommand);
      } else {
        throw error;
      }
    }
  }

  async deleteSecret(secretPath) {
    const { DeleteSecretCommand } = require('@aws-sdk/client-secrets-manager');

    try {
      const command = new DeleteSecretCommand({
        SecretId: secretPath,
        ForceDeleteWithoutRecovery: true
      });

      await this.client.send(command);
    } catch (error) {
      if (error.name !== 'ResourceNotFoundException') {
        throw error;
      }
    }
  }
}

module.exports = { SecretsManager, FileSecretsProvider, AWSSecretsProvider };
```

## 4. Dynamic Configuration Updates

### Configuration Update API
```javascript
// config-api.js
const express = require('express');
const router = express.Router();

class ConfigurationAPI {
  constructor(configManager, authService) {
    this.configManager = configManager;
    this.authService = authService;
    this.setupRoutes();
  }

  setupRoutes() {
    // Get configuration
    router.get('/config',
      this.authService.authenticate,
      this.authService.requirePermission('config:read'),
      this.getConfiguration.bind(this)
    );

    // Get specific configuration path
    router.get('/config/*',
      this.authService.authenticate,
      this.authService.requirePermission('config:read'),
      this.getConfigurationPath.bind(this)
    );

    // Update configuration
    router.put('/config/*',
      this.authService.authenticate,
      this.authService.requirePermission('config:write'),
      this.updateConfiguration.bind(this)
    );

    // Get project configuration
    router.get('/projects/:projectId/config',
      this.authService.authenticate,
      this.authService.requireProjectAccess('read'),
      this.getProjectConfiguration.bind(this)
    );

    // Update project configuration
    router.put('/projects/:projectId/config',
      this.authService.authenticate,
      this.authService.requireProjectAccess('write'),
      this.updateProjectConfiguration.bind(this)
    );

    // Reload configuration
    router.post('/config/reload',
      this.authService.authenticate,
      this.authService.requirePermission('config:admin'),
      this.reloadConfiguration.bind(this)
    );

    // Validate configuration
    router.post('/config/validate',
      this.authService.authenticate,
      this.authService.requirePermission('config:write'),
      this.validateConfiguration.bind(this)
    );
  }

  async getConfiguration(req, res) {
    try {
      // Filter sensitive configuration for non-admin users
      const config = this.filterSensitiveConfig(
        this.configManager.resolvedConfig,
        req.user
      );

      res.json({
        environment: this.configManager.getEnvironment(),
        config
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async getConfigurationPath(req, res) {
    try {
      const configPath = req.params[0]; // Everything after /config/
      const value = this.configManager.get(configPath);

      if (value === undefined) {
        return res.status(404).json({ error: 'Configuration path not found' });
      }

      // Check if user can access this configuration
      if (this.isSensitiveConfig(configPath) && !this.isAdmin(req.user)) {
        return res.status(403).json({ error: 'Access denied to sensitive configuration' });
      }

      res.json({
        path: configPath,
        value
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async updateConfiguration(req, res) {
    try {
      const configPath = req.params[0];
      const { value } = req.body;

      // Validate the new value
      await this.validateConfigurationValue(configPath, value);

      // Update configuration
      this.configManager.set(configPath, value);

      // Log the change
      console.log(`Configuration updated by ${req.user.id}: ${configPath} = ${JSON.stringify(value)}`);

      res.json({
        path: configPath,
        value,
        updated_by: req.user.id,
        updated_at: new Date().toISOString()
      });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }

  async getProjectConfiguration(req, res) {
    try {
      const { projectId } = req.params;
      const config = this.configManager.getProjectConfig(projectId);

      res.json({
        project_id: projectId,
        config
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async updateProjectConfiguration(req, res) {
    try {
      const { projectId } = req.params;
      const { config } = req.body;

      // Validate project configuration
      await this.validateProjectConfiguration(config);

      // Update configuration
      this.configManager.setProjectConfig(projectId, config);

      // Log the change
      console.log(`Project configuration updated by ${req.user.id}: ${projectId}`);

      res.json({
        project_id: projectId,
        config,
        updated_by: req.user.id,
        updated_at: new Date().toISOString()
      });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }

  async reloadConfiguration(req, res) {
    try {
      await this.configManager.reloadConfiguration();

      res.json({
        message: 'Configuration reloaded successfully',
        reloaded_at: new Date().toISOString(),
        reloaded_by: req.user.id
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async validateConfiguration(req, res) {
    try {
      const { config } = req.body;

      // Validate against schema
      const schema = this.configManager.schemas.get('main');
      if (schema) {
        const { error } = schema.validate(config);
        if (error) {
          return res.status(400).json({
            valid: false,
            errors: [error.message]
          });
        }
      }

      res.json({
        valid: true,
        message: 'Configuration is valid'
      });
    } catch (error) {
      res.status(400).json({
        valid: false,
        errors: [error.message]
      });
    }
  }

  filterSensitiveConfig(config, user) {
    if (this.isAdmin(user)) {
      return config;
    }

    // Remove sensitive configuration for non-admin users
    const filtered = JSON.parse(JSON.stringify(config));

    // Remove database passwords, API keys, etc.
    const sensitiveFields = ['password', 'secret', 'key', 'token'];

    const filterObject = (obj, path = '') => {
      for (const [key, value] of Object.entries(obj)) {
        const currentPath = path ? `${path}.${key}` : key;

        if (sensitiveFields.some(field => key.toLowerCase().includes(field))) {
          obj[key] = '[REDACTED]';
        } else if (typeof value === 'object' && value !== null) {
          filterObject(value, currentPath);
        }
      }
    };

    filterObject(filtered);
    return filtered;
  }

  isSensitiveConfig(configPath) {
    const sensitivePatterns = [
      /password/i,
      /secret/i,
      /key/i,
      /token/i,
      /credential/i
    ];

    return sensitivePatterns.some(pattern => pattern.test(configPath));
  }

  isAdmin(user) {
    return user.type === 'admin' || user.permissions?.includes('admin');
  }

  async validateConfigurationValue(path, value) {
    // Implement specific validation rules based on configuration path
    // This is a simplified example

    if (path.includes('port') && (typeof value !== 'number' || value < 1024 || value > 65535)) {
      throw new Error('Port must be a number between 1024 and 65535');
    }

    if (path.includes('percentage') && (typeof value !== 'number' || value < 0 || value > 100)) {
      throw new Error('Percentage must be a number between 0 and 100');
    }

    if (path.includes('timeout') && (typeof value !== 'number' || value < 0)) {
      throw new Error('Timeout must be a positive number');
    }
  }

  async validateProjectConfiguration(config) {
    // Validate project-specific configuration
    if (config.thresholds) {
      const { execution, coverage } = config.thresholds;

      if (execution?.pass_rate_min_percentage !== undefined) {
        if (typeof execution.pass_rate_min_percentage !== 'number' ||
            execution.pass_rate_min_percentage < 0 ||
            execution.pass_rate_min_percentage > 100) {
          throw new Error('Pass rate must be between 0 and 100');
        }
      }

      if (coverage?.line_coverage_min !== undefined) {
        if (typeof coverage.line_coverage_min !== 'number' ||
            coverage.line_coverage_min < 0 ||
            coverage.line_coverage_min > 100) {
          throw new Error('Line coverage must be between 0 and 100');
        }
      }
    }
  }

  getRoutes() {
    return router;
  }
}

module.exports = ConfigurationAPI;
```

This comprehensive configuration management system provides hierarchical configuration resolution, secure secrets management, dynamic updates, validation, and environment-aware settings to support all aspects of the Test Baseline Tracking System.