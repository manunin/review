
<template>
  <div>
    <div class="flex flex-wrap gap-4 p-mb-6 align-items-stretch" style="height: 14rem;">
      <div class="flex-1 min-w-20rem h-full">
        <Card class="p-mb-6 h-full">
          <template #title>
            <i class="pi pi-comment p-mr-2"></i>
            Analyze Single Review
          </template>
          <template #content>
            <Textarea
              v-model="singleReviewText"
              placeholder="Type or paste a review here..."
              :rows="4"
              :disabled="analyzing || taskPolling.isSingleInputBlocked.value"
              class="w-full p-mb-3"
              style="resize: none"
            />
            <Button
              label="Analyze Sentiment"
              icon="pi pi-search"
              :loading="analyzing"
              :disabled="!singleReviewText.trim() || taskPolling.isSingleInputBlocked.value"
              @click="analyzeSingleReview"
              class="p-mt-2"
            />
            <!-- Polling status message -->
            <div v-if="taskPolling.isSinglePolling.value" class="p-mt-3">
              <Message severity="info" :closable="false">
                <div class="flex align-items-center">
                  <ProgressSpinner style="width: 20px; height: 20px" strokeWidth="4" />
                  <span class="p-ml-2">Task is being processed... Checking status every 5 seconds.</span>
                </div>
              </Message>
            </div>
          </template>
        </Card>
      </div>
      <div class="flex-1 min-w-20rem h-full flex flex-column">
        <Card class="h-full flex flex-column">
          <template #title>
            <i class="pi pi-upload p-mr-2"></i>
            Batch Upload
          </template>
          <template #content>
            <div class="flex flex-column h-full flex-1 justify-content-between text-center">
              <div class="flex justify-content-center align-items-center gap-2 p-mb-2 font-medium text-base">
                <div class="w-12">
                  <FileUpload
                    ref="fileUploadRef"
                    mode="basic"
                    :auto="false"
                    accept=".csv,.txt,.json"
                    :maxFileSize="52428800"
                    @select="onFileSelect"
                    :disabled="uploading || taskPolling.isBatchInputBlocked.value"
                    chooseLabel="Choose File"
                    class="w-full font-medium text-base"
                  />
                </div>
                <Button
                  label="Upload and Analyze"
                  icon="pi pi-cloud-upload"
                  :loading="uploading"
                  :disabled="!selectedFile || taskPolling.isBatchInputBlocked.value"
                  @click="uploadFile"
                  class="w-12 font-medium text-base"
                />
              </div>
              <!-- Polling status message -->
              <div v-if="taskPolling.isBatchPolling.value" class="p-mt-3">
                <Message severity="info" :closable="false">
                  <div class="flex align-items-center">
                    <ProgressSpinner style="width: 20px; height: 20px" strokeWidth="4" />
                    <span class="p-ml-2">Batch task is being processed... Checking status every 5 seconds.</span>
                  </div>
                </Message>
              </div>
              <div class="mt-2 p-mt-2 text-base text-color-secondary">
                Supported formats: CSV, TXT, JSON (Max size: 50MB)
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Аналитика -->
    <Card v-if="!loading && singleReviewResult" class="mt-6">
        <template #title>
        <i class="pi pi-chart-line p-mr-2"></i>
            Single Review Results
        </template>
        <template #content>
        <div class="flex align-items-center">
            <i
            :class="getSentimentIcon(singleReviewResult.sentiment)"
            :style="`color: ${getSentimentColor(singleReviewResult.sentiment)}; font-size: 2rem`"
            class="p-mr-3"
            ></i>
            <div>
            <div class="ml-2 text-xl font-bold">
                {{ singleReviewResult.sentiment.toUpperCase() }}
            </div>
            <div class="ml-2 text-sm">
                Confidence: {{ (singleReviewResult.confidence * 100).toFixed(1) }}%
            </div>
            </div>
        </div>
        </template>
    </Card>

    <Card v-if="!loading && uploadResult" class="mt-6">
      <template #title>
        <i class="pi pi-chart-line p-mr-2"></i>
        Butch Results
      </template>
      <template #content>
    <!-- Analytics Summary Cards -->
    <div class="mt-6 grid p-mt-12">
      <div class="col-12 sm:col-6 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="p-p-4">
              <i class="pi pi-comments p-mb-2 block" style="color: var(--primary-color); font-size: 3rem"></i>
              <div class="text-3xl font-bold">{{ analytics.total_reviews || 0 }}</div>
              <div class="text-base">Total Reviews</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 sm:col-6 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="p-p-4">
              <i class="pi pi-thumbs-up p-mb-2 block" style="color: var(--green-500); font-size: 3rem"></i>
              <div class="text-3xl font-bold" style="color: var(--green-500)">{{ analytics.positive || 0 }}</div>
              <div class="text-base">Positive ({{ analytics.positive_percentage || 0 }}%)</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 sm:col-6 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="p-p-4">
              <i class="pi pi-thumbs-down p-mb-2 block" style="color: var(--red-500); font-size: 3rem"></i>
              <div class="text-3xl font-bold" style="color: var(--red-500)">{{ analytics.negative || 0 }}</div>
              <div class="text-base">Negative ({{ analytics.negative_percentage || 0 }}%)</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 sm:col-6 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="p-p-4">
              <i class="pi pi-minus p-mb-2 block" style="color: var(--orange-500); font-size: 3rem"></i>
              <div class="text-3xl font-bold" style="color: var(--orange-500)">{{ analytics.neutral || 0 }}</div>
              <div class="text-base">Neutral ({{ analytics.neutral_percentage || 0 }}%)</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid" v-if="!loading && analytics && analytics.total_reviews > 0">
      <div class="col-12 md:col-6">
        <Card>
          <template #title>
            <i class="pi pi-chart-pie p-mr-2"></i>
            Sentiment Distribution
          </template>
          <template #content>
            <canvas ref="pieChart" width="400" height="400"></canvas>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6">
        <Card>
          <template #title>
            <i class="pi pi-chart-bar p-mr-2"></i>
            Sentiment Comparison
          </template>
          <template #content>
            <canvas ref="barChart" width="400" height="400"></canvas>
          </template>
        </Card>
      </div>
    </div>

    <!-- Insights -->
    <div class="grid" v-if="!loading && analytics && analytics.total_reviews > 0">
      <div class="col-12">
        <Card>
          <template #title>
            <i class="pi pi-lightbulb p-mr-2"></i>
            Key Insights
          </template>
          <template #content>
            <div class="p-mb-3">
              <div class="flex align-items-center p-mb-3">
                <i
                  :class="`${dominantSentimentIcon} p-mr-3`"
                  :style="`color: ${dominantSentimentColor}; font-size: 1.5rem`"
                ></i>
                <div>
                  <div class="font-bold">
                    Dominant Sentiment: {{ dominantSentiment.charAt(0).toUpperCase() + dominantSentiment.slice(1) }}
                  </div>
                  <div class="text-sm text-color-secondary">
                    {{ dominantPercentage }}% of reviews show {{ dominantSentiment }} sentiment
                  </div>
                </div>
              </div>
              <div
                v-if="analytics.positive_percentage && analytics.positive_percentage > 70"
                class="flex align-items-center p-mb-3"
              >
                <i class="pi pi-check-circle p-mr-3" style="color: var(--green-500); font-size: 1.5rem"></i>
                <div>
                  <div class="font-bold">Excellent Customer Satisfaction</div>
                  <div class="text-sm text-color-secondary">
                    Over 70% positive sentiment indicates very good customer satisfaction
                  </div>
                </div>
              </div>
              <div
                v-else-if="analytics.negative_percentage && analytics.negative_percentage > 50"
                class="flex align-items-center p-mb-3"
              >
                <i class="pi pi-exclamation-triangle p-mr-3" style="color: var(--red-500); font-size: 1.5rem"></i>
                <div>
                  <div class="font-bold">Attention Required</div>
                  <div class="text-sm text-color-secondary">
                    High negative sentiment suggests areas for improvement
                  </div>
                </div>
              </div>
              <div
                v-else-if="analytics.neutral_percentage && analytics.neutral_percentage > 40"
                class="flex align-items-center p-mb-3"
              >
                <i class="pi pi-minus p-mr-3" style="color: var(--orange-500); font-size: 1.5rem"></i>
                <div>
                  <div class="font-bold">Mixed Reactions</div>
                  <div class="text-sm text-color-secondary">
                    High neutral sentiment indicates moderate satisfaction
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { useTaskStore } from '@/store'
import { useTaskPolling } from '@/composables/useTaskPolling'
import { useToast } from 'vue-toastification'
import { ref, computed, onMounted, nextTick, watch, type Ref } from 'vue'
import { Chart, registerables } from 'chart.js'
import type { SingleResult, BatchResult } from '@/types/api.types'

