import http
import json
import requests
import logging

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


User = get_user_model()
logging.basicConfig(
    filename='log_data.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s. %(message)s - %(filename)s',
    datefmt='%d-%b-%y %H:%M:%S'
)


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {'email': username, 'password': password}

        try:
            response = requests.post(url, data=json.dumps(payload))
            if response.status_code != http.HTTPStatus.OK:
                return  None

            data = response.json()
            user, created = User.objects.get_or_create(id=data['id'],)
            user.email = data.get('email')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.is_admin = data.get('role_id') == 3
            user.is_active = data.get('is_active') or 1
            user.save()
        except Exception as ex:
            logging.error('The following exception has occurred:', ex)
            return None
        return user

    def get_user(self, user_id):
        try:
            return  User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
