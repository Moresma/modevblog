from pathlib import Path

from django.conf import settings

# Fichiers dont la date de modification sert de "version".
_ASSETS = ["css/main.css", "js/main.js"]


def static_version(request):
    """
    Ajoute {{ static_version }} aux templates : un nombre qui change à chaque
    modification de main.css / main.js. Ajouté en ?v=... derrière l'adresse du
    fichier, il oblige le navigateur à recharger la nouvelle version au lieu
    d'utiliser une ancienne copie gardée en cache.
    """
    version = 0
    for folder in settings.STATICFILES_DIRS:
        for asset in _ASSETS:
            path = Path(folder) / asset
            if path.exists():
                version = max(version, int(path.stat().st_mtime))
    return {"static_version": version}