Chart.register(...registerables)

const taskStore = useTaskStore()
const taskPolling = useTaskPolling()
const toast = useToast()

// Reactive refs with proper typing
const singleReviewText: Ref<string> = ref('')
const singleReviewResult: Ref<SingleResult | null> = ref(null)
const selectedFile: Ref<File | null> = ref(null)
const uploadResult: Ref<BatchResult | null> = ref(null)

// Chart refs
const pieChart: Ref<HTMLCanvasElement | null> = ref(null)
const barChart: Ref<HTMLCanvasElement | null> = ref(null)
const fileUploadRef: Ref<any> = ref(null)

// Analytics computed
const analytics = computed(() => taskStore.getAnalyticsData)
const loading = computed(() => taskStore.isLoading)
const analyzing = computed(() => taskStore.isLoading || taskPolling.isSinglePolling.value)
const uploading = computed(() => taskStore.isLoading || taskPolling.isBatchPolling.value)

const dominantSentiment = computed((): string => {
  if (!analytics.value || analytics.value.total_reviews === 0) return 'neutral'
  const sentiments = [
    { name: 'positive', count: analytics.value.positive || 0 },
    { name: 'negative', count: analytics.value.negative || 0 },
    { name: 'neutral', count: analytics.value.neutral || 0 }
  ]
  return sentiments.reduce((prev, current) => prev.count > current.count ? prev : current).name
})

