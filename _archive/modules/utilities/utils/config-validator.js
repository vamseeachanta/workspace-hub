#!/usr/bin/env node

/**
 * Configuration Validator for Baseline Testing CI/CD
 * Validates all configuration files and environment settings
 */

const fs = require('fs');
const path = require('path');
const { URL } = require('url');

class ConfigValidator {
    constructor() {
        this.errors = [];
        this.warnings = [];
        this.validations = 0;
    }

    /**
     * Add error to validation results
     */
    addError(message, context = {}) {
        this.errors.push({ message, context, type: 'error' });
    }

    /**
     * Add warning to validation results
     */
    addWarning(message, context = {}) {
        this.warnings.push({ message, context, type: 'warning' });
    }

    /**
     * Validate all baseline testing configurations
     */
    async validateAll() {
        console.log('🔍 Starting comprehensive configuration validation...\n');

        // Validate project structure
        this.validateProjectStructure();

        // Validate GitHub Actions workflows
        this.validateGitHubActions();

        // Validate pre-commit configuration
        this.validatePreCommitConfig();

        // Validate Docker configuration
        this.validateDockerConfig();

        // Validate CI/CD pipeline configurations
        this.validateCIPipelines();

        // Validate notification configurations
        await this.validateNotificationConfig();

        // Validate environment variables
        this.validateEnvironmentVariables();

        // Validate package.json scripts
        this.validatePackageJsonScripts();

        // Generate validation report
        this.generateReport();

        return {
            valid: this.errors.length === 0,
            errors: this.errors,
            warnings: this.warnings,
            validations: this.validations
        };
    }

    /**
     * Validate project structure
     */
    validateProjectStructure() {
        console.log('📁 Validating project structure...');

        const requiredPaths = [
            '.github/workflows',
            'scripts/hooks',
            'scripts/ci',
            'scripts/notifications',
            'scripts/utils',
            'docker'
        ];

        const requiredFiles = [
            '.pre-commit-config.yaml',
            '.github/workflows/baseline-check.yml',
            '.github/workflows/baseline-audit.yml',
            'docker/Dockerfile.baseline-test',
            'docker/docker-compose.baseline.yml',
            'scripts/hooks/baseline-validation.sh',
            'scripts/notifications/webhook-manager.js',
            'scripts/utils/error-handler.js'
        ];

        // Check directories
        requiredPaths.forEach(dirPath => {
            this.validations++;
            if (!fs.existsSync(dirPath)) {
                this.addError(`Required directory missing: ${dirPath}`, { type: 'directory' });
            } else if (!fs.statSync(dirPath).isDirectory()) {
                this.addError(`Path exists but is not a directory: ${dirPath}`, { type: 'directory' });
            }
        });

        // Check files
        requiredFiles.forEach(filePath => {
            this.validations++;
            if (!fs.existsSync(filePath)) {
                this.addError(`Required file missing: ${filePath}`, { type: 'file' });
            } else if (!fs.statSync(filePath).isFile()) {
                this.addError(`Path exists but is not a file: ${filePath}`, { type: 'file' });
            }
        });

        // Check script permissions
        const scripts = [
            'scripts/hooks/baseline-validation.sh',
            'scripts/hooks/baseline-quick-check.sh',
            'scripts/hooks/baseline-auto-fix.sh'
        ];

        scripts.forEach(script => {
            this.validations++;
            if (fs.existsSync(script)) {
                try {
                    fs.accessSync(script, fs.constants.X_OK);
                } catch (error) {
                    this.addWarning(`Script not executable: ${script}`, { type: 'permission' });
                }
            }
        });
    }

    /**
     * Validate GitHub Actions workflows
     */
    validateGitHubActions() {
        console.log('⚡ Validating GitHub Actions workflows...');

        const workflows = [
            '.github/workflows/baseline-check.yml',
            '.github/workflows/baseline-audit.yml'
        ];

        workflows.forEach(workflow => {
            this.validations++;
            if (fs.existsSync(workflow)) {
                try {
                    const content = fs.readFileSync(workflow, 'utf8');

                    // Basic YAML validation (check for common issues)
                    if (!content.includes('name:')) {
                        this.addError(`Workflow missing name field: ${workflow}`, { type: 'yaml' });
                    }

                    if (!content.includes('on:')) {
                        this.addError(`Workflow missing trigger configuration: ${workflow}`, { type: 'yaml' });
                    }

                    if (!content.includes('jobs:')) {
                        this.addError(`Workflow missing jobs configuration: ${workflow}`, { type: 'yaml' });
                    }

                    // Check for required environment variables
                    const requiredEnvVars = ['NODE_VERSION', 'BASELINE_THRESHOLD'];
                    requiredEnvVars.forEach(envVar => {
                        if (!content.includes(envVar)) {
                            this.addWarning(`Workflow missing environment variable: ${envVar} in ${workflow}`, { type: 'env' });
                        }
                    });

                    // Check for security best practices
                    if (content.includes('${{ secrets.GITHUB_TOKEN }}')) {
                        // Good practice
                    } else if (content.includes('github.token')) {
                        this.addWarning(`Consider using secrets.GITHUB_TOKEN in ${workflow}`, { type: 'security' });
                    }

                } catch (error) {
                    this.addError(`Failed to read workflow file: ${workflow}`, { error: error.message });
                }
            }
        });
    }

