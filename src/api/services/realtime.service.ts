import { Server as SocketIOServer, Socket } from 'socket.io';
import jwt from 'jsonwebtoken';
import { JWTPayload, UserRole } from '../../types';

interface AuthenticatedSocket extends Socket {
  user?: JWTPayload;
}

export class RealtimeService {
  private io: SocketIOServer;
  private userSockets: Map<string, Set<string>> = new Map(); // userId -> socketIds
  private roomSubscriptions: Map<string, Set<string>> = new Map(); // room -> socketIds

  constructor(io: SocketIOServer) {
    this.io = io;
    this.setupMiddleware();
    this.setupEventHandlers();
  }

  // Setup authentication middleware
  private setupMiddleware() {
    this.io.use(async (socket: AuthenticatedSocket, next) => {
      try {
        const token = socket.handshake.auth.token || socket.handshake.headers.authorization?.split(' ')[1];
        
        if (!token) {
          return next(new Error('Authentication required'));
        }

        const decoded = jwt.verify(
          token,
          process.env.JWT_SECRET || 'dev-secret'
        ) as JWTPayload;

        socket.user = decoded;
        next();
      } catch (error) {
        next(new Error('Invalid token'));
      }
    });
  }

  // Setup event handlers
  private setupEventHandlers() {
    this.io.on('connection', (socket: AuthenticatedSocket) => {
      console.log(`User ${socket.user?.email} connected via WebSocket`);

      // Track user socket
      if (socket.user) {
        this.addUserSocket(socket.user.userId, socket.id);
      }

      // Join user to their personal room
      socket.join(`user:${socket.user?.userId}`);

      // Handle room subscriptions
      socket.on('subscribe', (room: string) => {
        if (this.canSubscribeToRoom(socket.user, room)) {
          socket.join(room);
          this.addRoomSubscription(room, socket.id);
          socket.emit('subscribed', { room });
        } else {
          socket.emit('subscription_error', { room, error: 'Insufficient permissions' });
        }
      });

      socket.on('unsubscribe', (room: string) => {
        socket.leave(room);
        this.removeRoomSubscription(room, socket.id);
        socket.emit('unsubscribed', { room });
      });

      // Handle keyword operations
      socket.on('keyword:update', async (data: any) => {
        if (this.canPerformAction(socket.user, 'keyword:update')) {
          // Broadcast to all clients in keyword room
          socket.to('keywords').emit('keyword:updated', data);
        }
      });

      // Handle content operations
      socket.on('content:update', async (data: any) => {
        if (this.canPerformAction(socket.user, 'content:update')) {
          socket.to('content').emit('content:updated', data);
        }
      });

      // Handle analytics updates
      socket.on('analytics:request', async (data: any) => {
        if (this.canPerformAction(socket.user, 'analytics:view')) {
          // Send analytics data to requesting user
          socket.emit('analytics:data', {
            // Analytics data would be fetched here
            timestamp: new Date()
          });
        }
      });

      // Handle disconnection
      socket.on('disconnect', () => {
        console.log(`User ${socket.user?.email} disconnected from WebSocket`);
        
        if (socket.user) {
          this.removeUserSocket(socket.user.userId, socket.id);
        }

        // Clean up room subscriptions
        this.cleanupSocketSubscriptions(socket.id);
      });

      // Error handling
      socket.on('error', (error) => {
        console.error('WebSocket error:', error);
      });
    });
  }

  // Broadcast keyword updates to all connected clients
  broadcastKeywordUpdate(action: string, data: any) {
    this.io.to('keywords').emit('keyword:update', {
      action,
      data,
      timestamp: new Date()
    });
  }

  // Broadcast content updates
  broadcastContentUpdate(action: string, data: any) {
    this.io.to('content').emit('content:update', {
      action,
      data,
      timestamp: new Date()
    });
  }

  // Broadcast import progress
  broadcastImportProgress(progress: {
    total: number;
    processed: number;
    success: number;
    failed: number;
  }) {
    this.io.to('import:progress').emit('import:progress', progress);
  }

