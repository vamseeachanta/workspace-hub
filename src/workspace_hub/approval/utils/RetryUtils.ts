/**
 * Retry utilities for handling transient failures in the approval system
 * Provides exponential backoff, circuit breaker, and retry policies
 */

import { IntegrationError } from '../errors/ApprovalErrors';

export interface RetryOptions {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  exponentialBase: number;
  jitter: boolean;
  retryCondition?: (error: Error) => boolean;
  onRetry?: (attempt: number, error: Error) => void;
}

export interface CircuitBreakerOptions {
  failureThreshold: number;
  resetTimeout: number;
  monitoringPeriod: number;
  volumeThreshold: number;
}

export enum CircuitBreakerState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN'
}

export class RetryUtils {
  private static readonly DEFAULT_RETRY_OPTIONS: RetryOptions = {
    maxAttempts: 3,
    baseDelay: 1000,
    maxDelay: 30000,
    exponentialBase: 2,
    jitter: true,
    retryCondition: (error: Error) => {
      // Retry on network errors, timeouts, and 5xx status codes
      return (
        error.message.includes('ECONNRESET') ||
        error.message.includes('ETIMEDOUT') ||
        error.message.includes('ENOTFOUND') ||
        error.message.includes('503') ||
        error.message.includes('502') ||
        error.message.includes('500')
      );
    }
  };

  /**
   * Execute function with retry logic
   */
  static async withRetry<T>(
    fn: () => Promise<T>,
    options: Partial<RetryOptions> = {}
  ): Promise<T> {
    const opts = { ...this.DEFAULT_RETRY_OPTIONS, ...options };
    let lastError: Error;

    for (let attempt = 1; attempt <= opts.maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;

        // Check if we should retry
        if (
          attempt === opts.maxAttempts ||
          (opts.retryCondition && !opts.retryCondition(lastError))
        ) {
          throw lastError;
        }

        // Call retry callback if provided
        if (opts.onRetry) {
          opts.onRetry(attempt, lastError);
        }

        // Calculate delay with exponential backoff and jitter
        const delay = this.calculateDelay(attempt, opts);
        await this.sleep(delay);
      }
    }

    throw lastError!;
  }

  /**
   * Calculate delay for retry attempt
   */
  private static calculateDelay(attempt: number, options: RetryOptions): number {
    const exponentialDelay = Math.min(
      options.baseDelay * Math.pow(options.exponentialBase, attempt - 1),
      options.maxDelay
    );

    if (options.jitter) {
      // Add jitter to prevent thundering herd
      const jitterAmount = exponentialDelay * 0.1;
      return exponentialDelay + (Math.random() * jitterAmount * 2 - jitterAmount);
    }

    return exponentialDelay;
  }

  /**
   * Sleep for specified milliseconds
   */
  private static sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export class CircuitBreaker {
  private state: CircuitBreakerState = CircuitBreakerState.CLOSED;
  private failureCount: number = 0;
  private successCount: number = 0;
  private lastFailureTime: number = 0;
  private nextAttemptTime: number = 0;
  private options: CircuitBreakerOptions;
  private name: string;

  constructor(name: string, options: Partial<CircuitBreakerOptions> = {}) {
    this.name = name;
    this.options = {
      failureThreshold: 5,
      resetTimeout: 60000, // 1 minute
      monitoringPeriod: 10000, // 10 seconds
      volumeThreshold: 10,
      ...options
    };
  }

  /**
   * Execute function with circuit breaker protection
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === CircuitBreakerState.OPEN) {
      if (Date.now() < this.nextAttemptTime) {
        throw new IntegrationError(
          `Circuit breaker '${this.name}' is open`,
          this.name,
          'circuit_breaker_open'
        );
      }
      
      // Transition to half-open
      this.state = CircuitBreakerState.HALF_OPEN;
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure(error as Error);
      throw error;
    }
  }

  /**
   * Handle successful execution
   */
  private onSuccess(): void {
    this.failureCount = 0;
    this.successCount++;

    if (this.state === CircuitBreakerState.HALF_OPEN) {
      this.state = CircuitBreakerState.CLOSED;
    }
  }

  /**
   * Handle failed execution
   */
  private onFailure(error: Error): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (
      this.failureCount >= this.options.failureThreshold &&
      this.getTotalRequests() >= this.options.volumeThreshold
    ) {
      this.state = CircuitBreakerState.OPEN;
      this.nextAttemptTime = Date.now() + this.options.resetTimeout;
    }
  }

  /**
   * Get total requests in monitoring period
   */
  private getTotalRequests(): number {
    return this.failureCount + this.successCount;
  }

  /**
   * Get current circuit breaker state
   */
  getState(): CircuitBreakerState {
    return this.state;
  }

  /**
   * Get circuit breaker metrics
   */
  getMetrics() {
    return {
      name: this.name,
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      failureRate: this.getTotalRequests() > 0 
        ? this.failureCount / this.getTotalRequests() 
        : 0,
      lastFailureTime: this.lastFailureTime,
      nextAttemptTime: this.nextAttemptTime
    };
  }

  /**
   * Reset circuit breaker to closed state
   */
  reset(): void {
    this.state = CircuitBreakerState.CLOSED;
    this.failureCount = 0;
    this.successCount = 0;
    this.lastFailureTime = 0;
    this.nextAttemptTime = 0;
  }
}

/**
 * Timeout utility for async operations
 */
