<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Card, Button, Badge, Table, Input, Modal, Pagination } from '@/components/ui'
import { useUIStore } from '@/stores'
import { useDocumentUpload } from '@/composables'
import {
  DocumentIcon,
  DocumentTextIcon,
  DocumentArrowUpIcon,
  DocumentArrowDownIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  TrashIcon,
  EyeIcon,
  ArrowPathIcon,
  CloudArrowUpIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ClockIcon,
} from '@heroicons/vue/24/outline'

const uiStore = useUIStore()
const { uploadDocument, uploadProgress, isUploading } = useDocumentUpload()

// State
const searchQuery = ref('')
const selectedType = ref('all')
const isLoading = ref(false)
const showUploadModal = ref(false)
const showPreviewModal = ref(false)
const selectedDocument = ref<any>(null)
const currentPage = ref(1)
const itemsPerPage = ref(10)

// Document types
const documentTypes = [
  { value: 'all', label: 'All Types' },
  { value: 'claim', label: 'Claim Documents' },
  { value: 'authorization', label: 'Authorizations' },
  { value: 'supporting', label: 'Supporting Documents' },
  { value: 'correspondence', label: 'Correspondence' },
]

// Mock documents data
const documents = ref([
  {
    id: 'DOC-001',
    name: 'Claim_CLM-2026-001234.pdf',
    type: 'claim',
    size: '245 KB',
    uploadedAt: '2026-01-15T10:30:00',
    claimId: 'CLM-2026-001234',
    status: 'verified',
  },
  {
    id: 'DOC-002',
    name: 'Prior_Authorization_PA-789.pdf',
    type: 'authorization',
    size: '128 KB',
    uploadedAt: '2026-01-14T14:22:00',
    claimId: 'CLM-2026-001232',
    status: 'verified',
  },
  {
    id: 'DOC-003',
    name: 'Lab_Results_Patient_456.pdf',
    type: 'supporting',
    size: '512 KB',
    uploadedAt: '2026-01-14T09:15:00',
    claimId: 'CLM-2026-001230',
    status: 'pending',
  },
  {
    id: 'DOC-004',
    name: 'Appeal_Letter_CLM-2026-001200.pdf',
    type: 'correspondence',
    size: '89 KB',
    uploadedAt: '2026-01-13T16:45:00',
    claimId: 'CLM-2026-001200',
    status: 'verified',
  },
  {
    id: 'DOC-005',
    name: 'Medical_Records_Summary.pdf',
    type: 'supporting',
    size: '1.2 MB',
    uploadedAt: '2026-01-12T11:00:00',
    claimId: 'CLM-2026-001195',
    status: 'processing',
  },
])

// Computed
const filteredDocuments = computed(() => {
  let result = documents.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(
      (doc) =>
        doc.name.toLowerCase().includes(query) ||
        doc.claimId.toLowerCase().includes(query)
    )
  }

  if (selectedType.value !== 'all') {
    result = result.filter((doc) => doc.type === selectedType.value)
  }

  return result
})

const paginatedDocuments = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredDocuments.value.slice(start, end)
})

const totalPages = computed(() =>
  Math.ceil(filteredDocuments.value.length / itemsPerPage.value)
)

// Methods
const getStatusBadge = (status: string) => {
  switch (status) {
    case 'verified':
      return { variant: 'success' as const, icon: CheckCircleIcon, label: 'Verified' }
    case 'pending':
      return { variant: 'warning' as const, icon: ClockIcon, label: 'Pending' }
    case 'processing':
      return { variant: 'info' as const, icon: ArrowPathIcon, label: 'Processing' }
    case 'failed':
      return { variant: 'danger' as const, icon: ExclamationCircleIcon, label: 'Failed' }
    default:
      return { variant: 'secondary' as const, icon: DocumentIcon, label: status }
  }
}

const getTypeLabel = (type: string) => {
  const typeObj = documentTypes.find((t) => t.value === type)
  return typeObj ? typeObj.label : type
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-CA', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const openPreview = (doc: any) => {
  selectedDocument.value = doc
  showPreviewModal.value = true
}

const downloadDocument = (doc: any) => {
  // TODO: Implement actual download
  console.log('Downloading:', doc.name)
}

const deleteDocument = async (doc: any) => {
  if (confirm(`Are you sure you want to delete ${doc.name}?`)) {
    // TODO: Implement actual delete
    documents.value = documents.value.filter((d) => d.id !== doc.id)
  }
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files

  if (files && files.length > 0) {
    try {
      for (const file of files) {
        await uploadDocument(file, 'claim', 'CLM-2026-001247')
      }
      showUploadModal.value = false
      // Refresh documents list
    } catch (error) {
      console.error('Upload failed:', error)
    }
  }
}

