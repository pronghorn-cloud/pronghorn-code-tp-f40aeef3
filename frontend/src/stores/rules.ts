import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  Rule, 
  RuleVersion, 
  RuleTestRequest, 
  RuleTestResult,
  RuleType,
  ConditionGroup 
} from '@/types'
import { rulesService } from '@/services/api'

export const useRulesStore = defineStore('rules', () => {
  // State
  const rules = ref<Rule[]>([])
  const currentRule = ref<Rule | null>(null)
  const ruleVersions = ref<RuleVersion[]>([])
  const testResult = ref<RuleTestResult | null>(null)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const isTesting = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeRules = computed(() => 
    rules.value.filter(r => r.isActive)
  )
  const validationRules = computed(() => 
    rules.value.filter(r => r.type === 'validation')
  )
  const adjudicationRules = computed(() => 
    rules.value.filter(r => r.type === 'adjudication')
  )
  const ruleById = computed(() => (id: string) => 
    rules.value.find(r => r.id === id)
  )
  const rulesByType = computed(() => (type: RuleType) => 
    rules.value.filter(r => r.type === type)
  )
  const sortedByPriority = computed(() => 
    [...rules.value].sort((a, b) => a.priority - b.priority)
  )

  // Actions
  async function fetchRules(params?: Record<string, any>): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await rulesService.list(params)
      rules.value = response.data.data || response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch rules'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRule(id: string): Promise<Rule> {
    isLoading.value = true
    error.value = null

    try {
      const response = await rulesService.get(id)
      currentRule.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch rule'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createRule(data: Partial<Rule>): Promise<Rule> {
    isSaving.value = true
    error.value = null

    try {
      const response = await rulesService.create(data)
      const newRule: Rule = response.data
      rules.value.push(newRule)
      currentRule.value = newRule
      return newRule
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create rule'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function updateRule(id: string, data: Partial<Rule>): Promise<Rule> {
    isSaving.value = true
    error.value = null

    try {
      const response = await rulesService.update(id, data)
      const updatedRule: Rule = response.data
      
      const index = rules.value.findIndex(r => r.id === id)
      if (index !== -1) {
        rules.value[index] = updatedRule
      }
      
      if (currentRule.value?.id === id) {
        currentRule.value = updatedRule
      }
      
      return updatedRule
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update rule'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function deleteRule(id: string): Promise<void> {
    isSaving.value = true
    error.value = null

    try {
      await rulesService.delete(id)
      rules.value = rules.value.filter(r => r.id !== id)
      
      if (currentRule.value?.id === id) {
        currentRule.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete rule'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function activateRule(id: string): Promise<Rule> {
    isSaving.value = true
    error.value = null

    try {
      const response = await rulesService.activate(id)
      const updatedRule: Rule = response.data
      
      const index = rules.value.findIndex(r => r.id === id)
      if (index !== -1) {
        rules.value[index] = updatedRule
      }
      
      if (currentRule.value?.id === id) {
        currentRule.value = updatedRule
      }
      
      return updatedRule
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to activate rule'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function deactivateRule(id: string): Promise<Rule> {
    isSaving.value = true
    error.value = null

    try {
      const response = await rulesService.deactivate(id)
      const updatedRule: Rule = response.data
      
      const index = rules.value.findIndex(r => r.id === id)
      if (index !== -1) {
        rules.value[index] = updatedRule
      }
      
      if (currentRule.value?.id === id) {
        currentRule.value = updatedRule
      }
      
      return updatedRule
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to deactivate rule'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function fetchRuleVersions(id: string): Promise<RuleVersion[]> {
    isLoading.value = true
    error.value = null

    try {
      const response = await rulesService.getVersions(id)
      ruleVersions.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch rule versions'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function rollbackRule(id: string, versionId: string): Promise<Rule> {
    isSaving.value = true
    error.value = null

    try {
      const response = await rulesService.rollback(id, versionId)
      const updatedRule: Rule = response.data
      
      const index = rules.value.findIndex(r => r.id === id)
      if (index !== -1) {
        rules.value[index] = updatedRule
      }
      
      if (currentRule.value?.id === id) {
        currentRule.value = updatedRule
      }
      
      return updatedRule
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to rollback rule'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function testRules(request: RuleTestRequest): Promise<RuleTestResult> {
    isTesting.value = true
    error.value = null
    testResult.value = null

    try {
      const response = await rulesService.test(request)
      testResult.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to test rules'
      throw err
    } finally {
      isTesting.value = false
    }
  }

  function clearCurrentRule(): void {
    currentRule.value = null
  }

  function clearTestResult(): void {
    testResult.value = null
  }

  function clearError(): void {
    error.value = null
  }

  return {
    // State
    rules,
    currentRule,
    ruleVersions,
    testResult,
    isLoading,
    isSaving,
    isTesting,
    error,
    // Getters
    activeRules,
    validationRules,
    adjudicationRules,
    ruleById,
    rulesByType,
    sortedByPriority,
    // Actions
    fetchRules,
    fetchRule,
    createRule,
    updateRule,
    deleteRule,
    activateRule,
    deactivateRule,
    fetchRuleVersions,
    rollbackRule,
    testRules,
    // Utility
    clearCurrentRule,
    clearTestResult,
    clearError,
  }
})
