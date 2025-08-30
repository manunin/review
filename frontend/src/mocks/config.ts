/**
 * Mock configuration and settings
 * Controls behavior of mock API service
 */

export interface MockConfig {
  enabled: boolean
  delays: {
    single: number
    batch: number
    result: number
  }
  errorRate: number
  errorScenarios: {
    validation: boolean
    timeout: boolean
    serverError: boolean
    notFound: boolean
  }
}

// Default mock configuration
export const defaultMockConfig: MockConfig = {
  enabled: import.meta.env.VITE_MOCK_API === 'true' || import.meta.env.NODE_ENV === 'development',
  delays: {
    single: 800, // ms for single task analysis
    batch: 2500, // ms for batch task analysis
    result: 300  // ms for result retrieval
  },
  errorRate: 0.1, // 10% chance of random errors
  errorScenarios: {
    validation: true,   // Enable validation error scenarios
    timeout: false,     // Disable timeout errors by default
    serverError: true,  // Enable server error scenarios
    notFound: true      // Enable not found error scenarios
  }
}

// Error scenarios configuration
export const errorScenarios = {
  validation: {
    code: 422,
    message: 'Validation failed',
    details: {
      text: ['This field is required', 'Text must be at least 1 character long'],
      user_id: ['This field is required']
    }
  },
  timeout: {
    code: 408,
    message: 'Request timeout'
  },
  serverError: {
    code: 500,
    message: 'Internal server error occurred'
  },
  notFound: {
    code: 404,
    message: 'Task not found'
  },
  fileTooLarge: {
    code: 413,
    message: 'File size exceeds maximum limit of 10MB'
  },
  unsupportedFormat: {
    code: 415,
    message: 'Unsupported file format. Supported: CSV, TXT, JSON'
  }
}

// Mock data configuration
export const mockDataConfig = {
  taskIdLength: 36, // UUID length
  maxTextLength: 512,
  maxFileSize: 10 * 1024 * 1024, // 10MB
  supportedFileTypes: ['text/csv', 'text/plain', 'application/json'],
  batchReviewCounts: {
    min: 50,
    max: 500
  }
}
