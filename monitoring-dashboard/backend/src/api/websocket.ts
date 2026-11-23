import { Server as SocketIOServer, Socket } from 'socket.io';
import { logger } from '../utils/logger';
import { RealtimeEvent } from '@monitoring-dashboard/shared';

export class WebSocketService {
  private io: SocketIOServer;
  private connectedClients = new Map<string, Socket>();

  constructor(io: SocketIOServer) {
    this.io = io;
    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    this.io.on('connection', (socket: Socket) => {
      logger.info(`Client connected: ${socket.id}`);
      this.connectedClients.set(socket.id, socket);

      // Handle client subscription to specific events
      socket.on('subscribe', (channels: string[]) => {
        channels.forEach(channel => {
          socket.join(channel);
          logger.debug(`Client ${socket.id} subscribed to ${channel}`);
        });
      });

      // Handle client unsubscription
      socket.on('unsubscribe', (channels: string[]) => {
        channels.forEach(channel => {
          socket.leave(channel);
          logger.debug(`Client ${socket.id} unsubscribed from ${channel}`);
        });
      });

      // Handle dashboard filter updates
      socket.on('filter_update', (filters: any) => {
        logger.debug(`Client ${socket.id} updated filters:`, filters);
        // Store client-specific filters for personalized updates
        socket.data.filters = filters;
      });

      // Handle disconnection
      socket.on('disconnect', (reason) => {
        logger.info(`Client disconnected: ${socket.id}, reason: ${reason}`);
        this.connectedClients.delete(socket.id);
      });

      // Send initial connection acknowledgment
      socket.emit('connected', {
        message: 'Connected to monitoring dashboard',
        timestamp: new Date().toISOString()
      });
    });
  }

  // Broadcast event to all clients
  public broadcast(event: RealtimeEvent): void {
    this.io.emit('realtime_event', event);
    logger.debug(`Broadcasted event: ${event.type}`);
  }

  // Send event to specific channel
  public broadcastToChannel(channel: string, event: RealtimeEvent): void {
    this.io.to(channel).emit('realtime_event', event);
    logger.debug(`Broadcasted event to ${channel}: ${event.type}`);
  }

  // Send event to specific client
  public sendToClient(clientId: string, event: RealtimeEvent): void {
    const socket = this.connectedClients.get(clientId);
    if (socket) {
      socket.emit('realtime_event', event);
      logger.debug(`Sent event to client ${clientId}: ${event.type}`);
    }
  }

  // Broadcast test execution updates
  public broadcastTestUpdate(testData: any): void {
    const event: RealtimeEvent = {
      type: 'test_completed',
      payload: testData,
      timestamp: new Date().toISOString()
    };

    this.broadcastToChannel('tests', event);
  }

  // Broadcast coverage updates
  public broadcastCoverageUpdate(coverageData: any): void {
    const event: RealtimeEvent = {
      type: 'coverage_updated',
      payload: coverageData,
      timestamp: new Date().toISOString()
    };

    this.broadcastToChannel('coverage', event);
  }

  // Broadcast alert notifications
  public broadcastAlert(alertData: any): void {
    const event: RealtimeEvent = {
      type: 'alert_triggered',
      payload: alertData,
      timestamp: new Date().toISOString()
    };

    // Send to all clients for critical alerts
    if (alertData.severity === 'critical') {
      this.broadcast(event);
    } else {
      this.broadcastToChannel('alerts', event);
    }
  }

  // Broadcast performance metrics
  public broadcastMetricUpdate(metricData: any): void {
    const event: RealtimeEvent = {
      type: 'metric_updated',
      payload: metricData,
      timestamp: new Date().toISOString()
    };

    this.broadcastToChannel('metrics', event);
  }

  // Get connected clients count
  public getConnectedClientsCount(): number {
    return this.connectedClients.size;
  }

  // Get clients in specific channel
  public async getChannelClients(channel: string): Promise<string[]> {
    const sockets = await this.io.in(channel).fetchSockets();
    return sockets.map(socket => socket.id);
  }

  // Send heartbeat to check client connectivity
  public sendHeartbeat(): void {
    this.io.emit('heartbeat', {
      timestamp: new Date().toISOString(),
      serverTime: Date.now()
    });
  }

  // Start periodic heartbeat
  public startHeartbeat(intervalMs: number = 30000): void {
    setInterval(() => {
      this.sendHeartbeat();
    }, intervalMs);

    logger.info(`WebSocket heartbeat started (${intervalMs}ms interval)`);
  }
}