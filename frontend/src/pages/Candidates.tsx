import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { toast } from 'react-hot-toast'
import { getCandidates, addCandidateToCollection, getRules } from '../lib/api'
import { formatDate, formatRelativeTime } from '../lib/utils'
import { Film, Tv, FolderPlus, X, Search, Filter } from 'lucide-react'

export default function Candidates() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedCandidateId, setSelectedCandidateId] = useState<number | null>(null)
  const [collectionName, setCollectionName] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRuleId, setSelectedRuleId] = useState<number | null>(null)
  const [selectedItemType, setSelectedItemType] = useState<string>('all')

  const { data: candidates, isLoading } = useQuery({
    queryKey: ['candidates'],
    queryFn: () => getCandidates().then((res) => res.data),
  })

  const { data: rules } = useQuery({
    queryKey: ['rules'],
    queryFn: () => getRules().then((res) => res.data),
  })

  // Filter candidates based on search, rule, and item type
  const filteredCandidates = useMemo(() => {
    if (!candidates) return []

    return candidates.filter((candidate: any) => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        const matchesSearch =
          candidate.item_title?.toLowerCase().includes(query) ||
          candidate.show_title?.toLowerCase().includes(query) ||
          candidate.rule?.name?.toLowerCase().includes(query)
        if (!matchesSearch) return false
      }

      // Rule filter
      if (selectedRuleId !== null && candidate.rule?.id !== selectedRuleId) {
        return false
      }

      // Item type filter
      if (selectedItemType !== 'all' && candidate.item_type !== selectedItemType) {
        return false
      }

      return true
    })
  }, [candidates, searchQuery, selectedRuleId, selectedItemType])

  const addToCollectionMutation = useMutation({
    mutationFn: ({ candidateId, collectionName }: { candidateId: number; collectionName?: string }) =>
      addCandidateToCollection(candidateId, collectionName || 'Keep'),
    onSuccess: (_, variables) => {
      const finalCollectionName = variables.collectionName || 'Keep'
      toast.success(`Item added to "${finalCollectionName}" collection! The rule will be rescanned automatically.`)
      // Close modal and reset state
      setIsModalOpen(false)
      setCollectionName('')
      setSelectedCandidateId(null)
      // Invalidate candidates to refresh the list after rescan (with a short delay to allow rescan to complete)
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['candidates'] })
      }, 2000)
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || error?.message || 'Failed to add to collection')
    },
  })

  const handleAddToCollectionClick = (candidateId: number) => {
    setSelectedCandidateId(candidateId)
    setCollectionName('') // Reset collection name
    setIsModalOpen(true)
  }

  const handleModalSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (selectedCandidateId) {
      addToCollectionMutation.mutate({ 
        candidateId: selectedCandidateId, 
        collectionName: collectionName.trim() || undefined 
      })
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setCollectionName('')
    setSelectedCandidateId(null)
  }

  if (isLoading) {
    return <div className="p-6">Loading...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
          {t('candidates.title')}
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Items scheduled for removal based on your rules
        </p>
      </div>

      {/* Search and Filters */}
      {(candidates && candidates.length > 0) && (
        <div className="mb-6 space-y-4 sm:space-y-0 sm:flex sm:items-center sm:gap-4">
          {/* Search Input */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Search by title, show, or rule name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Rule Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500 pointer-events-none" />
            <select
              value={selectedRuleId === null ? 'all' : selectedRuleId}
              onChange={(e) => setSelectedRuleId(e.target.value === 'all' ? null : parseInt(e.target.value))}
              className="pl-10 pr-8 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none cursor-pointer"
            >
              <option value="all">All Rules</option>
              {rules?.map((rule: any) => (
                <option key={rule.id} value={rule.id}>
                  {rule.name}
                </option>
              ))}
            </select>
          </div>

          {/* Item Type Filter */}
          <select
            value={selectedItemType}
            onChange={(e) => setSelectedItemType(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none cursor-pointer"
          >
            <option value="all">All Types</option>
            <option value="movie">Movies</option>
            <option value="season">Seasons</option>
          </select>
        </div>
      )}

      {/* Results count */}
      {candidates && candidates.length > 0 && (
        <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
          Showing {filteredCandidates.length} of {candidates.length} candidate{candidates.length !== 1 ? 's' : ''}
          {(searchQuery || selectedRuleId !== null || selectedItemType !== 'all') && (
            <button
              onClick={() => {
                setSearchQuery('')
                setSelectedRuleId(null)
                setSelectedItemType('all')
              }}
              className="ml-2 text-blue-600 dark:text-blue-400 hover:underline"
            >
              Clear filters
            </button>
          )}
        </div>
      )}

      {!candidates || candidates.length === 0 ? (
        <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="max-w-sm mx-auto">
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <Tv className="w-16 h-16 mx-auto" />
            </div>
            <p className="text-gray-600 dark:text-gray-400 font-medium">{t('candidates.noCandidates')}</p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">No items are currently scheduled for removal</p>
          </div>
        </div>
      ) : filteredCandidates.length === 0 ? (
        <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="max-w-sm mx-auto">
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <Search className="w-16 h-16 mx-auto" />
            </div>
            <p className="text-gray-600 dark:text-gray-400 font-medium">No candidates match your filters</p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">Try adjusting your search or filter criteria</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredCandidates.map((candidate: any) => (
            <div
              key={candidate.id}
              className="bg-white dark:bg-gray-800 shadow-sm rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start gap-4">
                {/* Icon */}
                <div className="flex-shrink-0 mt-1">
                  {candidate.item_type === 'season' ? (
                    <Tv className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  ) : (
                    <Film className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {candidate.item_type === 'season' && candidate.show_title ? (
                            <>
                              {candidate.show_title}
                              <span className="text-gray-500 dark:text-gray-400 font-normal ml-2">
                                • {candidate.item_title}
                              </span>
                            </>
                          ) : (
                            candidate.item_title
                          )}
                        </h3>
                        {/* Action Button */}
                        <button
                          onClick={() => handleAddToCollectionClick(candidate.id)}
                          disabled={addToCollectionMutation.isPending}
                          className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-green-700 bg-green-50 dark:bg-green-900/30 dark:text-green-400 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                          title="Add to collection to prevent deletion"
                        >
                          <FolderPlus className="w-4 h-4 mr-1.5" />
                          {addToCollectionMutation.isPending ? 'Adding...' : 'Add to Collection'}
                        </button>
                      </div>

                      {/* Season episode info */}
                      {candidate.item_type === 'season' && (
                        <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
                          {candidate.episode_count !== null && candidate.episode_count !== undefined && (
                            <div className="flex items-center gap-2 text-sm mb-2">
                              <span className="font-medium text-gray-700 dark:text-gray-300">
                                Episodes:
                              </span>
                              <span className="text-gray-900 dark:text-white">
                                {candidate.episode_count} episode{candidate.episode_count !== 1 ? 's' : ''}
                              </span>
                            </div>
                          )}
                          
                          {candidate.last_watched_episode_title ? (
                            <>
                              <div className="flex items-center gap-2 text-sm">
                                <span className="font-medium text-gray-700 dark:text-gray-300">
                                  Last watched:
                                </span>
                                <span className="text-gray-900 dark:text-white">
                                  S{candidate.season_number}E{candidate.last_watched_episode_number} - {candidate.last_watched_episode_title}
                                </span>
                              </div>
                              {candidate.last_watched_episode_date && (
                                <div className="flex items-center gap-2 text-sm mt-1.5 text-gray-600 dark:text-gray-400">
                                  <span>{formatDate(candidate.last_watched_episode_date)}</span>
                                  <span className="text-gray-400">•</span>
                                  <span>{formatRelativeTime(candidate.last_watched_episode_date)}</span>
                                </div>
                              )}
                            </>
                          ) : (
                            <div className="flex items-center gap-2 text-sm">
                              <span className="font-medium text-gray-700 dark:text-gray-300">
                                Last watched:
                              </span>
                              <span className="text-gray-600 dark:text-gray-400 italic">
                                Never watched
                              </span>
                            </div>
                          )}
                        </div>
                      )}

                      {candidate.rule && (
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                          Rule: <span className="font-medium text-gray-700 dark:text-gray-300">{candidate.rule.name}</span>
                        </p>
                      )}

                      {candidate.scheduled_date && (
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                          <span className="font-medium">{t('candidates.scheduledDate')}:</span>{' '}
                          {formatDate(candidate.scheduled_date)}
                        </p>
                      )}

                      <div className="mt-3 flex flex-wrap gap-2">
                        {candidate.actions?.map((action: any, idx: number) => (
                          <span
                            key={idx}
                            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                          >
                            {action.type}
                            {action.delay_days > 0 && ` (${action.delay_days}d delay)`}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add to Collection Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50" onClick={handleModalClose}>
          <div 
            className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full border border-gray-200 dark:border-gray-700"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Add to Collection
                </h3>
                <button
                  onClick={handleModalClose}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <form onSubmit={handleModalSubmit}>
                <div className="mb-4">
                  <label htmlFor="collection-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Collection Name
                  </label>
                  <input
                    id="collection-name"
                    type="text"
                    value={collectionName}
                    onChange={(e) => setCollectionName(e.target.value)}
                    placeholder="Keep (default)"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    autoFocus
                  />
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    Leave empty to use "Keep" as the default collection name. The rule will be rescanned automatically after adding.
                  </p>
                </div>
                
                <div className="flex gap-3 justify-end">
                  <button
                    type="button"
                    onClick={handleModalClose}
                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={addToCollectionMutation.isPending}
                    className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {addToCollectionMutation.isPending ? 'Adding...' : 'Add to Collection'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

