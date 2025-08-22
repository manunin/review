import { defineStore } from 'pinia'
import axios from 'axios'

// API client
const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const useReviewStore = defineStore('reviews', {
  state: () => ({
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
    getAllReviews: (state) => state.reviews,
    getAnalytics: (state) => state.analytics,
    isLoading: (state) => state.loading,
    getError: (state) => state.error,
    
    getReviewsBysentiment: (state) => (sentiment) => {
      if (sentiment === 'all') return state.reviews
      return state.reviews.filter(review => review.sentiment === sentiment)
    },
    
    getTotalReviews: (state) => state.reviews.length,
    
    getPositivePercentage: (state) => {
      if (state.reviews.length === 0) return 0
      const positive = state.reviews.filter(r => r.sentiment === 'positive').length
      return Math.round((positive / state.reviews.length) * 100)
    },
    
    getNegativePercentage: (state) => {
      if (state.reviews.length === 0) return 0
      const negative = state.reviews.filter(r => r.sentiment === 'negative').length
      return Math.round((negative / state.reviews.length) * 100)
    },
    
    getNeutralPercentage: (state) => {
      if (state.reviews.length === 0) return 0
      const neutral = state.reviews.filter(r => r.sentiment === 'neutral').length
      return Math.round((neutral / state.reviews.length) * 100)
    }
  },

  actions: {
    setLoading(loading) {
      this.loading = loading
    },

    setError(error) {
      this.error = error
    },

    clearError() {
      this.error = null
    },

    setReviews(reviews) {
      this.reviews = reviews
    },

    addReview(review) {
      this.reviews.unshift(review)
    },

    removeReview(reviewId) {
      const index = this.reviews.findIndex(r => r.id === reviewId)
      if (index !== -1) {
        this.reviews.splice(index, 1)
      }
    },

    setAnalytics(analytics) {
      this.analytics = analytics
    },

    async fetchReviews() {
      this.setLoading(true)
      this.clearError()
      
      try {
        const response = await api.get('/reviews/')
        this.setReviews(response.data)
      } catch (error) {
        console.error('Failed to fetch reviews:', error)
        this.setError(error.response?.data?.detail || error.message || 'Failed to fetch reviews')
      } finally {
        this.setLoading(false)
      }
    },

    async fetchAnalytics() {
      this.setLoading(true)
      this.clearError()
      
      try {
        const response = await api.get('/analytics/summary')
        this.setAnalytics(response.data.statistics)
      } catch (error) {
        console.error('Failed to fetch analytics:', error)
        this.setError(error.response?.data?.detail || error.message || 'Failed to fetch analytics')
      } finally {
        this.setLoading(false)
      }
    },

    async analyzeText(text) {
      this.setLoading(true)
      this.clearError()
      
      try {
        const response = await api.post('/reviews/analyze', { text })
        const review = response.data
        this.addReview(review)
        return review
      } catch (error) {
        console.error('Failed to analyze text:', error)
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to analyze text'
        this.setError(errorMessage)
        throw new Error(errorMessage)
      } finally {
        this.setLoading(false)
      }
    },

    async uploadFile(file) {
      this.setLoading(true)
      this.clearError()
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await api.post('/upload/file', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        // Refresh reviews after upload
        await this.fetchReviews()
        
        return response.data
      } catch (error) {
        console.error('Failed to upload file:', error)
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to upload file'
        this.setError(errorMessage)
        throw new Error(errorMessage)
      } finally {
        this.setLoading(false)
      }
    },

    async deleteReview(reviewId) {
      this.setLoading(true)
      this.clearError()
      
      try {
        await api.delete(`/reviews/${reviewId}`)
        this.removeReview(reviewId)
        return true
      } catch (error) {
        console.error('Failed to delete review:', error)
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete review'
        this.setError(errorMessage)
        throw new Error(errorMessage)
      } finally {
        this.setLoading(false)
      }
    },

    async getReview(reviewId) {
      this.setLoading(true)
      this.clearError()
      
      try {
        const response = await api.get(`/reviews/${reviewId}`)
        return response.data
      } catch (error) {
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
