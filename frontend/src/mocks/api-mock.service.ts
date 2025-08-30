/**
 * Mock API Service
 * Provides mock implementations of all API endpoints from openapi.yml
 */

import type {
  Task,
  SingleTaskRequest,
  BatchTaskRequest,
  TaskResultRequest,
  ApiResponse,
  ApiErrorResponse,
  ApiError,
  ValidationError
} from '@/types/api.types'

import { 
  generateTask, 
  generateUuid,
  generateSingleResult,
  generateBatchResult
} from './data-generators'

import { defaultMockConfig, errorScenarios, mockDataConfig } from './config'

// In-memory storage for mock tasks
const taskStorage = new Map<string, Map<string, Task>>() // userId -> tasks map

/**
 * Simulates network delay
 */
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Checks if should simulate an error based on error rate
 */
function shouldSimulateError(): boolean {
  return Math.random() < defaultMockConfig.errorRate
}

/**
 * Gets or creates user task storage
 */
function getUserTasks(userId: string): Map<string, Task> {
  if (!taskStorage.has(userId)) {
    taskStorage.set(userId, new Map())
  }
  return taskStorage.get(userId)!
}

/**
 * Gets the last task of specific type for user
 */
function getLastTask(userId: string, taskType: 'single' | 'batch'): Task | null {
  const userTasks = getUserTasks(userId)
  const tasks = Array.from(userTasks.values())
    .filter(task => task.type === taskType)
    .sort((a, b) => b.start - a.start)
  
  return tasks[0] || null
}

/**
 * Validates text input
 */
function validateText(text: string): ValidationError | null {
  const errors: Record<string, string[]> = {}
  
  if (!text || text.trim().length === 0) {
    errors.text = ['This field is required']
  } else if (text.length > mockDataConfig.maxTextLength) {
    errors.text = [`Text must be at most ${mockDataConfig.maxTextLength} characters long`]
  }
  
  if (Object.keys(errors).length > 0) {
    return {
      message: 'Validation failed',
      details: errors
    }
  }
  
  return null
}

/**
 * Validates file input
 */
function validateFile(file: File): ApiError | null {
  if (file.size > mockDataConfig.maxFileSize) {
    return {
      message: 'File size exceeds maximum limit of 10MB'
    }
  }
  
  if (!mockDataConfig.supportedFileTypes.includes(file.type)) {
    return {
      message: 'Unsupported file format. Supported: CSV, TXT, JSON'
    }
  }
  
  return null
}

/**
 * Mock API Service Class
 */
export class MockApiService {
  /**
   * POST /api/v1/task/run/single
   */
  async runSingleTask(request: SingleTaskRequest): Promise<ApiResponse<Task> | ApiErrorResponse> {
    await delay(defaultMockConfig.delays.single)
    
    // Simulate random errors
    if (shouldSimulateError() && defaultMockConfig.errorScenarios.serverError) {
      return {
        data: { message: errorScenarios.serverError.message },
        status: 500,
        statusText: 'Internal Server Error'
      }
    }
    
    // Validate request
    const validationError = validateText(request.text)
    if (validationError && defaultMockConfig.errorScenarios.validation) {
      return {
        data: validationError,
        status: 422,
        statusText: 'Validation Error'
      }
    }
    
    // Create and store task
    const task = generateTask('single', 'ready', request.text)
    const userTasks = getUserTasks(request.user_id)
    userTasks.set(task.task_id, task)
    
    return {
      data: task,
      status: 200,
      statusText: 'OK'
    }
  }
  
  /**
   * POST /api/v1/task/run/batch
   */
  async runBatchTask(request: BatchTaskRequest): Promise<ApiResponse<Task> | ApiErrorResponse> {
    await delay(defaultMockConfig.delays.batch)
    
    // Simulate random errors
    if (shouldSimulateError() && defaultMockConfig.errorScenarios.serverError) {
      return {
        data: { message: errorScenarios.serverError.message },
        status: 500,
        statusText: 'Internal Server Error'
      }
    }
    
    // Validate file
    const fileError = validateFile(request.file)
    if (fileError) {
      return {
        data: fileError,
        status: fileError.message.includes('10MB') ? 413 : 415,
        statusText: fileError.message.includes('10MB') ? 'File Too Large' : 'Unsupported Media Type'
      }
    }
    
    // Create and store task
    const totalReviews = Math.floor(Math.random() * 400) + 100 // 100-500 reviews
    const task = generateTask('batch', 'ready', undefined, totalReviews)
    const userTasks = getUserTasks(request.user_id)
    userTasks.set(task.task_id, task)
    
    return {
      data: task,
      status: 200,
      statusText: 'OK'
    }
  }
  
  /**
   * POST /api/v1/task/result/single
   */
  async getSingleTaskResult(request: TaskResultRequest): Promise<ApiResponse<Task> | ApiErrorResponse> {
    await delay(defaultMockConfig.delays.result)
    
    // Simulate random errors
    if (shouldSimulateError() && defaultMockConfig.errorScenarios.serverError) {
      return {
        data: { message: errorScenarios.serverError.message },
        status: 500,
        statusText: 'Internal Server Error'
      }
    }
    
    const task = getLastTask(request.user_id, 'single')
    
    if (!task && defaultMockConfig.errorScenarios.notFound) {
      return {
        data: { message: 'No single task found for this user' },
        status: 404,
        statusText: 'Not Found'
      }
    }
    
    // If no task exists, create a sample one
    if (!task) {
      const sampleTask = generateTask('single', 'ready', 'Sample analysis text')
      const userTasks = getUserTasks(request.user_id)
      userTasks.set(sampleTask.task_id, sampleTask)
      
      return {
        data: sampleTask,
        status: 200,
        statusText: 'OK'
      }
    }
    
    return {
      data: task,
      status: 200,
      statusText: 'OK'
    }
  }
  
  /**
   * POST /api/v1/task/result/batch
   */
  async getBatchTaskResult(request: TaskResultRequest): Promise<ApiResponse<Task> | ApiErrorResponse> {
    await delay(defaultMockConfig.delays.result)
    
    // Simulate random errors
    if (shouldSimulateError() && defaultMockConfig.errorScenarios.serverError) {
      return {
        data: { message: errorScenarios.serverError.message },
        status: 500,
        statusText: 'Internal Server Error'
      }
    }
    
    const task = getLastTask(request.user_id, 'batch')
    
    if (!task && defaultMockConfig.errorScenarios.notFound) {
      return {
        data: { message: 'No batch task found for this user' },
        status: 404,
        statusText: 'Not Found'
      }
    }
    
    // If no task exists, create a sample one
    if (!task) {
      const sampleTask = generateTask('batch', 'ready', undefined, 250)
      const userTasks = getUserTasks(request.user_id)
      userTasks.set(sampleTask.task_id, sampleTask)
      
      return {
        data: sampleTask,
        status: 200,
        statusText: 'OK'
      }
    }
    
    return {
      data: task,
      status: 200,
      statusText: 'OK'
    }
  }
  
  /**
   * Utility method to clear all tasks for testing
   */
  clearAllTasks(): void {
    taskStorage.clear()
  }
  
  /**
   * Utility method to get all tasks for a user
   */
  getUserTasks(userId: string): Task[] {
    const userTasks = getUserTasks(userId)
    return Array.from(userTasks.values()).sort((a, b) => b.start - a.start)
  }
}

// Export singleton instance
export const mockApiService = new MockApiService()
