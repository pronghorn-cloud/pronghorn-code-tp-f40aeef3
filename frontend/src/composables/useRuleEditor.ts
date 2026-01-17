import { ref, computed, watch } from 'vue'
import { useToast } from 'vue-toastification'
import type { 
  Rule, 
  RuleType, 
  RuleAction, 
  ConditionGroup, 
  Condition,
  ConditionOperator,
  RuleTestResult 
} from '@/types'
import { useRulesStore } from '@/stores'

export interface UseRuleEditorOptions {
  ruleId?: string
}

const OPERATORS: { value: ConditionOperator; label: string }[] = [
  { value: '=', label: 'Equals' },
  { value: '!=', label: 'Not Equals' },
  { value: '>', label: 'Greater Than' },
  { value: '<', label: 'Less Than' },
  { value: '>=', label: 'Greater Than or Equal' },
  { value: '<=', label: 'Less Than or Equal' },
  { value: 'in', label: 'In List' },
  { value: 'not_in', label: 'Not In List' },
  { value: 'contains', label: 'Contains' },
  { value: 'starts_with', label: 'Starts With' },
]

const RULE_FIELDS = [
  { value: 'claim.totalAmount', label: 'Total Amount', type: 'number' },
  { value: 'claim.status', label: 'Claim Status', type: 'select' },
  { value: 'patient.age', label: 'Patient Age', type: 'number' },
  { value: 'patient.gender', label: 'Patient Gender', type: 'select' },
  { value: 'serviceLine.procedureCode', label: 'Procedure Code', type: 'text' },
  { value: 'serviceLine.quantity', label: 'Service Quantity', type: 'number' },
  { value: 'serviceLine.unitPrice', label: 'Unit Price', type: 'number' },
  { value: 'provider.npiNumber', label: 'Provider NPI', type: 'text' },
  { value: 'claim.serviceDate', label: 'Service Date', type: 'date' },
  { value: 'claim.submittedAt', label: 'Submission Date', type: 'date' },
]

