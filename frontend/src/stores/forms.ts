import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  FormDefinition, 
  FormTemplate, 
  FormFieldDefinition,
  TemplateVersion,
  PaginatedResponse 
} from '@/types'
import { formsService, templatesService } from '@/services/api'

export const useFormsStore = defineStore('forms', () => {
  // State
  const forms = ref<FormDefinition[]>([])
  const templates = ref<FormTemplate[]>([])
  const currentForm = ref<FormDefinition | null>(null)
  const currentTemplate = ref<FormTemplate | null>(null)
  const templateVersions = ref<TemplateVersion[]>([])
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeForms = computed(() => 
    forms.value.filter(f => f.isActive)
  )
  const activeTemplates = computed(() => 
    templates.value.filter(t => t.isActive)
  )
  const formById = computed(() => (id: string) => 
    forms.value.find(f => f.id === id)
  )
  const templateById = computed(() => (id: string) => 
    templates.value.find(t => t.id === id)
  )

  // Form Actions
  async function fetchForms(): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await formsService.list()
      forms.value = response.data.data || response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch forms'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchForm(id: string): Promise<FormDefinition> {
    isLoading.value = true
    error.value = null

    try {
      const response = await formsService.get(id)
      currentForm.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch form'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createForm(data: Partial<FormDefinition>): Promise<FormDefinition> {
    isSaving.value = true
    error.value = null

    try {
      const response = await formsService.create(data)
      const newForm: FormDefinition = response.data
      forms.value.push(newForm)
      currentForm.value = newForm
      return newForm
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create form'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function updateForm(id: string, data: Partial<FormDefinition>): Promise<FormDefinition> {
    isSaving.value = true
    error.value = null

    try {
      const response = await formsService.update(id, data)
      const updatedForm: FormDefinition = response.data
      
      const index = forms.value.findIndex(f => f.id === id)
      if (index !== -1) {
        forms.value[index] = updatedForm
      }
      
      if (currentForm.value?.id === id) {
        currentForm.value = updatedForm
      }
      
      return updatedForm
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update form'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function deleteForm(id: string): Promise<void> {
    isSaving.value = true
    error.value = null

    try {
      await formsService.delete(id)
      forms.value = forms.value.filter(f => f.id !== id)
      
      if (currentForm.value?.id === id) {
        currentForm.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete form'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function duplicateForm(id: string): Promise<FormDefinition> {
    isSaving.value = true
    error.value = null

    try {
      const response = await formsService.duplicate(id)
      const newForm: FormDefinition = response.data
      forms.value.push(newForm)
      return newForm
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to duplicate form'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  // Template Actions
  async function fetchTemplates(): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await templatesService.list()
      templates.value = response.data.data || response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch templates'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTemplate(id: string): Promise<FormTemplate> {
    isLoading.value = true
    error.value = null

    try {
      const response = await templatesService.get(id)
      currentTemplate.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch template'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createTemplate(data: Partial<FormTemplate>): Promise<FormTemplate> {
    isSaving.value = true
    error.value = null

    try {
      const response = await templatesService.create(data)
      const newTemplate: FormTemplate = response.data
      templates.value.push(newTemplate)
      currentTemplate.value = newTemplate
      return newTemplate
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create template'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function updateTemplate(id: string, data: Partial<FormTemplate>): Promise<FormTemplate> {
    isSaving.value = true
    error.value = null

    try {
      const response = await templatesService.update(id, data)
      const updatedTemplate: FormTemplate = response.data
      
      const index = templates.value.findIndex(t => t.id === id)
      if (index !== -1) {
        templates.value[index] = updatedTemplate
      }
      
      if (currentTemplate.value?.id === id) {
        currentTemplate.value = updatedTemplate
      }
      
      return updatedTemplate
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update template'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function deleteTemplate(id: string): Promise<void> {
    isSaving.value = true
    error.value = null

    try {
      await templatesService.delete(id)
      templates.value = templates.value.filter(t => t.id !== id)
      
      if (currentTemplate.value?.id === id) {
        currentTemplate.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete template'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function duplicateTemplate(id: string): Promise<FormTemplate> {
    isSaving.value = true
    error.value = null

    try {
      const response = await templatesService.duplicate(id)
      const newTemplate: FormTemplate = response.data
      templates.value.push(newTemplate)
      return newTemplate
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to duplicate template'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function fetchTemplateVersions(id: string): Promise<TemplateVersion[]> {
    isLoading.value = true
    error.value = null

    try {
      const response = await templatesService.getVersions(id)
      templateVersions.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch template versions'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function rollbackTemplate(id: string, versionId: string): Promise<FormTemplate> {
    isSaving.value = true
    error.value = null

    try {
      const response = await templatesService.rollback(id, versionId)
      const updatedTemplate: FormTemplate = response.data
      
      const index = templates.value.findIndex(t => t.id === id)
      if (index !== -1) {
        templates.value[index] = updatedTemplate
      }
      
      if (currentTemplate.value?.id === id) {
        currentTemplate.value = updatedTemplate
      }
      
      return updatedTemplate
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to rollback template'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  function clearCurrentForm(): void {
    currentForm.value = null
  }

  function clearCurrentTemplate(): void {
    currentTemplate.value = null
  }

  function clearError(): void {
    error.value = null
  }

  return {
    // State
    forms,
    templates,
    currentForm,
    currentTemplate,
    templateVersions,
    isLoading,
    isSaving,
    error,
    // Getters
    activeForms,
    activeTemplates,
    formById,
    templateById,
    // Form Actions
    fetchForms,
    fetchForm,
    createForm,
    updateForm,
    deleteForm,
    duplicateForm,
    // Template Actions
    fetchTemplates,
    fetchTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    duplicateTemplate,
    fetchTemplateVersions,
    rollbackTemplate,
    // Utility
    clearCurrentForm,
    clearCurrentTemplate,
    clearError,
  }
})
