<script setup lang="ts">
import { computed } from 'vue'
import { ExclamationCircleIcon, ChevronDownIcon } from '@heroicons/vue/20/solid'

interface Option {
  value: string | number
  label: string
  disabled?: boolean
}

interface Props {
  modelValue?: string | number
  options: Option[]
  label?: string
  placeholder?: string
  error?: string
  hint?: string
  required?: boolean
  disabled?: boolean
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: 'Select an option',
  required: false,
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  change: [value: string | number]
}>()

const inputId = computed(() => props.id || `select-${Math.random().toString(36).substr(2, 9)}`)

const selectClasses = computed(() => [
  'block w-full px-3 py-2 pr-10 border rounded-md shadow-sm sm:text-sm appearance-none',
  'focus:outline-none focus:ring-1',
  props.error
    ? 'border-danger-300 text-danger-900 focus:ring-danger-500 focus:border-danger-500'
    : 'border-gray-300 focus:ring-primary-500 focus:border-primary-500',
  props.disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white cursor-pointer',
])

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('update:modelValue', target.value)
  emit('change', target.value)
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

    <!-- Select wrapper -->
    <div class="relative">
      <select
        :id="inputId"
        :value="modelValue"
        :class="selectClasses"
        :disabled="disabled"
        :required="required"
        @change="handleChange"
      >
        <option value="" disabled>
          {{ placeholder }}
        </option>
        <option
          v-for="option in options"
          :key="option.value"
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </option>
      </select>

      <!-- Dropdown icon -->
      <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
        <ChevronDownIcon
          v-if="!error"
          class="h-5 w-5 text-gray-400"
        />
        <ExclamationCircleIcon
          v-else
          class="h-5 w-5 text-danger-500"
        />
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
