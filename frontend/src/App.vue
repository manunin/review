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

<script>
export default {
  name: 'App',
  data() {
    return {
      menuItems: [
        { 
          label: 'Home', 
          icon: 'pi pi-home',
          command: () => this.$router.push('/')
        },
        { 
          label: 'Upload', 
          icon: 'pi pi-upload',
          command: () => this.$router.push('/upload')
        },

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
