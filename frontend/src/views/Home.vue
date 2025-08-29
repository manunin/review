<template>
  <div>
    <!-- Hero Section -->
    <div class="grid">
      <div class="col-12">
        <Card class="p-mb-6 bg-primary">
          <template #header>
            <div class="p-p-6 text-center">
              <h1 class="text-4xl p-mb-4">
                Viewman
              </h1>
              <h2 class="text-xl p-mb-4">
                AI-powered sentiment analysis platform for reviews
              </h2>
              <p class="text-lg">
                Upload your reviews and get instant sentiment analysis with detailed statistics and insights.
              </p>
            </div>
          </template>
          <template #content>
            <div class="p-p-6 text-center">
              <Button 
                label="Get Started" 
                icon="pi pi-upload" 
                class="p-button-outlined p-mr-4"
                @click="router.push('/upload')"
              />
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Features Section -->
    <div class="grid">
      <div class="col-12">
        <h2 class="text-center text-3xl p-mb-6">Key Features</h2>
      </div>
    </div>

    <div class="grid">
      <div 
        v-for="feature in features" 
        :key="feature.title"
        class="col-12 md:col-4"
      >
        <Card class="h-full">
          <template #content>
            <div class="text-center p-p-4">
              <i :class="feature.icon" :style="`color: ${feature.color}; font-size: 4rem`" class="p-mb-4 block"></i>
              <h3 class="text-xl p-mb-3">{{ feature.title }}</h3>
              <p class="text-base">{{ feature.description }}</p>
            </div>
          </template>
        </Card>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useReviewStore } from '@/store'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

interface Feature {
  title: string
  description: string
  icon: string
  color: string
}

const router = useRouter()
const reviewStore = useReviewStore()

const features: Feature[] = [
  {
    title: 'Sentiment Analysis',
    description: 'Automatic detection of emotional tone in reviews (positive, negative, neutral)',
    icon: 'pi pi-thumbs-up',
    color: 'var(--primary-color)'
  },
  {
    title: 'Batch Processing',
    description: 'Upload and analyze multiple reviews simultaneously with support for various file formats',
    icon: 'pi pi-file',
    color: 'var(--green-500)'
  },
  {
    title: 'Interactive Analytics',
    description: 'Visual insights with charts, graphs, and detailed statistical breakdowns',
    icon: 'pi pi-chart-pie',
    color: 'var(--orange-500)'
  }
]

onMounted(async (): Promise<void> => {
  await reviewStore.fetchAnalytics()
})
</script>

<style scoped>
.p-card {
  transition: transform 0.2s;
}

.p-card:hover {
  transform: translateY(-4px);
}
</style>
