#!/usr/bin/env node

/**
 * Webhook Manager for Baseline Testing Notifications
 * Supports multiple notification channels with retry logic and error handling
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

class WebhookManager {
    constructor(config = {}) {
        this.config = {
            maxRetries: 3,
            retryDelay: 1000, // Start with 1 second
            timeout: 10000, // 10 seconds
            logLevel: 'INFO',
            logFile: '.baseline-cache/logs/webhook.log',
            ...config
        };

        this.retryDelayMultiplier = 2;
        this.maxRetryDelay = 30000; // 30 seconds

        this.ensureLogDirectory();
    }

    /**
     * Ensure log directory exists
     */
    ensureLogDirectory() {
        const logDir = path.dirname(this.config.logFile);
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
    }

    /**
     * Log message with timestamp
     */
    log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = `[${timestamp}] [${level}] ${message}`;

        if (this.config.logLevel === 'DEBUG' ||
            (this.config.logLevel === 'INFO' && level !== 'DEBUG') ||
            (this.config.logLevel === 'WARN' && ['WARN', 'ERROR'].includes(level)) ||
            (this.config.logLevel === 'ERROR' && level === 'ERROR')) {

            console.log(logEntry);

            if (data) {
                console.log(JSON.stringify(data, null, 2));
            }
        }

        // Always write to log file
        try {
            const logLine = data ? `${logEntry}\n${JSON.stringify(data, null, 2)}\n` : `${logEntry}\n`;
            fs.appendFileSync(this.config.logFile, logLine);
        } catch (error) {
            console.error('Failed to write to log file:', error.message);
        }
    }

    /**
     * Send Slack notification
     */
    async sendSlackNotification(webhookUrl, payload) {
        const slackPayload = this.formatSlackPayload(payload);
        return this.sendWebhook(webhookUrl, slackPayload, 'Slack');
    }

    /**
     * Send Discord notification
     */
    async sendDiscordNotification(webhookUrl, payload) {
        const discordPayload = this.formatDiscordPayload(payload);
        return this.sendWebhook(webhookUrl, discordPayload, 'Discord');
    }

    /**
     * Send Microsoft Teams notification
     */
    async sendTeamsNotification(webhookUrl, payload) {
        const teamsPayload = this.formatTeamsPayload(payload);
        return this.sendWebhook(webhookUrl, teamsPayload, 'Teams');
    }

    /**
     * Send generic webhook
     */
    async sendWebhook(url, payload, service = 'Generic') {
        return new Promise((resolve, reject) => {
            this.sendWebhookWithRetry(url, payload, service, 0, resolve, reject);
        });
    }

    /**
     * Send webhook with retry logic
     */
    sendWebhookWithRetry(url, payload, service, attempt, resolve, reject) {
        this.log('INFO', `Sending ${service} notification (attempt ${attempt + 1}/${this.config.maxRetries + 1})`);

        const urlObject = new URL(url);
        const isHttps = urlObject.protocol === 'https:';
        const client = isHttps ? https : http;

        const postData = JSON.stringify(payload);
        const options = {
            hostname: urlObject.hostname,
            port: urlObject.port || (isHttps ? 443 : 80),
            path: urlObject.pathname + urlObject.search,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData),
                'User-Agent': 'Baseline-Testing-Webhook/1.0'
            },
            timeout: this.config.timeout
        };

        const req = client.request(options, (res) => {
            let responseData = '';

            res.on('data', (chunk) => {
                responseData += chunk;
            });

            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    this.log('INFO', `${service} notification sent successfully`, {
                        statusCode: res.statusCode,
                        response: responseData
                    });
                    resolve({
                        success: true,
                        statusCode: res.statusCode,
                        response: responseData,
                        service: service,
                        attempt: attempt + 1
                    });
                } else {
                    this.log('WARN', `${service} notification failed with status ${res.statusCode}`, {
                        statusCode: res.statusCode,
                        response: responseData
                    });

                    if (attempt < this.config.maxRetries) {
                        this.scheduleRetry(url, payload, service, attempt + 1, resolve, reject);
                    } else {
                        reject(new Error(`${service} notification failed after ${this.config.maxRetries + 1} attempts. Status: ${res.statusCode}`));
                    }
                }
            });
        });

        req.on('error', (error) => {
            this.log('ERROR', `${service} notification error`, { error: error.message });

            if (attempt < this.config.maxRetries) {
                this.scheduleRetry(url, payload, service, attempt + 1, resolve, reject);
            } else {
                reject(new Error(`${service} notification failed after ${this.config.maxRetries + 1} attempts: ${error.message}`));
            }
        });

        req.on('timeout', () => {
            req.destroy();
            this.log('WARN', `${service} notification timeout`);

            if (attempt < this.config.maxRetries) {
                this.scheduleRetry(url, payload, service, attempt + 1, resolve, reject);
            } else {
                reject(new Error(`${service} notification timed out after ${this.config.maxRetries + 1} attempts`));
            }
        });

        req.write(postData);
        req.end();
    }

    /**
     * Schedule retry with exponential backoff
     */
    scheduleRetry(url, payload, service, attempt, resolve, reject) {
        const delay = Math.min(
            this.config.retryDelay * Math.pow(this.retryDelayMultiplier, attempt - 1),
            this.maxRetryDelay
        );

        this.log('INFO', `Retrying ${service} notification in ${delay}ms`);

        setTimeout(() => {
            this.sendWebhookWithRetry(url, payload, service, attempt, resolve, reject);
        }, delay);
    }

    /**
     * Format payload for Slack
     */
    formatSlackPayload(payload) {
        const { status, score, testSuite, buildNumber, branch, commitHash, buildUrl, details } = payload;

        const color = status === 'PASS' ? 'good' : status === 'UNSTABLE' ? 'warning' : 'danger';
        const emoji = status === 'PASS' ? '✅' : status === 'UNSTABLE' ? '⚠️' : '❌';

        return {
            text: `${emoji} Baseline Tests ${status}`,
            attachments: [
                {
                    color: color,
                    fields: [
                        {
                            title: 'Score',
                            value: `${score}%`,
                            short: true
                        },
                        {
                            title: 'Test Suite',
                            value: testSuite || 'all',
                            short: true
                        },
                        {
                            title: 'Build',
                            value: buildNumber || 'N/A',
                            short: true
                        },
                        {
                            title: 'Branch',
                            value: branch || 'unknown',
                            short: true
                        }
                    ],
                    actions: buildUrl ? [
                        {
                            type: 'button',
                            text: 'View Build',
                            url: buildUrl
                        }
                    ] : [],
                    footer: 'Baseline Testing System',
                    ts: Math.floor(Date.now() / 1000)
                }
            ]
        };
    }

    /**
     * Format payload for Discord
     */
    formatDiscordPayload(payload) {
        const { status, score, testSuite, buildNumber, branch, commitHash, buildUrl, details } = payload;

        const color = status === 'PASS' ? 0x00ff00 : status === 'UNSTABLE' ? 0xffff00 : 0xff0000;
        const emoji = status === 'PASS' ? '✅' : status === 'UNSTABLE' ? '⚠️' : '❌';

        return {
            embeds: [
                {
                    title: `${emoji} Baseline Tests ${status}`,
                    color: color,
                    fields: [
                        {
                            name: 'Score',
                            value: `${score}%`,
                            inline: true
                        },
                        {
                            name: 'Test Suite',
                            value: testSuite || 'all',
                            inline: true
                        },
                        {
                            name: 'Build',
                            value: buildNumber || 'N/A',
                            inline: true
                        },
                        {
                            name: 'Branch',
                            value: branch || 'unknown',
                            inline: true
                        }
                    ],
                    footer: {
                        text: 'Baseline Testing System'
                    },
                    timestamp: new Date().toISOString(),
                    url: buildUrl
                }
            ]
        };
    }

    /**
     * Format payload for Microsoft Teams
     */
    formatTeamsPayload(payload) {
        const { status, score, testSuite, buildNumber, branch, commitHash, buildUrl, details } = payload;

        const color = status === 'PASS' ? 'good' : status === 'UNSTABLE' ? 'warning' : 'attention';
        const emoji = status === 'PASS' ? '✅' : status === 'UNSTABLE' ? '⚠️' : '❌';

        return {
            '@type': 'MessageCard',
            '@context': 'http://schema.org/extensions',
            themeColor: color === 'good' ? '00FF00' : color === 'warning' ? 'FFFF00' : 'FF0000',
            summary: `Baseline Tests ${status}`,
            sections: [
                {
                    activityTitle: `${emoji} Baseline Tests ${status}`,
                    activitySubtitle: 'Baseline Testing System',
                    facts: [
                        {
                            name: 'Score',
                            value: `${score}%`
                        },
                        {
                            name: 'Test Suite',
                            value: testSuite || 'all'
                        },
                        {
                            name: 'Build',
                            value: buildNumber || 'N/A'
                        },
                        {
                            name: 'Branch',
                            value: branch || 'unknown'
                        }
                    ]
                }
            ],
            potentialAction: buildUrl ? [
                {
                    '@type': 'OpenUri',
                    name: 'View Build',
                    targets: [
                        {
                            os: 'default',
                            uri: buildUrl
                        }
                    ]
                }
            ] : []
        };
    }

    /**
     * Send notifications to multiple channels
     */
    async sendMultipleNotifications(webhooks, payload) {
        const results = [];

        for (const webhook of webhooks) {
            try {
                let result;

                switch (webhook.type) {
                    case 'slack':
                        result = await this.sendSlackNotification(webhook.url, payload);
                        break;
                    case 'discord':
                        result = await this.sendDiscordNotification(webhook.url, payload);
                        break;
                    case 'teams':
                        result = await this.sendTeamsNotification(webhook.url, payload);
                        break;
                    default:
                        result = await this.sendWebhook(webhook.url, payload, webhook.type || 'Generic');
                        break;
                }

                results.push({
                    webhook: webhook.name || webhook.type,
                    success: true,
                    result: result
                });
            } catch (error) {
                this.log('ERROR', `Failed to send ${webhook.type} notification`, { error: error.message });
                results.push({
                    webhook: webhook.name || webhook.type,
                    success: false,
                    error: error.message
                });
            }
        }

        return results;
    }

    /**
     * Load configuration from file
     */
    static loadConfig(configPath) {
        try {
            if (fs.existsSync(configPath)) {
                const configData = fs.readFileSync(configPath, 'utf8');
                return JSON.parse(configData);
            }
        } catch (error) {
            console.error('Failed to load webhook config:', error.message);
        }
        return {};
    }
}

