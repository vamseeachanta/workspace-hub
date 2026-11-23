import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import toast from 'react-hot-toast';
import { RealtimeEvent } from '@shared/types';

interface WebSocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  connectionStatus: 'connected' | 'disconnected' | 'reconnecting';
  subscribe: (channels: string[]) => void;
  unsubscribe: (channels: string[]) => void;
  updateFilters: (filters: any) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('disconnected');

  useEffect(() => {
    // Initialize socket connection
    const socketInstance = io(process.env.NODE_ENV === 'production' ? '' : 'http://localhost:3001', {
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 20000,
    });

    setSocket(socketInstance);

    // Connection event handlers
    socketInstance.on('connect', () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setConnectionStatus('connected');
      toast.success('Connected to real-time updates');
    });

    socketInstance.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      setIsConnected(false);
      setConnectionStatus('disconnected');

      if (reason === 'io server disconnect') {
        // Server disconnected, manually reconnect
        socketInstance.connect();
      }
    });

    socketInstance.on('reconnect_attempt', (attemptNumber) => {
      console.log(`Reconnection attempt ${attemptNumber}`);
      setConnectionStatus('reconnecting');
    });

    socketInstance.on('reconnect', (attemptNumber) => {
      console.log(`Reconnected after ${attemptNumber} attempts`);
      setIsConnected(true);
      setConnectionStatus('connected');
      toast.success('Reconnected to real-time updates');
    });

    socketInstance.on('reconnect_error', (error) => {
      console.error('Reconnection error:', error);
      toast.error('Failed to reconnect to real-time updates');
    });

    socketInstance.on('reconnect_failed', () => {
      console.error('Reconnection failed');
      setConnectionStatus('disconnected');
      toast.error('Unable to establish real-time connection');
    });

    // Handle real-time events
    socketInstance.on('realtime_event', (event: RealtimeEvent) => {
      console.log('Received real-time event:', event);
      handleRealtimeEvent(event);
    });

    // Handle connection acknowledgment
    socketInstance.on('connected', (data) => {
      console.log('Connection acknowledged:', data);
    });

    // Handle heartbeat
    socketInstance.on('heartbeat', (data) => {
      console.log('Heartbeat received:', data);
    });

    // Cleanup on unmount
    return () => {
      socketInstance.disconnect();
    };
  }, []);

  const handleRealtimeEvent = useCallback((event: RealtimeEvent) => {
    switch (event.type) {
      case 'test_completed':
        const testData = event.payload as any;
        if (testData.status === 'failed') {
          toast.error(`Test failed: ${testData.name}`);
        } else if (testData.status === 'passed') {
          toast.success(`Test passed: ${testData.name}`);
        }
        break;

      case 'coverage_updated':
        const coverageData = event.payload as any;
        if (coverageData.overall < 80) {
          toast.warning(`Coverage dropped to ${coverageData.overall.toFixed(1)}%`);
        }
        break;

      case 'alert_triggered':
        const alertData = event.payload as any;
        const alertMessage = `${alertData.severity.toUpperCase()}: ${alertData.title}`;

        switch (alertData.severity) {
          case 'critical':
            toast.error(alertMessage, { duration: 8000 });
            break;
          case 'high':
            toast.error(alertMessage, { duration: 6000 });
            break;
          case 'medium':
            toast.warning(alertMessage);
            break;
          case 'low':
            toast(alertMessage);
            break;
        }
        break;

      case 'metric_updated':
        // Handle metric updates silently or with subtle notifications
        console.log('Metric updated:', event.payload);
        break;

      default:
        console.log('Unhandled real-time event:', event);
    }
  }, []);

  const subscribe = useCallback((channels: string[]) => {
    if (socket && isConnected) {
      socket.emit('subscribe', channels);
      console.log('Subscribed to channels:', channels);
    }
  }, [socket, isConnected]);

  const unsubscribe = useCallback((channels: string[]) => {
    if (socket && isConnected) {
      socket.emit('unsubscribe', channels);
      console.log('Unsubscribed from channels:', channels);
    }
  }, [socket, isConnected]);

  const updateFilters = useCallback((filters: any) => {
    if (socket && isConnected) {
      socket.emit('filter_update', filters);
      console.log('Updated filters:', filters);
    }
  }, [socket, isConnected]);

  const value = {
    socket,
    isConnected,
    connectionStatus,
    subscribe,
    unsubscribe,
    updateFilters,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}