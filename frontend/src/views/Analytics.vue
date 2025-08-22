<template>
  <div>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h3 mb-6">Analytics</h1>
        <p class="text-h6 mb-6">
          Detailed sentiment analysis and insights
        </p>
      </v-col>
    </v-row>

    <!-- Overview Cards -->
    <v-row v-if="!loading && analytics">
      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center pa-4">
          <v-icon color="primary" size="48" class="mb-2">mdi-comment-text-multiple</v-icon>
          <div class="text-h4 font-weight-bold">{{ analytics.total_reviews || 0 }}</div>
          <div class="text-body-1">Total Reviews</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center pa-4">
          <v-icon color="success" size="48" class="mb-2">mdi-emoticon-happy</v-icon>
          <div class="text-h4 font-weight-bold text-success">{{ analytics.positive || 0 }}</div>
          <div class="text-body-1">Positive ({{ analytics.positive_percentage || 0 }}%)</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center pa-4">
          <v-icon color="error" size="48" class="mb-2">mdi-emoticon-sad</v-icon>
          <div class="text-h4 font-weight-bold text-error">{{ analytics.negative || 0 }}</div>
          <div class="text-body-1">Negative ({{ analytics.negative_percentage || 0 }}%)</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center pa-4">
          <v-icon color="warning" size="48" class="mb-2">mdi-emoticon-neutral</v-icon>
          <div class="text-h4 font-weight-bold text-warning">{{ analytics.neutral || 0 }}</div>
          <div class="text-body-1">Neutral ({{ analytics.neutral_percentage || 0 }}%)</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts -->
        <!-- Charts -->
    <v-row v-if="!loading && analytics && analytics.total_reviews > 0">
      <!-- Pie Chart -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-pie</v-icon>
            Sentiment Distribution
          </v-card-title>
          <v-card-text>
            <canvas ref="pieChart" width="400" height="400"></canvas>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Bar Chart -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-bar</v-icon>
            Sentiment Comparison
          </v-card-title>
          <v-card-text>
            <canvas ref="barChart" width="400" height="400"></canvas>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Insights -->
    <v-row v-if="!loading && analytics && analytics.total_reviews > 0">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-lightbulb</v-icon>
            Key Insights
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon :color="dominantSentimentColor">{{ dominantSentimentIcon }}</v-icon>
                </template>
                <v-list-item-title>
                  Dominant Sentiment: {{ dominantSentiment.charAt(0).toUpperCase() + dominantSentiment.slice(1) }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ dominantPercentage }}% of reviews show {{ dominantSentiment }} sentiment
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item v-if="analytics.positive_percentage && analytics.positive_percentage > 70">
                <template v-slot:prepend>
                  <v-icon color="success">mdi-check-circle</v-icon>
                </template>
                <v-list-item-title>Excellent Customer Satisfaction</v-list-item-title>
                <v-list-item-subtitle>
                  Over 70% positive sentiment indicates very good customer satisfaction
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item v-else-if="analytics.negative_percentage && analytics.negative_percentage > 50">
                <template v-slot:prepend>
                  <v-icon color="error">mdi-alert</v-icon>
                </template>
                <v-list-item-title>Attention Required</v-list-item-title>
                <v-list-item-subtitle>
                  High negative sentiment suggests areas for improvement
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item v-else-if="analytics.neutral_percentage && analytics.neutral_percentage > 40">
                <template v-slot:prepend>
                  <v-icon color="warning">mdi-minus</v-icon>
                </template>
                <v-list-item-title>Mixed Reactions</v-list-item-title>
                <v-list-item-subtitle>
                  High neutral sentiment indicates moderate satisfaction
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-if="loading">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="mt-4">Loading analytics...</p>
      </v-col>
    </v-row>

    <!-- Empty State -->
    <v-row v-if="!loading && analytics && analytics.total_reviews === 0">
      <v-col cols="12" class="text-center">
        <v-icon size="64" color="grey">mdi-chart-line</v-icon>
        <h3 class="text-h5 mt-4 mb-2">No Data Available</h3>
        <p class="text-body-1 mb-4">
          Upload some reviews to see analytics and insights.
        </p>
        <v-btn color="primary" :to="'/upload'">
          <v-icon left>mdi-upload</v-icon>
          Upload Reviews
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { useReviewStore } from '@/store'
import { Chart, registerables } from 'chart.js'
import { computed, onMounted, nextTick, watch, ref } from 'vue'

Chart.register(...registerables)

export default {
  name: 'Analytics',
  setup() {
    const reviewStore = useReviewStore()
    const pieChart = ref(null)
    const barChart = ref(null)
    
    const analytics = computed(() => reviewStore.analytics)
    const loading = computed(() => reviewStore.loading)
    
    const dominantSentiment = computed(() => {
      if (!analytics.value || analytics.value.total_reviews === 0) return 'neutral'
      
      const sentiments = [
        { name: 'positive', count: analytics.value.positive || 0 },
        { name: 'negative', count: analytics.value.negative || 0 },
        { name: 'neutral', count: analytics.value.neutral || 0 }
      ]
      return sentiments.reduce((prev, current) => 
        prev.count > current.count ? prev : current
      ).name
    })
    
    const dominantPercentage = computed(() => {
      if (!analytics.value) return 0
      
      const percentages = {
        positive: analytics.value.positive_percentage || 0,
        negative: analytics.value.negative_percentage || 0,
        neutral: analytics.value.neutral_percentage || 0
      }
      return percentages[dominantSentiment.value] || 0
    })
    
    const dominantSentimentColor = computed(() => {
      const colors = {
        positive: 'success',
        negative: 'error',
        neutral: 'warning'
      }
      return colors[dominantSentiment.value]
    })
    
    const dominantSentimentIcon = computed(() => {
      const icons = {
        positive: 'mdi-emoticon-happy',
        negative: 'mdi-emoticon-sad',
        neutral: 'mdi-emoticon-neutral'
      }
      return icons[dominantSentiment.value]
    })
    
    const createPieChart = () => {
      if (!pieChart.value || !analytics.value || analytics.value.total_reviews === 0) return
      
      const ctx = pieChart.value.getContext('2d')
      
      // Clear any existing chart
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
              labels: {
                padding: 20
              }
            }
          }
        }
      })
    }
    
    const createBarChart = () => {
      if (!barChart.value || !analytics.value || analytics.value.total_reviews === 0) return
      
      const ctx = barChart.value.getContext('2d')
      
      // Clear any existing chart
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
              ticks: {
                stepSize: 1
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })
    }
    
    onMounted(async () => {
      await reviewStore.fetchAnalytics()
      
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

    return {
      pieChart,
      barChart,
      analytics,
      loading,
      dominantSentiment,
      dominantPercentage,
      dominantSentimentColor,
      dominantSentimentIcon
    }
  }
}
</script>

<style scoped>
canvas {
  max-height: 300px;
}
</style>
