import { Pool, PoolConfig } from 'pg';
import Redis from 'ioredis';
import dotenv from 'dotenv';

dotenv.config();

// PostgreSQL configuration
const pgConfig: PoolConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'eufy_geo',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'postgres',
  max: 20, // Maximum number of clients in the pool
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
};

// Create PostgreSQL pool
export const db = new Pool(pgConfig);

// Test database connection
db.on('connect', () => {
  console.log('✅ PostgreSQL connected');
});

db.on('error', (err) => {
  console.error('❌ PostgreSQL error:', err);
});

// Redis configuration
export const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
  maxRetriesPerRequest: 3,
  enableReadyCheck: true,
  lazyConnect: false,
  showFriendlyErrorStack: process.env.NODE_ENV === 'development',
});

redis.on('connect', () => {
  console.log('✅ Redis connected');
});

redis.on('error', (err) => {
  console.error('❌ Redis error:', err);
});

// Graceful shutdown
export const closeDatabaseConnections = async () => {
  await db.end();
  redis.disconnect();
  console.log('Database connections closed');
};