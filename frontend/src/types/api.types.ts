/**
 * API Types based on OpenAPI specification
 * Corresponds to schemas defined in api/openapi.yml
 */

export type TaskType = 'single' | 'batch'
export type TaskStatus = 'accepted' | 'queued' | 'ready' | 'error'
export type SentimentType = 'positive' | 'negative' | 'neutral'
export type TaskErrorCode = '01' | '02' | '03'

export interface Task {
  task_id: string
  type: TaskType
  status: TaskStatus
  start: number
  end?: number
  result?: SingleResult | BatchResult
  error?: TaskError
}

export interface SingleResult {
  sentiment: SentimentType
  confidence: number
  text?: string
}

export interface BatchResult {
  total_reviews: number
  positive: number
  negative: number
  neutral: number
  positive_percentage: number
  negative_percentage: number
  neutral_percentage: number
}

export interface TaskError {
  code: TaskErrorCode
  description?: string
}

export interface ApiError {
  message: string
  details?: Record<string, any>
}

export interface ValidationError {
  message: string
  details?: Record<string, string[]>
}

// Request types
export interface SingleTaskRequest {
  user_id: string
  text: string
}

export interface BatchTaskRequest {
  user_id: string
  file: File
}

export interface TaskResultRequest {
  user_id: string
}

// API Response types
export type ApiResponse<T> = {
  data: T
  status: number
  statusText: string
}

export type ApiErrorResponse = {
  data: ApiError | ValidationError
  status: number
  statusText: string
}
