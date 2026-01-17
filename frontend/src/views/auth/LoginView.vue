<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { useAuthStore } from '@/stores'
import { Button, Input } from '@/components/ui'
import { EnvelopeIcon, LockClosedIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLoading = ref(false)
const showPassword = ref(false)

const loginSchema = toTypedSchema(
  z.object({
    email: z.string().email('Please enter a valid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
  })
)

const { handleSubmit, errors, defineField, meta } = useForm({
  validationSchema: loginSchema,
})

const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')

const onSubmit = handleSubmit(async (values) => {
  isLoading.value = true

  try {
    const success = await authStore.login({
      email: values.email,
      password: values.password,
    })

    if (success) {
      // Redirect to intended page or default based on role
      const redirect = route.query.redirect as string
      if (redirect) {
        router.push(redirect)
      } else {
        router.push(authStore.isProvider ? '/' : '/admin')
      }
    }
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="w-full">
    <div class="text-center mb-8">
      <h2 class="text-2xl font-bold text-gray-900">Welcome back</h2>
      <p class="mt-2 text-sm text-gray-600">
        Sign in to your account to continue
      </p>
    </div>

    <!-- Error message -->
    <div
      v-if="authStore.error"
      class="mb-4 p-4 bg-danger-50 border border-danger-200 rounded-md"
    >
      <p class="text-sm text-danger-700">{{ authStore.error }}</p>
    </div>

    <form @submit="onSubmit" class="space-y-6">
      <!-- Email field -->
      <div>
        <label for="email" class="form-label">Email address</label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <EnvelopeIcon class="h-5 w-5 text-gray-400" />
          </div>
          <input
            id="email"
            v-model="email"
            type="email"
            autocomplete="email"
            :class="[
              'form-input pl-10',
              errors.email && 'border-danger-300 focus:border-danger-500 focus:ring-danger-500',
            ]"
            placeholder="you@example.com"
            v-bind="emailAttrs"
          />
        </div>
        <p v-if="errors.email" class="form-error">{{ errors.email }}</p>
      </div>

      <!-- Password field -->
      <div>
        <label for="password" class="form-label">Password</label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <LockClosedIcon class="h-5 w-5 text-gray-400" />
          </div>
          <input
            id="password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            :class="[
              'form-input pl-10 pr-10',
              errors.password && 'border-danger-300 focus:border-danger-500 focus:ring-danger-500',
            ]"
            placeholder="Enter your password"
            v-bind="passwordAttrs"
          />
          <button
            type="button"
            class="absolute inset-y-0 right-0 pr-3 flex items-center"
            @click="showPassword = !showPassword"
          >
            <svg
              v-if="showPassword"
              class="h-5 w-5 text-gray-400 hover:text-gray-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
              />
            </svg>
            <svg
              v-else
              class="h-5 w-5 text-gray-400 hover:text-gray-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
          </button>
        </div>
        <p v-if="errors.password" class="form-error">{{ errors.password }}</p>
      </div>

      <!-- Remember me & Forgot password -->
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <input
            id="remember-me"
            name="remember-me"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label for="remember-me" class="ml-2 block text-sm text-gray-700">
            Remember me
          </label>
        </div>

        <RouterLink
          to="/auth/forgot-password"
          class="text-sm font-medium text-primary-600 hover:text-primary-500"
        >
          Forgot your password?
        </RouterLink>
      </div>

      <!-- Submit button -->
      <Button
        type="submit"
        variant="primary"
        size="lg"
        class="w-full"
        :loading="isLoading"
        :disabled="!meta.valid"
      >
        Sign in
      </Button>
    </form>

    <!-- Demo credentials -->
    <div class="mt-6 p-4 bg-gray-50 rounded-md">
      <p class="text-xs text-gray-500 text-center mb-2">Demo Credentials</p>
      <div class="text-xs text-gray-600 space-y-1">
        <p><strong>Provider:</strong> provider@demo.com / password123</p>
        <p><strong>Admin:</strong> admin@demo.com / password123</p>
      </div>
    </div>
  </div>
</template>
