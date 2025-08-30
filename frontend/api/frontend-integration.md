# Frontend Integration Guide

Данный документ описывает интеграцию OpenAPI спецификации с frontend приложением согласно требованиям CONTEXT.MD.

## Service Layer

Согласно пункту 10 CONTEXT.MD, для API calls используется service layer. Основной API клиент находится в `src/services/api.service.ts` и `src/services/task.service.ts` для task-based операций:

```typescript
// Task Service для основных операций
export class TaskService {
  private apiService: ApiService

  constructor() {
    this.apiService = new ApiService()
  }

  async submitSingleTask(text: string): Promise<ApiResponse<Task> | ApiErrorResponse>
  async submitBatchTask(file: File): Promise<ApiResponse<Task> | ApiErrorResponse>
  async getFullTaskResult(taskType: TaskType): Promise<ApiResponse<Task> | ApiErrorResponse>
}
```

## TypeScript типизация

Согласно пункту 16 CONTEXT.MD, все типы должны быть properly typed. Типы API находятся в `src/types/api.types.ts` и `src/types/common.types.ts` и соответствуют OpenAPI схемам:

```typescript
// Соответствует task-based архитектуре
export interface Task {
  id: string
  status: TaskStatus
  task_type: TaskType
  created_at: string
  updated_at: string
  result?: SingleResult | BatchResult
  error?: TaskError
}

// Результаты анализа одного текста
export interface SingleResult {
  text: string
  sentiment: SentimentType
  confidence: number
  analysis_time: number
}

// Результаты batch анализа
export interface BatchResult {
  total_reviews: number
  positive: number
  negative: number
  neutral: number
  positive_percentage: number
  negative_percentage: number
  neutral_percentage: number
  reviews: SingleResult[]
  processing_time: number
}

// Типы для состояний
export interface LoadingState {
  isLoading: boolean
  message?: string
}

export interface ErrorState {
  hasError: boolean
  message?: string
  details?: Record<string, any>
}
```

## Логирование

Согласно пунктам 12-13 CONTEXT.MD, все API операции логируются:

```typescript
// Пример из task store - логирование ошибок
catch (error: any) {
  console.error('Task operation failed:', error)
  this.setError(error.message || 'Task operation failed', { 
    operation: 'analyzeSingleText',
    timestamp: new Date().toISOString() 
  })
}
```

## Обработка ошибок

Согласно пункту 17 CONTEXT.MD, реализована глобальная обработка ошибок. API ошибки обрабатываются на уровне task store:

```typescript
// Централизованная обработка ошибок в TaskStore
setError(message: string, details?: Record<string, any>): void {
  this.error = {
    hasError: true,
    message,
    details
  }
  this.setLoading(false)
}

clearError(): void {
  this.error = {
    hasError: false,
    message: undefined,
    details: undefined
  }
}
```

## Методы API

### Task-based операции

#### Анализ одного текста
```typescript
async analyzeSingleText(text: string): Promise<SingleResult | null> {
  this.setLoading(true, 'Analyzing text...')
  
  try {
    const taskResult = await taskService.submitSingleTask(text)
    
    if (!taskResult.success) {
      this.setError(taskResult.error || 'Failed to analyze text', { statusCode: taskResult.statusCode })
      return null
    }

    // Get result (in mock mode, result is immediately available)
    const resultData = await taskService.getFullTaskResult('single')
    
    if (resultData.success && resultData.data?.result) {
      const result = resultData.data.result as SingleResult
      this.setSingleResult(result)
      return result
    }
    
    return null
  } catch (error: any) {
    console.error('Single text analysis error:', error)
    this.setError(error.message || 'Unexpected error during text analysis')
    return null
  } finally {
    this.setLoading(false)
  }
}
```

