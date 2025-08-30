/**
 * Store Index
 * 
 * Central export point for all Pinia stores
 */

// Export all stores
export { useTaskStore } from './task.store'

// Re-export types for convenience
export type { TaskStoreState } from './task.store'

// Export common types
export type {
  LoadingState,
  ErrorState,
  AppState
} from '@/types/common.types'

export type {
  Task,
  SingleResult,
  BatchResult,
  TaskType,
  TaskStatus,
  SentimentType
} from '@/types/api.types'
