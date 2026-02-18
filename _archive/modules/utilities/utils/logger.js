#!/usr/bin/env node

/**
 * Advanced Logging System for Baseline Testing
 * Provides structured logging, log rotation, and multiple output formats
 */

const fs = require('fs');
const path = require('path');
const util = require('util');
const { EventEmitter } = require('events');

class BaselineLogger extends EventEmitter {
    constructor(config = {}) {
        super();

        this.config = {
            level: 'INFO',
            logDir: '.baseline-cache/logs',
            logFile: 'baseline.log',
            maxFileSize: 10 * 1024 * 1024, // 10MB
            maxFiles: 5,
            enableConsole: true,
            enableFile: true,
            enableStructured: true,
            timestampFormat: 'ISO',
            colorOutput: true,
            includeStack: false,
            ...config
        };

        this.levels = {
            ERROR: 0,
            WARN: 1,
            INFO: 2,
            DEBUG: 3,
            TRACE: 4
        };

        this.colors = {
            ERROR: '\x1b[31m', // Red
            WARN: '\x1b[33m',  // Yellow
            INFO: '\x1b[36m',  // Cyan
            DEBUG: '\x1b[32m', // Green
            TRACE: '\x1b[35m', // Magenta
            RESET: '\x1b[0m'
        };

        this.logFilePath = path.join(this.config.logDir, this.config.logFile);
        this.logStreams = new Map();

        this.ensureLogDirectory();
        this.setupLogRotation();
    }

    /**
     * Ensure log directory exists
     */
    ensureLogDirectory() {
        if (!fs.existsSync(this.config.logDir)) {
            fs.mkdirSync(this.config.logDir, { recursive: true });
        }
    }

    /**
     * Setup log rotation
     */
    setupLogRotation() {
        if (this.config.enableFile && fs.existsSync(this.logFilePath)) {
            const stats = fs.statSync(this.logFilePath);
            if (stats.size > this.config.maxFileSize) {
                this.rotateLogFile();
            }
        }
    }

    /**
     * Rotate log file when it gets too large
     */
    rotateLogFile() {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const rotatedPath = path.join(
            this.config.logDir,
            `${path.parse(this.config.logFile).name}-${timestamp}.log`
        );

        try {
            if (fs.existsSync(this.logFilePath)) {
                fs.renameSync(this.logFilePath, rotatedPath);
            }

            // Clean up old log files
            this.cleanupOldLogs();

            this.writeLog('INFO', 'Log file rotated', { rotatedPath });
        } catch (error) {
            console.error('Failed to rotate log file:', error.message);
        }
    }

    /**
     * Clean up old log files beyond maxFiles limit
     */
    cleanupOldLogs() {
        try {
            const files = fs.readdirSync(this.config.logDir)
                .filter(file => file.startsWith(path.parse(this.config.logFile).name) && file.endsWith('.log'))
                .map(file => ({
                    name: file,
                    path: path.join(this.config.logDir, file),
                    time: fs.statSync(path.join(this.config.logDir, file)).mtime
                }))
                .sort((a, b) => b.time - a.time);

            if (files.length > this.config.maxFiles) {
                const filesToDelete = files.slice(this.config.maxFiles);
                filesToDelete.forEach(file => {
                    try {
                        fs.unlinkSync(file.path);
                    } catch (error) {
                        console.error(`Failed to delete old log file ${file.name}:`, error.message);
                    }
                });
            }
        } catch (error) {
            console.error('Failed to cleanup old logs:', error.message);
        }
    }

    /**
     * Check if message should be logged based on level
     */
    shouldLog(level) {
        const messageLevel = this.levels[level.toUpperCase()];
        const configLevel = this.levels[this.config.level.toUpperCase()];
        return messageLevel <= configLevel;
    }

    /**
     * Format timestamp
     */
    formatTimestamp() {
        const now = new Date();
        switch (this.config.timestampFormat) {
            case 'ISO':
                return now.toISOString();
            case 'LOCAL':
                return now.toLocaleString();
            case 'UNIX':
                return Math.floor(now.getTime() / 1000).toString();
            default:
                return now.toISOString();
        }
    }

    /**
     * Format log message for console output
     */
    formatConsoleMessage(level, message, context, error) {
        const timestamp = this.formatTimestamp();
        const color = this.config.colorOutput ? this.colors[level] : '';
        const reset = this.config.colorOutput ? this.colors.RESET : '';

        let formatted = `${color}[${timestamp}] [${level}] ${message}${reset}`;

        if (context && Object.keys(context).length > 0) {
            formatted += `\n${color}Context: ${util.inspect(context, { depth: 3, colors: this.config.colorOutput })}${reset}`;
        }

        if (error) {
            formatted += `\n${color}Error: ${error.message}${reset}`;
            if (this.config.includeStack && error.stack) {
                formatted += `\n${color}Stack: ${error.stack}${reset}`;
            }
        }

        return formatted;
    }

