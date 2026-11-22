from .base import *  # noqa: F401,F403
from .base import os

DEBUG = False

# Obligatoire : lève KeyError au démarrage si la variable n'est pas définie.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

ALLOWED_HOSTS = [
    "monsite.com",
]
CSRF_TRUSTED_ORIGINS = ["https://monsite.com"]

# Sécurité HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Note : avec DEBUG=False, Django ne sert plus /static/ ni /media/.
# Il faut les servir via le serveur web (nginx…) ou whitenoise pour /static/.
