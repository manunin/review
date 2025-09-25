/**
 * Task Store
 * Pinia store for task-based operations using the new API architecture
 */

import { defineStore } from 'pinia'
import { taskService } from '@/services/task.service'
import type { 
  Task, 
  SingleResult, 
  BatchResult
} from '@/types/api.types'
import type { 
  LoadingState, 
  ErrorState 
} from '@/types/common.types'

export interface TaskStoreState {
  // Results
  lastSingleResult: SingleResult | null
  lastBatchResult: BatchResult | null
  
  // Current task IDs for polling
  currentSingleTaskId: string | null
  currentBatchTaskId: string | null
  
  // UI State
  loading: LoadingState
  error: ErrorState
  
  // Development mode flag
  mockMode: boolean
}

export const useTaskStore = defineStore('tasks', {
  state: (): TaskStoreState => ({
    lastSingleResult: null,
    lastBatchResult: null,
    currentSingleTaskId: null,
    currentBatchTaskId: null,
    loading: {
      isLoading: false,
      message: undefined
    },
    error: {
      hasError: false,
      message: undefined,
      details: undefined
    },
    mockMode: taskService.isMockMode()
  }),

  getters: {
    // Loading state
    isLoading: (state): boolean => state.loading.isLoading,
    loadingMessage: (state): string | undefined => state.loading.message,
    
    // Error state
    hasError: (state): boolean => state.error.hasError,
    errorMessage: (state): string | undefined => state.error.message,
    errorDetails: (state): Record<string, any> | undefined => state.error.details,
    
    // Results availability
    hasSingleResult: (state): boolean => state.lastSingleResult !== null,
    hasBatchResult: (state): boolean => state.lastBatchResult !== null,
    
    // Current task IDs
    getCurrentSingleTaskId: (state): string | null => state.currentSingleTaskId,
    getCurrentBatchTaskId: (state): string | null => state.currentBatchTaskId,
    
    // Analytics from batch result
    getAnalyticsData: (state) => {
      if (!state.lastBatchResult) {
        return {
          total_reviews: 0,
          positive: 0,
          negative: 0,
          neutral: 0,
          positive_percentage: 0,
          negative_percentage: 0,
          neutral_percentage: 0
        }
      }
      
      return state.lastBatchResult
    },
    
    // Development info
    isDevelopmentMode: (state): boolean => state.mockMode,
    getDevInfo: (state) => ({
      mockMode: state.mockMode,
      environment: import.meta.env.NODE_ENV,
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api/v1',
      debugMode: import.meta.env.VITE_DEBUG_MODE === 'true'
    })
  },

  actions: {
    // Loading management
    setLoading(isLoading: boolean, message?: string): void {
      this.loading = { isLoading, message }
      
      // Clear error when starting new operation
      if (isLoading) {
        this.clearError()
      }
    },

    // Error management
    setError(message: string, details?: Record<string, any>): void {
      this.error = {
        hasError: true,
        message,
        details
      }
      this.setLoading(false)
    },

    clearError(): void {
      this.error = {
        hasError: false,
        message: undefined,
        details: undefined
      }
    },

    // Task management
    setSingleResult(result: SingleResult | null): void {
      this.lastSingleResult = result
    },

    setBatchResult(result: BatchResult | null): void {
      this.lastBatchResult = result
    },

    setCurrentSingleTaskId(taskId: string | null): void {
      this.currentSingleTaskId = taskId
    },

    setCurrentBatchTaskId(taskId: string | null): void {
      this.currentBatchTaskId = taskId
    },

    // API Actions - simplified without UI logic
    async analyzeSingleText(text: string): Promise<SingleResult | null> {
      this.setLoading(true, 'Analyzing text...')
      
      try {
        // Submit task
        const taskResult = await taskService.analyzeSingleText(text)
        
        if (!taskResult.success) {
          this.setError(taskResult.error || 'Failed to analyze text', { statusCode: taskResult.statusCode })
          return null
        }

        const task = taskResult.data!
        this.setCurrentSingleTaskId(task.task_id)

        // Get result immediately if available
        const resultData = await taskService.getLastSingleResult()
        
        if (resultData.success) {
          this.setSingleResult(resultData.data!)
          this.setLoading(false)
          return resultData.data!
        } else {
          this.setLoading(false)
          return null
        }
      } catch (error: any) {
        console.error('Single text analysis error:', error)
        this.setError(error.message || 'Unexpected error during text analysis')
        return null
      }
    },

    async analyzeBatchFile(file: File): Promise<BatchResult | null> {
      this.setLoading(true, 'Processing file...')
      
      try {
        // Submit batch task
        const taskResult = await taskService.analyzeBatchFile(file)
        
        if (!taskResult.success) {
          this.setError(taskResult.error || 'Failed to process file', { statusCode: taskResult.statusCode })
          return null
        }

        const task = taskResult.data!
        this.setCurrentBatchTaskId(task.task_id)

        // Get result immediately if available
        const resultData = await taskService.getLastBatchResult()
        
        if (resultData.success) {
          this.setBatchResult(resultData.data!)
          this.setLoading(false)
          return resultData.data!
        } else {
          this.setLoading(false)
          return null
        }
      } catch (error: any) {
        console.error('Batch file analysis error:', error)
        this.setError(error.message || 'Unexpected error during file processing')
        return null
      }
    },

    async refreshSingleResult(): Promise<SingleResult | null> {
      this.setLoading(true, 'Refreshing result...')
      
      try {
        const resultData = await taskService.getLastSingleResult()
        
        if (resultData.success) {
          this.setSingleResult(resultData.data!)
          return resultData.data!
        } else if (resultData.statusCode === 404) {
          // No tasks found
          this.setSingleResult(null)
          return null
        } else {
          this.setError(resultData.error || 'Failed to refresh result', { statusCode: resultData.statusCode })
          return null
        }
      } catch (error: any) {
        console.error('Refresh single result error:', error)
        this.setError(error.message || 'Unexpected error while refreshing result')
        return null
      } finally {
        this.setLoading(false)
      }
    },

    async refreshBatchResult(): Promise<BatchResult | null> {
      this.setLoading(true, 'Refreshing analytics...')
      
      try {
        const resultData = await taskService.getLastBatchResult()
        
        if (resultData.success) {
          this.setBatchResult(resultData.data!)
          return resultData.data!
        } else if (resultData.statusCode === 404) {
          // No tasks found
          this.setBatchResult(null)
          return null
        } else {
          this.setError(resultData.error || 'Failed to refresh analytics', { statusCode: resultData.statusCode })
          return null
        }
      } catch (error: any) {
        console.error('Refresh batch result error:', error)
        this.setError(error.message || 'Unexpected error while refreshing analytics')
        return null
      } finally {
        this.setLoading(false)
      }
    },

    // Development actions
    toggleMockMode(): boolean {
      this.mockMode = taskService.toggleMockMode()
      return this.mockMode
    },

    // Clear all data
    clearAllData(): void {
      this.lastSingleResult = null
      this.lastBatchResult = null
      this.currentSingleTaskId = null
      this.currentBatchTaskId = null
      this.clearError()
      this.setLoading(false)
    }
  }
})