const dominantPercentage = computed((): number => {
  if (!analytics.value) return 0
  const percentages = {
    positive: analytics.value.positive_percentage || 0,
    negative: analytics.value.negative_percentage || 0,
    neutral: analytics.value.neutral_percentage || 0
  }
  return percentages[dominantSentiment.value as keyof typeof percentages] || 0
})

const dominantSentimentColor = computed((): string => {
  const colors = {
    positive: 'var(--green-500)',
    negative: 'var(--red-500)',
    neutral: 'var(--orange-500)'
  }
  return colors[dominantSentiment.value as keyof typeof colors] || 'var(--surface-400)'
})

const dominantSentimentIcon = computed((): string => {
  const icons = {
    positive: 'pi pi-thumbs-up',
    negative: 'pi pi-thumbs-down',
    neutral: 'pi pi-minus'
  }
  return icons[dominantSentiment.value as keyof typeof icons] || 'pi pi-question'
})
// Chart creation functions
const createPieChart = (): void => {
  if (!pieChart.value || !analytics.value || analytics.value.total_reviews === 0) return
  const ctx = pieChart.value.getContext('2d')
  if (!ctx) return
  
  Chart.getChart(pieChart.value)?.destroy()
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Positive', 'Negative', 'Neutral'],
      datasets: [{
        data: [
          analytics.value.positive || 0,
          analytics.value.negative || 0,
          analytics.value.neutral || 0
        ],
        backgroundColor: [
          '#4CAF50',
          '#F44336',
          '#FF9800'
        ],
        borderColor: [
          '#388E3C',
          '#D32F2F',
          '#F57C00'
        ],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { padding: 20 }
        }
      }
    }
  })
}

