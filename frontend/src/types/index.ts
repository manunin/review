// Export new API types (task-based architecture)
export type {
  Task,
  SingleResult,
  BatchResult,
  TaskError,
  SentimentType,
  TaskType,
  TaskStatus,
  TaskErrorCode,
  SingleTaskRequest,
  BatchTaskRequest,
  TaskResultRequest,
  ApiResponse,
  ApiErrorResponse,
  ValidationError
} from './api.types'

// Export common types
export type {
  LoadingState,
  ErrorState,
  AppState,
  EnvironmentConfig,
  Nullable,
  Optional,
  DeepReadonly,
  PaginationMeta,
  PaginatedResponse
} from './common.types'

// Legacy API Response Types (for backward compatibility)
export interface ReviewAnalysis {
  sentiment: 'positive' | 'negative' | 'neutral'
  confidence: number
  text?: string
}

export interface Review {
  id: string
  text: string
  sentiment: 'positive' | 'negative' | 'neutral'
  confidence: number
  created_at: string
}

export interface Analytics {
  total_reviews: number
  positive: number
  negative: number
  neutral: number
  positive_percentage: number
  negative_percentage: number
  neutral_percentage: number
}

export interface UploadResult {
  success: boolean
  message: string
  processed_count?: number
  results?: ReviewAnalysis[]
}

// Store State Types
export interface ReviewStoreState {
  reviews: Review[]
  analytics: Analytics
  loading: boolean
  error: string | null
}

// Legacy API Error Response (for backward compatibility)
export interface ApiError {
  message: string
  details?: Record<string, unknown>
}
