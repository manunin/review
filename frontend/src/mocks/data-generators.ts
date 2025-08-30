/**
 * Mock data generators
 * Generates realistic data for development and testing
 */

import type {
  Task,
  SingleResult,
  BatchResult,
  TaskError,
  SentimentType,
  TaskType,
  TaskStatus,
  TaskErrorCode
} from '@/types/api.types'

/**
 * Generates a random UUID-like string
 */
export function generateUuid(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

/**
 * Generates a random sentiment with confidence
 */
export function generateSentiment(): { sentiment: SentimentType; confidence: number } {
  const sentiments: SentimentType[] = ['positive', 'negative', 'neutral']
  const weights = [0.5, 0.3, 0.2] // Positive is more likely
  
  let random = Math.random()
  let sentiment: SentimentType = 'positive'
  
  for (let i = 0; i < weights.length; i++) {
    const weight = weights[i]
    const currentSentiment = sentiments[i]
    if (weight && currentSentiment && random < weight) {
      sentiment = currentSentiment
      break
    }
    if (weight) {
      random -= weight
    }
  }
  
  // Higher confidence for positive sentiment
  const confidence = sentiment === 'positive' 
    ? 0.8 + Math.random() * 0.2
    : 0.6 + Math.random() * 0.4
    
  return {
    sentiment,
    confidence: Math.round(confidence * 100) / 100
  }
}

/**
 * Generates sample texts for different sentiments
 */
export function generateSampleText(sentiment?: SentimentType): string {
  const texts = {
    positive: [
      'Excellent product, very satisfied with the quality!',
      'Amazing service, highly recommend to everyone!',
      'Great experience, will definitely buy again!',
      'Outstanding quality and fast delivery!',
      'Perfect product, exceeded my expectations!'
    ],
    negative: [
      'Terrible quality, very disappointed with this purchase.',
      'Poor service, would not recommend to anyone.',
      'Worst experience ever, complete waste of money.',
      'Product broke after one day of use.',
      'Horrible customer service, very rude staff.'
    ],
    neutral: [
      'The product is okay, nothing special but does the job.',
      'Average quality, met basic expectations.',
      'Standard service, no complaints but nothing outstanding.',
      'Decent product for the price point.',
      'Regular experience, everything was as expected.'
    ]
  }
  
  const category: SentimentType = sentiment || (['positive', 'negative', 'neutral'] as SentimentType[])[Math.floor(Math.random() * 3)]
  const categoryTexts = texts[category]
  return categoryTexts[Math.floor(Math.random() * categoryTexts.length)]
}

/**
 * Generates a single result with optional text
 */
export function generateSingleResult(text?: string): SingleResult {
  const { sentiment, confidence } = generateSentiment()
  
  return {
    sentiment,
    confidence,
    text: text || generateSampleText(sentiment)
  }
}

/**
 * Generates batch analysis results
 */
export function generateBatchResult(totalReviews?: number): BatchResult {
  const total = totalReviews || Math.floor(Math.random() * 400) + 100 // 100-500 reviews
  
  // Generate realistic distribution
  const positiveRate = 0.4 + Math.random() * 0.3 // 40-70%
  const negativeRate = 0.1 + Math.random() * 0.2 // 10-30%
  const neutralRate = 1 - positiveRate - negativeRate
  
  const positive = Math.floor(total * positiveRate)
  const negative = Math.floor(total * negativeRate)
  const neutral = total - positive - negative
  
  return {
    total_reviews: total,
    positive,
    negative,
    neutral,
    positive_percentage: Math.round((positive / total) * 100 * 10) / 10,
    negative_percentage: Math.round((negative / total) * 100 * 10) / 10,
    neutral_percentage: Math.round((neutral / total) * 100 * 10) / 10
  }
}

/**
 * Generates a task error
 */
export function generateTaskError(): TaskError {
  const codes: TaskErrorCode[] = ['01', '02', '03']
  const descriptions = [
    'Analysis model temporarily unavailable',
    'Text processing failed due to encoding issues',
    'Task execution timeout exceeded'
  ]
  
  const randomIndex = Math.floor(Math.random() * codes.length)
  
  return {
    code: codes[randomIndex],
    description: descriptions[randomIndex]
  }
}

/**
 * Generates a complete task object
 */
export function generateTask(
  type: TaskType,
  status: TaskStatus,
  text?: string,
  totalReviews?: number
): Task {
  const taskId = generateUuid()
  const start = Math.floor(Date.now() / 1000) - Math.floor(Math.random() * 3600) // Within last hour
  const hasResult = status === 'ready'
  const hasError = status === 'error'
  
  let result: SingleResult | BatchResult | undefined
  let error: TaskError | undefined
  let end: number | undefined
  
  if (hasResult) {
    end = start + Math.floor(Math.random() * 300) + 10 // 10-310 seconds later
    result = type === 'single' 
      ? generateSingleResult(text)
      : generateBatchResult(totalReviews)
  }
  
  if (hasError) {
    end = start + Math.floor(Math.random() * 60) + 5 // 5-65 seconds later
    error = generateTaskError()
  }
  
  return {
    task_id: taskId,
    type,
    status,
    start,
    end,
    result,
    error
  }
}

/**
 * Generates multiple tasks for testing
 */
export function generateTasks(count: number): Task[] {
  const tasks: Task[] = []
  const types: TaskType[] = ['single', 'batch']
  const statuses: TaskStatus[] = ['accepted', 'queued', 'ready', 'error']
  
  for (let i = 0; i < count; i++) {
    const type = types[Math.floor(Math.random() * types.length)]
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    
    tasks.push(generateTask(type, status))
  }
  
  return tasks
}
