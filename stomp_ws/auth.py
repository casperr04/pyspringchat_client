import json

import requests
from stomp_ws import config


class User:
    def __init__(self, username, token=None, password=None, id=None):
        self.username = username
        self._login(password)

    def _login(self, password):
        endpoint = f"{config.config.get('backendurl')}/v1/auth/login"
        payload = {"username": self.username, "password": password}
        r = requests.post(endpoint, json=payload)
        if r.status_code != 200:
            raise RequestException('Login failed')
        data = json.loads(r.text)
        self.token = data.get("token")
        self.id = data.get("id")


class RequestException(requests.RequestException):
    pass
