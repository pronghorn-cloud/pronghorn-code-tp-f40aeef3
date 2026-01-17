<script setup lang="ts">
import { computed } from 'vue'
import type { ClaimStatus } from '@/types'

type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info' | ClaimStatus

interface Props {
  variant?: BadgeVariant
  size?: 'sm' | 'md' | 'lg'
  dot?: boolean
  removable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  dot: false,
  removable: false,
})

const emit = defineEmits<{
  remove: []
}>()

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'bg-primary-100 text-primary-800'
    case 'success':
    case 'approved':
    case 'paid':
      return 'bg-green-100 text-green-800'
    case 'warning':
    case 'in_review':
      return 'bg-yellow-100 text-yellow-800'
    case 'danger':
    case 'denied':
      return 'bg-red-100 text-red-800'
    case 'info':
    case 'submitted':
      return 'bg-blue-100 text-blue-800'
    case 'draft':
      return 'bg-gray-100 text-gray-800'
    case 'adjudicated':
      return 'bg-purple-100 text-purple-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
})

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'px-2 py-0.5 text-xs'
    case 'md':
      return 'px-2.5 py-0.5 text-xs'
    case 'lg':
      return 'px-3 py-1 text-sm'
    default:
      return 'px-2.5 py-0.5 text-xs'
  }
})

const dotColor = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'bg-primary-500'
    case 'success':
    case 'approved':
    case 'paid':
      return 'bg-green-500'
    case 'warning':
    case 'in_review':
      return 'bg-yellow-500'
    case 'danger':
    case 'denied':
      return 'bg-red-500'
    case 'info':
    case 'submitted':
      return 'bg-blue-500'
    case 'draft':
      return 'bg-gray-500'
    case 'adjudicated':
      return 'bg-purple-500'
    default:
      return 'bg-gray-500'
  }
})

// Helper to format status labels
const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    draft: 'Draft',
    submitted: 'Submitted',
    in_review: 'In Review',
    adjudicated: 'Adjudicated',
    approved: 'Approved',
    denied: 'Denied',
    paid: 'Paid',
  }
  return labels[status] || status
}
</script>

<template>
  <span
    :class="[
      'inline-flex items-center font-medium rounded-full',
      variantClasses,
      sizeClasses,
    ]"
  >
    <!-- Dot indicator -->
    <span
      v-if="dot"
      :class="['w-1.5 h-1.5 rounded-full mr-1.5', dotColor]"
    />

    <slot>{{ getStatusLabel(variant) }}</slot>

    <!-- Remove button -->
    <button
      v-if="removable"
      type="button"
      class="ml-1.5 -mr-1 h-4 w-4 inline-flex items-center justify-center rounded-full hover:bg-black/10 focus:outline-none"
      @click="emit('remove')"
    >
      <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
        <path
          fill-rule="evenodd"
          d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
          clip-rule="evenodd"
        />
      </svg>
    </button>
  </span>
</template>
