import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Upload from '@/views/Upload.vue'
import Reviews from '@/views/Reviews.vue'
import Analytics from '@/views/Analytics.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/upload',
    name: 'Upload',
    component: Upload
  },
  {
    path: '/reviews',
    name: 'Reviews',
    component: Reviews
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: Analytics
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
