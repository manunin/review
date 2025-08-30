/**
 * Mock System Index
 * Main entry point for all mock functionality
 */

// Export types
export type {
  Task,
  SingleResult,
  BatchResult,
  TaskError,
  SentimentType,
  TaskType,
  TaskStatus,
  SingleTaskRequest,
  BatchTaskRequest,
  TaskResultRequest,
  ApiResponse,
  ApiErrorResponse,
  ApiError,
  ValidationError
} from '@/types/api.types'

export type {
  LoadingState,
  ErrorState,
  AppState,
  EnvironmentConfig
} from '@/types/common.types'

// Export mock configuration
export {
  defaultMockConfig,
  errorScenarios,
  mockDataConfig
} from './config'

// Export data generators
export {
  generateUuid,
  generateSentiment,
  generateSampleText,
  generateSingleResult,
  generateBatchResult,
  generateTaskError,
  generateTask,
  generateTasks
} from './data-generators'

// Export mock API service
export {
  MockApiService,
  mockApiService
} from './api-mock.service'

// Export main services
export { ApiService, apiService } from '@/services/api.service'
export { TaskService, taskService, type TaskOperationResult } from '@/services/task.service'

// Utility functions for development
export const mockUtils = {
  /**
   * Enable mock mode
   */
  enableMockMode(): void {
    localStorage.setItem('mock_enabled', 'true')
    console.info('Mock mode enabled')
  },

  /**
   * Disable mock mode
   */
  disableMockMode(): void {
    localStorage.setItem('mock_enabled', 'false')
    console.info('Mock mode disabled')
  },

  /**
   * Check if mock mode is enabled
   */
  isMockEnabled(): boolean {
    return localStorage.getItem('mock_enabled') === 'true' || 
           import.meta.env.VITE_MOCK_API === 'true' ||
           import.meta.env.NODE_ENV === 'development'
  },

  /**
   * Clear all mock data
   */
  clearMockData(): void {
    // Import dynamically to avoid circular dependency
    import('./api-mock.service').then(({ mockApiService }) => {
      mockApiService.clearAllTasks()
    })
    console.info('Mock data cleared')
  },

  /**
   * Get development info
   */
  getDevInfo(): Record<string, any> {
    return {
      mockEnabled: mockUtils.isMockEnabled(),
      environment: import.meta.env.NODE_ENV,
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api/v1',
      debugMode: import.meta.env.VITE_DEBUG_MODE === 'true'
    }
  }
}

// Global window object for development (only in development mode)
if (import.meta.env.NODE_ENV === 'development') {
  (window as any).__mockUtils = mockUtils
  console.info('Mock utilities available at window.__mockUtils')
}