    /**
     * Format log message for file output
     */
    formatFileMessage(level, message, context, error) {
        const logEntry = {
            timestamp: this.formatTimestamp(),
            level,
            message,
            ...(context && { context }),
            ...(error && {
                error: {
                    name: error.name,
                    message: error.message,
                    ...(this.config.includeStack && { stack: error.stack }),
                    ...(error.code && { code: error.code })
                }
            })
        };

        return this.config.enableStructured
            ? JSON.stringify(logEntry)
            : `[${logEntry.timestamp}] [${level}] ${message}${context ? ' Context: ' + JSON.stringify(context) : ''}${error ? ' Error: ' + error.message : ''}`;
    }

    /**
     * Write log entry
     */
    writeLog(level, message, context = null, error = null) {
        if (!this.shouldLog(level)) {
            return;
        }

        // Console output
        if (this.config.enableConsole) {
            const consoleMessage = this.formatConsoleMessage(level, message, context, error);
            const output = level === 'ERROR' ? console.error : console.log;
            output(consoleMessage);
        }

        // File output
        if (this.config.enableFile) {
            try {
                // Check if rotation is needed
                if (fs.existsSync(this.logFilePath)) {
                    const stats = fs.statSync(this.logFilePath);
                    if (stats.size > this.config.maxFileSize) {
                        this.rotateLogFile();
                    }
                }

                const fileMessage = this.formatFileMessage(level, message, context, error);
                fs.appendFileSync(this.logFilePath, fileMessage + '\n');
            } catch (writeError) {
                console.error('Failed to write to log file:', writeError.message);
            }
        }

        // Emit event for external handlers
        this.emit('log', {
            level,
            message,
            context,
            error,
            timestamp: this.formatTimestamp()
        });
    }

    /**
     * Log methods for different levels
     */
    error(message, context = null, error = null) {
        this.writeLog('ERROR', message, context, error);
    }

    warn(message, context = null, error = null) {
        this.writeLog('WARN', message, context, error);
    }

    info(message, context = null) {
        this.writeLog('INFO', message, context);
    }

    debug(message, context = null) {
        this.writeLog('DEBUG', message, context);
    }

    trace(message, context = null) {
        this.writeLog('TRACE', message, context);
    }

    /**
     * Log test results
     */
    logTestResult(testName, result, duration, context = {}) {
        const level = result === 'PASS' ? 'INFO' : 'ERROR';
        const message = `Test ${testName} ${result}`;
        this.writeLog(level, message, {
            testName,
            result,
            duration,
            ...context
        });
    }

    /**
     * Log performance metrics
     */
    logPerformance(operation, metrics, context = {}) {
        this.writeLog('INFO', `Performance: ${operation}`, {
            operation,
            metrics,
            ...context
        });
    }

    /**
     * Log system information
     */
    logSystemInfo() {
        const os = require('os');
        const systemInfo = {
            platform: os.platform(),
            arch: os.arch(),
            nodeVersion: process.version,
            totalMemory: os.totalmem(),
            freeMemory: os.freemem(),
            cpus: os.cpus().length,
            uptime: os.uptime()
        };

        this.info('System Information', systemInfo);
    }

    /**
     * Create a child logger with additional context
     */
    createChild(context = {}) {
        const childLogger = Object.create(this);
        childLogger.childContext = { ...this.childContext, ...context };

        // Override writeLog to include child context
        const originalWriteLog = this.writeLog.bind(this);
        childLogger.writeLog = (level, message, additionalContext = null, error = null) => {
            const mergedContext = {
                ...childLogger.childContext,
                ...additionalContext
            };
            originalWriteLog(level, message, mergedContext, error);
        };

        return childLogger;
    }

    /**
     * Create a timer for measuring operation duration
     */
    timer(operationName, context = {}) {
        const startTime = Date.now();
        const startHrTime = process.hrtime();

        return {
            end: (additionalContext = {}) => {
                const endTime = Date.now();
                const [seconds, nanoseconds] = process.hrtime(startHrTime);
                const duration = {
                    ms: endTime - startTime,
                    precise: seconds * 1000 + nanoseconds / 1000000
                };

                this.info(`Operation completed: ${operationName}`, {
                    operation: operationName,
                    duration,
                    ...context,
                    ...additionalContext
                });

                return duration;
            }
        };
    }

