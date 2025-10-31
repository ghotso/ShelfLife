import { useForm, useFieldArray, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { createRule, updateRule } from '../lib/api'
import { X, Plus, Trash2 } from 'lucide-react'
import { useEffect } from 'react'

// Allow empty strings - we'll filter out invalid conditions in onSubmit
const conditionSchema = z.object({
  field: z.string().default(''),
  operator: z.string().default(''),
  value: z.any().optional(),
})

const actionSchema = z.object({
  type: z.string().default(''), // Allow empty strings - we'll filter out invalid actions in onSubmit
  delay_days: z.number().nullable().optional(),
  collection_name: z.string().nullable().optional(), // Allow null values from form
  title_format: z.string().nullable().optional(), // Allow null values from form
})

// Custom validation for conditions - we'll validate in onSubmit instead
const ruleSchema = z.object({
  library_id: z.number().min(1),
  name: z.string().min(1),
  enabled: z.boolean(),
  dry_run: z.boolean(),
  logic: z.enum(['AND', 'OR']),
  conditions: z.array(conditionSchema), // Remove .min(1) - we'll validate in onSubmit
  immediate_actions: z.array(actionSchema),
  delayed_actions: z.array(actionSchema),
})

type RuleFormData = z.infer<typeof ruleSchema>

interface RuleBuilderProps {
  libraries: any[]
  rule?: any
  onClose: () => void
  onSave: () => void
}

const FIELD_OPTIONS = [
  { value: 'movie.lastPlayedDays', label: 'Days since last played (Movie)', type: 'number' },
  { value: 'movie.inCollections', label: 'In collections (Movie)', type: 'set' },
  { value: 'season.lastWatchedEpisodeDays', label: 'Days since last watched episode (Season)', type: 'number' },
  { value: 'season.inCollections', label: 'In collections (Season)', type: 'set' },
]

const OPERATOR_OPTIONS = {
  number: [
    { value: '>', label: 'Greater than' },
    { value: '>=', label: 'Greater than or equal' },
    { value: '<', label: 'Less than' },
    { value: '<=', label: 'Less than or equal' },
    { value: '=', label: 'Equal' },
    { value: '!=', label: 'Not equal' },
  ],
  boolean: [
    { value: 'IS_TRUE', label: 'Is true' },
    { value: 'IS_FALSE', label: 'Is false' },
  ],
  set: [
    { value: 'IN', label: 'In' },
    { value: 'NOT_IN', label: 'Not in' },
  ],
}

const ACTION_OPTIONS = {
  immediate: [
    { value: 'ADD_TO_COLLECTION', label: 'Add to collection' },
    { value: 'REMOVE_FROM_COLLECTION', label: 'Remove from collection' },
    { value: 'SET_TITLE_FORMAT', label: 'Set title format' },
    { value: 'CLEAR_TITLE_FORMAT', label: 'Clear title format' },
  ],
  delayed: [
    { value: 'DELETE_VIA_RADARR', label: 'Delete via Radarr' },
    { value: 'DELETE_VIA_SONARR', label: 'Delete via Sonarr' },
    { value: 'DELETE_IN_PLEX', label: 'Delete in Plex' },
    { value: 'REMOVE_FROM_COLLECTION', label: 'Remove from collection' },
    { value: 'CLEAR_TITLE_FORMAT', label: 'Clear title format' },
  ],
}

export default function RuleBuilder({ libraries, rule, onClose, onSave }: RuleBuilderProps) {
  const isEditing = !!rule

  const {
    register,
    control,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<RuleFormData>({
    resolver: zodResolver(ruleSchema),
    defaultValues: {
      library_id: libraries[0]?.id || 0,
      name: '',
      enabled: true,
      dry_run: true,
      logic: 'AND',
      conditions: [{ field: '', operator: '', value: '' }],
      immediate_actions: [],
      delayed_actions: [],
    },
  })

  // Reset form when rule changes (for editing)
  useEffect(() => {
    if (rule) {
      // Ensure conditions have proper default values
      const conditions = (rule.conditions || []).map((cond: any) => ({
        ...cond,
        value: cond.value !== null && cond.value !== undefined ? cond.value : '',
      }))
      
      // Normalize actions to use null instead of undefined for optional fields
      const normalizeActions = (actions: any[]) => {
        return (actions || []).map((action: any) => ({
          type: action.type || '',
          delay_days: action.delay_days ?? null,
          collection_name: action.collection_name ?? null,
          title_format: action.title_format ?? null,
        }))
      }
      
      reset({
        library_id: rule.library_id,
        name: rule.name,
        enabled: rule.enabled,
        dry_run: rule.dry_run,
        logic: rule.logic,
        conditions: conditions.length > 0 ? conditions : [{ field: '', operator: '', value: '' }],
        immediate_actions: normalizeActions(rule.immediate_actions),
        delayed_actions: normalizeActions(rule.delayed_actions),
      })
    } else {
      reset({
        library_id: libraries[0]?.id || 0,
        name: '',
        enabled: true,
        dry_run: true,
        logic: 'AND',
        conditions: [{ field: '', operator: '', value: '' }],
        immediate_actions: [],
        delayed_actions: [],
      })
    }
  }, [rule, reset, libraries])

  const {
    fields: conditionFields,
    append: appendCondition,
    remove: removeCondition,
  } = useFieldArray({
    control,
    name: 'conditions',
  })

  const {
    fields: immediateActionFields,
    append: appendImmediateAction,
    remove: removeImmediateAction,
  } = useFieldArray({
    control,
    name: 'immediate_actions',
  })

  const {
    fields: delayedActionFields,
    append: appendDelayedAction,
    remove: removeDelayedAction,
  } = useFieldArray({
    control,
    name: 'delayed_actions',
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => {
      console.log('🔄 Calling createRule API:', data)
      return createRule(data)
    },
    onSuccess: () => {
      console.log('✅ Rule created successfully')
      toast.success('Rule created successfully')
      onSave()
    },
    onError: (error: any) => {
      console.error('❌ Error creating rule:', error)
      toast.error(error?.response?.data?.detail || error?.message || 'Failed to create rule')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => {
      console.log('🔄 Calling updateRule API:', { id, data })
      return updateRule(id, data)
    },
    onSuccess: () => {
      console.log('✅ Rule updated successfully')
      toast.success('Rule updated successfully')
      onSave()
    },
    onError: (error: any) => {
      console.error('❌ Error updating rule:', error)
      toast.error(error?.response?.data?.detail || error?.message || 'Failed to update rule')
    },
  })

  const onSubmit = (data: RuleFormData) => {
    console.log('=== FORM SUBMISSION ===')
    console.log('Form data:', JSON.stringify(data, null, 2))
    console.log('Form errors:', errors)
    
    // Process all conditions from form data
    const conditions: any[] = []
    const formConditions = data.conditions || []
    console.log('Form conditions array:', formConditions)
    console.log('Form conditions length:', formConditions.length)
    
    for (let idx = 0; idx < formConditions.length; idx++) {
      const condition = formConditions[idx]
      const field = condition?.field
      const operator = condition?.operator
      let value = condition?.value
      
      console.log(`\nCondition ${idx}:`)
      console.log(`  field = "${field}"`)
      console.log(`  operator = "${operator}"`)
      console.log(`  value =`, value, `(type: ${typeof value})`)
      
      // Skip if missing field or operator
      if (!field || !operator) {
        console.log(`  ❌ Skipping - missing field or operator`)
        continue
      }
      
      // For set operations (IN/NOT_IN), validate and process value
      if (operator === 'IN' || operator === 'NOT_IN') {
        // Handle null, undefined, NaN, empty string
        let valueStr = ''
        if (value !== null && value !== undefined && value !== '' && String(value) !== 'NaN') {
          valueStr = String(value).trim()
        }
        
        console.log(`  Set operation - processed value: "${valueStr}"`)
        
        if (!valueStr) {
          console.log(`  ❌ Skipping - empty value for ${operator}`)
          continue
        }
        
        conditions.push({
          field: field,
          operator: operator,
          value: valueStr,
        })
        console.log(`  ✅ Added condition`)
      } else {
        // For other operations (number comparisons), allow empty value
        // Empty means the condition will use the field value directly
        const processedValue = (value !== null && value !== undefined && String(value) !== 'NaN') ? value : ''
        conditions.push({
          field: field,
          operator: operator,
          value: processedValue,
        })
        console.log(`  ✅ Added condition`)
      }
    }
    
    console.log('\n=== FINAL CONDITIONS ===')
    console.log(JSON.stringify(conditions, null, 2))
    console.log(`Total: ${conditions.length} condition(s)`)

    if (conditions.length === 0) {
      console.error('❌ NO VALID CONDITIONS!')
      toast.error('Please add at least one valid condition')
      return
    }

    // Process immediate actions - filter out invalid ones (empty type)
    const immediate_actions = (data.immediate_actions || []).filter((action: any) => {
      return action.type && action.type.trim() !== ''
    }).map((action: any) => {
      const processed: any = { type: action.type }
      // Only include collection_name if it's a non-empty string
      if (action.collection_name && String(action.collection_name).trim() !== '') {
        processed.collection_name = String(action.collection_name).trim()
      }
      // Only include title_format if it's a non-empty string
      if (action.title_format && String(action.title_format).trim() !== '') {
        processed.title_format = String(action.title_format).trim()
      }
      return processed
    })

    // Process delayed actions - filter out invalid ones (empty type)
    const delayed_actions = (data.delayed_actions || []).filter((action: any) => {
      return action.type && action.type.trim() !== ''
    }).map((action: any) => {
      const processed: any = { type: action.type }
      // Only include delay_days if it's a valid number
      if (action.delay_days !== undefined && action.delay_days !== null && !isNaN(Number(action.delay_days))) {
        processed.delay_days = Number(action.delay_days)
      }
      // Only include collection_name if it's a non-empty string
      if (action.collection_name && String(action.collection_name).trim() !== '') {
        processed.collection_name = String(action.collection_name).trim()
      }
      return processed
    })

    // Build the payload with all form data
    const payload: any = {
      name: data.name,
      enabled: data.enabled,
      dry_run: data.dry_run,
      logic: data.logic,
      conditions: conditions,
      immediate_actions: immediate_actions,
      delayed_actions: delayed_actions,
    }

    console.log('\n=== FINAL PAYLOAD ===')
    console.log(JSON.stringify(payload, null, 2))

    if (isEditing) {
      console.log('✅ Updating rule')
      updateMutation.mutate({ id: rule.id, data: payload })
    } else {
      payload.library_id = data.library_id
      console.log('✅ Creating rule')
      createMutation.mutate(payload)
    }
  }

  const getFieldType = (fieldValue: string) => {
    const field = FIELD_OPTIONS.find((f) => f.value === fieldValue)
    return field?.type || 'number'
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm overflow-y-auto h-full w-full z-50 flex items-start justify-center p-4 pt-12 pb-12">
      <div className="relative w-full max-w-4xl bg-white dark:bg-gray-800 shadow-2xl rounded-xl border border-gray-200 dark:border-gray-700 animate-in fade-in slide-in-from-top-4 duration-200">
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 rounded-t-xl">
          <div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
              {isEditing ? 'Edit Rule' : 'Create Rule'}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
              Configure conditions and actions for automated library maintenance
            </p>
          </div>
          <button 
            onClick={onClose} 
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form 
          onSubmit={handleSubmit(
            (data) => {
              console.log('✅ Form validation passed, calling onSubmit')
              onSubmit(data)
            },
            (errors) => {
              console.error('❌ Form validation failed:', errors)
              toast.error('Please fix form errors before saving')
            }
          )} 
          className="px-6 py-6 space-y-6"
        >
          {/* Basic Information */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Rule Name <span className="text-red-500">*</span>
              </label>
              <input
                {...register('name')}
                placeholder="e.g., Clean up unwatched movies"
                className="block w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              {errors.name && <p className="text-red-500 text-sm mt-1.5 flex items-center gap-1">
                <span>⚠</span> {errors.name.message}
              </p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  Library <span className="text-red-500">*</span>
                </label>
                <select
                  {...register('library_id', { valueAsNumber: true })}
                  className="block w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer"
                >
                  {libraries.map((lib) => (
                    <option key={lib.id} value={lib.id}>
                      {lib.title} ({lib.library_type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  Logic
                </label>
                <select
                  {...register('logic')}
                  className="block w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer"
                >
                  <option value="AND">AND (all conditions must match)</option>
                  <option value="OR">OR (any condition must match)</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-6 p-4 bg-gray-50 dark:bg-gray-900/30 rounded-lg">
              <label className="flex items-center cursor-pointer group">
                <input 
                  type="checkbox" 
                  {...register('enabled')} 
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer" 
                />
                <span className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-gray-100">
                  Enabled
                </span>
              </label>
              <label className="flex items-center cursor-pointer group">
                <input 
                  type="checkbox" 
                  {...register('dry_run')} 
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer" 
                />
                <span className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-gray-100">
                  Dry Run (preview only)
                </span>
              </label>
            </div>
          </div>

          {/* Conditions Section */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <div className="flex justify-between items-center mb-4">
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100">
                  Conditions
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  Define when this rule should apply
                </p>
              </div>
              <button
                type="button"
                onClick={() => appendCondition({ field: '', operator: '', value: '' })}
                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 dark:bg-blue-900/30 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
              >
                <Plus className="w-4 h-4 mr-1.5" />
                Add Condition
              </button>
            </div>
            {conditionFields.map((field, index) => {
              const fieldValue = watch(`conditions.${index}.field`)
              const fieldType = getFieldType(fieldValue)
              const operators = OPERATOR_OPTIONS[fieldType as keyof typeof OPERATOR_OPTIONS] || []

              return (
                <div key={field.id} className="p-4 bg-gray-50 dark:bg-gray-900/30 rounded-lg border border-gray-200 dark:border-gray-700 mb-3">
                  <div className="flex gap-3 items-start">
                    <div className="flex-1 grid grid-cols-3 gap-3">
                      <select
                        {...register(`conditions.${index}.field`)}
                        className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer"
                      >
                        <option value="">Select field...</option>
                        {FIELD_OPTIONS.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                      <select
                        {...register(`conditions.${index}.operator`)}
                        className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer"
                      >
                        <option value="">Select operator...</option>
                        {operators.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                      {fieldType === 'number' && (
                        <input
                          type="number"
                          {...register(`conditions.${index}.value`, { valueAsNumber: true })}
                          placeholder="Value"
                          className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        />
                      )}
                      {fieldType === 'boolean' && (
                        <select
                          {...register(`conditions.${index}.value`)}
                          className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer"
                        >
                          <option value="">N/A</option>
                        </select>
                      )}
                      {fieldType === 'set' && (
                        <Controller
                          name={`conditions.${index}.value`}
                          control={control}
                          defaultValue=""
                          rules={{
                            validate: (value) => {
                              const operator = watch(`conditions.${index}.operator`)
                              if ((operator === 'IN' || operator === 'NOT_IN') && (!value || String(value).trim() === '')) {
                                return 'Collection name is required'
                              }
                              return true
                            }
                          }}
                          render={({ field }) => (
                            <input
                              type="text"
                              {...field}
                              value={field.value || ""}
                              placeholder="Collection name"
                              className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                              onChange={(e) => {
                                field.onChange(e.target.value)
                              }}
                            />
                          )}
                        />
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeCondition(index)}
                      className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                      title="Remove condition"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  {errors.conditions?.[index]?.value && (
                    <p className="text-red-500 text-xs mt-2 flex items-center gap-1">
                      <span>⚠</span> {String(errors.conditions[index]?.value?.message || 'Invalid value')}
                    </p>
                  )}
                </div>
              )
            })}
          </div>

          {/* Immediate Actions Section */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <div className="flex justify-between items-center mb-4">
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100">
                  Immediate Actions
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  Actions executed immediately when conditions match
                </p>
              </div>
              <button
                type="button"
                onClick={() => appendImmediateAction({ type: '', collection_name: null, title_format: null })}
                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 dark:bg-blue-900/30 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
              >
                <Plus className="w-4 h-4 mr-1.5" />
                Add Action
              </button>
            </div>
            {immediateActionFields.map((field, index) => {
              const actionType = watch(`immediate_actions.${index}.type`)
              return (
                <div key={field.id} className="p-4 bg-gray-50 dark:bg-gray-900/30 rounded-lg border border-gray-200 dark:border-gray-700 mb-3">
                  <div className="flex gap-3 items-start">
                    <div className="flex-1 flex flex-col gap-3">
                      <div className="flex gap-3 items-start">
                        <select
                          {...register(`immediate_actions.${index}.type`)}
                          className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer"
                          style={{ minWidth: '200px' }}
                        >
                          <option value="">Select action...</option>
                          {ACTION_OPTIONS.immediate.map((opt) => (
                            <option key={opt.value} value={opt.value}>
                              {opt.label}
                            </option>
                          ))}
                        </select>
                        {(actionType === 'ADD_TO_COLLECTION' || actionType === 'REMOVE_FROM_COLLECTION') && (
                          <input
                            type="text"
                            {...register(`immediate_actions.${index}.collection_name`)}
                            placeholder="Collection name"
                            className="flex-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                          />
                        )}
                        {actionType === 'SET_TITLE_FORMAT' && (
                          <input
                            type="text"
                            {...register(`immediate_actions.${index}.title_format`)}
                            placeholder="e.g., [Archived] Movie Title"
                            className="flex-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                          />
                        )}
                        <button
                          type="button"
                          onClick={() => removeImmediateAction(index)}
                          className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                          title="Remove action"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      {actionType === 'SET_TITLE_FORMAT' && (
                        <div className="w-full">
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            <span className="text-gray-400 dark:text-gray-500">Variables: </span>
                            <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs ml-1">{"{title}"}</code> - Original title
                            <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs ml-1">{"{deletion_date}"}</code> - Deletion date (YYYY-MM-DD)
                            <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs ml-1">{"{deletion_date_readable}"}</code> - Readable date
                            <br />
                            <span className="text-gray-400 dark:text-gray-500">Examples: </span>
                            <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs">[Archived] {`{title}`}</code>, 
                            <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs ml-1">{`{title}`} - Deletes {`{deletion_date}`}</code>
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Delayed Actions Section */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <div className="flex justify-between items-center mb-4">
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100">
                  Delayed Actions
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  Actions executed after a delay (scheduled as candidates)
                </p>
              </div>
              <button
                type="button"
                onClick={() => appendDelayedAction({ type: '', delay_days: null, collection_name: null })}
                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 dark:bg-blue-900/30 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
              >
                <Plus className="w-4 h-4 mr-1.5" />
                Add Action
              </button>
            </div>
            {delayedActionFields.map((field, index) => {
              const actionType = watch(`delayed_actions.${index}.type`)
              return (
                <div key={field.id} className="p-4 bg-gray-50 dark:bg-gray-900/30 rounded-lg border border-gray-200 dark:border-gray-700 mb-3">
                  <div className="flex gap-3 items-start">
                    <div className="flex-1 flex gap-3">
                      <select
                        {...register(`delayed_actions.${index}.type`)}
                        className="flex-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer"
                      >
                        <option value="">Select action...</option>
                        {ACTION_OPTIONS.delayed.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                      <input
                        type="number"
                        {...register(`delayed_actions.${index}.delay_days`, { valueAsNumber: true })}
                        className="w-28 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        placeholder="Days"
                        min="0"
                      />
                      {actionType === 'REMOVE_FROM_COLLECTION' && (
                        <input
                          type="text"
                          {...register(`delayed_actions.${index}.collection_name`)}
                          placeholder="Collection name"
                          className="flex-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        />
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeDelayedAction(index)}
                      className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                      title="Remove action"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 pt-6 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
              className="px-5 py-2.5 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {createMutation.isPending || updateMutation.isPending
                ? 'Saving...'
                : isEditing
                ? 'Update Rule'
                : 'Create Rule'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

