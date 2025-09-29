import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '../../utils/cn';

interface MetricCardProps {
  title: string;
  value: string;
  change?: 'improving' | 'degrading' | 'stable';
  changeValue?: string;
  icon: LucideIcon;
  color?: 'success' | 'warning' | 'error' | 'info';
  className?: string;
}

export function MetricCard({
  title,
  value,
  change = 'stable',
  changeValue,
  icon: Icon,
  color = 'info',
  className
}: MetricCardProps) {
  const getTrendIcon = () => {
    switch (change) {
      case 'improving':
        return <TrendingUp className="h-4 w-4" />;
      case 'degrading':
        return <TrendingDown className="h-4 w-4" />;
      case 'stable':
      default:
        return <Minus className="h-4 w-4" />;
    }
  };

  const getTrendColor = () => {
    switch (change) {
      case 'improving':
        return 'text-success';
      case 'degrading':
        return 'text-error';
      case 'stable':
      default:
        return 'text-muted-foreground';
    }
  };

  const getIconColor = () => {
    switch (color) {
      case 'success':
        return 'text-success';
      case 'warning':
        return 'text-warning';
      case 'error':
        return 'text-error';
      case 'info':
      default:
        return 'text-info';
    }
  };

  return (
    <div className={cn('metric-card', className)}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-muted-foreground mb-1">
            {title}
          </p>
          <p className="text-2xl font-bold tracking-tight">
            {value}
          </p>
          {changeValue && (
            <div className={cn('flex items-center gap-1 mt-2 text-sm', getTrendColor())}>
              {getTrendIcon()}
              <span>{changeValue}</span>
              <span className="text-muted-foreground">vs last period</span>
            </div>
          )}
        </div>
        <div className={cn('p-2 rounded-lg bg-muted/20', getIconColor())}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}