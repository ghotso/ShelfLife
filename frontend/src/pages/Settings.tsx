import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'
import {
  getSettings,
  updateSettings,
  testPlexConnection,
  testRadarrConnection,
  testSonarrConnection,
  importLibraries,
} from '../lib/api'
import { CheckCircle, XCircle, Eye, EyeOff, Server, Film, Tv, Globe, Download } from 'lucide-react'
import { availableLanguages } from '../i18n'

const MASKED_TOKEN = '••••••••••••'

export default function Settings() {
  const { t, i18n } = useTranslation()
  const queryClient = useQueryClient()
  const [plexUrl, setPlexUrl] = useState('')
  const [plexToken, setPlexToken] = useState('')
  const [radarrUrl, setRadarrUrl] = useState('')
  const [radarrApiKey, setRadarrApiKey] = useState('')
  const [sonarrUrl, setSonarrUrl] = useState('')
  const [sonarrApiKey, setSonarrApiKey] = useState('')
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string }>>({})
  
  // Track whether tokens exist (for showing masked values)
  const [hasPlexToken, setHasPlexToken] = useState(false)
  const [hasRadarrKey, setHasRadarrKey] = useState(false)
  const [hasSonarrKey, setHasSonarrKey] = useState(false)
  
  // Track visibility of password fields
  const [showPlexToken, setShowPlexToken] = useState(false)
  const [showRadarrKey, setShowRadarrKey] = useState(false)
  const [showSonarrKey, setShowSonarrKey] = useState(false)

  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: () => getSettings().then((res) => res.data),
  })

  useEffect(() => {
    if (settings) {
      setPlexUrl(settings.plex_url || '')
      setRadarrUrl(settings.radarr_url || '')
      setSonarrUrl(settings.sonarr_url || '')
      
      // Backend doesn't return tokens for security, but we can infer they exist
      // if the URL is set (user likely configured it before)
      // Show masked token if URL exists but token field is empty
      if (settings.plex_url && !plexToken) {
        setHasPlexToken(true)
        setPlexToken(MASKED_TOKEN)
      }
      if (settings.radarr_url && !radarrApiKey) {
        setHasRadarrKey(true)
        setRadarrApiKey(MASKED_TOKEN)
      }
      if (settings.sonarr_url && !sonarrApiKey) {
        setHasSonarrKey(true)
        setSonarrApiKey(MASKED_TOKEN)
      }
    }
  }, [settings])

  const updateMutation = useMutation({
    mutationFn: updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      toast.success(t('settings.saved'))
      // Reset token visibility after save
      setShowPlexToken(false)
      setShowRadarrKey(false)
      setShowSonarrKey(false)
    },
  })

  const importLibrariesMutation = useMutation({
    mutationFn: importLibraries,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['libraries'] })
      toast.success('Libraries imported successfully')
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || error?.message || 'Failed to import libraries')
    },
  })

  const handleTest = async (service: 'plex' | 'radarr' | 'sonarr') => {
    try {
      let result
      if (service === 'plex') {
        // If token is masked, send empty string - backend will use stored token
        const tokenToUse = plexToken === MASKED_TOKEN ? '' : plexToken
        // If URL is empty, send empty string - backend will use stored URL
        const urlToUse = plexUrl || ''
        result = await testPlexConnection(urlToUse, tokenToUse)
      } else if (service === 'radarr') {
        const keyToUse = radarrApiKey === MASKED_TOKEN ? '' : radarrApiKey
        const urlToUse = radarrUrl || ''
        result = await testRadarrConnection(urlToUse, keyToUse)
      } else {
        const keyToUse = sonarrApiKey === MASKED_TOKEN ? '' : sonarrApiKey
        const urlToUse = sonarrUrl || ''
        result = await testSonarrConnection(urlToUse, keyToUse)
      }
      setTestResults({ ...testResults, [service]: result.data })
      if (result.data.success) {
        toast.success(`${service.charAt(0).toUpperCase() + service.slice(1)} connection test successful`)
      } else {
        toast.error(result.data.message || `Failed to test ${service} connection`)
      }
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || `Failed to test ${service} connection`
      setTestResults({
        ...testResults,
        [service]: { success: false, message: errorMessage },
      })
      toast.error(errorMessage)
    }
  }

  const handleSave = () => {
    updateMutation.mutate({
      plex_url: plexUrl,
      plex_token: plexToken === MASKED_TOKEN ? undefined : plexToken || undefined,
      radarr_url: radarrUrl,
      radarr_api_key: radarrApiKey === MASKED_TOKEN ? undefined : radarrApiKey || undefined,
      sonarr_url: sonarrUrl,
      sonarr_api_key: sonarrApiKey === MASKED_TOKEN ? undefined : sonarrApiKey || undefined,
      language: settings?.language || 'en',
      theme: settings?.theme || 'light',
      auth_enabled: settings?.auth_enabled || false,
    })
  }

  const handleLanguageChange = (lang: string) => {
    i18n.changeLanguage(lang)
    if (settings) {
      updateMutation.mutate({
        plex_url: plexUrl,
        plex_token: plexToken === MASKED_TOKEN ? undefined : plexToken || undefined,
        radarr_url: radarrUrl,
        radarr_api_key: radarrApiKey === MASKED_TOKEN ? undefined : radarrApiKey || undefined,
        sonarr_url: sonarrUrl,
        sonarr_api_key: sonarrApiKey === MASKED_TOKEN ? undefined : sonarrApiKey || undefined,
        language: lang,
        theme: settings.theme || 'light',
        auth_enabled: settings.auth_enabled || false,
      })
    }
  }

  const handleTokenChange = (value: string, type: 'plex' | 'radarr' | 'sonarr') => {
    // Clear masked token when user starts typing
    if (value === MASKED_TOKEN) {
      value = ''
    }
    if (type === 'plex') {
      setPlexToken(value)
      if (value && value !== MASKED_TOKEN) {
        setHasPlexToken(true)
      }
    } else if (type === 'radarr') {
      setRadarrApiKey(value)
      if (value && value !== MASKED_TOKEN) {
        setHasRadarrKey(true)
      }
    } else {
      setSonarrApiKey(value)
      if (value && value !== MASKED_TOKEN) {
        setHasSonarrKey(true)
      }
    }
  }

  const handleTokenFocus = (type: 'plex' | 'radarr' | 'sonarr') => {
    if (type === 'plex' && plexToken === MASKED_TOKEN) {
      setPlexToken('')
    } else if (type === 'radarr' && radarrApiKey === MASKED_TOKEN) {
      setRadarrApiKey('')
    } else if (type === 'sonarr' && sonarrApiKey === MASKED_TOKEN) {
      setSonarrApiKey('')
    }
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
          {t('settings.title')}
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Configure your Plex, Radarr, and Sonarr integrations
        </p>
      </div>

      <div className="space-y-6">
        {/* Plex Settings */}
        <div className="bg-white dark:bg-gray-800 shadow-sm rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <Server className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {t('settings.plex')}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">Plex Media Server configuration</p>
              </div>
            </div>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('settings.url')}
              </label>
              <input
                type="text"
                value={plexUrl}
                onChange={(e) => setPlexUrl(e.target.value)}
                placeholder="http://192.168.1.100:32400"
                className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('settings.token')}
              </label>
              <div className="relative">
                <input
                  type={showPlexToken ? 'text' : 'password'}
                  value={plexToken}
                  onChange={(e) => handleTokenChange(e.target.value, 'plex')}
                  onFocus={() => handleTokenFocus('plex')}
                  placeholder={hasPlexToken ? MASKED_TOKEN : 'Plex token'}
                  className="w-full px-4 py-2.5 pr-10 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPlexToken(!showPlexToken)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                  {showPlexToken ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>
            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={() => handleTest('plex')}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 rounded-lg transition-colors"
              >
                {t('settings.testConnection')}
              </button>
              {testResults.plex && (
                <div className="flex items-center gap-2">
                  {testResults.plex.success ? (
                    <>
                      <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                      <span className="text-sm text-green-600 dark:text-green-400 font-medium">
                        {testResults.plex.message}
                      </span>
                    </>
                  ) : (
                    <>
                      <XCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                      <span className="text-sm text-red-600 dark:text-red-400">
                        {testResults.plex.message}
                      </span>
                    </>
                  )}
                </div>
              )}
            </div>
            <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={() => importLibrariesMutation.mutate()}
                disabled={importLibrariesMutation.isPending}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-4 h-4" />
                {importLibrariesMutation.isPending ? 'Importing...' : 'Import Libraries'}
              </button>
            </div>
          </div>
        </div>

        {/* Radarr Settings */}
        <div className="bg-white dark:bg-gray-800 shadow-sm rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <Film className="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {t('settings.radarr')}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">Movie management configuration</p>
              </div>
            </div>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('settings.url')}
              </label>
              <input
                type="text"
                value={radarrUrl}
                onChange={(e) => setRadarrUrl(e.target.value)}
                placeholder="http://192.168.1.100:7878"
                className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('settings.apiKey')}
              </label>
              <div className="relative">
                <input
                  type={showRadarrKey ? 'text' : 'password'}
                  value={radarrApiKey}
                  onChange={(e) => handleTokenChange(e.target.value, 'radarr')}
                  onFocus={() => handleTokenFocus('radarr')}
                  placeholder={hasRadarrKey ? MASKED_TOKEN : 'Radarr API key'}
                  className="w-full px-4 py-2.5 pr-10 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowRadarrKey(!showRadarrKey)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                  {showRadarrKey ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>
            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={() => handleTest('radarr')}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 dark:bg-green-600 dark:hover:bg-green-700 rounded-lg transition-colors"
              >
                {t('settings.testConnection')}
              </button>
              {testResults.radarr && (
                <div className="flex items-center gap-2">
                  {testResults.radarr.success ? (
                    <>
                      <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                      <span className="text-sm text-green-600 dark:text-green-400 font-medium">
                        {testResults.radarr.message}
                      </span>
                    </>
                  ) : (
                    <>
                      <XCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                      <span className="text-sm text-red-600 dark:text-red-400">
                        {testResults.radarr.message}
                      </span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sonarr Settings */}
        <div className="bg-white dark:bg-gray-800 shadow-sm rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <Tv className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {t('settings.sonarr')}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">TV show management configuration</p>
              </div>
            </div>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('settings.url')}
              </label>
              <input
                type="text"
                value={sonarrUrl}
                onChange={(e) => setSonarrUrl(e.target.value)}
                placeholder="http://192.168.1.100:8989"
                className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('settings.apiKey')}
              </label>
              <div className="relative">
                <input
                  type={showSonarrKey ? 'text' : 'password'}
                  value={sonarrApiKey}
                  onChange={(e) => handleTokenChange(e.target.value, 'sonarr')}
                  onFocus={() => handleTokenFocus('sonarr')}
                  placeholder={hasSonarrKey ? MASKED_TOKEN : 'Sonarr API key'}
                  className="w-full px-4 py-2.5 pr-10 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowSonarrKey(!showSonarrKey)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                  {showSonarrKey ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>
            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={() => handleTest('sonarr')}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 dark:bg-purple-600 dark:hover:bg-purple-700 rounded-lg transition-colors"
              >
                {t('settings.testConnection')}
              </button>
              {testResults.sonarr && (
                <div className="flex items-center gap-2">
                  {testResults.sonarr.success ? (
                    <>
                      <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                      <span className="text-sm text-green-600 dark:text-green-400 font-medium">
                        {testResults.sonarr.message}
                      </span>
                    </>
                  ) : (
                    <>
                      <XCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                      <span className="text-sm text-red-600 dark:text-red-400">
                        {testResults.sonarr.message}
                      </span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* General Settings */}
        <div className="bg-white dark:bg-gray-800 shadow-sm rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <Globe className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  General
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">Application preferences</p>
              </div>
            </div>
          </div>
          <div className="p-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('settings.language')}
              </label>
              <select
                value={(settings as any)?.language || 'en'}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer"
              >
                {availableLanguages.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.nativeName} ({lang.name})
                  </option>
                ))}
              </select>
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                To add a new language, create a translation file in <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">frontend/src/i18n/locales/</code> and add it to <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">availableLanguages</code> in <code className="px-1 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">i18n/index.ts</code>
              </p>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="px-6 py-3 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 rounded-lg shadow-sm transition-all hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {updateMutation.isPending ? 'Saving...' : t('settings.save')}
          </button>
        </div>
      </div>
    </div>
  )
}
