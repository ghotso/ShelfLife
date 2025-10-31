import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { toast } from 'react-hot-toast'
import { getRules, deleteRule, scanRule, updateRule, getLibraries } from '../lib/api'
import { Plus, Trash2, Play, Edit, ToggleLeft, ToggleRight, FileText, Filter, X } from 'lucide-react'
import { useState, useMemo } from 'react'
import RuleBuilder from '../components/RuleBuilder'
import ConfirmDialog from '../components/ConfirmDialog'

export default function Rules() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [showBuilder, setShowBuilder] = useState(false)
  const [editingRule, setEditingRule] = useState<any>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; ruleId: number | null }>({
    isOpen: false,
    ruleId: null,
  })
  const [selectedLibraryId, setSelectedLibraryId] = useState<number | null>(null)

  const { data: rules, isLoading } = useQuery({
    queryKey: ['rules'],
    queryFn: () => getRules().then((res) => res.data),
  })

  const { data: libraries } = useQuery({
    queryKey: ['libraries'],
    queryFn: () => getLibraries().then((res) => res.data),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] })
      toast.success('Rule deleted successfully')
      setDeleteConfirm({ isOpen: false, ruleId: null })
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || error?.message || 'Failed to delete rule')
    },
  })

  const scanMutation = useMutation({
    mutationFn: scanRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
    },
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, enabled }: { id: number; enabled: boolean }) =>
      updateRule(id, { enabled }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] })
    },
  })

  // Filter rules based on selected library
  const filteredRules = useMemo(() => {
    if (!rules) return []
    if (!selectedLibraryId) return rules
    return rules.filter((rule: any) => rule.library_id === selectedLibraryId)
  }, [rules, selectedLibraryId])

  const hasActiveFilter = selectedLibraryId !== null

  if (isLoading) {
    return <div className="p-6">Loading...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            {t('rules.title')}
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Define rules to automatically maintain your Plex libraries
          </p>
        </div>
        <button
          onClick={() => {
            setEditingRule(null)
            setShowBuilder(true)
          }}
          className="inline-flex items-center px-5 py-2.5 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 rounded-lg shadow-sm transition-all hover:shadow-md"
        >
          <Plus className="w-5 h-5 mr-2" />
          {t('rules.createRule')}
        </button>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <div className="flex items-center gap-2 flex-1">
          <Filter className="w-5 h-5 text-gray-400 dark:text-gray-500" />
          <select
            value={selectedLibraryId || ''}
            onChange={(e) => setSelectedLibraryId(e.target.value ? Number(e.target.value) : null)}
            className="flex-1 max-w-xs px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer"
          >
            <option value="">All Libraries</option>
            {libraries?.map((lib: any) => (
              <option key={lib.id} value={lib.id}>
                {lib.title} ({lib.library_type})
              </option>
            ))}
          </select>
        </div>
        {hasActiveFilter && (
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <span>
              Showing {filteredRules?.length || 0} of {rules?.length || 0} rule{filteredRules?.length !== 1 ? 's' : ''}
            </span>
            <button
              onClick={() => setSelectedLibraryId(null)}
              className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
              Clear filter
            </button>
          </div>
        )}
      </div>

      {showBuilder && (
        <RuleBuilder
          libraries={libraries || []}
          rule={editingRule}
          onClose={() => {
            setShowBuilder(false)
            setEditingRule(null)
          }}
          onSave={() => {
            setShowBuilder(false)
            setEditingRule(null)
            queryClient.invalidateQueries({ queryKey: ['rules'] })
          }}
        />
      )}

      {!rules || rules.length === 0 ? (
        <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="max-w-sm mx-auto">
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <FileText className="w-16 h-16 mx-auto" />
            </div>
            <p className="text-gray-600 dark:text-gray-400 font-medium">{t('rules.noRules')}</p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">Create your first rule to get started</p>
          </div>
        </div>
      ) : filteredRules && filteredRules.length === 0 ? (
        <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="max-w-sm mx-auto">
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <Filter className="w-16 h-16 mx-auto" />
            </div>
            <p className="text-gray-600 dark:text-gray-400 font-medium">No rules match the selected filter</p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">Try selecting a different library or clear the filter</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredRules.map((rule: any) => (
            <div
              key={rule.id}
              className="bg-white dark:bg-gray-800 shadow-sm rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {rule.name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1.5">
                    Library: <span className="font-medium text-gray-700 dark:text-gray-300">{rule.library?.title || 'Unknown'}</span>
                  </p>
                  <div className="mt-3 flex items-center space-x-3">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        rule.enabled
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                      }`}
                    >
                      {rule.enabled ? t('rules.enabled') : t('rules.disabled')}
                    </span>
                    {rule.dry_run && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                        {t('rules.dryRun')}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => toggleMutation.mutate({ id: rule.id, enabled: !rule.enabled })}
                    className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    title={rule.enabled ? 'Disable rule' : 'Enable rule'}
                  >
                    {rule.enabled ? (
                      <ToggleRight className="w-5 h-5" />
                    ) : (
                      <ToggleLeft className="w-5 h-5" />
                    )}
                  </button>
                  <button
                    onClick={() => scanMutation.mutate(rule.id)}
                    disabled={scanMutation.isPending}
                    className="p-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors disabled:opacity-50"
                    title="Scan rule"
                  >
                    <Play className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => {
                      setEditingRule(rule)
                      setShowBuilder(true)
                    }}
                    className="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    title="Edit rule"
                  >
                    <Edit className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => {
                      setDeleteConfirm({ isOpen: true, ruleId: rule.id })
                    }}
                    className="p-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                    title="Delete rule"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        title="Delete Rule"
        message="Are you sure you want to delete this rule? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={() => {
          if (deleteConfirm.ruleId) {
            deleteMutation.mutate(deleteConfirm.ruleId)
          }
        }}
        onCancel={() => setDeleteConfirm({ isOpen: false, ruleId: null })}
      />
    </div>
  )
}

