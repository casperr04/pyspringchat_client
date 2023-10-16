import json

import requests
from stomp_ws import config


def try_token(token):
    """
    Checks the token to see if it is valid.
    :param token:
    :return: string username of the user if token is valid, boolean False if not.
    """
    endpoint = f"{config.config.get('backendurl')}/demo/controller"
    r = requests.get(endpoint, headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200:
        return False
    else:
        return r.text


class User:
    """
    Class for encapsulating user info, providing login and registration methods
    """
    def __init__(self, config):
        self.config = config
        self.endpoint = config.config.get("backendurl")
        self.id = None
        self.token = config.config.get("token")
        self.username = config.config.get("username")

    def login(self, password, passed_user=None):
        """
        Logs in the user
        :param password:
        :param passed_user: Username of the user, uses the objects own self.username if not passed.
        :return: Self
        """
        if passed_user is not None:
            self.username = passed_user
        endpoint = f"{self.endpoint}/v1/auth/login"
        payload = {"username": self.username, "password": password}
        r = requests.post(endpoint, json=payload)
        if r.status_code != 200:
            raise RequestException('Login failed')
        data = json.loads(r.text)
        self.token = data.get("token")
        self.id = data.get("id")
        return self

    def register(self, username, password):
        """
        Registers the user
        :param username:
        :param password:
        :return: Self
        """
        endpoint = f"{self.endpoint}/v1/auth/register"
        payload = {"username": username, "password": password}
        r = requests.post(endpoint, json=payload)
        if r.status_code != 200:
            raise RequestException(r.json())
        data = json.loads(r.text)
        self.token = data.get("token")
        self.id = data.get("id")
        self.username = username
        return self


class RequestException(requests.RequestException):
    pass
