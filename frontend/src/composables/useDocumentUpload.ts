import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import type { Document, DocumentType, DocumentUploadRequest } from '@/types'
import { documentsService } from '@/services/api'

export interface UploadingFile {
  id: string
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
  documentId?: string
}

export interface UseDocumentUploadOptions {
  claimId: string
  maxFileSize?: number // in bytes
  allowedTypes?: string[]
  maxFiles?: number
}

const DEFAULT_MAX_SIZE = 10 * 1024 * 1024 // 10MB
const DEFAULT_ALLOWED_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
]

export function useDocumentUpload(options: UseDocumentUploadOptions) {
  const toast = useToast()
  
  const {
    claimId,
    maxFileSize = DEFAULT_MAX_SIZE,
    allowedTypes = DEFAULT_ALLOWED_TYPES,
    maxFiles = 10,
  } = options

  // State
  const documents = ref<Document[]>([])
  const uploadingFiles = ref<UploadingFile[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasDocuments = computed(() => documents.value.length > 0)
  const isUploading = computed(() => 
    uploadingFiles.value.some(f => f.status === 'uploading')
  )
  const uploadProgress = computed(() => {
    if (uploadingFiles.value.length === 0) return 0
    const total = uploadingFiles.value.reduce((sum, f) => sum + f.progress, 0)
    return Math.round(total / uploadingFiles.value.length)
  })
  const canAddMore = computed(() => 
    documents.value.length + uploadingFiles.value.length < maxFiles
  )

  // Validation
  function validateFile(file: File): { valid: boolean; error?: string } {
    // Check file type
    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: `File type "${file.type}" is not allowed. Allowed types: PDF, JPEG, PNG, GIF, WebP`,
      }
    }

    // Check file size
    if (file.size > maxFileSize) {
      const maxMB = Math.round(maxFileSize / (1024 * 1024))
      return {
        valid: false,
        error: `File size exceeds ${maxMB}MB limit`,
      }
    }

    return { valid: true }
  }

  // Load existing documents
  async function loadDocuments(): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await documentsService.list(claimId)
      documents.value = response.data.data || response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to load documents'
    } finally {
      isLoading.value = false
    }
  }

  // Upload single file
  async function uploadFile(
    file: File, 
    documentType: DocumentType = 'other'
  ): Promise<Document | null> {
    const validation = validateFile(file)
    if (!validation.valid) {
      toast.error(validation.error!)
      return null
    }

    const uploadId = crypto.randomUUID()
    const uploadingFile: UploadingFile = {
      id: uploadId,
      file,
      progress: 0,
      status: 'pending',
    }

    uploadingFiles.value.push(uploadingFile)

    try {
      uploadingFile.status = 'uploading'

      // Step 1: Get pre-signed upload URL
      const urlResponse = await documentsService.getUploadUrl({
        claimId,
        fileName: file.name,
        fileType: file.type,
      })

      const { uploadUrl, documentId } = urlResponse.data
      uploadingFile.progress = 20

      // Step 2: Upload file to pre-signed URL
      await uploadToPresignedUrl(uploadUrl, file, (progress) => {
        uploadingFile.progress = 20 + Math.round(progress * 0.6)
      })

      uploadingFile.progress = 80

      // Step 3: Confirm upload
      const confirmResponse = await documentsService.confirmUpload(documentId, {
        documentType,
      })

      uploadingFile.progress = 100
      uploadingFile.status = 'success'
      uploadingFile.documentId = documentId

      const newDocument: Document = confirmResponse.data
      documents.value.push(newDocument)

      // Remove from uploading list after delay
      setTimeout(() => {
        const index = uploadingFiles.value.findIndex(f => f.id === uploadId)
        if (index !== -1) {
          uploadingFiles.value.splice(index, 1)
        }
      }, 2000)

      return newDocument
    } catch (err: any) {
      uploadingFile.status = 'error'
      uploadingFile.error = err.response?.data?.message || 'Upload failed'
      toast.error(`Failed to upload ${file.name}`)
      return null
    }
  }

  // Upload to pre-signed URL with progress tracking
  async function uploadToPresignedUrl(
    url: string, 
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          onProgress(event.loaded / event.total)
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve()
        } else {
          reject(new Error(`Upload failed with status ${xhr.status}`))
        }
      })

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed'))
      })

      xhr.open('PUT', url)
      xhr.setRequestHeader('Content-Type', file.type)
      xhr.send(file)
    })
  }

  // Upload multiple files
  async function uploadFiles(
    files: FileList | File[], 
    documentType: DocumentType = 'other'
  ): Promise<Document[]> {
    const fileArray = Array.from(files)
    const uploadedDocs: Document[] = []

    for (const file of fileArray) {
      if (!canAddMore.value) {
        toast.warning(`Maximum of ${maxFiles} files allowed`)
        break
      }

      const doc = await uploadFile(file, documentType)
      if (doc) {
        uploadedDocs.push(doc)
      }
    }

    return uploadedDocs
  }

  // Delete document
  async function deleteDocument(documentId: string): Promise<boolean> {
    try {
      await documentsService.delete(documentId)
      documents.value = documents.value.filter(d => d.id !== documentId)
      toast.success('Document deleted')
      return true
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to delete document')
      return false
    }
  }

  // Download document
  async function downloadDocument(documentId: string): Promise<void> {
    try {
      const response = await documentsService.download(documentId)
      const { downloadUrl } = response.data
      
      // Open download URL in new tab
      window.open(downloadUrl, '_blank')
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Failed to download document')
    }
  }

  // Cancel upload
  function cancelUpload(uploadId: string): void {
    const index = uploadingFiles.value.findIndex(f => f.id === uploadId)
    if (index !== -1) {
      uploadingFiles.value.splice(index, 1)
    }
  }

  // Clear all uploading files
  function clearUploads(): void {
    uploadingFiles.value = []
  }

  // Get file icon based on type
  function getFileIcon(fileType: string): string {
    if (fileType === 'application/pdf') return 'pdf'
    if (fileType.startsWith('image/')) return 'image'
    return 'document'
  }

  // Format file size
  function formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return {
    // State
    documents,
    uploadingFiles,
    isLoading,
    error,
    // Computed
    hasDocuments,
    isUploading,
    uploadProgress,
    canAddMore,
    // Methods
    validateFile,
    loadDocuments,
    uploadFile,
    uploadFiles,
    deleteDocument,
    downloadDocument,
    cancelUpload,
    clearUploads,
    getFileIcon,
    formatFileSize,
  }
}