// CLI interface
if (require.main === module) {
    const args = process.argv.slice(2);

    if (args.length === 0) {
        console.log(`
Usage: node webhook-manager.js [command] [options]

Commands:
  send-notification <payload-file>  Send notification with payload from file
  test-webhook <webhook-url>        Test webhook endpoint

Options:
  --config <file>                   Configuration file path
  --type <slack|discord|teams>      Webhook type
  --retry <number>                  Number of retries (default: 3)
  --timeout <ms>                    Request timeout (default: 10000)
  --log-level <level>               Log level (DEBUG|INFO|WARN|ERROR)

Examples:
  node webhook-manager.js send-notification baseline-results.json
  node webhook-manager.js test-webhook https://hooks.slack.com/... --type slack
        `);
        process.exit(1);
    }

    const command = args[0];
    const configPath = args.includes('--config') ? args[args.indexOf('--config') + 1] : './webhook-config.json';
    const webhookType = args.includes('--type') ? args[args.indexOf('--type') + 1] : 'slack';
    const retries = args.includes('--retry') ? parseInt(args[args.indexOf('--retry') + 1]) : 3;
    const timeout = args.includes('--timeout') ? parseInt(args[args.indexOf('--timeout') + 1]) : 10000;
    const logLevel = args.includes('--log-level') ? args[args.indexOf('--log-level') + 1] : 'INFO';

    const config = WebhookManager.loadConfig(configPath);
    const manager = new WebhookManager({
        maxRetries: retries,
        timeout: timeout,
        logLevel: logLevel,
        ...config
    });

    async function main() {
        try {
            switch (command) {
                case 'send-notification':
                    const payloadFile = args[1];
                    if (!payloadFile || !fs.existsSync(payloadFile)) {
                        console.error('Payload file not found');
                        process.exit(1);
                    }

                    const payload = JSON.parse(fs.readFileSync(payloadFile, 'utf8'));

                    if (config.webhooks) {
                        const results = await manager.sendMultipleNotifications(config.webhooks, payload);
                        console.log('Notification results:', JSON.stringify(results, null, 2));
                    } else {
                        console.error('No webhooks configured');
                        process.exit(1);
                    }
                    break;

                case 'test-webhook':
                    const webhookUrl = args[1];
                    if (!webhookUrl) {
                        console.error('Webhook URL required');
                        process.exit(1);
                    }

                    const testPayload = {
                        status: 'PASS',
                        score: 95,
                        testSuite: 'test',
                        buildNumber: 'TEST-001',
                        branch: 'main',
                        commitHash: 'abc123'
                    };

                    const result = await manager.sendWebhook(webhookUrl, testPayload, webhookType);
                    console.log('Test result:', JSON.stringify(result, null, 2));
                    break;

                default:
                    console.error('Unknown command:', command);
                    process.exit(1);
            }
        } catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    }

    main();
}

module.exports = WebhookManager;