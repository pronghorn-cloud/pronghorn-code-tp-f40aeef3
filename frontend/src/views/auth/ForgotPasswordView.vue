<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { authService } from '@/services/api'
import { Button } from '@/components/ui'
import { EnvelopeIcon, ArrowLeftIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'

const isLoading = ref(false)
const isSubmitted = ref(false)
const error = ref('')

const schema = toTypedSchema(
  z.object({
    email: z.string().email('Please enter a valid email address'),
  })
)

const { handleSubmit, errors, defineField, meta } = useForm({
  validationSchema: schema,
})

const [email, emailAttrs] = defineField('email')

const onSubmit = handleSubmit(async (values) => {
  isLoading.value = true
  error.value = ''

  try {
    await authService.forgotPassword(values.email)
    isSubmitted.value = true
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Failed to send reset email. Please try again.'
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="w-full">
    <!-- Back link -->
    <RouterLink
      to="/auth/login"
      class="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-6"
    >
      <ArrowLeftIcon class="h-4 w-4 mr-1" />
      Back to login
    </RouterLink>

    <!-- Success state -->
    <div v-if="isSubmitted" class="text-center">
      <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-success-100">
        <CheckCircleIcon class="h-6 w-6 text-success-600" />
      </div>
      <h2 class="mt-4 text-2xl font-bold text-gray-900">Check your email</h2>
      <p class="mt-2 text-sm text-gray-600">
        We've sent a password reset link to <strong>{{ email }}</strong>
      </p>
      <p class="mt-4 text-sm text-gray-500">
        Didn't receive the email? Check your spam folder or
        <button
          type="button"
          class="text-primary-600 hover:text-primary-500 font-medium"
          @click="isSubmitted = false"
        >
          try again
        </button>
      </p>
    </div>

    <!-- Form state -->
    <template v-else>
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-gray-900">Forgot your password?</h2>
        <p class="mt-2 text-sm text-gray-600">
          No worries, we'll send you reset instructions.
        </p>
      </div>

      <!-- Error message -->
      <div
        v-if="error"
        class="mb-4 p-4 bg-danger-50 border border-danger-200 rounded-md"
      >
        <p class="text-sm text-danger-700">{{ error }}</p>
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
              placeholder="Enter your email"
              v-bind="emailAttrs"
            />
          </div>
          <p v-if="errors.email" class="form-error">{{ errors.email }}</p>
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
          Reset password
        </Button>
      </form>
    </template>
  </div>
</template>
