<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { Button } from '@/components/ui'
import { MagnifyingGlassIcon, HomeIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()

const homeRoute = computed(() => {
  if (!authStore.isAuthenticated) return '/auth/login'
  return authStore.user?.role === 'provider' ? '/' : '/admin'
})

const goBack = () => {
  if (window.history.length > 2) {
    router.back()
  } else {
    router.push(homeRoute.value)
  }
}

const goHome = () => {
  router.push(homeRoute.value)
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full text-center">
      <!-- Icon -->
      <div class="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-blue-100">
        <MagnifyingGlassIcon class="h-12 w-12 text-blue-600" />
      </div>

      <!-- Error Code -->
      <h1 class="mt-6 text-6xl font-extrabold text-gray-900">404</h1>

      <!-- Title -->
      <h2 class="mt-2 text-2xl font-bold text-gray-900">Page Not Found</h2>

      <!-- Description -->
      <p class="mt-4 text-gray-600">
        Sorry, we couldn't find the page you're looking for. The page may have been moved, deleted, or never existed.
      </p>

      <!-- Suggestions -->
      <div class="mt-6 bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm font-medium text-gray-900 mb-2">Here are some helpful links:</p>
        <ul class="text-sm text-gray-600 space-y-1">
          <li>
            <RouterLink to="/" class="text-blue-600 hover:text-blue-500">Provider Dashboard</RouterLink>
          </li>
          <li>
            <RouterLink to="/claims" class="text-blue-600 hover:text-blue-500">My Claims</RouterLink>
          </li>
          <li>
            <RouterLink to="/admin" class="text-blue-600 hover:text-blue-500">Admin Dashboard</RouterLink>
          </li>
        </ul>
      </div>

      <!-- Actions -->
      <div class="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
        <Button
          variant="outline"
          @click="goBack"
          class="w-full sm:w-auto"
        >
          <ArrowLeftIcon class="w-4 h-4 mr-2" />
          Go Back
        </Button>
        <Button
          variant="primary"
          @click="goHome"
          class="w-full sm:w-auto"
        >
          <HomeIcon class="w-4 h-4 mr-2" />
          Go to Dashboard
        </Button>
      </div>

      <!-- Report Issue -->
      <div class="mt-8 pt-6 border-t border-gray-200">
        <p class="text-sm text-gray-500">
          Think this is a mistake?
          <a href="mailto:support@hlink.ca" class="font-medium text-blue-600 hover:text-blue-500">
            Report this issue
          </a>
        </p>
      </div>
    </div>
  </div>
</template>