onMounted(() => {
  uiStore.setBreadcrumbs([
    { label: 'Dashboard', to: '/provider' },
    { label: 'Documents' },
  ])
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Documents</h1>
        <p class="mt-1 text-sm text-gray-500">
          Manage your uploaded documents and attachments
        </p>
      </div>
      <Button @click="showUploadModal = true">
        <CloudArrowUpIcon class="w-5 h-5 mr-2" />
        Upload Document
      </Button>
    </div>

    <!-- Filters -->
    <Card class="p-4">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
        <div class="flex-1">
          <div class="relative">
            <MagnifyingGlassIcon
              class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
            />
            <Input
              v-model="searchQuery"
              type="text"
              placeholder="Search documents..."
              class="pl-10"
            />
          </div>
        </div>
        <div class="flex items-center gap-3">
          <FunnelIcon class="w-5 h-5 text-gray-400" />
          <select
            v-model="selectedType"
            class="block rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option v-for="type in documentTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>
      </div>
    </Card>

    <!-- Documents Table -->
    <Card>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Document
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Type
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Claim ID
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Size
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Uploaded
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="doc in paginatedDocuments" :key="doc.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <DocumentTextIcon class="w-8 h-8 text-gray-400 mr-3" />
                  <div>
                    <div class="text-sm font-medium text-gray-900">{{ doc.name }}</div>
                    <div class="text-sm text-gray-500">{{ doc.id }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ getTypeLabel(doc.type) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <router-link
                  :to="`/provider/claims/${doc.claimId}`"
                  class="text-sm text-blue-600 hover:text-blue-500"
                >
                  {{ doc.claimId }}
                </router-link>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ doc.size }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge :variant="getStatusBadge(doc.status).variant" size="sm">
                  <component :is="getStatusBadge(doc.status).icon" class="w-3 h-3 mr-1" />
                  {{ getStatusBadge(doc.status).label }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(doc.uploadedAt) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button
                    @click="openPreview(doc)"
                    class="text-gray-400 hover:text-blue-600"
                    title="Preview"
                  >
                    <EyeIcon class="w-5 h-5" />
                  </button>
                  <button
                    @click="downloadDocument(doc)"
                    class="text-gray-400 hover:text-green-600"
                    title="Download"
                  >
                    <DocumentArrowDownIcon class="w-5 h-5" />
                  </button>
                  <button
                    @click="deleteDocument(doc)"
                    class="text-gray-400 hover:text-red-600"
                    title="Delete"
                  >
                    <TrashIcon class="w-5 h-5" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="paginatedDocuments.length === 0">
              <td colspan="7" class="px-6 py-12 text-center">
                <DocumentIcon class="w-12 h-12 mx-auto text-gray-300" />
                <p class="mt-2 text-sm text-gray-500">No documents found</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-6 py-4 border-t border-gray-200">
        <Pagination
          :current-page="currentPage"
          :total-pages="totalPages"
          @update:current-page="currentPage = $event"
        />
      </div>
    </Card>

    <!-- Upload Modal -->
    <Modal v-model="showUploadModal" title="Upload Document">
      <div class="space-y-4">
        <div
          class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors"
        >
          <CloudArrowUpIcon class="w-12 h-12 mx-auto text-gray-400" />
          <p class="mt-2 text-sm text-gray-600">Drag and drop files here, or click to browse</p>
          <input
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.png,.jpg,.jpeg"
            class="hidden"
            id="file-upload"
            @change="handleFileUpload"
          />
          <label for="file-upload">
            <Button variant="outline" class="mt-4" as="span">
              Select Files
            </Button>
          </label>
        </div>

        <div v-if="isUploading" class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span>Uploading...</span>
            <span>{{ uploadProgress }}%</span>
          </div>
          <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              class="h-full bg-blue-600 transition-all duration-300"
              :style="{ width: `${uploadProgress}%` }"
            />
          </div>
        </div>

        <p class="text-xs text-gray-500">
          Accepted formats: PDF, DOC, DOCX, PNG, JPG. Max size: 10MB per file.
        </p>
      </div>
    </Modal>

    <!-- Preview Modal -->
    <Modal v-model="showPreviewModal" :title="selectedDocument?.name || 'Document Preview'" size="lg">
      <div v-if="selectedDocument" class="space-y-4">
        <div class="bg-gray-100 rounded-lg p-8 text-center min-h-[400px] flex items-center justify-center">
          <div>
            <DocumentTextIcon class="w-16 h-16 mx-auto text-gray-400" />
            <p class="mt-4 text-gray-600">Document preview not available</p>
            <Button variant="outline" class="mt-4" @click="downloadDocument(selectedDocument)">
              <DocumentArrowDownIcon class="w-4 h-4 mr-2" />
              Download to View
            </Button>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-gray-500">Type:</span>
            <span class="ml-2 font-medium">{{ getTypeLabel(selectedDocument.type) }}</span>
          </div>
          <div>
            <span class="text-gray-500">Size:</span>
            <span class="ml-2 font-medium">{{ selectedDocument.size }}</span>
          </div>
          <div>
            <span class="text-gray-500">Claim ID:</span>
            <span class="ml-2 font-medium">{{ selectedDocument.claimId }}</span>
          </div>
          <div>
            <span class="text-gray-500">Uploaded:</span>
            <span class="ml-2 font-medium">{{ formatDate(selectedDocument.uploadedAt) }}</span>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>
