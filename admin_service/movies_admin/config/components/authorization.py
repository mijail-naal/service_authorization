
# Default user model

AUTH_USER_MODEL = 'users.User'


AUTHENTICATION_BACKENDS = [
    'users.auth.CustomBackend',
]

AUTH_API_LOGIN_URL = os.environ.get('AUTH_API_LOGIN_URL', default='http://localhost:8001/api/v1/admin/signin')
