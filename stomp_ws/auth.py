import json

import requests
from stomp_ws import config


def try_token(token):
    endpoint = f"{config.config.get('backendurl')}/demo/controller"
    r = requests.get(endpoint, headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200:
        return False
    else:
        return r.text


class User:
    def __init__(self, username, token=None, user_id=None):
        self.token = token
        self.id = user_id
        self.username = username

    def login(self, password):
        endpoint = f"{config.config.get('backendurl')}/v1/auth/login"
        payload = {"username": self.username, "password": password}
        r = requests.post(endpoint, json=payload)
        if r.status_code != 200:
            raise RequestException('Login failed')
        data = json.loads(r.text)
        self.token = data.get("token")
        self.id = data.get("id")

    def register(self, password):
        endpoint = f"{config.config.get('backendurl')}/v1/auth/register"
        payload = {"username": self.username, "password": password}
        r = requests.post(endpoint, json=payload)
        if r.status_code != 200:
            raise RequestException(r.json())
        data = json.loads(r.text)
        self.token = data.get("token")
        self.id = data.get("id")


class RequestException(requests.RequestException):
    pass