    /**
     * Validate pre-commit configuration
     */
    validatePreCommitConfig() {
        console.log('🪝 Validating pre-commit configuration...');

        const preCommitFile = '.pre-commit-config.yaml';
        this.validations++;

        if (fs.existsSync(preCommitFile)) {
            try {
                const content = fs.readFileSync(preCommitFile, 'utf8');

                // Check for required hooks
                const requiredHooks = ['baseline-validation', 'baseline-quick-check'];
                requiredHooks.forEach(hook => {
                    if (!content.includes(hook)) {
                        this.addError(`Pre-commit missing required hook: ${hook}`, { type: 'hook' });
                    }
                });

                // Check for hook script files
                const hookScripts = content.match(/entry:\s*scripts\/hooks\/[\w-]+\.sh/g) || [];
                hookScripts.forEach(match => {
                    const scriptPath = match.replace('entry:', '').trim();
                    this.validations++;
                    if (!fs.existsSync(scriptPath)) {
                        this.addError(`Hook script missing: ${scriptPath}`, { type: 'hook-script' });
                    }
                });

            } catch (error) {
                this.addError(`Failed to read pre-commit config: ${preCommitFile}`, { error: error.message });
            }
        }
    }

    /**
     * Validate Docker configuration
     */
    validateDockerConfig() {
        console.log('🐳 Validating Docker configuration...');

        const dockerFiles = [
            'docker/Dockerfile.baseline-test',
            'docker/docker-compose.baseline.yml'
        ];

        dockerFiles.forEach(dockerFile => {
            this.validations++;
            if (fs.existsSync(dockerFile)) {
                try {
                    const content = fs.readFileSync(dockerFile, 'utf8');

                    if (dockerFile.includes('Dockerfile')) {
                        // Validate Dockerfile
                        if (!content.includes('FROM')) {
                            this.addError(`Dockerfile missing FROM instruction: ${dockerFile}`, { type: 'dockerfile' });
                        }

                        if (!content.includes('WORKDIR')) {
                            this.addWarning(`Dockerfile missing WORKDIR instruction: ${dockerFile}`, { type: 'dockerfile' });
                        }

                        // Check for security best practices
                        if (content.includes('USER root')) {
                            this.addWarning(`Dockerfile running as root user: ${dockerFile}`, { type: 'security' });
                        }

                        if (!content.includes('USER ') && !content.includes('USER root')) {
                            this.addWarning(`Dockerfile not setting user: ${dockerFile}`, { type: 'security' });
                        }

                    } else if (dockerFile.includes('docker-compose')) {
                        // Validate docker-compose
                        if (!content.includes('version:')) {
                            this.addError(`Docker Compose missing version: ${dockerFile}`, { type: 'compose' });
                        }

                        if (!content.includes('services:')) {
                            this.addError(`Docker Compose missing services: ${dockerFile}`, { type: 'compose' });
                        }

                        // Check for required services
                        const requiredServices = ['baseline-test'];
                        requiredServices.forEach(service => {
                            if (!content.includes(`${service}:`)) {
                                this.addWarning(`Docker Compose missing service: ${service}`, { type: 'compose' });
                            }
                        });
                    }

                } catch (error) {
                    this.addError(`Failed to read Docker file: ${dockerFile}`, { error: error.message });
                }
            }
        });
    }

