from .settings import *
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use a faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging to file in tests to avoid FileNotFoundError if logs dir is missing
LOGGING['handlers']['file'] = {
    'level': 'INFO',
    'class': 'logging.NullHandler',
}

# Use simple static files storage for tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
