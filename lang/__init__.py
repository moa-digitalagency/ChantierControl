# Language support
MESSAGES = {
    'fr': {
        'login_required': 'Veuillez vous connecter',
        'access_denied': 'Accès non autorisé',
        'success': 'Opération réussie',
        'error': 'Une erreur est survenue',
    }
}

def get_message(key, lang='fr'):
    return MESSAGES.get(lang, {}).get(key, key)
