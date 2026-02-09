import os
import json

# Directory containing this script and JSON files
LANG_DIR = os.path.dirname(os.path.abspath(__file__))
LANGUAGES = {}

def load_languages():
    """Loads all JSON language files from the current directory."""
    global LANGUAGES
    for filename in os.listdir(LANG_DIR):
        if filename.endswith('.json'):
            lang_code = filename.split('.')[0]
            try:
                with open(os.path.join(LANG_DIR, filename), 'r', encoding='utf-8') as f:
                    LANGUAGES[lang_code] = json.load(f)
            except Exception as e:
                print(f"Error loading language file {filename}: {e}")

# Initial load
load_languages()

def get_text(key, lang='fr'):
    """
    Retrieves the translation for a given key and language.
    Falls back to French if the language or key is missing.
    If the key is missing in 'fr' too, returns the key itself.
    """
    # specific fix for potential 'None' lang
    if not lang:
        lang = 'fr'

    # 1. Try exact match
    if lang in LANGUAGES and key in LANGUAGES[lang]:
        return LANGUAGES[lang][key]

    # 2. Fallback to 'fr' if we weren't already looking at it
    if lang != 'fr' and 'fr' in LANGUAGES and key in LANGUAGES['fr']:
        return LANGUAGES['fr'][key]

    # 3. Fallback: return the key itself
    return key

def get_message(key, lang='fr'):
    """
    Legacy wrapper for get_text to maintain backward compatibility.
    """
    return get_text(key, lang)
