/**
 * Common types and interfaces used throughout the application
 */

export interface LoadingState {
  isLoading: boolean
  message?: string | undefined
}

export interface ErrorState {
  hasError: boolean
  message?: string | undefined
  details?: Record<string, any> | undefined
}

export interface AppState {
  loading: LoadingState
  error: ErrorState
}

// Utility types
export type Nullable<T> = T | null
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P]
}

// Environment configuration
export interface EnvironmentConfig {
  apiBaseUrl: string
  mockEnabled: boolean
  debugMode: boolean
  logLevel: 'info' | 'warn' | 'error' | 'debug'
}

// Generic API pagination (for future use)
export interface PaginationMeta {
  page: number
  limit: number
  total: number
  totalPages: number
}

export interface PaginatedResponse<T> {
  data: T[]
  meta: PaginationMeta
}
