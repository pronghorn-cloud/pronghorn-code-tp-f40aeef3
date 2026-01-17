<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { Button } from '@/components/ui'
import { ShieldExclamationIcon, HomeIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'

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
      <div class="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-red-100">
        <ShieldExclamationIcon class="h-12 w-12 text-red-600" />
      </div>

      <!-- Error Code -->
      <h1 class="mt-6 text-6xl font-extrabold text-gray-900">403</h1>

      <!-- Title -->
      <h2 class="mt-2 text-2xl font-bold text-gray-900">Access Denied</h2>

      <!-- Description -->
      <p class="mt-4 text-gray-600">
        Sorry, you don't have permission to access this page. This area may be restricted to certain user roles.
      </p>

      <!-- Help Text -->
      <p class="mt-2 text-sm text-gray-500">
        If you believe this is an error, please contact your administrator or try logging in with different credentials.
      </p>

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

      <!-- Additional Links -->
      <div class="mt-8 pt-6 border-t border-gray-200">
        <p class="text-sm text-gray-500">
          Need help?
          <a href="mailto:support@hlink.ca" class="font-medium text-blue-600 hover:text-blue-500">
            Contact Support
          </a>
        </p>
      </div>
    </div>
  </div>
</template>
