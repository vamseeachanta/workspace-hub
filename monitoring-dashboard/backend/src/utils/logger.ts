import winston from 'winston';

const isProduction = process.env.NODE_ENV === 'production';

// Custom format for console logging
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp(),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    const metaString = Object.keys(meta).length ? JSON.stringify(meta, null, 2) : '';
    return `${timestamp} [${level}]: ${message} ${metaString}`;
  })
);

// Format for file logging
const fileFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

// Create logger instance
export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || (isProduction ? 'info' : 'debug'),
  format: fileFormat,
  defaultMeta: { service: 'monitoring-dashboard-api' },
  transports: [
    // Console transport
    new winston.transports.Console({
      format: consoleFormat,
      silent: process.env.NODE_ENV === 'test'
    }),

    // File transports for production
    ...(isProduction ? [
      new winston.transports.File({
        filename: 'logs/error.log',
        level: 'error',
        maxsize: 5242880, // 5MB
        maxFiles: 5
      }),
      new winston.transports.File({
        filename: 'logs/combined.log',
        maxsize: 5242880, // 5MB
        maxFiles: 5
      })
    ] : [])
  ]
});

// Performance logging utility
export const performanceLogger = {
  start: (operation: string): { end: () => void } => {
    const startTime = Date.now();

    return {
      end: () => {
        const duration = Date.now() - startTime;
        logger.debug(`Performance: ${operation} completed in ${duration}ms`);
      }
    };
  }
};

// Request logging utility
export const requestLogger = {
  logRequest: (method: string, path: string, statusCode: number, duration: number, userId?: string) => {
    logger.info('Request completed', {
      method,
      path,
      statusCode,
      duration,
      userId: userId || 'anonymous'
    });
  },

  logError: (method: string, path: string, error: Error, userId?: string) => {
    logger.error('Request failed', {
      method,
      path,
      error: error.message,
      stack: error.stack,
      userId: userId || 'anonymous'
    });
  }
};