/**
 * API Service
 * Handles API calls with automatic switching between mock and real API
 * Based on environment configuration
 */

import axios, { type AxiosInstance, type AxiosResponse, type AxiosError } from 'axios'
import type {
  Task,
  SingleTaskRequest,
  BatchTaskRequest,
  TaskResultRequest,
  ApiResponse,
  ApiErrorResponse
} from '@/types/api.types'

import { mockApiService } from '@/mocks/api-mock.service'
import { defaultMockConfig } from '@/mocks/config'

/**
 * API Service Class
 */
export class ApiService {
  private axiosInstance: AxiosInstance
  private mockEnabled: boolean

  constructor() {
    this.mockEnabled = defaultMockConfig.enabled
    
    this.axiosInstance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  /**
   * Setup request/response interceptors
   */
  private setupInterceptors(): void {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // Add JWT token if available
        const token = this.getAuthToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        
        // Log request in debug mode
        if (import.meta.env.VITE_DEBUG_MODE === 'true') {
          console.debug('API Request:', {
            method: config.method,
            url: config.url,
            data: config.data
          })
        }
        
        return config
      },
      (error) => {
        console.error('Request interceptor error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response) => {
        // Log response in debug mode
        if (import.meta.env.VITE_DEBUG_MODE === 'true') {
          console.debug('API Response:', {
            status: response.status,
            data: response.data
          })
        }
        
        return response
      },
      (error: AxiosError) => {
        // Handle token refresh logic here if needed
        if (error.response?.status === 401) {
          this.handleTokenExpiration()
        }
        
        console.error('API Error:', {
          status: error.response?.status,
          message: error.message,
          data: error.response?.data
        })
        
        return Promise.reject(error)
      }
    )
  }

  /**
   * Get auth token from storage
   */
  private getAuthToken(): string | null {
    return localStorage.getItem('auth_token')
  }

  /**
   * Handle token expiration
   */
  private handleTokenExpiration(): void {
    localStorage.removeItem('auth_token')
    // Redirect to login or refresh token
    console.warn('Token expired, user needs to re-authenticate')
  }

  /**
   * Get user ID from cookies or generate one
   */
  private getUserId(): string {
    let userId = localStorage.getItem('user_id')
    if (!userId) {
      userId = `user_${Math.random().toString(36).substr(2, 9)}`
      localStorage.setItem('user_id', userId)
    }
    return userId
  }

  /**
   * Convert AxiosResponse to ApiResponse
   */
  private toApiResponse<T>(response: AxiosResponse<T>): ApiResponse<T> {
    return {
      data: response.data,
      status: response.status,
      statusText: response.statusText
    }
  }

  /**
   * Convert AxiosError to ApiErrorResponse
   */
  private toApiErrorResponse(error: AxiosError): ApiErrorResponse {
    const errorData = error.response?.data as any
    return {
      data: errorData || { message: error.message || 'Unknown error' },
      status: error.response?.status || 500,
      statusText: error.response?.statusText || 'Internal Server Error'
    }
  }

  /**
   * POST /api/v1/task/run/single
   */
  async runSingleTask(text: string): Promise<ApiResponse<Task> | ApiErrorResponse> {
    const request: SingleTaskRequest = {
      user_id: this.getUserId(),
      text
    }

    if (this.mockEnabled) {
      return mockApiService.runSingleTask(request)
    }

    try {
      const response = await this.axiosInstance.post<Task>('/task/run/single', request)
      return this.toApiResponse(response)
    } catch (error) {
      return this.toApiErrorResponse(error as AxiosError)
    }
  }

  /**
   * POST /api/v1/task/run/batch
   */
  async runBatchTask(file: File): Promise<ApiResponse<Task> | ApiErrorResponse> {
    if (this.mockEnabled) {
      const request: BatchTaskRequest = {
        user_id: this.getUserId(),
        file
      }
      return mockApiService.runBatchTask(request)
    }

    try {
      const formData = new FormData()
      formData.append('user_id', this.getUserId())
      formData.append('file', file)

      const response = await this.axiosInstance.post<Task>('/task/run/batch', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      return this.toApiResponse(response)
    } catch (error) {
      return this.toApiErrorResponse(error as AxiosError)
    }
  }

  /**
   * POST /api/v1/task/result/single
   */
  async getSingleTaskResult(): Promise<ApiResponse<Task> | ApiErrorResponse> {
    const request: TaskResultRequest = {
      user_id: this.getUserId()
    }

    if (this.mockEnabled) {
      return mockApiService.getSingleTaskResult(request)
    }

    try {
      const response = await this.axiosInstance.post<Task>('/task/result/single', request)
      return this.toApiResponse(response)
    } catch (error) {
      return this.toApiErrorResponse(error as AxiosError)
    }
  }

  /**
   * POST /api/v1/task/result/batch
   */
  async getBatchTaskResult(): Promise<ApiResponse<Task> | ApiErrorResponse> {
    const request: TaskResultRequest = {
      user_id: this.getUserId()
    }

    if (this.mockEnabled) {
      return mockApiService.getBatchTaskResult(request)
    }

    try {
      const response = await this.axiosInstance.post<Task>('/task/result/batch', request)
      return this.toApiResponse(response)
    } catch (error) {
      return this.toApiErrorResponse(error as AxiosError)
    }
  }

  /**
   * Toggle mock mode (for development)
   */
  toggleMockMode(): boolean {
    this.mockEnabled = !this.mockEnabled
    console.info(`Mock API ${this.mockEnabled ? 'enabled' : 'disabled'}`)
    return this.mockEnabled
  }

  /**
   * Check if mock mode is enabled
   */
  isMockEnabled(): boolean {
    return this.mockEnabled
  }
}

// Export singleton instance
export const apiService = new ApiService()
