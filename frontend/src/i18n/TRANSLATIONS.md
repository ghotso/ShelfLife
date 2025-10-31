# Adding New Languages

To add a new language to ShelfLife, follow these simple steps:

## Step 1: Create Translation File

Create a new JSON file in `frontend/src/i18n/locales/` with the language code (e.g., `fr.json` for French, `es.json` for Spanish).

Copy the structure from `en.json` and translate all the values:

```json
{
  "app": {
    "title": "ShelfLife",
    "tagline": "Keep your Plex libraries clean — automatically, safely, and visibly."
  },
  "nav": {
    "dashboard": "Dashboard",
    "rules": "Rules",
    "candidates": "Candidates",
    "logs": "Logs",
    "settings": "Settings"
  },
  ...
}
```

## Step 2: Import and Register

In `frontend/src/i18n/index.ts`:

1. **Import** your new translation file:
   ```typescript
   import fr from './locales/fr.json'
   ```

2. **Add** it to the `resources` object:
   ```typescript
   const resources = {
     en: { translation: en },
     de: { translation: de },
     fr: { translation: fr },  // Add this
   }
   ```

3. **Add** it to the `availableLanguages` array:
   ```typescript
   export const availableLanguages = [
     { code: 'en', name: 'English', nativeName: 'English' },
     { code: 'de', name: 'German', nativeName: 'Deutsch' },
     { code: 'fr', name: 'French', nativeName: 'Français' },  // Add this
   ] as const
   ```

## Step 3: Done!

The new language will automatically appear in the Settings page language dropdown. Users can select it and the entire application will switch to that language.

## Features

- ✅ Automatic language detection from browser settings
- ✅ Language preference saved in localStorage
- ✅ Language preference synced with backend settings
- ✅ Easy to add new languages (just 3 steps above)
- ✅ Type-safe language codes with TypeScript

## Language Codes

Use standard ISO 639-1 language codes (2 letters):
- `en` - English
- `de` - German  
- `fr` - French
- `es` - Spanish
- `it` - Italian
- `pt` - Portuguese
- `ja` - Japanese
- `zh` - Chinese
- etc.