#### Анализ batch файла
```typescript
async analyzeBatchFile(file: File): Promise<BatchResult | null> {
  this.setLoading(true, 'Processing file...')
  
  try {
    const taskResult = await taskService.submitBatchTask(file)
    
    if (!taskResult.success) {
      this.setError(taskResult.error || 'Failed to process file', { statusCode: taskResult.statusCode })
      return null
    }

    // Get result (in mock mode, result is immediately available)
    const resultData = await taskService.getFullTaskResult('batch')
    
    if (resultData.success && resultData.data?.result) {
      const result = resultData.data.result as BatchResult
      this.setBatchResult(result)
      return result
    }
    
    return null
  } catch (error: any) {
    console.error('Batch analysis error:', error)
    this.setError(error.message || 'Unexpected error during batch processing')
    return null
  } finally {
    this.setLoading(false)
  }
}
```

#### Получить детали задачи
```typescript
async getFullTaskDetails(taskType: TaskType): Promise<Task | null> {
  this.setLoading(true, 'Getting task details...')
  
  try {
    const taskResult = await taskService.getFullTaskResult(taskType)
    
    if (taskResult.success) {
      return taskResult.data!
    } else {
      this.setError(taskResult.error || 'Failed to get task details', { statusCode: taskResult.statusCode })
      return null
    }
  } catch (error: any) {
    console.error('Get task details error:', error)
    this.setError(error.message || 'Unexpected error while getting task details')
    return null
  } finally {
    this.setLoading(false)
  }
}
```

## Конфигурация окружения

Согласно пункту 21 CONTEXT.MD, URL настраиваются через env файлы. В `vite.config.ts`:

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

Переменные окружения в `.env`:
```bash
VITE_API_BASE_URL=/api/v1
VITE_API_TIMEOUT=10000
VITE_DEBUG_MODE=true
VITE_MOCK_ENABLED=true
```

## Composition API

Согласно пункту 2 CONTEXT.MD, используется Composition API. Пример использования task store в компонентах:

```vue
<script setup lang="ts">
import { useTaskStore } from '@/store'
import { ref, onMounted } from 'vue'

const taskStore = useTaskStore()
const textInput = ref('')
const selectedFile = ref<File | null>(null)

// Анализ одного текста
const analyzeSingleText = async () => {
  if (textInput.value.trim()) {
    const result = await taskStore.analyzeSingleText(textInput.value)
    if (result) {
      console.log('Analysis result:', result)
    }
  }
}

// Анализ batch файла
const analyzeBatchFile = async () => {
  if (selectedFile.value) {
    const result = await taskStore.analyzeBatchFile(selectedFile.value)
    if (result) {
      console.log('Batch analysis result:', result)
    }
  }
}

// Получить аналитические данные
const getAnalytics = () => {
  return taskStore.getAnalyticsData
}

// Проверка состояния загрузки
const isLoading = computed(() => taskStore.isLoading)
const hasError = computed(() => taskStore.hasError)

onMounted(() => {
  // Инициализация при необходимости
  taskStore.clearAllData()
})
</script>
```

## Доступность

Согласно пункту 19 CONTEXT.MD, все интерактивные элементы должны быть keyboard accessible с ARIA labels.

## Производительность

Согласно пункту 18 CONTEXT.MD, используются оптимизации:
- Lazy loading для компонентов
- shallowRef для больших объектов без глубокой реактивности

## Соответствие OpenAPI

Все методы API в frontend точно соответствуют описанным в OpenAPI спецификации:
- URL endpoints (`/api/v1/tasks/single`, `/api/v1/tasks/batch`, `/api/v1/tasks/result/{task_type}`)
- HTTP методы (POST для создания задач, GET для получения результатов)
- Request/Response форматы (JSON с четкой типизацией)
- Коды ошибок (обработка 400, 404, 422, 500)
- Типы данных (Task, SingleResult, BatchResult, TaskError)

Дополнительные возможности:
- Mock система для разработки и тестирования
- Продвинутая обработка ошибок с детализацией
- Состояние загрузки с сообщениями для пользователя
- Типизация TypeScript для всех операций

Это обеспечивает полную совместимость между frontend и backend реализациями с возможностью автономной разработки через mock систему.
