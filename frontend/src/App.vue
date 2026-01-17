<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { onMounted } from 'vue'

const authStore = useAuthStore()

onMounted(async () => {
  // Check for existing session on app load
  await authStore.checkAuth()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <RouterView />
  </div>
</template>

<style>
/* App-level styles */
#app {
  min-height: 100vh;
}
</style>
