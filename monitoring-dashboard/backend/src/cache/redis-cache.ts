import Redis from 'ioredis';
import { logger } from '../utils/logger';

export interface CacheService {
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  get<T>(key: string): Promise<T | null>;
  set(key: string, value: any, ttlSeconds?: number): Promise<void>;
  del(key: string): Promise<void>;
  exists(key: string): Promise<boolean>;
  keys(pattern: string): Promise<string[]>;
  flush(): Promise<void>;
  increment(key: string, value?: number): Promise<number>;
  expire(key: string, ttlSeconds: number): Promise<void>;
}

class RedisCacheService implements CacheService {
  private client: Redis;
  private isConnected = false;

  constructor() {
    const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';

    this.client = new Redis(redisUrl, {
      retryDelayOnFailover: 100,
      maxRetriesPerRequest: 3,
      lazyConnect: true,
      reconnectOnError: (err) => {
        const targetError = 'READONLY';
        return err.message.includes(targetError);
      }
    });

    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    this.client.on('connect', () => {
      logger.info('Redis client connected');
      this.isConnected = true;
    });

    this.client.on('ready', () => {
      logger.info('Redis client ready');
    });

    this.client.on('error', (error) => {
      logger.error('Redis client error:', error);
      this.isConnected = false;
    });

    this.client.on('close', () => {
      logger.warn('Redis client disconnected');
      this.isConnected = false;
    });

    this.client.on('reconnecting', () => {
      logger.info('Redis client reconnecting');
    });
  }

  async connect(): Promise<void> {
    try {
      await this.client.connect();
      this.isConnected = true;
      logger.info('Redis cache service connected');
    } catch (error) {
      logger.error('Failed to connect to Redis:', error);
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    try {
      await this.client.disconnect();
      this.isConnected = false;
      logger.info('Redis cache service disconnected');
    } catch (error) {
      logger.error('Error disconnecting from Redis:', error);
    }
  }

  async get<T>(key: string): Promise<T | null> {
    try {
      if (!this.isConnected) {
        logger.warn('Redis not connected, skipping cache get');
        return null;
      }

      const value = await this.client.get(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      logger.error(`Error getting cache key ${key}:`, error);
      return null;
    }
  }

  async set(key: string, value: any, ttlSeconds?: number): Promise<void> {
    try {
      if (!this.isConnected) {
        logger.warn('Redis not connected, skipping cache set');
        return;
      }

      const serializedValue = JSON.stringify(value);

      if (ttlSeconds) {
        await this.client.setex(key, ttlSeconds, serializedValue);
      } else {
        await this.client.set(key, serializedValue);
      }
    } catch (error) {
      logger.error(`Error setting cache key ${key}:`, error);
    }
  }

  async del(key: string): Promise<void> {
    try {
      if (!this.isConnected) {
        logger.warn('Redis not connected, skipping cache delete');
        return;
      }

      await this.client.del(key);
    } catch (error) {
      logger.error(`Error deleting cache key ${key}:`, error);
    }
  }

  async exists(key: string): Promise<boolean> {
    try {
      if (!this.isConnected) {
        return false;
      }

      const result = await this.client.exists(key);
      return result === 1;
    } catch (error) {
      logger.error(`Error checking cache key ${key}:`, error);
      return false;
    }
  }

  async keys(pattern: string): Promise<string[]> {
    try {
      if (!this.isConnected) {
        return [];
      }

      return await this.client.keys(pattern);
    } catch (error) {
      logger.error(`Error getting cache keys with pattern ${pattern}:`, error);
      return [];
    }
  }

  async flush(): Promise<void> {
    try {
      if (!this.isConnected) {
        logger.warn('Redis not connected, skipping cache flush');
        return;
      }

      await this.client.flushall();
      logger.info('Cache flushed');
    } catch (error) {
      logger.error('Error flushing cache:', error);
    }
  }

  async increment(key: string, value: number = 1): Promise<number> {
    try {
      if (!this.isConnected) {
        logger.warn('Redis not connected, skipping cache increment');
        return 0;
      }

      return await this.client.incrby(key, value);
    } catch (error) {
      logger.error(`Error incrementing cache key ${key}:`, error);
      return 0;
    }
  }

  async expire(key: string, ttlSeconds: number): Promise<void> {
    try {
      if (!this.isConnected) {
        logger.warn('Redis not connected, skipping cache expire');
        return;
      }

      await this.client.expire(key, ttlSeconds);
    } catch (error) {
      logger.error(`Error setting expiry for cache key ${key}:`, error);
    }
  }
}

// In-memory fallback cache for development
class InMemoryCacheService implements CacheService {
  private cache = new Map<string, { value: any; expires?: number }>();

  async connect(): Promise<void> {
    logger.info('In-memory cache service connected');
  }

  async disconnect(): Promise<void> {
    this.cache.clear();
    logger.info('In-memory cache service disconnected');
  }

  async get<T>(key: string): Promise<T | null> {
    const item = this.cache.get(key);

    if (!item) {
      return null;
    }

    if (item.expires && Date.now() > item.expires) {
      this.cache.delete(key);
      return null;
    }

    return item.value;
  }

  async set(key: string, value: any, ttlSeconds?: number): Promise<void> {
    const expires = ttlSeconds ? Date.now() + (ttlSeconds * 1000) : undefined;
    this.cache.set(key, { value, expires });
  }

  async del(key: string): Promise<void> {
    this.cache.delete(key);
  }

  async exists(key: string): Promise<boolean> {
    const exists = this.cache.has(key);

    if (exists) {
      const item = this.cache.get(key);
      if (item?.expires && Date.now() > item.expires) {
        this.cache.delete(key);
        return false;
      }
    }

    return exists;
  }

  async keys(pattern: string): Promise<string[]> {
    const regex = new RegExp(pattern.replace(/\*/g, '.*'));
    return Array.from(this.cache.keys()).filter(key => regex.test(key));
  }

  async flush(): Promise<void> {
    this.cache.clear();
  }

  async increment(key: string, value: number = 1): Promise<number> {
    const current = await this.get<number>(key) || 0;
    const newValue = current + value;
    await this.set(key, newValue);
    return newValue;
  }

  async expire(key: string, ttlSeconds: number): Promise<void> {
    const item = this.cache.get(key);
    if (item) {
      item.expires = Date.now() + (ttlSeconds * 1000);
    }
  }
}

// Export cache service instance
export const cacheService: CacheService = process.env.NODE_ENV === 'production' || process.env.REDIS_URL
  ? new RedisCacheService()
  : new InMemoryCacheService();