const createBarChart = (): void => {
  if (!barChart.value || !analytics.value || analytics.value.total_reviews === 0) return
  const ctx = barChart.value.getContext('2d')
  if (!ctx) return
  
  Chart.getChart(barChart.value)?.destroy()
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Positive', 'Negative', 'Neutral'],
      datasets: [{
        label: 'Number of Reviews',
        data: [
          analytics.value.positive || 0,
          analytics.value.negative || 0,
          analytics.value.neutral || 0
        ],
        backgroundColor: [
          '#4CAF50',
          '#F44336',
          '#FF9800'
        ],
        borderColor: [
          '#388E3C',
          '#D32F2F',
          '#F57C00'
        ],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  })
}

// Lifecycle hooks
onMounted(async (): Promise<void> => {
  // Task store automatically provides analytics from batch results
  nextTick(() => {
    if (analytics.value.total_reviews > 0) {
      createPieChart()
      createBarChart()
    }
  })
})

watch(analytics, () => {
  nextTick(() => {
    if (analytics.value.total_reviews > 0) {
      createPieChart()
      createBarChart()
    }
  })
}, { deep: true })

// Action functions
const analyzeSingleReview = async (): Promise<void> => {
  if (!singleReviewText.value.trim()) return
  
  singleReviewResult.value = null
  
  try {
    const result = await taskPolling.analyzeSingleTextWithPolling(singleReviewText.value)
    if (result) {
      singleReviewResult.value = result
      uploadResult.value = null
      toast.success('Review analyzed successfully!')
    } else if (taskPolling.isSinglePolling.value) {
      toast.info('Review submitted for processing. You will see results when ready.')
    } else {
      toast.error('Failed to analyze review - no result returned')
    }
  } catch (error: any) {
    toast.error('Failed to analyze review: ' + error.message)
  }
}

interface FileSelectEvent {
  files: File[]
}

const onFileSelect = (event: FileSelectEvent): void => {
  uploadResult.value = null
  selectedFile.value = event.files[0] || null
}

const uploadFile = async (): Promise<void> => {
  if (!selectedFile.value) return

  uploadResult.value = null
  
  try {
    const result = await taskPolling.analyzeBatchFileWithPolling(selectedFile.value)
    if (result) {
      singleReviewResult.value = null
      uploadResult.value = result
      toast.success('File uploaded and analyzed successfully!')
      
      // Update charts with new data
      nextTick(() => {
        createPieChart()
        createBarChart()
      })

      clearSelectedFile()
    } else if (taskPolling.isBatchPolling.value) {
      toast.info('File submitted for processing. You will see analytics when ready.')
    } else {
      toast.error('Upload failed - no result returned')
    }
  } catch (error: any) {
    toast.error('Upload failed: ' + error.message)
  }
}

const clearSelectedFile = (): void => {
  selectedFile.value = null
  if (fileUploadRef.value) {
    fileUploadRef.value.clear()
  }
}

// Watchers for store state changes
watch(() => taskStore.lastSingleResult, (newResult) => {
  if (newResult && !taskPolling.isSinglePolling.value) {
    singleReviewResult.value = newResult
    uploadResult.value = null
    toast.success('Review analysis completed!')
  }
})

watch(() => taskStore.lastBatchResult, (newResult) => {
  if (newResult && !taskPolling.isBatchPolling.value) {
    singleReviewResult.value = null
    uploadResult.value = newResult
    toast.success('Batch analysis completed!')
    
    // Update charts with new data
    nextTick(() => {
      createPieChart()
      createBarChart()
    })
  }
})

// Helper functions
const getSentimentColor = (sentiment: string): string => {
  const colors = {
    positive: 'var(--green-500)',
    negative: 'var(--red-500)',
    neutral: 'var(--orange-500)'
  }
  return colors[sentiment as keyof typeof colors] || 'var(--surface-400)'
}

const getSentimentIcon = (sentiment: string): string => {
  const icons = {
    positive: 'pi pi-thumbs-up',
    negative: 'pi pi-thumbs-down',
    neutral: 'pi pi-minus'
  }
  return icons[sentiment as keyof typeof icons] || 'pi pi-question'
}
</script>
<style scoped>
.p-fileupload {
  max-width: 400px;
  margin: 0 auto;
}
</style>
