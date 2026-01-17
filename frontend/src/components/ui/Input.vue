<script setup lang="ts">
import { computed, useAttrs } from 'vue'
import { ExclamationCircleIcon } from '@heroicons/vue/20/solid'

interface Props {
  modelValue?: string | number
  label?: string
  error?: string
  hint?: string
  required?: boolean
  disabled?: boolean
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  required: false,
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
}>()

const attrs = useAttrs()

const inputId = computed(() => props.id || `input-${Math.random().toString(36).substr(2, 9)}`)

const inputClasses = computed(() => [
  'block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 sm:text-sm',
  'focus:outline-none focus:ring-1',
  props.error
    ? 'border-danger-300 text-danger-900 placeholder-danger-300 focus:ring-danger-500 focus:border-danger-500'
    : 'border-gray-300 focus:ring-primary-500 focus:border-primary-500',
  props.disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white',
])

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div>
    <!-- Label -->
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium text-gray-700 mb-1"
    >
      {{ label }}
      <span v-if="required" class="text-danger-500">*</span>
    </label>

    <!-- Input wrapper -->
    <div class="relative">
      <input
        :id="inputId"
        :value="modelValue"
        :class="inputClasses"
        :disabled="disabled"
        :required="required"
        v-bind="attrs"
        @input="handleInput"
        @blur="emit('blur', $event)"
        @focus="emit('focus', $event)"
      />

      <!-- Error icon -->
      <div
        v-if="error"
        class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none"
      >
        <ExclamationCircleIcon class="h-5 w-5 text-danger-500" />
      </div>
    </div>

    <!-- Error message -->
    <p v-if="error" class="mt-1 text-sm text-danger-600">
      {{ error }}
    </p>

    <!-- Hint text -->
    <p v-else-if="hint" class="mt-1 text-sm text-gray-500">
      {{ hint }}
    </p>
  </div>
</template>
