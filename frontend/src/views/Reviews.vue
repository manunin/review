<template>
  <div>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h3 mb-6">Reviews</h1>
        <p class="text-h6 mb-6">
          Browse and manage analyzed reviews
        </p>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-row>
      <v-col cols="12" md="4">
        <v-select
          v-model="selectedSentiment"
          :items="sentimentOptions"
          label="Filter by Sentiment"
          variant="outlined"
          @update:model-value="filterReviews"
        ></v-select>
      </v-col>
      <v-col cols="12" md="4">
        <v-text-field
          v-model="searchText"
          label="Search reviews"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          @input="filterReviews"
        ></v-text-field>
      </v-col>
      <v-col cols="12" md="4" class="d-flex align-center">
        <v-btn 
          color="primary" 
          @click="refreshReviews"
          :loading="loading"
        >
          <v-icon left>mdi-refresh</v-icon>
          Refresh
        </v-btn>
      </v-col>
    </v-row>

    <!-- Reviews List -->
    <v-row v-if="!loading && filteredReviews.length > 0">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-comment-text-multiple</v-icon>
            Reviews ({{ filteredReviews.length }})
          </v-card-title>
          <v-card-text class="pa-0">
            <v-list>
              <v-list-item
                v-for="review in paginatedReviews"
                :key="review.id"
                class="border-b"
              >
                <template v-slot:prepend>
                  <v-avatar :color="getSentimentColor(review.sentiment)">
                    <v-icon color="white">{{ getSentimentIcon(review.sentiment) }}</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title class="text-wrap">
                  {{ review.text }}
                </v-list-item-title>
                
                <v-list-item-subtitle>
                  <v-chip 
                    :color="getSentimentColor(review.sentiment)" 
                    size="small" 
                    class="mr-2"
                  >
                    {{ review.sentiment.toUpperCase() }}
                  </v-chip>
                  <span class="text-caption">
                    Confidence: {{ (review.confidence * 100).toFixed(1) }}% • 
                    {{ formatDate(review.created_at) }}
                  </span>
                </v-list-item-subtitle>

                <template v-slot:append>
                  <v-menu>
                    <template v-slot:activator="{ props }">
                      <v-btn icon v-bind="props" variant="text" size="small">
                        <v-icon>mdi-dots-vertical</v-icon>
                      </v-btn>
                    </template>
                    <v-list>
                      <v-list-item @click="viewDetails(review)">
                        <v-list-item-title>View Details</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click="deleteReview(review.id)">
                        <v-list-item-title>Delete</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
        
        <!-- Pagination -->
        <div class="text-center mt-4">
          <v-pagination
            v-model="currentPage"
            :length="totalPages"
            :total-visible="7"
          ></v-pagination>
        </div>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-else-if="loading">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="mt-4">Loading reviews...</p>
      </v-col>
    </v-row>

    <!-- Empty State -->
    <v-row v-else>
      <v-col cols="12" class="text-center">
        <v-icon size="64" color="grey">mdi-comment-remove</v-icon>
        <h3 class="text-h5 mt-4 mb-2">No Reviews Found</h3>
        <p class="text-body-1 mb-4">
          {{ searchText || selectedSentiment !== 'all' ? 'No reviews match your filters.' : 'Start by uploading some reviews to analyze.' }}
        </p>
        <v-btn color="primary" :to="'/upload'">
          <v-icon left>mdi-upload</v-icon>
          Upload Reviews
        </v-btn>
      </v-col>
    </v-row>

    <!-- Review Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="600">
      <v-card v-if="selectedReview">
        <v-card-title>
          <v-icon class="mr-2">mdi-comment-text</v-icon>
          Review Details
        </v-card-title>
        <v-card-text>
          <v-list>
            <v-list-item>
              <v-list-item-title>Review Text</v-list-item-title>
              <v-list-item-subtitle class="text-wrap">
                {{ selectedReview.text }}
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Sentiment</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip :color="getSentimentColor(selectedReview.sentiment)">
                  {{ selectedReview.sentiment.toUpperCase() }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Confidence</v-list-item-title>
              <v-list-item-subtitle>
                {{ (selectedReview.confidence * 100).toFixed(1) }}%
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Created</v-list-item-title>
              <v-list-item-subtitle>
                {{ formatDate(selectedReview.created_at) }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="detailsDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { useReviewStore } from '@/store'
import { useToast } from 'vue-toastification'
import { ref, onMounted, computed } from 'vue'

export default {
  name: 'Reviews',
  setup() {
    const reviewStore = useReviewStore()
    const toast = useToast()
    
    const selectedSentiment = ref('all')
    const searchText = ref('')
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const detailsDialog = ref(false)
    const selectedReview = ref(null)
    
    const sentimentOptions = [
      { title: 'All Sentiments', value: 'all' },
      { title: 'Positive', value: 'positive' },
      { title: 'Negative', value: 'negative' },
      { title: 'Neutral', value: 'neutral' }
    ]
    
    const reviews = computed(() => reviewStore.reviews)
    const loading = computed(() => reviewStore.loading)
    
    const filteredReviews = computed(() => {
      let filtered = reviews.value
      
      // Filter by sentiment
      if (selectedSentiment.value !== 'all') {
        filtered = filtered.filter(review => review.sentiment === selectedSentiment.value)
      }
      
      // Filter by search text
      if (searchText.value) {
        const searchLower = searchText.value.toLowerCase()
        filtered = filtered.filter(review => 
          review.text.toLowerCase().includes(searchLower)
        )
      }
      
      return filtered
    })
    
    const totalPages = computed(() => {
      return Math.ceil(filteredReviews.value.length / itemsPerPage.value)
    })
    
    const paginatedReviews = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredReviews.value.slice(start, end)
    })
    
    const refreshReviews = async () => {
      await reviewStore.fetchReviews()
    }
    
    const filterReviews = () => {
      currentPage.value = 1
    }
    
    const viewDetails = (review) => {
      selectedReview.value = review
      detailsDialog.value = true
    }
    
    const deleteReview = async (reviewId) => {
      if (!confirm('Are you sure you want to delete this review?')) return
      
      try {
        await reviewStore.deleteReview(reviewId)
        toast.success('Review deleted successfully!')
      } catch (error) {
        toast.error('Failed to delete review: ' + error.message)
      }
    }
    
    const getSentimentColor = (sentiment) => {
      const colors = {
        positive: 'success',
        negative: 'error',
        neutral: 'warning'
      }
      return colors[sentiment] || 'grey'
    }
    
    const getSentimentIcon = (sentiment) => {
      const icons = {
        positive: 'mdi-emoticon-happy',
        negative: 'mdi-emoticon-sad',
        neutral: 'mdi-emoticon-neutral'
      }
      return icons[sentiment] || 'mdi-help'
    }
    
    const formatDate = (dateString) => {
      const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }
      return new Date(dateString).toLocaleDateString('en-US', options)
    }
    
    onMounted(async () => {
      await reviewStore.fetchReviews()
    })

    return {
      selectedSentiment,
      searchText,
      currentPage,
      itemsPerPage,
      detailsDialog,
      selectedReview,
      sentimentOptions,
      reviews,
      loading,
      filteredReviews,
      totalPages,
      paginatedReviews,
      refreshReviews,
      filterReviews,
      viewDetails,
      deleteReview,
      getSentimentColor,
      getSentimentIcon,
      formatDate
    }
  }
}
</script>

<style scoped>
.border-b {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.text-wrap {
  white-space: normal !important;
  word-break: break-word;
}
</style>
