/**
 * Task Service
 * High-level service for task operations
 * Provides business logic layer on top of API service
 */

import { apiService } from './api.service'
import type { 
  Task, 
  SingleResult, 
  BatchResult,
  ApiResponse, 
  ApiErrorResponse 
} from '@/types/api.types'

export interface TaskOperationResult<T = Task> {
  success: boolean
  data?: T
  error?: string
  statusCode?: number
}

/**
 * Task Service Class
 */
export class TaskService {
  /**
   * Analyze single text
   */
  async analyzeSingleText(text: string): Promise<TaskOperationResult<Task>> {
    try {
      // Validate input
      if (!text || text.trim().length === 0) {
        return {
          success: false,
          error: 'Text is required for analysis',
          statusCode: 400
        }
      }

      if (text.length > 512) {
        return {
          success: false,
          error: 'Text must be at most 512 characters long',
          statusCode: 400
        }
      }

      const response = await apiService.runSingleTask(text)
      
      if (response.status >= 200 && response.status < 300) {
        return {
          success: true,
          data: response.data as Task
        }
      } else {
        const errorData = response.data as any
        return {
          success: false,
          error: errorData.message || 'Failed to analyze text',
          statusCode: response.status
        }
      }
    } catch (error) {
      console.error('Task service error:', error)
      return {
        success: false,
        error: 'Unexpected error occurred during analysis',
        statusCode: 500
      }
    }
  }

  /**
   * Upload and analyze batch file
   */
  async analyzeBatchFile(file: File): Promise<TaskOperationResult<Task>> {
    try {
      // Validate file
      if (!file) {
        return {
          success: false,
          error: 'File is required for batch analysis',
          statusCode: 400
        }
      }

      // Check file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        return {
          success: false,
          error: 'File size exceeds maximum limit of 10MB',
          statusCode: 413
        }
      }

      // Check file type
      const supportedTypes = ['text/csv', 'text/plain', 'application/json']
      if (!supportedTypes.includes(file.type)) {
        return {
          success: false,
          error: 'Unsupported file format. Supported: CSV, TXT, JSON',
          statusCode: 415
        }
      }

      const response = await apiService.runBatchTask(file)
      
      if (response.status >= 200 && response.status < 300) {
        return {
          success: true,
          data: response.data as Task
        }
      } else {
        const errorData = response.data as any
        return {
          success: false,
          error: errorData.message || 'Failed to analyze batch file',
          statusCode: response.status
        }
      }
    } catch (error) {
      console.error('Task service error:', error)
      return {
        success: false,
        error: 'Unexpected error occurred during batch analysis',
        statusCode: 500
      }
    }
  }

  /**
   * Get last single task result
   */
  async getLastSingleResult(): Promise<TaskOperationResult<SingleResult>> {
    try {
      const response = await apiService.getSingleTaskResult()
      
      if (response.status >= 200 && response.status < 300) {
        const task = response.data as Task
        
        if (task.status === 'ready' && task.result) {
          return {
            success: true,
            data: task.result as SingleResult
          }
        } else if (task.status === 'error') {
          return {
            success: false,
            error: task.error?.description || 'Task execution failed',
            statusCode: 500
          }
        } else {
          return {
            success: false,
            error: 'Task is still processing',
            statusCode: 202
          }
        }
      } else if (response.status === 404) {
        return {
          success: false,
          error: 'No single analysis tasks found',
          statusCode: 404
        }
      } else {
        const errorData = response.data as any
        return {
          success: false,
          error: errorData.message || 'Failed to get task result',
          statusCode: response.status
        }
      }
    } catch (error) {
      console.error('Task service error:', error)
      return {
        success: false,
        error: 'Unexpected error occurred while retrieving result',
        statusCode: 500
      }
    }
  }

  /**
   * Get last batch task result
   */
  async getLastBatchResult(): Promise<TaskOperationResult<BatchResult>> {
    try {
      const response = await apiService.getBatchTaskResult()
      
      if (response.status >= 200 && response.status < 300) {
        const task = response.data as Task
        
        if (task.status === 'ready' && task.result) {
          return {
            success: true,
            data: task.result as BatchResult
          }
        } else if (task.status === 'error') {
          return {
            success: false,
            error: task.error?.description || 'Task execution failed',
            statusCode: 500
          }
        } else {
          return {
            success: false,
            error: 'Task is still processing',
            statusCode: 202
          }
        }
      } else if (response.status === 404) {
        return {
          success: false,
          error: 'No batch analysis tasks found',
          statusCode: 404
        }
      } else {
        const errorData = response.data as any
        return {
          success: false,
          error: errorData.message || 'Failed to get task result',
          statusCode: response.status
        }
      }
    } catch (error) {
      console.error('Task service error:', error)
      return {
        success: false,
        error: 'Unexpected error occurred while retrieving result',
        statusCode: 500
      }
    }
  }

  /**
   * Check if mock mode is enabled
   */
  isMockMode(): boolean {
    return apiService.isMockEnabled()
  }

  /**
   * Toggle mock mode (for development)
   */
  toggleMockMode(): boolean {
    return apiService.toggleMockMode()
  }
}

// Export singleton instance
export const taskService = new TaskService()
