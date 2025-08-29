<template>
  <div id="app" style="max-width: 66vw; margin: 0 auto;">
    <Menubar :model="menuItems" class="mb-3 flex justify-content-between align-items-center">
      <template #start>
        <span class="font-bold pl-2">VIEWMA</span>
      </template>
    </Menubar>
    <div>
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

interface MenuItem {
  label: string
  icon: string
  command: () => void
}

const router = useRouter()

const menuItems = ref<MenuItem[]>([
  { 
    label: 'Home', 
    icon: 'pi pi-home',
    command: () => router.push('/')
  },
  { 
    label: 'Upload', 
    icon: 'pi pi-upload',
    command: () => router.push('/upload')
  }
])
</script>

<style>
#app {
  font-family: 'Roboto', sans-serif;
}
</style>
