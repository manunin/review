<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-app-bar-title>
        <v-icon class="mr-2">mdi-magnify</v-icon>
        Smart Review Analyzer
      </v-app-bar-title>
      
      <v-spacer></v-spacer>
      
      <v-btn
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        :class="{ 'v-btn--active': $route.path === item.path }"
        text
        class="mr-2"
      >
        <v-icon left>{{ item.icon }}</v-icon>
        {{ item.label }}
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      navItems: [
        { label: 'Home', path: '/', icon: 'mdi-home' },
        { label: 'Upload', path: '/upload', icon: 'mdi-upload' },
        { label: 'Reviews', path: '/reviews', icon: 'mdi-comment-text-multiple' },
        { label: 'Analytics', path: '/analytics', icon: 'mdi-chart-line' },
      ]
    }
  }
}
</script>

<style>
#app {
  font-family: 'Roboto', sans-serif;
}
</style>
