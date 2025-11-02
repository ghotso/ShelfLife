# Adding Translations

This guide explains how to add new languages to ShelfLife.

## Overview

ShelfLife uses [i18next](https://www.i18next.com/) for internationalization. The translation system is simple and straightforward - all translations are stored in JSON files, and adding a new language requires just a few steps.

## Current Languages

- English (`en`) - Default
- German (`de`) - Deutsch

## Adding a New Language

### Step 1: Create Translation File

Create a new JSON file in `frontend/src/i18n/locales/` using the ISO 639-1 language code (2 letters):

- `fr.json` - French
- `es.json` - Spanish
- `it.json` - Italian
- `pt.json` - Portuguese
- `ja.json` - Japanese
- `zh.json` - Chinese
- etc.

**Copy the structure from `en.json`** and translate all the values:

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
  "rules": {
    "title": "Rules",
    "createRule": "Create Rule",
    "noRules": "No rules configured yet",
    ...
  },
  ...
}
```

**Important:**
- Keep all the keys exactly the same - only translate the values
- Maintain the JSON structure (nesting, arrays, etc.)
- Don't translate:
  - Technical terms that should remain in English (e.g., "Plex", "Radarr", "Sonarr")
  - Code values or identifiers
  - URLs or paths

### Step 2: Import and Register

Edit `frontend/src/i18n/index.ts`:

1. **Import** your new translation file at the top:

```typescript
import en from './locales/en.json'
import de from './locales/de.json'
import fr from './locales/fr.json'  // Add this line
```

2. **Add** it to the `resources` object:

```typescript
const resources = {
  en: { translation: en },
  de: { translation: de },
  fr: { translation: fr },  // Add this line
}
```

3. **Add** it to the `availableLanguages` array:

```typescript
export const availableLanguages = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'de', name: 'German', nativeName: 'Deutsch' },
  { code: 'fr', name: 'French', nativeName: 'Français' },  // Add this line
] as const
```

**Note:** The `nativeName` is how the language name appears in its own language (e.g., "Deutsch" for German, "Français" for French).

### Step 3: Test Your Translation

1. Start the development server:
   ```bash
   cd frontend
   npm run dev
   ```

2. Go to Settings in the ShelfLife UI

3. Check that your new language appears in the Language dropdown

4. Select your language and verify that the interface updates correctly

5. Navigate through all pages to ensure all strings are translated:
   - Dashboard
   - Rules
   - Candidates
   - Logs
   - Settings

### Step 4: Submit Your Translation

1. Create a pull request with:
   - Your new translation file (`frontend/src/i18n/locales/XX.json`)
   - Updated `frontend/src/i18n/index.ts`

2. In your PR description, mention:
   - Which language you're adding
   - Any questions or concerns about specific translations

## Translation Guidelines

### Keep Keys Unchanged

**Never modify the keys** - they are used throughout the codebase. Only translate the values:

```json
// ✅ Correct
{
  "rules": {
    "title": "Regeln"  // Translated value
  }
}

// ❌ Wrong
{
  "regeln": {  // Changed key - DON'T DO THIS!
    "title": "Regeln"
  }
}
```

### Maintain Structure

Keep the exact same JSON structure as the English file:

- Same nesting levels
- Same array structures
- Same key names

### Technical Terms

Some terms should remain in English:

- **Service names**: Plex, Radarr, Sonarr
- **Technical terms**: API, URL, HTTP
- **Brand names**: ShelfLife (unless there's an official translation)

Use your judgment - if a term is commonly translated in your language, translate it. Otherwise, keep it in English.

### Consistency

- Use consistent terminology throughout
- Match the tone and style of the English version
- Keep button labels, menu items, and error messages consistent

### Pluralization

ShelfLife uses simple pluralization. If your language has complex plural rules, you may need to adjust the translation to handle different cases:

```json
{
  "candidates": {
    "count": "{{count}} candidate",  // English
    "count_plural": "{{count}} candidates"  // English plural
  }
}
```

Some languages may need additional plural forms. Check i18next's pluralization rules for your language.

### Context and Clarity

- Translate for clarity, not word-for-word
- Adapt phrases to sound natural in your language
- Consider cultural differences where appropriate

## Updating Existing Translations

If you find translation errors or want to improve existing translations:

1. Edit the translation file directly
2. Test your changes
3. Submit a PR with improvements

## Missing Translations

If a translation is missing (you see a key like `translation.key.name`), it means:

1. The key exists in `en.json` but not in your language file
2. A new feature was added and the translation file wasn't updated

**To fix:**
1. Compare your translation file with `en.json`
2. Add the missing keys
3. Translate the values
4. Submit a PR

## Language Codes

Use standard ISO 639-1 language codes (2 letters):

| Code | Language | Native Name |
|------|----------|-------------|
| `en` | English | English |
| `de` | German | Deutsch |
| `fr` | French | Français |
| `es` | Spanish | Español |
| `it` | Italian | Italiano |
| `pt` | Portuguese | Português |
| `ru` | Russian | Русский |
| `ja` | Japanese | 日本語 |
| `zh` | Chinese | 中文 |
| `ko` | Korean | 한국어 |
| `nl` | Dutch | Nederlands |
| `sv` | Swedish | Svenska |
| `no` | Norwegian | Norsk |
| `da` | Danish | Dansk |
| `fi` | Finnish | Suomi |
| `pl` | Polish | Polski |
| `cs` | Czech | Čeština |

For more codes, see [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).

## Features

The translation system includes:

- ✅ **Automatic language detection** from browser settings
- ✅ **Language preference saved** in localStorage
- ✅ **Language preference synced** with backend settings
- ✅ **Easy to add new languages** (just 3 steps)
- ✅ **Type-safe language codes** with TypeScript
- ✅ **Dynamic language loading** - no page reload needed

## Troubleshooting

### Language doesn't appear in dropdown

- Check that you added it to `availableLanguages` array
- Verify the import is correct
- Check browser console for errors

### Some strings aren't translated

- Verify all keys exist in your translation file
- Compare with `en.json` to find missing keys
- Check for typos in key names

### Translation file has errors

- Validate JSON syntax (use a JSON validator)
- Ensure all brackets and quotes are properly closed
- Check for trailing commas

### Changes not appearing

- Clear browser cache
- Restart development server
- Check that the file is saved correctly

## Need Help?

- Check the [Contributing Guide](CONTRIBUTING.md) for general contribution guidelines
- Open an issue if you have questions
- Ask in discussions if you're unsure about a translation

Thank you for helping make ShelfLife accessible to more users! 🌍

---

*Documentation version: 1.0 | Last updated: 02.11.2025*