export class TimeoutUtils {
  /**
   * Execute function with timeout
   */
  static async withTimeout<T>(
    fn: () => Promise<T>,
    timeoutMs: number,
    timeoutMessage: string = 'Operation timed out'
  ): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(timeoutMessage));
      }, timeoutMs);

      fn()
        .then(result => {
          clearTimeout(timer);
          resolve(result);
        })
        .catch(error => {
          clearTimeout(timer);
          reject(error);
        });
    });
  }

  /**
   * Execute function with both retry and timeout
   */
  static async withRetryAndTimeout<T>(
    fn: () => Promise<T>,
    retryOptions: Partial<RetryOptions> = {},
    timeoutMs: number = 30000
  ): Promise<T> {
    return this.withTimeout(
      () => RetryUtils.withRetry(fn, retryOptions),
      timeoutMs
    );
  }
}

/**
 * Bulkhead pattern implementation for resource isolation
 */
export class Bulkhead {
  private semaphore: Semaphore;
  private name: string;
  private activeRequests: number = 0;
  private totalRequests: number = 0;
  private rejectedRequests: number = 0;

  constructor(name: string, maxConcurrency: number) {
    this.name = name;
    this.semaphore = new Semaphore(maxConcurrency);
  }

  /**
   * Execute function with bulkhead protection
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    this.totalRequests++;

    if (!this.semaphore.tryAcquire()) {
      this.rejectedRequests++;
      throw new IntegrationError(
        `Bulkhead '${this.name}' capacity exceeded`,
        this.name,
        'bulkhead_capacity_exceeded'
      );
    }

    try {
      this.activeRequests++;
      return await fn();
    } finally {
      this.activeRequests--;
      this.semaphore.release();
    }
  }

  /**
   * Get bulkhead metrics
   */
  getMetrics() {
    return {
      name: this.name,
      activeRequests: this.activeRequests,
      totalRequests: this.totalRequests,
      rejectedRequests: this.rejectedRequests,
      rejectionRate: this.totalRequests > 0 
        ? this.rejectedRequests / this.totalRequests 
        : 0,
      availableCapacity: this.semaphore.getAvailablePermits()
    };
  }
}

/**
 * Simple semaphore implementation
 */
class Semaphore {
  private permits: number;
  private maxPermits: number;
  private waitQueue: Array<() => void> = [];

  constructor(permits: number) {
    this.permits = permits;
    this.maxPermits = permits;
  }

  /**
   * Try to acquire a permit without waiting
   */
  tryAcquire(): boolean {
    if (this.permits > 0) {
      this.permits--;
      return true;
    }
    return false;
  }

  /**
   * Acquire a permit, waiting if necessary
   */
  async acquire(): Promise<void> {
    if (this.permits > 0) {
      this.permits--;
      return;
    }

    return new Promise<void>(resolve => {
      this.waitQueue.push(resolve);
    });
  }

  /**
   * Release a permit
   */
  release(): void {
    if (this.permits < this.maxPermits) {
      this.permits++;
      
      if (this.waitQueue.length > 0) {
        const resolve = this.waitQueue.shift()!;
        this.permits--;
        resolve();
      }
    }
  }

  /**
   * Get available permits
   */
  getAvailablePermits(): number {
    return this.permits;
  }
}

/**
 * Resilience wrapper combining multiple patterns
 */
export class ResilienceWrapper {
  private circuitBreaker?: CircuitBreaker;
  private bulkhead?: Bulkhead;
  private retryOptions?: Partial<RetryOptions>;
  private timeoutMs?: number;

  constructor(options: {
    name: string;
    circuitBreakerOptions?: Partial<CircuitBreakerOptions>;
    bulkheadMaxConcurrency?: number;
    retryOptions?: Partial<RetryOptions>;
    timeoutMs?: number;
  }) {
    if (options.circuitBreakerOptions) {
      this.circuitBreaker = new CircuitBreaker(options.name, options.circuitBreakerOptions);
    }

    if (options.bulkheadMaxConcurrency) {
      this.bulkhead = new Bulkhead(options.name, options.bulkheadMaxConcurrency);
    }

    this.retryOptions = options.retryOptions;
    this.timeoutMs = options.timeoutMs;
  }

  /**
   * Execute function with all configured resilience patterns
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    let wrappedFn = fn;

    // Apply bulkhead if configured
    if (this.bulkhead) {
      const bulkhead = this.bulkhead;
      wrappedFn = () => bulkhead.execute(fn);
    }

    // Apply circuit breaker if configured
    if (this.circuitBreaker) {
      const circuitBreaker = this.circuitBreaker;
      const previousFn = wrappedFn;
      wrappedFn = () => circuitBreaker.execute(previousFn);
    }

    // Apply timeout if configured
    if (this.timeoutMs) {
      const timeoutMs = this.timeoutMs;
      const previousFn = wrappedFn;
      wrappedFn = () => TimeoutUtils.withTimeout(previousFn, timeoutMs);
    }

    // Apply retry if configured
    if (this.retryOptions) {
      const retryOptions = this.retryOptions;
      const previousFn = wrappedFn;
      wrappedFn = () => RetryUtils.withRetry(previousFn, retryOptions);
    }

    return wrappedFn();
  }

  /**
   * Get metrics from all configured patterns
   */
  getMetrics() {
    return {
      circuitBreaker: this.circuitBreaker?.getMetrics(),
      bulkhead: this.bulkhead?.getMetrics()
    };
  }
}