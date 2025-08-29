# Frontend Integration Guide

This document describes the integration of OpenAPI specification with the frontend application according to CONTEXT.MD requirements.

## Service Layer

According to point 10 of CONTEXT.MD, a service layer is used for API calls. The main API client is located in `src/store/index.ts`:

```typescript
import axios, { type AxiosResponse } from 'axios'

// API client
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})
```

## TypeScript Typing

According to point 16 of CONTEXT.MD, all types should be properly typed. API types are located in `src/types/index.ts` and correspond to OpenAPI schemas:

```typescript
// Corresponds to Task schema in OpenAPI
export interface Task {
  task_id: string
  type: 'single' | 'batch'
  status: 'accepted' | 'queued' | 'ready' | 'error'
  start: number
  end?: number
  result?: SingleResult | BatchResult
  error?: TaskError
}

// Corresponds to SingleResult schema in OpenAPI
export interface SingleResult {
  sentiment: 'positive' | 'negative' | 'neutral'
  confidence: number
  text?: string
}

// Corresponds to BatchResult schema in OpenAPI
export interface BatchResult {
  total_reviews: number
  positive: number
  negative: number
  neutral: number
  positive_percentage: number
  negative_percentage: number
  neutral_percentage: number
}

// Corresponds to TaskError schema in OpenAPI
export interface TaskError {
  code: '01' | '02' | '03'
  description?: string
}

// Request types
export interface TaskResultRequest {
  user_id: string
}

export interface SingleTaskRequest {
  user_id: string
  text: string
}
```

## User Session Management

The API uses user_id from cookies for user identification:

```typescript
// Get user ID from cookies
function getUserId(): string {
  // Implementation depends on your cookie strategy
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('user_id='))
    ?.split('=')[1] || 'default_user_id'
}
```

## Logging

According to points 12-13 of CONTEXT.MD, all API operations are logged:

```typescript
// Example from store - error logging
catch (error: any) {
  console.error('Failed to fetch task result:', error)
  this.setError(error.response?.data?.message || error.message || 'API request failed')
}
```

## Error Handling

According to point 17 of CONTEXT.MD, global error handling is implemented. API errors are handled at the store level:

```typescript
// Centralized API error handling
setError(error: string | null) {
  this.error = error
}

clearError() {
  this.error = null
}
```

## API Methods

### Task Results

#### Get last single task result
```typescript
async getLastSingleResult(): Promise<Task | null> {
  try {
    const response: AxiosResponse<Task> = await api.post('/task/result/single', {
      user_id: getUserId()
    })
    return response.data
  } catch (error: any) {
    if (error.response?.status === 404) {
      return null // No result available
    }
    throw error
  }
}
```

#### Get last batch task result
```typescript
async getLastBatchResult(): Promise<Task | null> {
  try {
    const response: AxiosResponse<Task> = await api.post('/task/result/batch', {
      user_id: getUserId()
    })
    return response.data
  } catch (error: any) {
    if (error.response?.status === 404) {
      return null // No result available
    }
    throw error
  }
}
```

### Task Execution

#### Send task for single text analysis
```typescript
async runSingleTask(text: string): Promise<Task> {
  const response: AxiosResponse<Task> = await api.post('/task/run/single', {
    user_id: getUserId(),
    text: text
  })
  return response.data
}
```

#### Send task for batch analysis
```typescript
async runBatchTask(file: File): Promise<Task> {
  const formData = new FormData()
  formData.append('user_id', getUserId())
  formData.append('file', file)
  
  const response: AxiosResponse<Task> = await api.post('/task/run/batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return response.data
}
```

## Task Status Polling

Since tasks are processed asynchronously, you might want to implement polling:

```typescript
async pollTaskResult(taskType: 'single' | 'batch', maxAttempts: number = 30): Promise<Task | null> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const result = taskType === 'single' 
      ? await this.getLastSingleResult()
      : await this.getLastBatchResult()
    
    if (result && (result.status === 'ready' || result.status === 'error')) {
      return result
    }
    
    // Wait 2 seconds before next attempt
    await new Promise(resolve => setTimeout(resolve, 2000))
  }
  
  return null // Timeout
}
```

## Environment Configuration

According to point 21 of CONTEXT.MD, URLs are configured through env files. In `vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false
    }
  }
}
```

## Composition API Usage

According to point 2 of CONTEXT.MD, Composition API is used. Example of store usage in components:

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useReviewStore } from '@/store'
import type { Task } from '@/types'

const reviewStore = useReviewStore()
const currentTask = ref<Task | null>(null)
const isLoading = ref(false)

// Send single text analysis task
async function analyzeSingleText(text: string) {
  isLoading.value = true
  try {
    const task = await reviewStore.runSingleTask(text)
    currentTask.value = task
    
    // Poll for result
    const result = await reviewStore.pollTaskResult('single')
    if (result) {
      currentTask.value = result
    }
  } catch (error) {
    console.error('Analysis failed:', error)
  } finally {
    isLoading.value = false
  }
}

// Send batch analysis task
async function analyzeBatchFile(file: File) {
  isLoading.value = true
  try {
    const task = await reviewStore.runBatchTask(file)
    currentTask.value = task
    
    // Poll for result
    const result = await reviewStore.pollTaskResult('batch')
    if (result) {
      currentTask.value = result
    }
  } catch (error) {
    console.error('Batch analysis failed:', error)
  } finally {
    isLoading.value = false
  }
}

// Computed properties for task status
const taskStatus = computed(() => currentTask.value?.status || 'idle')
const isTaskReady = computed(() => taskStatus.value === 'ready')
const hasTaskError = computed(() => taskStatus.value === 'error')

// Get result based on task type
const singleResult = computed(() => {
  if (currentTask.value?.type === 'single' && isTaskReady.value) {
    return currentTask.value.result as SingleResult
  }
  return null
})

const batchResult = computed(() => {
  if (currentTask.value?.type === 'batch' && isTaskReady.value) {
    return currentTask.value.result as BatchResult
  }
  return null
})
</script>

<template>
  <div>
    <button @click="analyzeSingleText('Test text')" :disabled="isLoading">
      Analyze Text
    </button>
    
    <input type="file" @change="analyzeBatchFile($event.target.files[0])" />
    
    <div v-if="isLoading">Processing...</div>
    <div v-if="taskStatus === 'queued'">Task is queued...</div>
    <div v-if="hasTaskError">Error: {{ currentTask.error?.description }}</div>
    
    <div v-if="singleResult">
      Sentiment: {{ singleResult.sentiment }} ({{ singleResult.confidence }})
    </div>
    
    <div v-if="batchResult">
      Total: {{ batchResult.total_reviews }}, 
      Positive: {{ batchResult.positive_percentage }}%
    </div>
  </div>
</template>
```

## Accessibility

According to point 19 of CONTEXT.MD, all interactive elements must be keyboard accessible with ARIA labels.

## Performance

According to point 18 of CONTEXT.MD, optimizations are used:
- Lazy loading for components
- shallowRef for large objects without deep reactivity

## OpenAPI Compliance

All frontend API methods exactly correspond to those described in the OpenAPI specification:
- URL endpoints (task-based architecture)
- HTTP methods (all POST for consistency)
- Request/Response formats (user_id required for all operations)
- Error codes (404, 400, 422, 413, 415, 500)
- Data types (Task, SingleResult, BatchResult schemas)

This ensures full compatibility between frontend and backend implementations with the new task-based API architecture.
