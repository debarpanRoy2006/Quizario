import os
import dj_database_url

# Import all settings from the base settings.py file.
# Any settings defined here will override the base settings.
from .settings import *


# --- Core Deployment Settings ---

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# A new, secret key used only for production.
# This is loaded from an environment variable for security.
SECRET_KEY = os.environ.get('SECRET_KEY')

# The domain name(s) that this Django site can serve.
# Loaded from an environment variable.
ALLOWED_HOSTS = [os.environ.get('WEB_DOMAIN'), 'localhost']


# --- Database Configuration ---

# This configuration uses the DATABASE_URL environment variable
# to connect to a production database (e.g., PostgreSQL).
# Format: postgres://USER:PASSWORD@HOST:PORT/NAME
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}


# --- Static Files (CSS, JavaScript, Images) ---
# https://docs.djangoproject.com/en/stable/howto/static-files/
# http://whitenoise.evans.io/en/stable/

# The absolute path to the directory where collectstatic will collect static files for deployment.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Add WhiteNoise middleware to serve static files efficiently in production.
# It should be placed after the SecurityMiddleware.
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Use WhiteNoise's compressed manifest storage for caching and performance.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- Security Settings ---
# These settings enhance the security of your deployed application.

# Redirect all non-HTTPS requests to HTTPS.
SECURE_SSL_REDIRECT = True

# Ensure the session cookie is only sent over HTTPS.
SESSION_COOKIE_SECURE = True

# Ensure the CSRF cookie is only sent over HTTPS.
CSRF_COOKIE_SECURE = True

# Enable HTTP Strict Transport Security (HSTS) to prevent man-in-the-middle attacks.
# The value is the time in seconds browsers should remember to only access the site using HTTPS.
# Start with a small value (e.g., 3600 for 1 hour) and increase it once you are confident.
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

print("✅ Loaded PRODUCTION settings.")