  // Send notification to specific user
  sendToUser(userId: string, event: string, data: any) {
    const socketIds = this.userSockets.get(userId);
    
    if (socketIds) {
      socketIds.forEach(socketId => {
        this.io.to(socketId).emit(event, data);
      });
    }
  }

  // Send notification to users with specific role
  sendToRole(role: UserRole, event: string, data: any) {
    this.io.sockets.sockets.forEach((socket: AuthenticatedSocket) => {
      if (socket.user && socket.user.role === role) {
        socket.emit(event, data);
      }
    });
  }

  // Analytics real-time updates
  broadcastAnalyticsUpdate(metric: string, data: any) {
    this.io.to('analytics').emit('analytics:update', {
      metric,
      data,
      timestamp: new Date()
    });
  }

  // Report generation progress
  broadcastReportProgress(reportId: string, progress: number, status: string) {
    this.io.to(`report:${reportId}`).emit('report:progress', {
      reportId,
      progress,
      status,
      timestamp: new Date()
    });
  }

  // Private helper methods
  private canSubscribeToRoom(user: JWTPayload | undefined, room: string): boolean {
    if (!user) return false;

    // Room permission mapping
    const roomPermissions: Record<string, UserRole[]> = {
      'keywords': ['admin', 'manager', 'analyst', 'viewer'],
      'content': ['admin', 'manager', 'analyst'],
      'analytics': ['admin', 'manager', 'analyst', 'viewer'],
      'import:progress': ['admin', 'manager'],
      'reports': ['admin', 'manager', 'analyst']
    };

    const allowedRoles = roomPermissions[room];
    return allowedRoles ? allowedRoles.includes(user.role) : false;
  }

  private canPerformAction(user: JWTPayload | undefined, action: string): boolean {
    if (!user) return false;

    // Action permission mapping
    const actionPermissions: Record<string, UserRole[]> = {
      'keyword:update': ['admin', 'manager'],
      'content:update': ['admin', 'manager'],
      'analytics:view': ['admin', 'manager', 'analyst', 'viewer'],
      'report:generate': ['admin', 'manager', 'analyst']
    };

    const allowedRoles = actionPermissions[action];
    return allowedRoles ? allowedRoles.includes(user.role) : false;
  }

  private addUserSocket(userId: string, socketId: string) {
    if (!this.userSockets.has(userId)) {
      this.userSockets.set(userId, new Set());
    }
    this.userSockets.get(userId)!.add(socketId);
  }

  private removeUserSocket(userId: string, socketId: string) {
    const sockets = this.userSockets.get(userId);
    
    if (sockets) {
      sockets.delete(socketId);
      
      if (sockets.size === 0) {
        this.userSockets.delete(userId);
      }
    }
  }

  private addRoomSubscription(room: string, socketId: string) {
    if (!this.roomSubscriptions.has(room)) {
      this.roomSubscriptions.set(room, new Set());
    }
    this.roomSubscriptions.get(room)!.add(socketId);
  }

  private removeRoomSubscription(room: string, socketId: string) {
    const sockets = this.roomSubscriptions.get(room);
    
    if (sockets) {
      sockets.delete(socketId);
      
      if (sockets.size === 0) {
        this.roomSubscriptions.delete(room);
      }
    }
  }

  private cleanupSocketSubscriptions(socketId: string) {
    this.roomSubscriptions.forEach((sockets, room) => {
      sockets.delete(socketId);
      
      if (sockets.size === 0) {
        this.roomSubscriptions.delete(room);
      }
    });
  }

  // Get connected users count
  getConnectedUsersCount(): number {
    return this.userSockets.size;
  }

  // Get room subscribers count
  getRoomSubscribersCount(room: string): number {
    return this.roomSubscriptions.get(room)?.size || 0;
  }

  // Get all active rooms
  getActiveRooms(): string[] {
    return Array.from(this.roomSubscriptions.keys());
  }
}