    /**
     * Validate CI/CD pipeline configurations
     */
    validateCIPipelines() {
        console.log('🔄 Validating CI/CD pipelines...');

        const pipelines = [
            { file: 'scripts/ci/jenkins/Jenkinsfile', type: 'jenkins' },
            { file: 'scripts/ci/gitlab/.gitlab-ci.yml', type: 'gitlab' },
            { file: 'scripts/ci/circleci/config.yml', type: 'circleci' },
            { file: 'scripts/ci/azure/azure-pipelines.yml', type: 'azure' }
        ];

        pipelines.forEach(({ file, type }) => {
            this.validations++;
            if (fs.existsSync(file)) {
                try {
                    const content = fs.readFileSync(file, 'utf8');

                    switch (type) {
                        case 'jenkins':
                            if (!content.includes('pipeline {')) {
                                this.addError(`Jenkins pipeline missing pipeline block: ${file}`, { type: 'jenkins' });
                            }
                            if (!content.includes('stages {')) {
                                this.addError(`Jenkins pipeline missing stages: ${file}`, { type: 'jenkins' });
                            }
                            break;

                        case 'gitlab':
                            if (!content.includes('stages:')) {
                                this.addError(`GitLab CI missing stages: ${file}`, { type: 'gitlab' });
                            }
                            if (!content.includes('image:')) {
                                this.addWarning(`GitLab CI missing default image: ${file}`, { type: 'gitlab' });
                            }
                            break;

                        case 'circleci':
                            if (!content.includes('version:')) {
                                this.addError(`CircleCI config missing version: ${file}`, { type: 'circleci' });
                            }
                            if (!content.includes('workflows:')) {
                                this.addError(`CircleCI config missing workflows: ${file}`, { type: 'circleci' });
                            }
                            break;

                        case 'azure':
                            if (!content.includes('trigger:')) {
                                this.addWarning(`Azure pipeline missing trigger: ${file}`, { type: 'azure' });
                            }
                            if (!content.includes('stages:')) {
                                this.addError(`Azure pipeline missing stages: ${file}`, { type: 'azure' });
                            }
                            break;
                    }

                    // Common validations
                    if (!content.includes('baseline')) {
                        this.addWarning(`Pipeline might not be configured for baseline testing: ${file}`, { type: 'baseline' });
                    }

                } catch (error) {
                    this.addError(`Failed to read pipeline file: ${file}`, { error: error.message });
                }
            }
        });
    }

    /**
     * Validate notification configurations
     */
    async validateNotificationConfig() {
        console.log('🔔 Validating notification configurations...');

        const notificationFiles = [
            'scripts/notifications/webhook-manager.js',
            'scripts/notifications/email-notifier.py'
        ];

        notificationFiles.forEach(file => {
            this.validations++;
            if (fs.existsSync(file)) {
                try {
                    const content = fs.readFileSync(file, 'utf8');

                    if (file.includes('webhook-manager')) {
                        // Validate webhook manager
                        if (!content.includes('sendSlackNotification')) {
                            this.addWarning(`Webhook manager missing Slack support: ${file}`, { type: 'webhook' });
                        }
                        if (!content.includes('sendDiscordNotification')) {
                            this.addWarning(`Webhook manager missing Discord support: ${file}`, { type: 'webhook' });
                        }
                    }

                    if (file.includes('email-notifier')) {
                        // Validate email notifier
                        if (!content.includes('smtplib')) {
                            this.addError(`Email notifier missing SMTP support: ${file}`, { type: 'email' });
                        }
                        if (!content.includes('Template')) {
                            this.addWarning(`Email notifier missing template support: ${file}`, { type: 'email' });
                        }
                    }

                } catch (error) {
                    this.addError(`Failed to read notification file: ${file}`, { error: error.message });
                }
            }
        });

        // Check for webhook configuration file
        const webhookConfig = 'webhook-config.json';
        if (fs.existsSync(webhookConfig)) {
            try {
                const config = JSON.parse(fs.readFileSync(webhookConfig, 'utf8'));
                this.validations++;

                if (!config.webhooks || !Array.isArray(config.webhooks)) {
                    this.addWarning('Webhook config missing webhooks array', { type: 'config' });
                } else {
                    config.webhooks.forEach((webhook, index) => {
                        this.validations++;
                        if (!webhook.url) {
                            this.addError(`Webhook ${index} missing URL`, { type: 'webhook-config' });
                        } else {
                            try {
                                new URL(webhook.url);
                            } catch (error) {
                                this.addError(`Webhook ${index} has invalid URL: ${webhook.url}`, { type: 'webhook-config' });
                            }
                        }

                        if (!webhook.type) {
                            this.addWarning(`Webhook ${index} missing type`, { type: 'webhook-config' });
                        }
                    });
                }
            } catch (error) {
                this.addError(`Invalid webhook configuration: ${webhookConfig}`, { error: error.message });
            }
        }
    }