export function useRuleEditor(options: UseRuleEditorOptions = {}) {
  const toast = useToast()
  const rulesStore = useRulesStore()

  // State
  const isLoading = ref(false)
  const isSaving = ref(false)
  const isTesting = ref(false)
  const isDirty = ref(false)
  const errors = ref<Record<string, string>>({})

  // Rule data
  const ruleId = ref<string | null>(options.ruleId || null)
  const name = ref('')
  const description = ref('')
  const type = ref<RuleType>('validation')
  const action = ref<RuleAction>('approve')
  const priority = ref(100)
  const isActive = ref(true)
  const effectiveFrom = ref('')
  const effectiveTo = ref('')

  // Condition builder
  const conditionLogic = ref<ConditionGroup>({
    type: 'AND',
    conditions: [],
  })

  // Test results
  const testResult = ref<RuleTestResult | null>(null)

  // Computed
  const isValid = computed(() => {
    return name.value.trim() !== '' && 
           conditionLogic.value.conditions.length > 0
  })

  const canSave = computed(() => isValid.value && !isSaving.value)

  const ruleData = computed<Partial<Rule>>(() => ({
    name: name.value,
    description: description.value,
    type: type.value,
    conditionLogic: conditionLogic.value,
    action: action.value,
    priority: priority.value,
    isActive: isActive.value,
    effectiveFrom: effectiveFrom.value,
    effectiveTo: effectiveTo.value || undefined,
  }))

  // Condition management
  function addCondition(parentGroup: ConditionGroup = conditionLogic.value): void {
    const newCondition: Condition = {
      field: '',
      operator: '=',
      value: '',
    }
    parentGroup.conditions.push(newCondition)
    isDirty.value = true
  }

  function addConditionGroup(
    type: 'AND' | 'OR' = 'AND', 
    parentGroup: ConditionGroup = conditionLogic.value
  ): void {
    const newGroup: ConditionGroup = {
      type,
      conditions: [],
    }
    parentGroup.conditions.push(newGroup)
    isDirty.value = true
  }

  function removeCondition(index: number, parentGroup: ConditionGroup = conditionLogic.value): void {
    parentGroup.conditions.splice(index, 1)
    isDirty.value = true
  }

  function updateCondition(
    index: number, 
    updates: Partial<Condition>,
    parentGroup: ConditionGroup = conditionLogic.value
  ): void {
    const condition = parentGroup.conditions[index]
    if (condition && 'field' in condition) {
      Object.assign(condition, updates)
      isDirty.value = true
    }
  }

  function toggleGroupType(group: ConditionGroup): void {
    group.type = group.type === 'AND' ? 'OR' : 'AND'
    isDirty.value = true
  }

  function isConditionGroup(item: Condition | ConditionGroup): item is ConditionGroup {
    return 'type' in item && 'conditions' in item
  }

  // Validation
  function validateRule(): boolean {
    const newErrors: Record<string, string> = {}

    if (!name.value.trim()) {
      newErrors.name = 'Rule name is required'
    }

    if (!effectiveFrom.value) {
      newErrors.effectiveFrom = 'Effective from date is required'
    }

    if (conditionLogic.value.conditions.length === 0) {
      newErrors.conditions = 'At least one condition is required'
    }

    // Validate each condition
    function validateConditions(group: ConditionGroup, path: string): void {
      group.conditions.forEach((item, index) => {
        if (isConditionGroup(item)) {
          validateConditions(item, `${path}.${index}`)
        } else {
          if (!item.field) {
            newErrors[`${path}.${index}.field`] = 'Field is required'
          }
          if (item.value === '' || item.value === null || item.value === undefined) {
            newErrors[`${path}.${index}.value`] = 'Value is required'
          }
        }
      })
    }

    validateConditions(conditionLogic.value, 'conditions')

    errors.value = newErrors
    return Object.keys(newErrors).length === 0
  }

  // Save operations
  async function saveRule(): Promise<boolean> {
    if (!validateRule()) {
      toast.error('Please fix validation errors')
      return false
    }

    isSaving.value = true

    try {
      if (ruleId.value) {
        await rulesStore.updateRule(ruleId.value, ruleData.value)
        toast.success('Rule updated successfully')
      } else {
        const newRule = await rulesStore.createRule(ruleData.value)
        ruleId.value = newRule.id
        toast.success('Rule created successfully')
      }

      isDirty.value = false
      return true
    } catch (error: any) {
      toast.error(error.message || 'Failed to save rule')
      return false
    } finally {
      isSaving.value = false
    }
  }

  // Test rule
  async function testRule(testClaimData?: Record<string, any>): Promise<void> {
    isTesting.value = true
    testResult.value = null

    try {
      const result = await rulesStore.testRules({
        ruleIds: ruleId.value ? [ruleId.value] : [],
        claimData: testClaimData,
      })
      testResult.value = result
    } catch (error: any) {
      toast.error(error.message || 'Failed to test rule')
    } finally {
      isTesting.value = false
    }
  }

  // Load existing rule
  async function loadRule(id: string): Promise<void> {
    isLoading.value = true

    try {
      const rule = await rulesStore.fetchRule(id)

      ruleId.value = rule.id
      name.value = rule.name
      description.value = rule.description || ''
      type.value = rule.type
      action.value = rule.action
      priority.value = rule.priority
      isActive.value = rule.isActive
      effectiveFrom.value = rule.effectiveFrom
      effectiveTo.value = rule.effectiveTo || ''
      conditionLogic.value = JSON.parse(JSON.stringify(rule.conditionLogic))

      isDirty.value = false
    } catch (error: any) {
      toast.error('Failed to load rule')
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Reset form
  function resetForm(): void {
    ruleId.value = null
    name.value = ''
    description.value = ''
    type.value = 'validation'
    action.value = 'approve'
    priority.value = 100
    isActive.value = true
    effectiveFrom.value = new Date().toISOString().split('T')[0]
    effectiveTo.value = ''
    conditionLogic.value = {
      type: 'AND',
      conditions: [],
    }
    errors.value = {}
    isDirty.value = false
    testResult.value = null
  }

  // Watch for changes
  watch(
    [name, description, type, action, priority, isActive, effectiveFrom, effectiveTo, conditionLogic],
    () => {
      isDirty.value = true
    },
    { deep: true }
  )

  return {
    // State
    isLoading,
    isSaving,
    isTesting,
    isDirty,
    errors,
    ruleId,
    name,
    description,
    type,
    action,
    priority,
    isActive,
    effectiveFrom,
    effectiveTo,
    conditionLogic,
    testResult,
    // Computed
    isValid,
    canSave,
    ruleData,
    // Constants
    OPERATORS,
    RULE_FIELDS,
    // Methods
    addCondition,
    addConditionGroup,
    removeCondition,
    updateCondition,
    toggleGroupType,
    isConditionGroup,
    validateRule,
    saveRule,
    testRule,
    loadRule,
    resetForm,
  }
}
