// Date utilities
export const formatDate = (date: string | Date): string => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const formatDuration = (milliseconds: number): string => {
  if (milliseconds < 1000) {
    return `${milliseconds}ms`;
  }

  const seconds = milliseconds / 1000;
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }

  const minutes = seconds / 60;
  if (minutes < 60) {
    return `${minutes.toFixed(1)}m`;
  }

  const hours = minutes / 60;
  return `${hours.toFixed(1)}h`;
};

export const formatRelativeTime = (date: string | Date): string => {
  const now = new Date().getTime();
  const then = new Date(date).getTime();
  const diff = now - then;

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) {
    return `${days} day${days !== 1 ? 's' : ''} ago`;
  }
  if (hours > 0) {
    return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
  }
  if (minutes > 0) {
    return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
  }
  return `${seconds} second${seconds !== 1 ? 's' : ''} ago`;
};

export const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';

  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

export const formatPercentage = (value: number, total?: number): string => {
  if (total !== undefined) {
    return `${((value / total) * 100).toFixed(1)}%`;
  }
  return `${value.toFixed(1)}%`;
};

// Status and trend formatters
export const getTrendIcon = (trend: string): string => {
  switch (trend) {
    case 'improving':
    case 'up':
      return '↗️';
    case 'degrading':
    case 'down':
      return '↘️';
    case 'stable':
    default:
      return '→';
  }
};

export const getTrendColor = (trend: string): string => {
  switch (trend) {
    case 'improving':
    case 'up':
      return 'text-success';
    case 'degrading':
    case 'down':
      return 'text-error';
    case 'stable':
    default:
      return 'text-muted-foreground';
  }
};

export const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    passed: 'text-success',
    failed: 'text-error',
    skipped: 'text-warning',
    running: 'text-info',
    pending: 'text-muted-foreground',
    resolved: 'text-success',
    unresolved: 'text-error',
    critical: 'text-error',
    high: 'text-destructive',
    medium: 'text-warning',
    low: 'text-info'
  };
  return colors[status] || 'text-muted-foreground';
};

export const getCoverageColor = (percentage: number): string => {
  if (percentage >= 90) return 'text-success';
  if (percentage >= 80) return 'text-info';
  if (percentage >= 70) return 'text-warning';
  return 'text-error';
};

export const getCoverageLevel = (percentage: number): string => {
  if (percentage >= 90) return 'excellent';
  if (percentage >= 80) return 'good';
  if (percentage >= 70) return 'fair';
  return 'poor';
};

// Chart data formatters
export const formatChartValue = (value: number, type: string): string => {
  switch (type) {
    case 'percentage':
      return `${value.toFixed(1)}%`;
    case 'duration':
      return formatDuration(value);
    case 'bytes':
      return formatBytes(value);
    case 'number':
      return formatNumber(value);
    default:
      return value.toFixed(2);
  }
};

// URL and slug formatters
export const slugify = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

export const capitalize = (text: string): string => {
  return text.charAt(0).toUpperCase() + text.slice(1);
};

export const camelCaseToTitle = (text: string): string => {
  return text
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase())
    .trim();
};