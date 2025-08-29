import { defineStore } from 'pinia'
import axios, { type AxiosResponse } from 'axios'
import type { 
  ReviewStoreState, 
  Review, 
  Analytics, 
  ReviewAnalysis, 
  UploadResult
} from '@/types'

// API client
const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const useReviewStore = defineStore('reviews', {
  state: (): ReviewStoreState => ({
    reviews: [],
    analytics: {
      total_reviews: 0,
      positive: 0,
      negative: 0,
      neutral: 0,
      positive_percentage: 0,
      negative_percentage: 0,
      neutral_percentage: 0
    },
    loading: false,
    error: null
  }),

  getters: {
    getAllReviews: (state): Review[] => state.reviews,
    getAnalytics: (state): Analytics => state.analytics,
    isLoading: (state): boolean => state.loading,
    getError: (state): string | null => state.error,
    
    getReviewsBysentiment: (state) => (sentiment: string): Review[] => {
      if (sentiment === 'all') return state.reviews
      return state.reviews.filter(review => review.sentiment === sentiment)
    },
    
    getTotalReviews: (state): number => state.reviews.length,
    
    getPositivePercentage: (state): number => {
      if (state.reviews.length === 0) return 0
      const positive = state.reviews.filter(r => r.sentiment === 'positive').length
      return Math.round((positive / state.reviews.length) * 100)
    },
    
    getNegativePercentage: (state): number => {
      if (state.reviews.length === 0) return 0
      const negative = state.reviews.filter(r => r.sentiment === 'negative').length
      return Math.round((negative / state.reviews.length) * 100)
    },
    
    getNeutralPercentage: (state): number => {
      if (state.reviews.length === 0) return 0
      const neutral = state.reviews.filter(r => r.sentiment === 'neutral').length
      return Math.round((neutral / state.reviews.length) * 100)
    }
  },

  actions: {
    setLoading(loading: boolean): void {
      this.loading = loading
    },

    setError(error: string | null): void {
      this.error = error
    },

    clearError(): void {
      this.error = null
    },

    setReviews(reviews: Review[]): void {
      this.reviews = reviews
    },

    addReview(review: Review): void {
      this.reviews.unshift(review)
    },

    removeReview(reviewId: string): void {
      const index = this.reviews.findIndex(r => r.id === reviewId)
      if (index !== -1) {
        this.reviews.splice(index, 1)
      }
    },

    setAnalytics(analytics: Analytics): void {
      this.analytics = analytics
    },

    async fetchReviews(): Promise<void> {
      this.setLoading(true)
      this.clearError()
      
      try {
        const response: AxiosResponse<Review[]> = await api.get('/reviews/')
        this.setReviews(response.data)
      } catch (error: any) {
        console.error('Failed to fetch reviews:', error)
        this.setError(error.response?.data?.detail || error.message || 'Failed to fetch reviews')
      } finally {
        this.setLoading(false)
      }
    },

    async fetchAnalytics(): Promise<void> {
      this.setLoading(true)
      this.clearError()
      
      try {
        const response: AxiosResponse<Analytics> = await api.get('/analytics/summary')
        this.setAnalytics(response.data)
      } catch (error: any) {
        console.error('Failed to fetch analytics:', error)
        this.setError(error.response?.data?.detail || error.message || 'Failed to fetch analytics')
      } finally {
        this.setLoading(false)
      }
    },

    async analyzeText(text: string): Promise<ReviewAnalysis> {
      this.setLoading(true)
      this.clearError()
      
      try {
        const response: AxiosResponse<ReviewAnalysis> = await api.post('/reviews/analyze', { text })
        const review = response.data
        return review
      } catch (error: any) {
        console.error('Failed to analyze text:', error)
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to analyze text'
        this.setError(errorMessage)
        throw new Error(errorMessage)
      } finally {
        this.setLoading(false)
      }
    },

    async uploadFile(file: File): Promise<UploadResult> {
      this.setLoading(true)
      this.clearError()
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response: AxiosResponse<UploadResult> = await api.post('/upload/file', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        // Refresh reviews after upload
        await this.fetchReviews()
        
        return response.data
      } catch (error: any) {
        console.error('Failed to upload file:', error)
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to upload file'
        this.setError(errorMessage)
        throw new Error(errorMessage)
      } finally {
        this.setLoading(false)
      }
    },

    async deleteReview(reviewId: string): Promise<boolean> {
      this.setLoading(true)
      this.clearError()
      
      try {
        await api.delete(`/reviews/${reviewId}`)
        this.removeReview(reviewId)
        return true
      } catch (error: any) {
        console.error('Failed to delete review:', error)
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete review'
        this.setError(errorMessage)
        throw new Error(errorMessage)
      } finally {
        this.setLoading(false)
      }
    },

    async getReview(reviewId: string): Promise<Review> {
      this.setLoading(true)
      this.clearError()
      
      try {
        const response: AxiosResponse<Review> = await api.get(`/reviews/${reviewId}`)
        return response.data
      } catch (error: any) {
        console.error('Failed to get review:', error)
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to get review'
        this.setError(errorMessage)
        throw new Error(errorMessage)
      } finally {
        this.setLoading(false)
      }
    }
  }
})
