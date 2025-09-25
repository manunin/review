/**
 * Task Polling Composable
 * Handles UI logic for task polling and input blocking
 */

import { ref, computed, onUnmounted } from 'vue'
import { useTaskStore } from '@/store/task.store'
import { taskService } from '@/services/task.service'
import type { SingleResult, BatchResult } from '@/types/api.types'

export function useTaskPolling() {
  const taskStore = useTaskStore()
  
  // UI state
  const singleInputBlocked = ref(false)
  const batchInputBlocked = ref(false)
  
  // Polling state
  const singlePollingActive = ref(false)
  const batchPollingActive = ref(false)
  const singlePollingInterval = ref<number | null>(null)
  const batchPollingInterval = ref<number | null>(null)
  
  // Computed getters
  const isSingleInputBlocked = computed(() => singleInputBlocked.value)
  const isBatchInputBlocked = computed(() => batchInputBlocked.value)
  const isSinglePolling = computed(() => singlePollingActive.value)
  const isBatchPolling = computed(() => batchPollingActive.value)
  
  // Start single task polling
  const startSinglePolling = (taskId: string) => {
    stopSinglePolling() // Stop any existing polling
    
    singleInputBlocked.value = true
    singlePollingActive.value = true
    
    // Start polling every 5 seconds
    singlePollingInterval.value = window.setInterval(async () => {
      try {
        const resultData = await taskService.getLastSingleResult()
        
        if (resultData.success && resultData.data) {
          // Task completed successfully
          taskStore.setSingleResult(resultData.data)
          stopSinglePolling()
        } else if (resultData.statusCode === 202) {
          // Task still processing, continue polling
          console.log('Single task still processing...')
        } else if (resultData.statusCode === 404) {
          // No task found, stop polling
          stopSinglePolling()
        } else {
          // Error occurred, stop polling and show error
          taskStore.setError(resultData.error || 'Failed to check task status')
          stopSinglePolling()
        }
      } catch (error: any) {
        console.error('Error polling single task status:', error)
        taskStore.setError(error.message || 'Unexpected error while checking task status')
        stopSinglePolling()
      }
    }, 5000)
  }
  
  // Stop single task polling
  const stopSinglePolling = () => {
    if (singlePollingInterval.value !== null) {
      clearInterval(singlePollingInterval.value)
      singlePollingInterval.value = null
    }
    
    singlePollingActive.value = false
    singleInputBlocked.value = false
  }
  
  // Start batch task polling
  const startBatchPolling = (taskId: string) => {
    stopBatchPolling() // Stop any existing polling
    
    batchInputBlocked.value = true
    batchPollingActive.value = true
    
    // Start polling every 5 seconds
    batchPollingInterval.value = window.setInterval(async () => {
      try {
        const resultData = await taskService.getLastBatchResult()
        
        if (resultData.success && resultData.data) {
          // Task completed successfully
          taskStore.setBatchResult(resultData.data)
          stopBatchPolling()
        } else if (resultData.statusCode === 202) {
          // Task still processing, continue polling
          console.log('Batch task still processing...')
        } else if (resultData.statusCode === 404) {
          // No task found, stop polling
          stopBatchPolling()
        } else {
          // Error occurred, stop polling and show error
          taskStore.setError(resultData.error || 'Failed to check task status')
          stopBatchPolling()
        }
      } catch (error: any) {
        console.error('Error polling batch task status:', error)
        taskStore.setError(error.message || 'Unexpected error while checking task status')
        stopBatchPolling()
      }
    }, 5000)
  }
  
  // Stop batch task polling
  const stopBatchPolling = () => {
    if (batchPollingInterval.value !== null) {
      clearInterval(batchPollingInterval.value)
      batchPollingInterval.value = null
    }
    
    batchPollingActive.value = false
    batchInputBlocked.value = false
  }
  
  // Enhanced analyze functions that handle polling
  const analyzeSingleTextWithPolling = async (text: string): Promise<SingleResult | null> => {
    const result = await taskStore.analyzeSingleText(text)
    
    // If no immediate result, check if we need to start polling
    if (!result && taskStore.getCurrentSingleTaskId) {
      const taskId = taskStore.getCurrentSingleTaskId
      if (taskId) {
        startSinglePolling(taskId)
      }
    }
    
    return result
  }
  
  const analyzeBatchFileWithPolling = async (file: File): Promise<BatchResult | null> => {
    const result = await taskStore.analyzeBatchFile(file)
    
    // If no immediate result, check if we need to start polling
    if (!result && taskStore.getCurrentBatchTaskId) {
      const taskId = taskStore.getCurrentBatchTaskId
      if (taskId) {
        startBatchPolling(taskId)
      }
    }
    
    return result
  }
  
  // Cleanup on unmount
  onUnmounted(() => {
    stopSinglePolling()
    stopBatchPolling()
  })
  
  return {
    // State
    isSingleInputBlocked,
    isBatchInputBlocked,
    isSinglePolling,
    isBatchPolling,
    
    // Actions
    startSinglePolling,
    stopSinglePolling,
    startBatchPolling,
    stopBatchPolling,
    analyzeSingleTextWithPolling,
    analyzeBatchFileWithPolling
  }
}
