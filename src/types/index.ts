// Shared TypeScript type definitions for Eufy GEO Platform

// Keyword related types
export interface Keyword {
  id: number;
  keyword: string;
  search_volume: number;
  difficulty: number;
  cpc: number;
  competition: number;
  priority_tier: PriorityTier;
  aio_status: AIOStatus;
  current_rank: number | null;
  previous_rank: number | null;
  traffic: number;
  traffic_value: number;
  product_category: string | null;
  user_intent: UserIntent | null;
  metadata?: Record<string, any>;
  created_at: Date;
  updated_at: Date;
  // Computed fields
  content_count?: number;
  avg_position_30d?: number;
  clicks_30d?: number;
}

export type PriorityTier = 'P0' | 'P1' | 'P2' | 'P3' | 'P4';
export type AIOStatus = 'active' | 'inactive' | 'monitoring';
export type UserIntent = 'informational' | 'transactional' | 'navigational' | 'commercial';

// Content related types
export interface Content {
  id: string;
  title: string;
  slug?: string;
  type: ContentType;
  status: ContentStatus;
  content_brief?: string;
  content_body?: string;
  meta_title?: string;
  meta_description?: string;
  target_keywords?: number[];
  channel: string;
  metadata?: Record<string, any>;
  created_by: string;
  published_at?: Date;
  version?: number;
  ai_generated?: boolean;
  created_at: Date;
  updated_at: Date;
  // Relations
  author_name?: string;
  keywords?: Keyword[];
  keyword_count?: number;
  total_impressions?: number;
  total_clicks?: number;
}

export type ContentType = 'article' | 'video' | 'social';
export type ContentStatus = 'draft' | 'published' | 'scheduled';

// User types
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  is_active: boolean;
  created_at: Date;
  updated_at: Date;
  last_login?: Date;
}

export type UserRole = 'admin' | 'manager' | 'analyst' | 'viewer';

// Analytics types
export interface KeywordPerformance {
  keyword_id: number;
  date: Date;
  impressions: number;
  clicks: number;
  ctr: number;
  position: number;
  aio_appearances: number;
  traffic_value: number;
}

export interface AnalyticsSummary {
  total_keywords: number;
  aio_coverage_rate: number;
  total_traffic: number;
  total_revenue: number;
  avg_position: number;
  conversion_rate: number;
}

// API Request/Response types
export interface PaginationParams {
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface KeywordFilters extends PaginationParams {
  priority_tier?: PriorityTier;
  aio_status?: AIOStatus;
  product_category?: string;
  min_volume?: number;
  max_volume?: number;
  search?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

// Import/Export types
export interface ImportResult {
  total: number;
  imported: number;
  updated: number;
  errors: ImportError[];
  jobId?: string;
  status: 'processing' | 'completed' | 'failed';
}

export interface ImportError {
  row: number;
  error: string;
  data?: any;
}

// Dashboard types
export interface PyramidData {
  tiers: {
    priority_tier: PriorityTier;
    count: number;
    avg_volume: number;
    total_traffic: number;
    aio_active_count: number;
  }[];
  summary: {
    total_keywords: number;
    total_traffic: number;
    aio_coverage: number;
  };
}

// WebSocket event types
export interface RealtimeEvent {
  type: 'keyword:updated' | 'analytics:updated' | 'import:progress' | 'content:published';
  data: any;
  timestamp: Date;
}

// Auth types
export interface JWTPayload {
  userId: string;
  email: string;
  role: UserRole;
}

// Additional types for server
export interface ImportProgress {
  total: number;
  processed: number;
  success: number;
  failed: number;
}

export interface WSKeywordUpdate {
  action: 'created' | 'updated' | 'deleted';
  data: Partial<Keyword>;
  timestamp: Date;
}

export interface WSContentUpdate {
  action: 'created' | 'updated' | 'deleted';
  data: Partial<Content>;
  timestamp: Date;
}

export interface WSAnalyticsUpdate {
  metric: string;
  data: any;
  timestamp: Date;
}

export interface WSReportProgress {
  reportId: string;
  progress: number;
  status: string;
  timestamp: Date;
}

export interface ContentPerformance {
  content_id: string;
  date: Date;
  impressions: number;
  clicks: number;
  ctr: number;
  engagement_rate: number;
  conversions?: number;
}

export interface AnalyticsReport {
  id: string;
  name: string;
  type: 'keyword_performance' | 'content_performance' | 'channel_analysis' | 'custom';
  config: Record<string, any>;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: any;
  error?: string;
  created_by: string;
  created_at: Date;
  completed_at?: Date;
}