    /**
     * Log function execution with timing
     */
    async logExecution(operationName, func, context = {}) {
        const timer = this.timer(operationName, context);
        this.debug(`Starting operation: ${operationName}`, context);

        try {
            const result = await func();
            timer.end({ status: 'success' });
            return result;
        } catch (error) {
            timer.end({ status: 'error' });
            this.error(`Operation failed: ${operationName}`, context, error);
            throw error;
        }
    }

    /**
     * Get log statistics
     */
    getLogStats() {
        const stats = {
            logFile: this.logFilePath,
            logSize: 0,
            logCount: 0
        };

        try {
            if (fs.existsSync(this.logFilePath)) {
                const fileStats = fs.statSync(this.logFilePath);
                stats.logSize = fileStats.size;

                // Count lines in log file (approximate)
                const content = fs.readFileSync(this.logFilePath, 'utf8');
                stats.logCount = content.split('\n').length - 1;
            }

            // Count rotated log files
            const logFiles = fs.readdirSync(this.config.logDir)
                .filter(file => file.startsWith(path.parse(this.config.logFile).name));
            stats.totalLogFiles = logFiles.length;

        } catch (error) {
            this.error('Failed to get log stats', null, error);
        }

        return stats;
    }

    /**
     * Export logs for analysis
     */
    exportLogs(outputPath, format = 'json') {
        try {
            const logs = [];

            if (fs.existsSync(this.logFilePath)) {
                const content = fs.readFileSync(this.logFilePath, 'utf8');
                const lines = content.split('\n').filter(line => line.trim());

                for (const line of lines) {
                    try {
                        if (this.config.enableStructured) {
                            logs.push(JSON.parse(line));
                        } else {
                            // Parse unstructured logs (basic parsing)
                            const match = line.match(/\[(.*?)\] \[(.*?)\] (.*)/);
                            if (match) {
                                logs.push({
                                    timestamp: match[1],
                                    level: match[2],
                                    message: match[3]
                                });
                            }
                        }
                    } catch (parseError) {
                        // Skip unparseable lines
                    }
                }
            }

            let output;
            switch (format) {
                case 'json':
                    output = JSON.stringify(logs, null, 2);
                    break;
                case 'csv':
                    if (logs.length > 0) {
                        const headers = Object.keys(logs[0]);
                        const csvLines = [headers.join(',')];
                        logs.forEach(log => {
                            const values = headers.map(header =>
                                JSON.stringify(log[header] || '').replace(/"/g, '""')
                            );
                            csvLines.push(values.join(','));
                        });
                        output = csvLines.join('\n');
                    } else {
                        output = '';
                    }
                    break;
                default:
                    output = logs.map(log => JSON.stringify(log)).join('\n');
            }

            fs.writeFileSync(outputPath, output);
            this.info(`Logs exported to: ${outputPath}`, { format, count: logs.length });

        } catch (error) {
            this.error('Failed to export logs', { outputPath, format }, error);
        }
    }

    /**
     * Close logger and cleanup resources
     */
    close() {
        this.logStreams.forEach(stream => {
            if (stream && typeof stream.end === 'function') {
                stream.end();
            }
        });
        this.logStreams.clear();
    }
}

// Create default logger instance
const defaultLogger = new BaselineLogger();

module.exports = {
    BaselineLogger,
    logger: defaultLogger
};

// CLI interface
if (require.main === module) {
    const args = process.argv.slice(2);
    const command = args[0];

    switch (command) {
        case 'test':
            console.log('Testing logger...');
            const testLogger = new BaselineLogger({
                level: 'TRACE',
                enableStructured: true
            });

            testLogger.trace('This is a trace message');
            testLogger.debug('This is a debug message', { debug: true });
            testLogger.info('This is an info message', { info: 'data' });
            testLogger.warn('This is a warning', { warning: true });
            testLogger.error('This is an error', { error: true }, new Error('Test error'));

            testLogger.logSystemInfo();

            const timer = testLogger.timer('test_operation');
            setTimeout(() => {
                timer.end({ result: 'success' });
            }, 100);

            console.log('Test completed. Check log files in .baseline-cache/logs/');
            break;

        case 'export':
            const outputPath = args[1] || 'exported-logs.json';
            const format = args[2] || 'json';
            defaultLogger.exportLogs(outputPath, format);
            break;

        case 'stats':
            console.log('Log statistics:', defaultLogger.getLogStats());
            break;

        default:
            console.log(`
Usage: node logger.js [command] [options]

Commands:
  test                     Run logger test
  export <file> [format]   Export logs (formats: json, csv)
  stats                    Show log statistics

The BaselineLogger class can be imported and used:

const { BaselineLogger, logger } = require('./logger');

// Use default logger
logger.info('Message', { context: 'data' });

// Create custom logger
const customLogger = new BaselineLogger({
    level: 'DEBUG',
    logFile: 'custom.log'
});
            `);
    }
}