    /**
     * Validate environment variables
     */
    validateEnvironmentVariables() {
        console.log('🌍 Validating environment variables...');

        const requiredEnvVars = [
            'NODE_ENV',
            'BASELINE_LOG_LEVEL',
            'BASELINE_THRESHOLD'
        ];

        const optionalEnvVars = [
            'SLACK_WEBHOOK_URL',
            'DISCORD_WEBHOOK_URL',
            'SMTP_HOST',
            'SMTP_USER',
            'SMTP_PASS'
        ];

        requiredEnvVars.forEach(envVar => {
            this.validations++;
            if (!process.env[envVar]) {
                this.addWarning(`Required environment variable not set: ${envVar}`, { type: 'env' });
            }
        });

        optionalEnvVars.forEach(envVar => {
            this.validations++;
            if (!process.env[envVar]) {
                // Just log for information, not a warning
                console.log(`  ℹ️ Optional environment variable not set: ${envVar}`);
            }
        });

        // Validate specific environment variable formats
        if (process.env.BASELINE_THRESHOLD) {
            const threshold = parseInt(process.env.BASELINE_THRESHOLD);
            if (isNaN(threshold) || threshold < 0 || threshold > 100) {
                this.addError('BASELINE_THRESHOLD must be a number between 0 and 100', { type: 'env-validation' });
            }
        }

        if (process.env.SLACK_WEBHOOK_URL) {
            try {
                new URL(process.env.SLACK_WEBHOOK_URL);
            } catch (error) {
                this.addError('SLACK_WEBHOOK_URL is not a valid URL', { type: 'env-validation' });
            }
        }
    }

    /**
     * Validate package.json scripts
     */
    validatePackageJsonScripts() {
        console.log('📦 Validating package.json scripts...');

        if (fs.existsSync('package.json')) {
            try {
                const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
                const scripts = packageJson.scripts || {};

                const requiredScripts = [
                    'test:baseline:unit',
                    'test:baseline:integration',
                    'test:baseline:performance',
                    'test:baseline:security',
                    'lint:check',
                    'lint:fix'
                ];

                requiredScripts.forEach(script => {
                    this.validations++;
                    if (!scripts[script]) {
                        this.addWarning(`Package.json missing script: ${script}`, { type: 'npm-script' });
                    }
                });

                // Check for common script patterns
                Object.keys(scripts).forEach(script => {
                    const command = scripts[script];
                    if (command.includes('baseline') && !command.includes('test')) {
                        this.addWarning(`Baseline script might not be a test: ${script}`, { type: 'npm-script' });
                    }
                });

            } catch (error) {
                this.addError('Failed to parse package.json', { error: error.message });
            }
        } else {
            this.addError('package.json not found', { type: 'package' });
        }
    }

    /**
     * Generate validation report
     */
    generateReport() {
        console.log('\n📊 Validation Report');
        console.log('='.repeat(50));

        console.log(`\n✅ Validations performed: ${this.validations}`);
        console.log(`❌ Errors found: ${this.errors.length}`);
        console.log(`⚠️  Warnings found: ${this.warnings.length}`);

        if (this.errors.length > 0) {
            console.log('\n❌ ERRORS:');
            this.errors.forEach((error, index) => {
                console.log(`  ${index + 1}. ${error.message}`);
                if (error.context.type) {
                    console.log(`     Type: ${error.context.type}`);
                }
            });
        }

        if (this.warnings.length > 0) {
            console.log('\n⚠️  WARNINGS:');
            this.warnings.forEach((warning, index) => {
                console.log(`  ${index + 1}. ${warning.message}`);
                if (warning.context.type) {
                    console.log(`     Type: ${warning.context.type}`);
                }
            });
        }

        if (this.errors.length === 0 && this.warnings.length === 0) {
            console.log('\n🎉 All validations passed! Configuration looks good.');
        }

        // Save detailed report
        const report = {
            timestamp: new Date().toISOString(),
            summary: {
                validations: this.validations,
                errors: this.errors.length,
                warnings: this.warnings.length,
                valid: this.errors.length === 0
            },
            errors: this.errors,
            warnings: this.warnings
        };

        const reportPath = '.baseline-cache/validation-report.json';
        try {
            fs.mkdirSync(path.dirname(reportPath), { recursive: true });
            fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
            console.log(`\n📄 Detailed report saved to: ${reportPath}`);
        } catch (error) {
            console.error('Failed to save validation report:', error.message);
        }
    }
}

// CLI interface
if (require.main === module) {
    const validator = new ConfigValidator();
    validator.validateAll().then(result => {
        process.exit(result.valid ? 0 : 1);
    }).catch(error => {
        console.error('Validation failed:', error.message);
        process.exit(1);
    });
}

module.exports = ConfigValidator;