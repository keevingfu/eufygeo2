import { Router, Request, Response } from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import { db } from '../config/database';
import { asyncHandler } from '../middleware/errorHandler';
import { JWTPayload, UserRole } from '../../types';

const router = Router();

// Validation schemas
const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6)
});

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).regex(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
    'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
  ),
  name: z.string().min(2),
  role: z.enum(['viewer', 'analyst', 'manager', 'admin']).optional()
});

const refreshSchema = z.object({
  refreshToken: z.string()
});

// Helper function to generate tokens
function generateTokens(userId: string, email: string, role: UserRole) {
  const payload: JWTPayload = { userId, email, role };
  
  const accessToken = jwt.sign(
    payload,
    process.env.JWT_SECRET || 'dev-secret',
    { expiresIn: process.env.JWT_EXPIRES_IN || '1h' }
  );
  
  const refreshToken = jwt.sign(
    payload,
    process.env.JWT_REFRESH_SECRET || 'dev-refresh-secret',
    { expiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d' }
  );
  
  return { accessToken, refreshToken };
}

// POST /auth/register - Register new user
router.post('/register', asyncHandler(async (req: Request, res: Response) => {
  const data = registerSchema.parse(req.body);
  
  // Check if user already exists
  const existingUser = await db.query(
    'SELECT id FROM users WHERE email = $1',
    [data.email]
  );
  
  if (existingUser.rows.length > 0) {
    return res.status(409).json({ error: 'User already exists' });
  }
  
  // Hash password
  const hashedPassword = await bcrypt.hash(data.password, 10);
  
  // Create user
  const query = `
    INSERT INTO users (email, password_hash, name, role)
    VALUES ($1, $2, $3, $4)
    RETURNING id, email, name, role, created_at
  `;
  
  const values = [
    data.email,
    hashedPassword,
    data.name,
    data.role || 'viewer'
  ];
  
  const result = await db.query(query, values);
  const user = result.rows[0];
  
  // Generate tokens
  const tokens = generateTokens(user.id, user.email, user.role);
  
  res.status(201).json({
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
      role: user.role
    },
    ...tokens
  });
}));

// POST /auth/login - Login user
router.post('/login', asyncHandler(async (req: Request, res: Response) => {
  const data = loginSchema.parse(req.body);
  
  // Find user
  const query = 'SELECT * FROM users WHERE email = $1';
  const result = await db.query(query, [data.email]);
  
  if (result.rows.length === 0) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  const user = result.rows[0];
  
  // Verify password
  const isValidPassword = await bcrypt.compare(data.password, user.password_hash);
  
  if (!isValidPassword) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  // Update last login
  await db.query(
    'UPDATE users SET last_login = NOW() WHERE id = $1',
    [user.id]
  );
  
  // Generate tokens
  const tokens = generateTokens(user.id, user.email, user.role);
  
  res.json({
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
      role: user.role
    },
    ...tokens
  });
}));

// POST /auth/refresh - Refresh access token
router.post('/refresh', asyncHandler(async (req: Request, res: Response) => {
  const data = refreshSchema.parse(req.body);
  
  try {
    // Verify refresh token
    const decoded = jwt.verify(
      data.refreshToken,
      process.env.JWT_REFRESH_SECRET || 'dev-refresh-secret'
    ) as JWTPayload;
    
    // Check if user still exists and is active
    const result = await db.query(
      'SELECT id, email, role FROM users WHERE id = $1 AND is_active = true',
      [decoded.userId]
    );
    
    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid refresh token' });
    }
    
    const user = result.rows[0];
    
    // Generate new tokens
    const tokens = generateTokens(user.id, user.email, user.role);
    
    res.json(tokens);
  } catch (error) {
    res.status(401).json({ error: 'Invalid refresh token' });
  }
}));

// POST /auth/logout - Logout user (optional: blacklist token)
router.post('/logout', asyncHandler(async (req: Request, res: Response) => {
  // In a production environment, you might want to blacklist the token
  // For now, we'll just return success and let the client discard the token
  res.json({ message: 'Logged out successfully' });
}));

export default router;