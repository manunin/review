<template>
  <div>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h3 mb-6">Upload Reviews</h1>
        <p class="text-h6 mb-6">
          Upload your review files (CSV, TXT, JSON) or analyze individual reviews
        </p>
      </v-col>
    </v-row>

    <!-- Single Review Analysis -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-6">
          <v-card-title>
            <v-icon class="mr-2">mdi-text-box</v-icon>
            Analyze Single Review
          </v-card-title>
          <v-card-text>
            <v-textarea
              v-model="singleReviewText"
              label="Enter review text"
              placeholder="Type or paste a review here..."
              rows="4"
              variant="outlined"
              :disabled="analyzing"
            ></v-textarea>
            <v-btn
              color="primary"
              :loading="analyzing"
              :disabled="!singleReviewText.trim()"
              @click="analyzeSingleReview"
              class="mt-2"
            >
              <v-icon left>mdi-brain</v-icon>
              Analyze Sentiment
            </v-btn>
            
            <!-- Single Review Result -->
            <v-card 
              v-if="singleReviewResult" 
              class="mt-4" 
              :color="getSentimentColor(singleReviewResult.sentiment)"
              variant="tonal"
            >
              <v-card-text>
                <v-row align="center">
                  <v-col cols="auto">
                    <v-icon size="32">{{ getSentimentIcon(singleReviewResult.sentiment) }}</v-icon>
                  </v-col>
                  <v-col>
                    <div class="text-h6">{{ singleReviewResult.sentiment.toUpperCase() }}</div>
                    <div class="text-body-2">
                      Confidence: {{ (singleReviewResult.confidence * 100).toFixed(1) }}%
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- File Upload -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-upload</v-icon>
            Batch Upload
          </v-card-title>
          <v-card-text>
            <div class="text-center">
              <v-file-input
                v-model="selectedFile"
                label="Choose file"
                accept=".csv,.txt,.json"
                variant="outlined"
                prepend-icon="mdi-paperclip"
                :disabled="uploading"
                @change="onFileSelect"
              ></v-file-input>
              
              <div class="mt-4">
                <v-btn
                  color="primary"
                  :loading="uploading"
                  :disabled="!selectedFile"
                  @click="uploadFile"
                  size="large"
                >
                  <v-icon left>mdi-cloud-upload</v-icon>
                  Upload and Analyze
                </v-btn>
              </div>
              
              <div class="mt-4 text-body-2 text-medium-emphasis">
                Supported formats: CSV, TXT, JSON (Max size: 50MB)
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Upload Results -->
    <v-row v-if="uploadResult">
      <v-col cols="12">
        <v-card class="mt-6">
          <v-card-title>
            <v-icon class="mr-2" color="success">mdi-check-circle</v-icon>
            Upload Results
          </v-card-title>
          <v-card-text>
            <v-alert type="success" class="mb-4">
              {{ uploadResult.message }}
            </v-alert>
            
            <v-row>
              <v-col cols="12" sm="6">
                <v-list>
                  <v-list-item>
                    <v-list-item-title>Filename</v-list-item-title>
                    <v-list-item-subtitle>{{ uploadResult.filename }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>Total Reviews</v-list-item-title>
                    <v-list-item-subtitle>{{ uploadResult.total_reviews }}</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
              <v-col cols="12" sm="6">
                <v-btn 
                  color="primary" 
                  :to="'/reviews'" 
                  variant="outlined"
                  class="mr-2"
                >
                  <v-icon left>mdi-eye</v-icon>
                  View Reviews
                </v-btn>
                <v-btn 
                  color="secondary" 
                  :to="'/analytics'"
                  variant="outlined"
                >
                  <v-icon left>mdi-chart-line</v-icon>
                  View Analytics
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { useReviewStore } from '@/store'
import { useToast } from 'vue-toastification'
import { ref } from 'vue'

export default {
  name: 'Upload',
  setup() {
    const reviewStore = useReviewStore()
    const toast = useToast()
    
    const singleReviewText = ref('')
    const singleReviewResult = ref(null)
    const analyzing = ref(false)
    const selectedFile = ref(null)
    const uploading = ref(false)
    const uploadResult = ref(null)
    
    const analyzeSingleReview = async () => {
      if (!singleReviewText.value.trim()) return
      
      analyzing.value = true
      singleReviewResult.value = null
      
      try {
        const result = await reviewStore.analyzeText(singleReviewText.value)
        singleReviewResult.value = result
        toast.success('Review analyzed successfully!')
      } catch (error) {
        toast.error('Failed to analyze review: ' + error.message)
      } finally {
        analyzing.value = false
      }
    }
    
    const onFileSelect = () => {
      uploadResult.value = null
    }
    
    const uploadFile = async () => {
      if (!selectedFile.value) return
      
      uploading.value = true
      uploadResult.value = null
      
      try {
        const result = await reviewStore.uploadFile(selectedFile.value)
        uploadResult.value = result
        toast.success('File uploaded and analyzed successfully!')
        
        // Clear the file input
        selectedFile.value = null
        
      } catch (error) {
        toast.error('Upload failed: ' + error.message)
      } finally {
        uploading.value = false
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

    return {
      singleReviewText,
      singleReviewResult,
      analyzing,
      selectedFile,
      uploading,
      uploadResult,
      analyzeSingleReview,
      onFileSelect,
      uploadFile,
      getSentimentColor,
      getSentimentIcon
    }
  }
}
</script>

<style scoped>
.v-file-input {
  max-width: 400px;
  margin: 0 auto;
}
</style>
