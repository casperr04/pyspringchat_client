import json

import requests
import stomp_ws.exception as ex


class Requests:
    """
    Holds methods that interacts with the PySpringChat server API, except for authentication.
    """
    def __init__(self, config):
        self.config = config
        self.backendurl = config.config.get('backendurl')
        self.bearer = config.config.get('token')
        self.auth = {"Authorization": f"Bearer {self.bearer}"}

    def check_server_status(self):
        """
        Checks the status of the server
        :return: False if server is down, True if it is up.
        """
        endpoint = f"{self.backendurl}/demo/controller/public"
        try:
            r = requests.get(endpoint)
        except requests.exceptions.ConnectionError:
            return False
        if r.status_code != 200:
            return False
        else:
            return True

    def check_if_in_server(self, channel_id):
        """
        Checks if the currently logged user is in channel.
        :param channel_id:
        :return:
        """
        endpoint = f"{self.backendurl}/v1/channels/private-channel/check/{channel_id}"
        r = requests.get(endpoint, headers=self.auth)
        if r.status_code != 200:
            return False
        else:
            return True

    def create_private_channel(self, username):
        """
        Creates a private channel with a friend
        :param username: Username of a friended user to create a private channel with.
        :return:
        """
        endpoint = f"{self.backendurl}/v1/channels/private-channel/create/{username}"
        r = requests.post(endpoint, headers=self.auth)
        if r.status_code != 200:
            try:
                raise ex.RequestException(json.loads(r.text).get("message"))
            except KeyError:
                raise ex.RequestException("\nCouldn't create channel\n")
        else:
            return True

    def friend_user(self, username):
        """
        Send a friend request to a user.
        :param username:
        :return:
        """
        endpoint = f"{self.backendurl}/v1/friend/request/{username}"
        r = requests.post(endpoint, headers=self.auth)
        if r.status_code == 404:
            raise ex.RequestException("\nCouldn't send friend request\n")
        else:
            return True

    def private_channels(self) -> list:
        endpoint = f"{self.backendurl}/v1/channels/private-channel"
        r = requests.get(endpoint, headers=self.auth)
        if r.status_code == 404:
            raise ex.RequestException("\nCouldn't send friend request\n")
        else:
            return json.loads(r.text)
