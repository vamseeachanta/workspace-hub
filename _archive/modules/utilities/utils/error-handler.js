#!/usr/bin/env node

/**
 * Comprehensive Error Handler for Baseline Testing
 * Provides centralized error handling, retry logic, and circuit breaker patterns
 */

const fs = require('fs');
const path = require('path');
const { EventEmitter } = require('events');

class ErrorHandler extends EventEmitter {
    constructor(config = {}) {
        super();
        this.config = {
            maxRetries: 3,
            retryDelayMs: 1000,
            exponentialBackoff: true,
            maxRetryDelayMs: 30000,
            circuitBreakerThreshold: 5,
            circuitBreakerTimeout: 60000,
            logLevel: 'INFO',
            logFile: '.baseline-cache/logs/error-handler.log',
            enableMetrics: true,
            ...config
        };

        this.retryCount = new Map();
        this.circuitBreakers = new Map();
        this.errorMetrics = {
            totalErrors: 0,
            retriedErrors: 0,
            circuitBreakerTrips: 0,
            errorsByType: new Map(),
            errorsByOperation: new Map()
        };

        this.ensureLogDirectory();
        this.setupErrorTypes();
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
     * Setup predefined error types and their handling strategies
     */
    setupErrorTypes() {
        this.errorStrategies = {
            'NETWORK_ERROR': {
                retryable: true,
                maxRetries: 5,
                retryDelay: 2000,
                exponentialBackoff: true
            },
            'TIMEOUT_ERROR': {
                retryable: true,
                maxRetries: 3,
                retryDelay: 5000,
                exponentialBackoff: false
            },
            'VALIDATION_ERROR': {
                retryable: false,
                maxRetries: 0,
                retryDelay: 0,
                exponentialBackoff: false
            },
            'AUTHENTICATION_ERROR': {
                retryable: false,
                maxRetries: 0,
                retryDelay: 0,
                exponentialBackoff: false
            },
            'RESOURCE_ERROR': {
                retryable: true,
                maxRetries: 3,
                retryDelay: 1000,
                exponentialBackoff: true
            },
            'TEST_FAILURE': {
                retryable: true,
                maxRetries: 2,
                retryDelay: 3000,
                exponentialBackoff: false
            },
            'FILESYSTEM_ERROR': {
                retryable: true,
                maxRetries: 3,
                retryDelay: 1000,
                exponentialBackoff: true
            },
            'PERMISSION_ERROR': {
                retryable: false,
                maxRetries: 0,
                retryDelay: 0,
                exponentialBackoff: false
            }
        };
    }

    /**
     * Log error with structured information
     */
    log(level, message, error = null, context = {}) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            context,
            ...(error && {
                error: {
                    name: error.name,
                    message: error.message,
                    stack: error.stack,
                    code: error.code,
                    errno: error.errno,
                    syscall: error.syscall,
                    path: error.path
                }
            })
        };

        // Console output
        if (this.shouldLog(level)) {
            console.log(`[${timestamp}] [${level}] ${message}`);
            if (error) {
                console.error(error);
            }
            if (Object.keys(context).length > 0) {
                console.log('Context:', JSON.stringify(context, null, 2));
            }
        }

        // File output
        try {
            fs.appendFileSync(this.config.logFile, JSON.stringify(logEntry) + '\n');
        } catch (logError) {
            console.error('Failed to write to log file:', logError.message);
        }

