import 'reflect-metadata';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';

import { logger } from './utils/logger';
import { cacheService } from './cache/redis-cache';
import { apiRoutes } from './api/routes';
import { graphqlServer } from './graphql/server';
import { WebSocketService } from './api/websocket';
import { AlertService } from './api/alert-service';

// Load environment variables
dotenv.config();

const PORT = process.env.PORT || 3001;
const NODE_ENV = process.env.NODE_ENV || 'development';

class Application {
  private app: express.Application;
  private server: any;
  private io: SocketIOServer;
  private wsService: WebSocketService;

  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    this.io = new SocketIOServer(this.server, {
      cors: {
        origin: process.env.FRONTEND_URL || 'http://localhost:3000',
        methods: ['GET', 'POST']
      }
    });

    this.wsService = new WebSocketService(this.io);
  }

  private setupMiddleware(): void {
    // Security middleware
    this.app.use(helmet());

    // CORS
    this.app.use(cors({
      origin: process.env.FRONTEND_URL || 'http://localhost:3000',
      credentials: true
    }));

    // Compression
    this.app.use(compression());

    // Rate limiting
    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 1000, // limit each IP to 1000 requests per windowMs
      message: 'Too many requests from this IP'
    });
    this.app.use('/api', limiter);

    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));

    // Request logging
    this.app.use((req, res, next) => {
      logger.info(`${req.method} ${req.path}`, {
        ip: req.ip,
        userAgent: req.get('User-Agent')
      });
      next();
    });
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        environment: NODE_ENV
      });
    });

    // API routes
    this.app.use('/api', apiRoutes);

    // 404 handler
    this.app.use('*', (req, res) => {
      res.status(404).json({
        success: false,
        error: 'Endpoint not found',
        timestamp: new Date().toISOString()
      });
    });
  }

  private setupErrorHandling(): void {
    // Global error handler
    this.app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
      logger.error('Unhandled error:', error);

      res.status(error.status || 500).json({
        success: false,
        error: NODE_ENV === 'production' ? 'Internal server error' : error.message,
        timestamp: new Date().toISOString()
      });
    });

    // Uncaught exception handler
    process.on('uncaughtException', (error) => {
      logger.error('Uncaught Exception:', error);
      process.exit(1);
    });

    // Unhandled rejection handler
    process.on('unhandledRejection', (reason, promise) => {
      logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
      process.exit(1);
    });
  }

  private async setupServices(): Promise<void> {
    try {
      // Initialize cache service
      await cacheService.connect();
      logger.info('Cache service connected');

      // Setup GraphQL server
      await graphqlServer.start();
      graphqlServer.applyMiddleware({ app: this.app, path: '/graphql' });
      logger.info('GraphQL server started');

      // Initialize alert service
      const alertService = new AlertService();
      await alertService.initialize();
      logger.info('Alert service initialized');

    } catch (error) {
      logger.error('Failed to setup services:', error);
      throw error;
    }
  }

  public async start(): Promise<void> {
    try {
      this.setupMiddleware();
      await this.setupServices();
      this.setupRoutes();
      this.setupErrorHandling();

      this.server.listen(PORT, () => {
        logger.info(`Server running on port ${PORT} in ${NODE_ENV} mode`);
        logger.info(`GraphQL endpoint: http://localhost:${PORT}/graphql`);
        logger.info(`WebSocket server ready`);
      });

    } catch (error) {
      logger.error('Failed to start server:', error);
      process.exit(1);
    }
  }

  public async stop(): Promise<void> {
    logger.info('Shutting down server...');

    this.server.close(() => {
      logger.info('HTTP server closed');
    });

    await cacheService.disconnect();
    logger.info('Cache service disconnected');

    process.exit(0);
  }
}

// Graceful shutdown
const app = new Application();

process.on('SIGTERM', () => app.stop());
process.on('SIGINT', () => app.stop());

// Start the application
app.start().catch((error) => {
  logger.error('Failed to start application:', error);
  process.exit(1);
});

export default app;