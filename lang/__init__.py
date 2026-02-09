import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory containing this script and JSON files
LANG_DIR = os.path.dirname(os.path.abspath(__file__))
LANGUAGES = {}
DEFAULT_LANG = 'fr'

def load_languages():
    """Loads all JSON language files from the current directory."""
    global LANGUAGES
    LANGUAGES = {}
    try:
        if not os.path.exists(LANG_DIR):
            logger.error(f"Language directory not found: {LANG_DIR}")
            return

        for filename in os.listdir(LANG_DIR):
            if filename.endswith('.json'):
                lang_code = filename.split('.')[0]
                try:
                    with open(os.path.join(LANG_DIR, filename), 'r', encoding='utf-8') as f:
                        LANGUAGES[lang_code] = json.load(f)
                        logger.info(f"Loaded language: {lang_code}")
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing language file {filename}: {e}")
                except Exception as e:
                    logger.error(f"Error loading language file {filename}: {e}")
    except Exception as e:
        logger.error(f"Critical error loading languages: {e}")

# Initial load
load_languages()

def get_text(key, lang='fr'):
    """
    Retrieves the translation for a given key and language.
    Falls back to French if the language or key is missing.
    If the key is missing in 'fr' too, returns the key itself.
    """
    if key is None:
        return ""

    key = str(key)

    # specific fix for potential 'None' lang
    if not lang:
        lang = DEFAULT_LANG

    # Ensure languages are loaded
    if not LANGUAGES:
        load_languages()

    # 1. Try exact match
    if lang in LANGUAGES and key in LANGUAGES[lang]:
        return LANGUAGES[lang][key]

    # 2. Fallback to default language (fr) if we weren't already looking at it
    if lang != DEFAULT_LANG and DEFAULT_LANG in LANGUAGES and key in LANGUAGES[DEFAULT_LANG]:
        return LANGUAGES[DEFAULT_LANG][key]

    # 3. Fallback: return the key itself
    return key

def get_message(key, lang='fr'):
    """
    Legacy wrapper for get_text to maintain backward compatibility.
    """
    return get_text(key, lang)
