<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/20/solid'

interface Props {
  page: number
  totalPages: number
  total: number
  limit: number
  showInfo?: boolean
  showLimitSelector?: boolean
  limitOptions?: number[]
}

const props = withDefaults(defineProps<Props>(), {
  showInfo: true,
  showLimitSelector: true,
  limitOptions: () => [10, 20, 50, 100],
})

const emit = defineEmits<{
  'update:page': [page: number]
  'update:limit': [limit: number]
}>()

const hasNext = computed(() => props.page < props.totalPages)
const hasPrevious = computed(() => props.page > 1)

const startItem = computed(() => {
  if (props.total === 0) return 0
  return (props.page - 1) * props.limit + 1
})

const endItem = computed(() => {
  return Math.min(props.page * props.limit, props.total)
})

const pageNumbers = computed(() => {
  const pages: (number | 'ellipsis')[] = []
  const maxVisible = 7

  if (props.totalPages <= maxVisible) {
    for (let i = 1; i <= props.totalPages; i++) {
      pages.push(i)
    }
  } else {
    const current = props.page
    const showFirst = current > 3
    const showLast = current < props.totalPages - 2

    if (showFirst) {
      pages.push(1)
      if (current > 4) pages.push('ellipsis')
    }

    const start = Math.max(showFirst ? current - 1 : 1, 1)
    const end = Math.min(showLast ? current + 1 : props.totalPages, props.totalPages)

    for (let i = start; i <= end; i++) {
      if (!pages.includes(i)) pages.push(i)
    }

    if (showLast) {
      if (current < props.totalPages - 3) pages.push('ellipsis')
      pages.push(props.totalPages)
    }
  }

  return pages
})

const goToPage = (page: number) => {
  if (page >= 1 && page <= props.totalPages) {
    emit('update:page', page)
  }
}

const changeLimit = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('update:limit', parseInt(target.value))
}
</script>

<template>
  <div class="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6">
    <!-- Mobile pagination -->
    <div class="flex flex-1 justify-between sm:hidden">
      <button
        type="button"
        :disabled="!hasPrevious"
        class="btn-secondary"
        @click="goToPage(page - 1)"
      >
        Previous
      </button>
      <button
        type="button"
        :disabled="!hasNext"
        class="btn-secondary"
        @click="goToPage(page + 1)"
      >
        Next
      </button>
    </div>

    <!-- Desktop pagination -->
    <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
      <div class="flex items-center gap-4">
        <!-- Info text -->
        <p v-if="showInfo" class="text-sm text-gray-700">
          Showing
          <span class="font-medium">{{ startItem }}</span>
          to
          <span class="font-medium">{{ endItem }}</span>
          of
          <span class="font-medium">{{ total }}</span>
          results
        </p>

        <!-- Limit selector -->
        <div v-if="showLimitSelector" class="flex items-center gap-2">
          <label for="limit" class="text-sm text-gray-700">Show</label>
          <select
            id="limit"
            :value="limit"
            class="form-select py-1 text-sm rounded-md border-gray-300"
            @change="changeLimit"
          >
            <option v-for="opt in limitOptions" :key="opt" :value="opt">
              {{ opt }}
            </option>
          </select>
        </div>
      </div>

      <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
        <!-- Previous button -->
        <button
          type="button"
          :disabled="!hasPrevious"
          class="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
          @click="goToPage(page - 1)"
        >
          <span class="sr-only">Previous</span>
          <ChevronLeftIcon class="h-5 w-5" />
        </button>

        <!-- Page numbers -->
        <template v-for="(pageNum, index) in pageNumbers" :key="index">
          <span
            v-if="pageNum === 'ellipsis'"
            class="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-700 ring-1 ring-inset ring-gray-300"
          >
            ...
          </span>
          <button
            v-else
            type="button"
            :class="[
              'relative inline-flex items-center px-4 py-2 text-sm font-semibold ring-1 ring-inset focus:z-20 focus:outline-offset-0',
              pageNum === page
                ? 'z-10 bg-primary-600 text-white ring-primary-600'
                : 'text-gray-900 ring-gray-300 hover:bg-gray-50',
            ]"
            @click="goToPage(pageNum)"
          >
            {{ pageNum }}
          </button>
        </template>

        <!-- Next button -->
        <button
          type="button"
          :disabled="!hasNext"
          class="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
          @click="goToPage(page + 1)"
        >
          <span class="sr-only">Next</span>
          <ChevronRightIcon class="h-5 w-5" />
        </button>
      </nav>
    </div>
  </div>
</template>
