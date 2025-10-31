import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

// Import all available language files
import en from './locales/en.json'
import de from './locales/de.json'

// List of available languages - add new languages here
export const availableLanguages = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'de', name: 'German', nativeName: 'Deutsch' },
] as const

export type LanguageCode = typeof availableLanguages[number]['code']

// Auto-generate resources from imports
const resources = {
  en: { translation: en },
  de: { translation: de },
}

// Get initial language from localStorage or browser, fallback to 'en'
const getInitialLanguage = (): string => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('shelflife-language')
    if (saved && availableLanguages.some(lang => lang.code === saved)) {
      return saved
    }
  }
  return 'en'
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: getInitialLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'shelflife-language',
      caches: ['localStorage'],
    },
  })

// Save language preference when changed
i18n.on('languageChanged', (lng) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('shelflife-language', lng)
  }
})

export default i18n

