from .base import *  # noqa: F401,F403
from .base import os

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Clé de développement uniquement : ne jamais l'utiliser en production.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-...")
