import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { getSettings } from '../lib/api'
import { scanAllRules } from '../lib/api'
import { Play } from 'lucide-react'

export default function Dashboard() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()

  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: () => getSettings().then((res) => res.data),
  })

  const scanMutation = useMutation({
    mutationFn: scanAllRules,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
      queryClient.invalidateQueries({ queryKey: ['logs'] })
    },
  })

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          {t('dashboard.title')}
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {t('app.tagline')}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            {t('dashboard.systemStatus')}
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Plex</span>
              <span
                className={`text-sm font-medium ${
                  settings?.plex_url ? 'text-green-600' : 'text-gray-400'
                }`}
              >
                {settings?.plex_url ? 'Connected' : 'Not configured'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Radarr</span>
              <span
                className={`text-sm font-medium ${
                  settings?.radarr_url ? 'text-green-600' : 'text-gray-400'
                }`}
              >
                {settings?.radarr_url ? 'Connected' : 'Not configured'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Sonarr</span>
              <span
                className={`text-sm font-medium ${
                  settings?.sonarr_url ? 'text-green-600' : 'text-gray-400'
                }`}
              >
                {settings?.sonarr_url ? 'Connected' : 'Not configured'}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            {t('dashboard.quickActions')}
          </h3>
          <button
            onClick={() => scanMutation.mutate()}
            disabled={scanMutation.isPending}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <Play className="w-4 h-4 mr-2" />
            {scanMutation.isPending ? 'Scanning...' : t('dashboard.scanAllRules')}
          </button>
        </div>
      </div>
    </div>
  )
}

