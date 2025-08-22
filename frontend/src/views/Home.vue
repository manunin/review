<template>
  <div>
    <!-- Hero Section -->
    <v-row>
      <v-col cols="12">
        <v-card class="pa-6 mb-6" color="primary" dark>
          <v-card-title class="text-h3 mb-4">
            <v-icon size="48" class="mr-4">mdi-magnify</v-icon>
            Smart Review Analyzer
          </v-card-title>
          <v-card-subtitle class="text-h6 mb-4">
            AI-powered sentiment analysis platform for reviews
          </v-card-subtitle>
          <v-card-text class="text-h6">
            Upload your reviews and get instant sentiment analysis with detailed statistics and insights.
          </v-card-text>
          <v-card-actions>
            <v-btn 
              size="large" 
              color="white" 
              variant="outlined" 
              :to="'/upload'"
              class="mr-4"
            >
              <v-icon left>mdi-upload</v-icon>
              Get Started
            </v-btn>
            <v-btn 
              size="large" 
              color="white" 
              variant="text" 
              :to="'/analytics'"
            >
              <v-icon left>mdi-chart-line</v-icon>
              View Analytics
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Features Section -->
    <v-row>
      <v-col cols="12">
        <h2 class="text-h4 mb-6 text-center">Key Features</h2>
      </v-col>
    </v-row>

    <v-row>
      <v-col 
        v-for="feature in features" 
        :key="feature.title"
        cols="12" 
        md="4"
      >
        <v-card height="300" class="d-flex flex-column">
          <v-card-text class="d-flex flex-column flex-grow-1">
            <div class="text-center mb-4">
              <v-icon :color="feature.color" size="64">{{ feature.icon }}</v-icon>
            </div>
            <h3 class="text-h5 text-center mb-3">{{ feature.title }}</h3>
            <p class="text-body-1 text-center flex-grow-1">{{ feature.description }}</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Stats -->
    <v-row class="mt-8">
      <v-col cols="12">
        <h2 class="text-h4 mb-6 text-center">Quick Statistics</h2>
      </v-col>
    </v-row>

    <v-row v-if="!loading">
      <v-col 
        v-for="stat in stats" 
        :key="stat.title"
        cols="12" 
        sm="6" 
        md="3"
      >
        <v-card class="text-center pa-4">
          <v-icon :color="stat.color" size="48" class="mb-2">{{ stat.icon }}</v-icon>
          <div class="text-h4 font-weight-bold">{{ stat.value }}</div>
          <div class="text-body-1">{{ stat.title }}</div>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-else>
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="mt-4">Loading statistics...</p>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { useReviewStore } from '@/store'
import { storeToRefs } from 'pinia'
import { onMounted, computed } from 'vue'

export default {
  name: 'Home',
  setup() {
    const reviewStore = useReviewStore()
    const { analytics, loading } = storeToRefs(reviewStore)
    
    const features = [
      {
        title: 'Sentiment Analysis',
        description: 'Automatic detection of emotional tone in reviews (positive, negative, neutral)',
        icon: 'mdi-brain',
        color: 'primary'
      },
      {
        title: 'Batch Processing',
        description: 'Upload and analyze multiple reviews simultaneously with support for various file formats',
        icon: 'mdi-file-multiple',
        color: 'success'
      },
      {
        title: 'Interactive Analytics',
        description: 'Visual insights with charts, graphs, and detailed statistical breakdowns',
        icon: 'mdi-chart-pie',
        color: 'warning'
      }
    ]

    const stats = computed(() => [
      {
        title: 'Total Reviews',
        value: analytics.value.total_reviews || 0,
        icon: 'mdi-comment-text-multiple',
        color: 'primary'
      },
      {
        title: 'Positive',
        value: `${analytics.value.positive_percentage || 0}%`,
        icon: 'mdi-emoticon-happy',
        color: 'success'
      },
      {
        title: 'Negative',
        value: `${analytics.value.negative_percentage || 0}%`,
        icon: 'mdi-emoticon-sad',
        color: 'error'
      },
      {
        title: 'Neutral',
        value: `${analytics.value.neutral_percentage || 0}%`,
        icon: 'mdi-emoticon-neutral',
        color: 'warning'
      }
    ])

    onMounted(async () => {
      await reviewStore.fetchAnalytics()
    })

    return {
      features,
      stats,
      analytics,
      loading
    }
  }
}
</script>

<style scoped>
.v-card {
  transition: transform 0.2s;
}

.v-card:hover {
  transform: translateY(-4px);
}
</style>
