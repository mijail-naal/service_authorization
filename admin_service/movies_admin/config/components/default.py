# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS').split(',')


# Api variables

PAGES = os.environ.get('VALUE_PAGE')
