import React from 'react';
import { Wifi, WifiOff, RotateCcw } from 'lucide-react';
import { cn } from '../../utils/cn';

interface ConnectionStatusProps {
  isConnected: boolean;
  status: 'connected' | 'disconnected' | 'reconnecting';
  className?: string;
}

export function ConnectionStatus({ isConnected, status, className }: ConnectionStatusProps) {
  const getIcon = () => {
    switch (status) {
      case 'connected':
        return <Wifi className="h-4 w-4" />;
      case 'reconnecting':
        return <RotateCcw className="h-4 w-4 animate-spin" />;
      case 'disconnected':
      default:
        return <WifiOff className="h-4 w-4" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'text-success';
      case 'reconnecting':
        return 'text-warning';
      case 'disconnected':
      default:
        return 'text-error';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'Real-time connected';
      case 'reconnecting':
        return 'Reconnecting...';
      case 'disconnected':
      default:
        return 'Real-time disconnected';
    }
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className={cn('flex items-center', getStatusColor())}>
        {getIcon()}
      </div>
      <span className={cn('text-xs hidden sm:block', getStatusColor())}>
        {getStatusText()}
      </span>
      {status === 'connected' && (
        <div className="pulse-dot relative">
          <div className="absolute inset-0 bg-success rounded-full animate-ping opacity-75" />
        </div>
      )}
    </div>
  );
}