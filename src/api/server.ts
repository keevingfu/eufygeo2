import express, { Application, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import compression from 'compression';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import rateLimit from 'express-rate-limit';

// Load environment variables
dotenv.config();

// Import configurations and routes
import { db, redis, closeDatabaseConnections } from './config/database';
import keywordsRouter from './routes/keywords';
import contentRouter from './routes/content';
import analyticsRouter from './routes/analytics';
import authRouter from './routes/auth';
import { errorHandler } from './middleware/errorHandler';
import { authenticate } from './middleware/auth';
import { RealtimeService } from './services/realtime.service';

// Initialize Express app
const app: Application = express();
const PORT = process.env.PORT || 5001;
const API_PREFIX = process.env.API_PREFIX || '/api/v1';

// Create HTTP server for Socket.IO
const httpServer = createServer(app);

// Initialize Socket.IO
const io = new SocketIOServer(httpServer, {
  cors: {
    origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
    credentials: true
  }
});

// Initialize realtime service
export const realtimeService = new RealtimeService(io);

// Security middleware
app.use(helmet({
  crossOriginResourcePolicy: { policy: "cross-origin" }
}));

// CORS configuration
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  credentials: true,
  optionsSuccessStatus: 200
}));

// Request parsing middleware
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Logging
if (process.env.NODE_ENV === 'development') {
  app.use(morgan('dev'));
} else {
  app.use(morgan('combined'));
}

// Rate limiting
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});

const expensiveLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 10, // Limit each IP to 10 requests per hour
  skipSuccessfulRequests: false,
});

// Apply rate limiting to API routes
app.use(API_PREFIX, apiLimiter);

// Health check endpoints
app.get('/health', (req: Request, res: Response) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'development'
  });
});

app.get('/ready', async (req: Request, res: Response) => {
  try {
    // Check database connection
    await db.query('SELECT 1');
    
    // Check Redis connection
    await redis.ping();
    
    res.json({ 
      status: 'ready',
      services: {
        database: 'connected',
        redis: 'connected'
      }
    });
  } catch (error) {
    res.status(503).json({ 
      status: 'not ready',
      error: error.message 
    });
  }
});

// API routes
app.use(`${API_PREFIX}/auth`, authRouter);
app.use(`${API_PREFIX}/keywords`, authenticate, keywordsRouter);
app.use(`${API_PREFIX}/content`, authenticate, contentRouter);
app.use(`${API_PREFIX}/analytics`, authenticate, analyticsRouter);

// Apply expensive rate limiter to specific routes
app.use(`${API_PREFIX}/keywords/bulk-import`, expensiveLimiter);
app.use(`${API_PREFIX}/analytics/generate-report`, expensiveLimiter);

// Static files (for uploaded content)
app.use('/uploads', express.static('uploads'));

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({ 
    error: { 
      message: 'Not Found', 
      status: 404,
      path: req.originalUrl
    } 
  });
});

// Error handling middleware (must be last)
app.use(errorHandler);

// Start server
httpServer.listen(PORT, () => {
  console.log(`
🚀 Eufy GEO Platform API Server
================================
🌍 Environment: ${process.env.NODE_ENV || 'development'}
📡 API URL: http://localhost:${PORT}${API_PREFIX}
🔌 WebSocket: ws://localhost:${PORT}
📊 Health: http://localhost:${PORT}/health
================================
  `);
});

// Graceful shutdown
const gracefulShutdown = async (signal: string) => {
  console.log(`\n${signal} received. Starting graceful shutdown...`);
  
  // Stop accepting new connections
  httpServer.close(() => {
    console.log('HTTP server closed');
  });
  
  // Close database connections
  await closeDatabaseConnections();
  
  // Exit process
  process.exit(0);
};

// Handle shutdown signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  gracefulShutdown('UNCAUGHT_EXCEPTION');
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  gracefulShutdown('UNHANDLED_REJECTION');
});

export { app, httpServer };