        // Emit event for external handlers
        this.emit('log', logEntry);
    }

    /**
     * Check if log level should be output
     */
    shouldLog(level) {
        const levels = ['DEBUG', 'INFO', 'WARN', 'ERROR'];
        const configLevel = levels.indexOf(this.config.logLevel);
        const messageLevel = levels.indexOf(level);
        return messageLevel >= configLevel;
    }

    /**
     * Execute function with comprehensive error handling and retry logic
     */
    async executeWithRetry(operation, operationName, context = {}) {
        const operationId = `${operationName}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        this.log('DEBUG', `Starting operation: ${operationName}`, null, { operationId, ...context });

        let lastError;
        let attempt = 0;

        while (attempt <= this.getMaxRetries(null, operationName)) {
            try {
                // Check circuit breaker
                if (this.isCircuitBreakerOpen(operationName)) {
                    throw new Error(`Circuit breaker open for operation: ${operationName}`);
                }

                const result = await operation();

                // Success - reset circuit breaker and retry count
                this.resetCircuitBreaker(operationName);
                this.retryCount.delete(operationId);

                this.log('INFO', `Operation succeeded: ${operationName}`, null, {
                    operationId,
                    attempt: attempt + 1,
                    ...context
                });

                return result;

            } catch (error) {
                lastError = error;
                attempt++;

                this.updateErrorMetrics(error, operationName);
                this.updateCircuitBreaker(operationName);

                const errorType = this.classifyError(error);
                const strategy = this.errorStrategies[errorType] || this.errorStrategies['RESOURCE_ERROR'];

                this.log('WARN', `Operation failed: ${operationName} (attempt ${attempt})`, error, {
                    operationId,
                    errorType,
                    attempt,
                    maxRetries: this.getMaxRetries(error, operationName),
                    ...context
                });

                // Check if we should retry
                if (!strategy.retryable || attempt > this.getMaxRetries(error, operationName)) {
                    break;
                }

                // Calculate delay and wait
                const delay = this.calculateRetryDelay(attempt, error, operationName);
                this.log('INFO', `Retrying in ${delay}ms`, null, { operationId, attempt });

                await this.sleep(delay);
            }
        }

        // All retries exhausted
        this.log('ERROR', `Operation failed permanently: ${operationName}`, lastError, {
            operationId,
            totalAttempts: attempt,
            ...context
        });

        // Emit error event
        this.emit('error', {
            operationName,
            operationId,
            error: lastError,
            attempts: attempt,
            context
        });

        throw lastError;
    }

    /**
     * Classify error by type for appropriate handling strategy
     */
    classifyError(error) {
        if (!error) return 'UNKNOWN_ERROR';

        // Network related errors
        if (error.code === 'ENOTFOUND' || error.code === 'ECONNREFUSED' ||
            error.code === 'ECONNRESET' || error.code === 'ETIMEDOUT' ||
            error.message.includes('network') || error.message.includes('connection')) {
            return 'NETWORK_ERROR';
        }

        // Timeout errors
        if (error.code === 'TIMEOUT' || error.message.includes('timeout') ||
            error.message.includes('timed out')) {
            return 'TIMEOUT_ERROR';
        }

        // Authentication errors
        if (error.code === 401 || error.statusCode === 401 ||
            error.message.includes('authentication') || error.message.includes('unauthorized')) {
            return 'AUTHENTICATION_ERROR';
        }

        // Permission errors
        if (error.code === 'EACCES' || error.code === 'EPERM' ||
            error.code === 403 || error.statusCode === 403) {
            return 'PERMISSION_ERROR';
        }

        // Filesystem errors
        if (error.code === 'ENOENT' || error.code === 'EISDIR' ||
            error.code === 'ENOTDIR' || error.code === 'EMFILE') {
            return 'FILESYSTEM_ERROR';
        }

        // Validation errors
        if (error.name === 'ValidationError' || error.message.includes('validation') ||
            error.message.includes('invalid')) {
            return 'VALIDATION_ERROR';
        }

        // Test failures
        if (error.message.includes('test') && (error.message.includes('failed') ||
            error.message.includes('assertion'))) {
            return 'TEST_FAILURE';
        }

        // Resource errors (default)
        return 'RESOURCE_ERROR';
    }

    /**
     * Get maximum retries for error/operation combination
     */
    getMaxRetries(error, operationName) {
        if (error) {
            const errorType = this.classifyError(error);
            const strategy = this.errorStrategies[errorType];
            if (strategy) {
                return strategy.maxRetries;
            }
        }
        return this.config.maxRetries;
    }

    /**
     * Calculate retry delay with exponential backoff
     */
    calculateRetryDelay(attempt, error, operationName) {
        const errorType = this.classifyError(error);
        const strategy = this.errorStrategies[errorType] || {};

        let baseDelay = strategy.retryDelay || this.config.retryDelayMs;

        if (strategy.exponentialBackoff !== false && this.config.exponentialBackoff) {
            baseDelay = baseDelay * Math.pow(2, attempt - 1);
        }

        // Add jitter to prevent thundering herd
        const jitter = Math.random() * 0.1 * baseDelay;
        const delay = baseDelay + jitter;

        return Math.min(delay, this.config.maxRetryDelayMs);
    }

    /**
     * Update error metrics
     */
    updateErrorMetrics(error, operationName) {
        if (!this.config.enableMetrics) return;

        this.errorMetrics.totalErrors++;

        const errorType = this.classifyError(error);
        this.errorMetrics.errorsByType.set(
            errorType,
            (this.errorMetrics.errorsByType.get(errorType) || 0) + 1
        );

        this.errorMetrics.errorsByOperation.set(
            operationName,
            (this.errorMetrics.errorsByOperation.get(operationName) || 0) + 1
        );
    }

    /**
     * Circuit breaker implementation
     */
    updateCircuitBreaker(operationName) {
        if (!this.circuitBreakers.has(operationName)) {
            this.circuitBreakers.set(operationName, {
                failures: 0,
                lastFailure: null,
                state: 'CLOSED' // CLOSED, OPEN, HALF_OPEN
            });
        }

        const breaker = this.circuitBreakers.get(operationName);
        breaker.failures++;
        breaker.lastFailure = Date.now();

        if (breaker.failures >= this.config.circuitBreakerThreshold) {
            breaker.state = 'OPEN';
            this.errorMetrics.circuitBreakerTrips++;

            this.log('WARN', `Circuit breaker opened for operation: ${operationName}`, null, {
                failures: breaker.failures,
                threshold: this.config.circuitBreakerThreshold
            });
        }
    }

    /**
     * Check if circuit breaker is open
     */
    isCircuitBreakerOpen(operationName) {
        const breaker = this.circuitBreakers.get(operationName);
        if (!breaker || breaker.state === 'CLOSED') return false;

        if (breaker.state === 'OPEN') {
            const timeSinceLastFailure = Date.now() - breaker.lastFailure;
            if (timeSinceLastFailure > this.config.circuitBreakerTimeout) {
                breaker.state = 'HALF_OPEN';
                this.log('INFO', `Circuit breaker half-open for operation: ${operationName}`);
                return false;
            }
            return true;
        }

        return false;
    }

    /**
     * Reset circuit breaker on success
     */
    resetCircuitBreaker(operationName) {
        const breaker = this.circuitBreakers.get(operationName);
        if (breaker) {
            breaker.failures = 0;
            breaker.state = 'CLOSED';
            breaker.lastFailure = null;
        }
    }

    /**
     * Utility sleep function
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get error metrics
     */
    getMetrics() {
        return {
            ...this.errorMetrics,
            errorsByType: Object.fromEntries(this.errorMetrics.errorsByType),
            errorsByOperation: Object.fromEntries(this.errorMetrics.errorsByOperation),
            circuitBreakers: Object.fromEntries(
                Array.from(this.circuitBreakers.entries()).map(([name, breaker]) => [
                    name,
                    { ...breaker }
                ])
            )
        };
    }

    /**
     * Reset metrics
     */
    resetMetrics() {
        this.errorMetrics = {
            totalErrors: 0,
            retriedErrors: 0,
            circuitBreakerTrips: 0,
            errorsByType: new Map(),
            errorsByOperation: new Map()
        };
        this.circuitBreakers.clear();
        this.retryCount.clear();
    }

    /**
     * Create a wrapped function with error handling
     */
    wrap(operation, operationName, context = {}) {
        return (...args) => {
            return this.executeWithRetry(
                () => operation(...args),
                operationName,
                context
            );
        };
    }

    /**
     * Create error with additional context
     */
    static createError(message, code, context = {}) {
        const error = new Error(message);
        error.code = code;
        Object.assign(error, context);
        return error;
    }

    /**
     * Save error report to file
     */
    saveErrorReport(filePath = '.baseline-cache/error-report.json') {
        const report = {
            timestamp: new Date().toISOString(),
            config: this.config,
            metrics: this.getMetrics(),
            errorStrategies: this.errorStrategies
        };

        try {
            fs.writeFileSync(filePath, JSON.stringify(report, null, 2));
            this.log('INFO', `Error report saved to: ${filePath}`);
        } catch (error) {
            this.log('ERROR', 'Failed to save error report', error);
        }
    }
}

// Utility functions for common error scenarios
class BaselineErrorHandler extends ErrorHandler {
    constructor(config = {}) {
        super({
            logFile: '.baseline-cache/logs/baseline-errors.log',
            ...config
        });
    }

    /**
     * Handle test execution with specific error strategies
     */
    async executeTest(testFunction, testName, testContext = {}) {
        return this.executeWithRetry(testFunction, `test_${testName}`, {
            testType: 'baseline',
            ...testContext
        });
    }

    /**
     * Handle file operations with appropriate retry logic
     */
    async executeFileOperation(fileOperation, operationName, filePath) {
        return this.executeWithRetry(fileOperation, `file_${operationName}`, {
            filePath,
            operationType: 'filesystem'
        });
    }

    /**
     * Handle network operations
     */
    async executeNetworkOperation(networkOperation, operationName, url) {
        return this.executeWithRetry(networkOperation, `network_${operationName}`, {
            url,
            operationType: 'network'
        });
    }

    /**
     * Handle command execution
     */
    async executeCommand(commandFunction, commandName, command) {
        return this.executeWithRetry(commandFunction, `command_${commandName}`, {
            command,
            operationType: 'command'
        });
    }
}

// Export for use in other modules
module.exports = {
    ErrorHandler,
    BaselineErrorHandler
};

// CLI interface
if (require.main === module) {
    const args = process.argv.slice(2);

    if (args[0] === 'test') {
        console.log('Testing error handler...');

        const handler = new BaselineErrorHandler({
            logLevel: 'DEBUG',
            maxRetries: 2
        });

        // Test with a function that fails then succeeds
        let attempts = 0;
        handler.executeWithRetry(
            () => {
                attempts++;
                if (attempts < 3) {
                    throw new Error('Simulated failure');
                }
                return 'Success!';
            },
            'test_operation'
        ).then(result => {
            console.log('Result:', result);
            console.log('Metrics:', handler.getMetrics());
        }).catch(error => {
            console.error('Final error:', error.message);
            console.log('Metrics:', handler.getMetrics());
        });
    } else {
        console.log(`
Usage: node error-handler.js [command]

Commands:
  test    Run error handler test

The ErrorHandler class can be imported and used in other modules:

const { BaselineErrorHandler } = require('./error-handler');
const handler = new BaselineErrorHandler();

// Wrap functions with error handling
const safeFunction = handler.wrap(riskyFunction, 'operation_name');

// Or use directly
handler.executeWithRetry(riskyFunction, 'operation_name')
  .then(result => console.log(result))
  .catch(error => console.error(error));
        `);
    }
}